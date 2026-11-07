"""Run the paired grid and the solo marginals (PREREGISTRATION.md).

One API call per agent, nothing passed between agents. Every request and raw
reply is appended to a JSONL file under results/. Finished pairs and solos are
skipped on rerun, so the script is resumable. Several workers can run at once;
each writes its own file.

Provider: Adaption Responses API (amendment 1). Needs ADAPTION_API_KEY in .env.

  python -m schelling.run --probe                   # throwaway prompt to candidate models
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

import httpx
from dotenv import load_dotenv

from schelling.prompts import (CONDITIONS, COPY_MODEL, MENUS, N_PAIRS, N_SOLO, OTHER_MODEL,
                               SOLO_SPECS, TEMPERATURE, option_order, render)

RESULTS = Path(__file__).resolve().parent / "results"
BASE_URL = "https://api.prod.adaptionlabs.ai/api/v1"
SPEND_CAP_CREDITS = 100.0   # of the 1500 available; expected spend is far below
MAX_ATTEMPTS = 3
MAX_OUTPUT_TOKENS = 60

# Adaption list prices, credits per million tokens (input, output), docs read 7 Nov 2026.
PRICES = {
    "gemma-4-31b-it": (0.09, 0.34),
    "gemma-4-26b-a4b-it": (0.0765, 0.255),
    "qwen3.5-397b": (0.55, 3.50),
    "qwen3.8-27b": (0.039, 1.25),
    "deepseek-v4-flash": (0.04444, 0.13332),
    "glm-5.2": (1.40, 4.40),
    "glm-53-flash": (0.15, 0.50),
}
PROBE_MODELS = ["gemma-4-31b-it", "deepseek-v4-flash", "qwen3.8-27b", "glm-53-flash",
                "gemma-4-26b-a4b-it"]


class Client:
    def __init__(self) -> None:
        load_dotenv()
        key = os.environ.get("ADAPTION_API_KEY")
        if not key:
            raise SystemExit("ADAPTION_API_KEY not set (put it in .env)")
        self.http = httpx.Client(base_url=BASE_URL, timeout=60.0,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})

    def respond(self, model: str, prompt: str, max_output_tokens: int = MAX_OUTPUT_TOKENS,
                temperature: float = TEMPERATURE, reasoning: str = "none") -> dict:
        body = {"model": model, "input": prompt, "temperature": temperature,
                "max_output_tokens": max_output_tokens, "store": False}
        # Amendment 2: hidden reasoning off for every model, so each reply is a
        # single forward pass to the JSON. Gemma reports 0 reasoning tokens either
        # way; DeepSeek drops from ~26 to 0 with this. Round 2 Block C omits the
        # field ("default") to turn reasoning back on.
        if reasoning == "none":
            body["reasoning"] = {"effort": "none"}
        r = self.http.post("/responses", json=body)
        r.raise_for_status()
        return r.json()


def output_text(resp: dict) -> str:
    if resp.get("output_text"):
        return resp["output_text"]
    parts = []
    for item in resp.get("output", []):
        for c in item.get("content", []) or []:
            if c.get("type") == "output_text" and c.get("text"):
                parts.append(c["text"])
    return "".join(parts)


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


def cost_credits(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    p_in, p_out = PRICES.get(model, (0.0, 0.0))
    return (prompt_tokens * p_in + completion_tokens * p_out) / 1e6


def one_call(client: Client, model: str, prompt: str, options: list[str],
             temperature: float = TEMPERATURE, reasoning: str = "none",
             max_output_tokens: int = MAX_OUTPUT_TOKENS) -> dict:
    """One agent's decision. Retries parse failures and transport errors."""
    attempts = []
    choice = None
    usage = {"prompt": 0, "completion": 0, "reasoning": 0}
    for attempt in range(MAX_ATTEMPTS):
        try:
            resp = client.respond(model, prompt, max_output_tokens=max_output_tokens,
                                  temperature=temperature, reasoning=reasoning)
        except Exception as exc:  # rate limit or network: back off, retry
            attempts.append({"raw": f"ERROR {exc}"})
            time.sleep(3 + 7 * attempt)
            continue
        raw = output_text(resp)
        u = resp.get("usage") or {}
        usage["prompt"] += int(u.get("input_tokens", 0) or 0)
        usage["completion"] += int(u.get("output_tokens", 0) or 0)
        details = u.get("output_tokens_details") or {}
        try:
            usage["reasoning"] += int(details.get("reasoning_tokens", 0) or 0)
        except (TypeError, ValueError):
            pass
        attempts.append({"raw": raw, "status": resp.get("status"),
                         "incomplete": resp.get("incomplete_details")})
        choice = parse_choice(raw, options)
        if choice is not None:
            break
    return {"model": model, "prompt": prompt, "options": options, "attempts": attempts,
            "choice": choice, "usage": usage, "temperature": temperature, "reasoning": reasoning,
            "cost_usd": cost_credits(model, usage["prompt"], usage["completion"])}


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


def run_pair(client: Client, job: dict) -> dict:
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
    rec["cost_usd"] = sum(a["cost_usd"] for a in agents)   # field name kept; unit is credits
    rec["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return rec


def run_solo(client: Client, job: dict) -> dict:
    order = list(MENUS[job["menu"]])
    res = one_call(client, job["model"], render(job["menu"], job["variant"], order), order)
    res["variant"] = job["variant"]
    rec = dict(job)
    rec["key"] = job_key(job)
    rec["agent"] = res
    rec["cost_usd"] = res["cost_usd"]
    rec["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return rec


def probe(client: Client, models: list[str] = PROBE_MODELS, out_name: str = "probe") -> list[dict]:
    """Throwaway prompt, not from the grid: does the model answer with bare JSON,
    does it spend reasoning tokens, how long does it take."""
    prompt = ('Pick one colour from this list: red, green, blue. Reply with JSON only, '
              'in the form {"choice": "<colour>"}.')
    out_dir = RESULTS / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in models:
        t0 = time.time()
        try:
            resp = client.respond(model, prompt)
        except Exception as exc:
            print(f"{model}: ERROR {exc}")
            rows.append({"model": model, "error": str(exc)[:200], "eligible": False})
            continue
        dt = time.time() - t0
        (out_dir / f"{model}.json").write_text(json.dumps(resp, indent=1), encoding="utf-8")
        u = resp.get("usage") or {}
        details = u.get("output_tokens_details") or {}
        text = output_text(resp)
        parsed = parse_choice(text, ["red", "green", "blue"])
        reasoning = int(details.get("reasoning_tokens") or 0)
        row = {"model": model, "seconds": round(dt, 1), "output_tokens": u.get("output_tokens"),
               "reasoning_tokens": reasoning, "text": text, "parsed": parsed,
               "eligible": parsed is not None and reasoning == 0 and dt < 20}
        rows.append(row)
        print(f"{model}: {dt:.1f}s out={u.get('output_tokens')} reasoning={reasoning} "
              f"text={text!r} eligible={row['eligible']}")
    (out_dir / "probe_summary.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only-solo", action="store_true")
    ap.add_argument("--only-pairs", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--probe-all", action="store_true", help="round 2: all hosted models")
    args = ap.parse_args()

    client = Client()
    if args.probe:
        probe(client)
        return
    if args.probe_all:
        from schelling.prompts import HOSTED_MODELS
        probe(client, HOSTED_MODELS, out_name="probe_round2")
        return
    if args.smoke:
        out_dir = RESULTS / "smoke"
        out_dir.mkdir(parents=True, exist_ok=True)
        recs = [run_pair(client, {"kind": "pair", "menu": "spec", "condition": "cross",
                                  "pair": 99}),
                run_solo(client, {"kind": "solo", "menu": "neutral", "model": COPY_MODEL,
                                  "variant": "base", "index": 99})]
        with (out_dir / "smoke.jsonl").open("a", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
                agents = r.get("agents") or [r.get("agent")]
                print(r["key"], [(a["model"], a["choice"], a["usage"]) for a in agents])
        print(f"smoke cost {sum(r['cost_usd'] for r in recs):.5f} credits")
        return

    RESULTS.mkdir(parents=True, exist_ok=True)
    existing = load_records(RESULTS)
    done = {r["key"] for r in existing}
    spent = sum(r["cost_usd"] for r in existing)
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
            if spent >= SPEND_CAP_CREDITS:
                print(f"spend cap reached ({spent:.2f} credits); stopping")
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
