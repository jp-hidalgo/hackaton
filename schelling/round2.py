"""Round 2 driver (PREREGISTRATION.md, amendment 4).

Blocks:
  A  scale and menu robustness (neutral A at 100 pairs; neutral B, C, D at 50)
  B  model matrix (all eligible hosted models, self and cross pairs, 50 each)
  C  reasoning on vs off (deepseek, qwen3.8, glm-53-flash; same and shuffle; 50)
  D  deviation-pressure ladder (spec menu L0-L3; same and cross; 60)
  E  temperature 0.3 and 0.7 (gemma, deepseek; same and shuffle; 50)

Records go to results/round2/<block>/records_w<k>.jsonl; solos to results/round2/solo/.
Jobs are skipped if their key exists anywhere under results/round2/, so the
script is resumable and several workers can run at once.

  python -m schelling.round2 --worker 0 --workers 4
  python -m schelling.round2 --block D --worker 0 --workers 2
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from schelling.prompts import (COPY_MODEL, HOSTED_MODELS, LADDER, OTHER_MODEL, TEMPERATURE,
                               agent_spec, option_order2, render)
from schelling.run import RESULTS, Client, load_records, one_call

OUT = RESULTS / "round2"
SPEND_CAP_CREDITS = 300.0
REASONING_MAX_TOKENS = 2000

GEMMA, DEEPSEEK = COPY_MODEL, OTHER_MODEL
REASONING_MODELS = ["deepseek-v4-flash", "qwen3.8-27b", "glm-53-flash"]


def eligible_models() -> list[str]:
    path = RESULTS / "probe_round2" / "probe_summary.json"
    if not path.exists():
        raise SystemExit("run `python -m schelling.run --probe-all` first (Block B needs the probe)")
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [r["model"] for r in rows if r.get("eligible")]


def pair_job(block: str, cell: str, menu: str, pair: int, a1: dict, a2: dict) -> dict:
    return {"kind": "pair2", "block": block, "cell": cell, "menu": menu, "pair": pair,
            "agents": [a1, a2], "key": f"r2|{block}|{cell}|{menu}|{pair}"}


def solo_job(menu: str, model: str, variant: str, index: int,
             temperature: float = TEMPERATURE, reasoning: str = "none") -> dict:
    return {"kind": "solo2", "block": "solo", "menu": menu, "model": model, "variant": variant,
            "temperature": temperature, "reasoning": reasoning, "index": index,
            "key": f"r2solo|{menu}|{model}|{variant}|{temperature}|{reasoning}|{index}"}


def block_a() -> list[dict]:
    jobs = []
    g, d = agent_spec(GEMMA), agent_spec(DEEPSEEK)
    gs, ds = agent_spec(GEMMA, shuffled=True), agent_spec(DEEPSEEK, shuffled=True)
    gp = agent_spec(GEMMA, variant="paraphrase")
    cells = {"same": (g, g), "shuffle": (gs, gs), "paraphrase": (g, gp), "cross": (g, d),
             "cross_shuffle": (gs, ds)}
    for cell, (a1, a2) in cells.items():
        for k in range(30, 130):
            jobs.append(pair_job("A", cell, "neutral", k, a1, a2))
    for menu in ("neutralB", "neutralC", "neutralD"):
        for cell in ("same", "shuffle", "cross"):
            a1, a2 = cells[cell]
            for k in range(50):
                jobs.append(pair_job("A", cell, menu, k, a1, a2))
    for menu in ("neutral", "neutralB", "neutralC", "neutralD"):
        for model in (GEMMA, DEEPSEEK):
            jobs += [solo_job(menu, model, "base", k) for k in range(100)]
    jobs += [solo_job("neutral", GEMMA, "paraphrase", k) for k in range(100)]
    return jobs


def block_b() -> list[dict]:
    models = eligible_models()
    jobs = []
    for i, m1 in enumerate(models):
        for m2 in models[i:]:
            cell = f"{m1}__{m2}"
            for k in range(50):
                jobs.append(pair_job("B", cell, "neutral", k, agent_spec(m1), agent_spec(m2)))
    for model in models:
        jobs += [solo_job("neutral", model, "base", k) for k in range(100)]
    return jobs


def block_c() -> list[dict]:
    jobs = []
    for model in REASONING_MODELS:
        for reasoning in ("default", "none"):
            for cell_kind, shuffled in (("same", False), ("shuffle", True)):
                spec = agent_spec(model, shuffled=shuffled, reasoning=reasoning)
                cell = f"{model}__reason_{reasoning}__{cell_kind}"
                for k in range(50):
                    jobs.append(pair_job("C", cell, "neutral", k, spec, spec))
        jobs += [solo_job("neutral", model, "base", k, reasoning="default") for k in range(50)]
    return jobs


def block_d() -> list[dict]:
    jobs = []
    for level in LADDER:
        g, d = agent_spec(GEMMA, variant=level), agent_spec(DEEPSEEK, variant=level)
        for cell_kind, (a1, a2) in (("same", (g, g)), ("cross", (g, d))):
            for k in range(60):
                jobs.append(pair_job("D", f"{level}_{cell_kind}", "spec", k, a1, a2))
        for model in (GEMMA, DEEPSEEK):
            jobs += [solo_job("spec", model, level, k) for k in range(60)]
    return jobs


def block_e() -> list[dict]:
    jobs = []
    for model in (GEMMA, DEEPSEEK):
        for temp in (0.3, 0.7):
            for cell_kind, shuffled in (("same", False), ("shuffle", True)):
                spec = agent_spec(model, shuffled=shuffled, temperature=temp)
                cell = f"{model}__t{temp}__{cell_kind}"
                for k in range(50):
                    jobs.append(pair_job("E", cell, "neutral", k, spec, spec))
            jobs += [solo_job("neutral", model, "base", k, temperature=temp) for k in range(50)]
    return jobs


BLOCKS = {"A": block_a, "B": block_b, "C": block_c, "D": block_d, "E": block_e}


def jobs_for(blocks: list[str]) -> list[dict]:
    seen, out = set(), []
    for b in blocks:
        for j in BLOCKS[b]():
            if j["key"] not in seen:
                seen.add(j["key"])
                out.append(j)
    return out


def max_tokens(spec: dict) -> int:
    return REASONING_MAX_TOKENS if spec["reasoning"] == "default" else 60


def run_pair(client: Client, job: dict) -> dict:
    agents = []
    for idx, spec in enumerate(job["agents"], start=1):
        order = option_order2(job["menu"], job["cell"], job["pair"], idx, spec["shuffled"])
        res = one_call(client, spec["model"], render(job["menu"], spec["variant"], order), order,
                       temperature=spec["temperature"], reasoning=spec["reasoning"],
                       max_output_tokens=max_tokens(spec))
        res.update({"variant": spec["variant"], "shuffled": spec["shuffled"]})
        agents.append(res)
    rec = {k: v for k, v in job.items() if k != "agents"}
    rec["specs"] = job["agents"]
    rec["agents"] = agents
    rec["match"] = agents[0]["choice"] is not None and agents[0]["choice"] == agents[1]["choice"]
    rec["cost_usd"] = sum(a["cost_usd"] for a in agents)
    rec["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return rec


def run_solo(client: Client, job: dict) -> dict:
    from schelling.prompts import MENUS
    order = list(MENUS[job["menu"]])
    spec = agent_spec(job["model"], job["variant"], False, job["temperature"], job["reasoning"])
    res = one_call(client, job["model"], render(job["menu"], job["variant"], order), order,
                   temperature=job["temperature"], reasoning=job["reasoning"],
                   max_output_tokens=max_tokens(spec))
    res["variant"] = job["variant"]
    rec = dict(job)
    rec["agent"] = res
    rec["cost_usd"] = res["cost_usd"]
    rec["time"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return rec


def load_round2() -> list[dict]:
    recs = []
    if OUT.exists():
        for sub in sorted(p for p in OUT.iterdir() if p.is_dir()):
            recs += load_records(sub)
    return recs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--block", default="ABCDE", help="letters of the blocks to run, in order")
    args = ap.parse_args()

    client = Client()
    existing = load_round2()
    done = {r["key"] for r in existing}
    spent = sum(r["cost_usd"] for r in existing)
    jobs = jobs_for(list(args.block))
    mine = [j for k, j in enumerate(jobs) if k % args.workers == args.worker]
    handles: dict[str, object] = {}
    try:
        for j in mine:
            if j["key"] in done:
                continue
            if spent >= SPEND_CAP_CREDITS:
                print(f"spend cap reached ({spent:.2f} credits); stopping")
                return
            block_dir = OUT / j["block"]
            if j["block"] not in handles:
                block_dir.mkdir(parents=True, exist_ok=True)
                handles[j["block"]] = (block_dir / f"records_w{args.worker}.jsonl").open("a", encoding="utf-8")
            rec = run_pair(client, j) if j["kind"] == "pair2" else run_solo(client, j)
            spent += rec["cost_usd"]
            fh = handles[j["block"]]
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if j["kind"] == "pair2":
                c = [a["choice"] for a in rec["agents"]]
                print(f"[w{args.worker}] {j['key']}: {c} match={rec['match']} spent={spent:.3f}")
            else:
                print(f"[w{args.worker}] {j['key']}: {rec['agent']['choice']} spent={spent:.3f}")
    finally:
        for fh in handles.values():
            fh.close()


if __name__ == "__main__":
    main()
