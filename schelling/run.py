"""Run the paired grid and the solo marginals (PREREGISTRATION.md).

One API call per agent, nothing passed between agents. Every request and raw
reply is appended to a JSONL file under results/. Finished pairs and solos are
skipped on rerun, so the script is resumable. Several workers can run at once;
each writes its own file.

  python -m schelling.run --smoke                   # one pair + one solo, results/smoke/
  python -m schelling.run --worker 0 --workers 2    # full grid
  python -m schelling.run --only-solo               # solo marginals only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from schelling.prompts import (CONDITIONS, GEMINI, GPT, MENUS, N_PAIRS, N_SOLO, SOLO_SPECS,
                               TEMPERATURE, option_order, render)

RESULTS = Path(__file__).resolve().parent / "results"
SPEND_CAP_USD = 20.0
MAX_ATTEMPTS = 3

# OpenRouter list prices, USD per million tokens (prompt, completion), 7 Nov 2026.
PRICES = {GPT: (0.40, 1.60), GEMINI: (0.30, 2.50)}


def make_client() -> OpenAI:
    load_dotenv()
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY not set (put it in .env)")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)


def request_extras(model: str) -> dict:
    """Gemini 2.5 thinks by default; turn it off so the reply is the bare JSON."""
    return {"reasoning": {"enabled": False}} if "gemini" in model else {}


def parse_choice(text: str, options: list[str]) -> str | None:
    """Option named in '"choice": "<x>"' (case-insensitive), else the unique option
    mentioned anywhere in the text, else None."""
    lower = {o.lower(): o for o in options}
    m = re.search(r'"choice"\s*:\s*"([^"]+)"', text)
    if m:
        val = m.group(1).strip().lower()
        if val in lower:
            return lower[val]
    found = [o for o in options if re.search(r"\b" + re.escape(o) + r"\b", text, re.IGNORECASE)]
    if len(found) == 1:
        return found[0]
    return None


def cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    p_in, p_out = PRICES[model]
    return (prompt_tokens * p_in + completion_tokens * p_out) / 1e6


def one_call(client: OpenAI, model: str, prompt: str, options: list[str]) -> dict:
    """One agent's decision. Retries parse failures and transport errors."""
    attempts = []
    choice = None
    usage = {"prompt": 0, "completion": 0}
    for attempt in range(MAX_ATTEMPTS):
        try:
            resp = client.chat.completions.create(
                model=model, temperature=TEMPERATURE, max_tokens=40,
                messages=[{"role": "user", "content": prompt}],
                extra_body=request_extras(model),
            )
        except Exception as exc:  # rate limit or network: back off, retry
            attempts.append({"raw": f"ERROR {exc}"})
            time.sleep(3 + 7 * attempt)
            continue
        raw = resp.choices[0].message.content or ""
        if resp.usage:
            usage["prompt"] += resp.usage.prompt_tokens
            usage["completion"] += resp.usage.completion_tokens
        attempts.append({"raw": raw})
        choice = parse_choice(raw, options)
        if choice is not None:
            break
    return {"model": model, "prompt": prompt, "options": options, "attempts": attempts,
            "choice": choice, "usage": usage,
            "cost_usd": cost_usd(model, usage["prompt"], usage["completion"])}


def pair_jobs() -> list[dict]:
    out = []
    for menu in MENUS:
        for cond in CONDITIONS:
            for k in range(N_PAIRS):
                out.append({"kind": "pair", "menu": menu, "condition": cond, "pair": k})
    return out


def solo_jobs() -> list[dict]:
    out = []
    for menu in MENUS:
        for model, variant in SOLO_SPECS:
            for k in range(N_SOLO):
                out.append({"kind": "solo", "menu": menu, "model": model, "variant": variant,
                            "index": k})
    return out


def job_key(j: dict) -> str:
    if j["kind"] == "pair":
        return f"pair|{j['menu']}|{j['condition']}|{j['pair']}"
    return f"solo|{j['menu']}|{j['model']}|{j['variant']}|{j['index']}"


def load_records(results_dir: Path) -> list[dict]:
    records = []
    for path in sorted(results_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


def run_pair(client: OpenAI, job: dict) -> dict:
    (m1, v1), (m2, v2), shuffled = CONDITIONS[job["condition"]]
    agents = []
    for idx, (model, variant) in enumerate(((m1, v1), (m2, v2)), start=1):
        order = option_order(job["menu"], job["condition"], job["pair"], idx, shuffled)
        res = one_call(client, model, render(job["menu"], variant, order), order)
        res["variant"] = variant
        agents.append(res)
    rec = dict(job)
    rec["key"] = job_key(job)
    rec["agents"] = agents
    rec["match"] = (agents[0]["choice"] is not None and agents[0]["choice"] == agents[1]["choice"])
    rec["cost_usd"] = sum(a["cost_usd"] for a in agents)
    rec["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return rec


def run_solo(client: OpenAI, job: dict) -> dict:
    order = list(MENUS[job["menu"]])
    res = one_call(client, job["model"], render(job["menu"], job["variant"], order), order)
    res["variant"] = job["variant"]
    rec = dict(job)
    rec["key"] = job_key(job)
    rec["agent"] = res
    rec["cost_usd"] = res["cost_usd"]
    rec["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only-solo", action="store_true")
    ap.add_argument("--only-pairs", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    client = make_client()
    if args.smoke:
        out_dir = RESULTS / "smoke"
        out_dir.mkdir(parents=True, exist_ok=True)
        recs = [run_pair(client, {"kind": "pair", "menu": "spec", "condition": "cross",
                                  "pair": 99}),
                run_solo(client, {"kind": "solo", "menu": "neutral", "model": GPT,
                                  "variant": "base", "index": 99})]
        with (out_dir / "smoke.jsonl").open("a", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
                print(json.dumps({k: r[k] for k in r if k not in ("agents", "agent")}),
                      [a["choice"] for a in r.get("agents", [r.get("agent")])])
        print(f"smoke cost USD {sum(r['cost_usd'] for r in recs):.5f}")
        return

    RESULTS.mkdir(parents=True, exist_ok=True)
    done = {r["key"] for r in load_records(RESULTS)}
    spent = sum(r["cost_usd"] for r in load_records(RESULTS))
    jobs = []
    if not args.only_solo:
        jobs += pair_jobs()
    if not args.only_pairs:
        jobs += solo_jobs()
    mine = [j for k, j in enumerate(jobs) if k % args.workers == args.worker]
    out_path = RESULTS / f"records_w{args.worker}.jsonl"
    with out_path.open("a", encoding="utf-8") as fh:
        for j in mine:
            key = job_key(j)
            if key in done:
                continue
            if spent >= SPEND_CAP_USD:
                print(f"spend cap reached ({spent:.2f} USD); stopping")
                return
            rec = run_pair(client, j) if j["kind"] == "pair" else run_solo(client, j)
            spent += rec["cost_usd"]
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if j["kind"] == "pair":
                c = [a["choice"] for a in rec["agents"]]
                print(f"[w{args.worker}] {key}: {c} match={rec['match']} spent={spent:.4f}")
            else:
                print(f"[w{args.worker}] {key}: {rec['agent']['choice']} spent={spent:.4f}")


if __name__ == "__main__":
    main()
