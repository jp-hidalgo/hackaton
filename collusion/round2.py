"""Round 2 of the LLM arm (PREREGISTRATION.md, amendment of Sat 24 Oct, 17:45).

Settings, each written to results/llm2/<setting>/<condition>_seed<k>.json:

  r60        P-strong, P-weak, N at 60 rounds, seeds 3-9 (round 1 had 0-2)
  r200       P-strong, P-weak, N at 200 rounds, seeds 0-4
  N_t0.3     N at temperature 0.3, 60 rounds, seeds 0-4
  N_t0.7     N at temperature 0.7, 60 rounds, seeds 0-4
  N_gemini   N with all four agents google/gemini-2.5-flash, 60 rounds, seeds 0-4
  N_mixed    N with A, B gpt-4.1-mini and C, D gemini-2.5-flash, 60 rounds, seeds 0-4

Round 3 (amendment of Sat 24 Oct, 18:35):

  r200_strongB  P-strong and N at 200 rounds with B on openai/gpt-4.1 and
                A, C, D on gpt-4.1-mini, seeds 0-4

Games are skipped if their file exists, so the script is resumable. Run several
workers in parallel:

  python -m collusion.round2 --worker 0 --workers 6
  python -m collusion.round2 --only r200_strongB --worker 0 --workers 5
"""

from __future__ import annotations

import argparse
from pathlib import Path

from collusion.llm_game import MODEL, NAMES, RESULTS, play

GEMINI = "google/gemini-2.5-flash"
STRONG = "openai/gpt-4.1"
OUT = RESULTS.parent / "llm2"


def jobs() -> list[dict]:
    out = []
    for cond in ("P-strong", "P-weak", "N"):
        for seed in range(5):
            out.append(dict(setting="r200", condition=cond, seed=seed, rounds=200))
    for cond in ("P-strong", "P-weak", "N"):
        for seed in range(3, 10):
            out.append(dict(setting="r60", condition=cond, seed=seed, rounds=60))
    for temp in (0.3, 0.7):
        for seed in range(5):
            out.append(dict(setting=f"N_t{temp}", condition="N", seed=seed, rounds=60,
                            temperature=temp))
    for seed in range(5):
        out.append(dict(setting="N_gemini", condition="N", seed=seed, rounds=60,
                        model=GEMINI, models={n: GEMINI for n in NAMES}))
    for seed in range(5):
        out.append(dict(setting="N_mixed", condition="N", seed=seed, rounds=60,
                        models={n: (GEMINI if n in ("C", "D") else MODEL) for n in NAMES}))
    strong_b = {n: (STRONG if n == "B" else MODEL) for n in NAMES}
    for cond in ("P-strong", "N"):
        for seed in range(5):
            out.append(dict(setting="r200_strongB", condition=cond, seed=seed, rounds=200,
                            models=strong_b))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", default=None, help="run only this setting")
    ap.add_argument("--seed", type=int, default=None, help="run only this seed")
    args = ap.parse_args()
    selected = [j for j in jobs() if (args.only is None or j["setting"] == args.only)
                and (args.seed is None or j["seed"] == args.seed)]
    mine = [j for k, j in enumerate(selected) if k % args.workers == args.worker]
    for j in mine:
        out_dir = OUT / j["setting"]
        path = out_dir / f"{j['condition']}_seed{j['seed']}.json"
        if path.exists():
            print(f"skip {path}")
            continue
        kwargs = {k: v for k, v in j.items() if k != "setting"}
        play(out_dir=out_dir, **kwargs)


if __name__ == "__main__":
    main()
