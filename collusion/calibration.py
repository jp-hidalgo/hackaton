"""Post hoc calibration check (PREREGISTRATION.md, amendment of 24 Oct, 18:20).

For each positive LLM setting, run the scripted four-player game at the
collusion strength the LLM games actually realized (excess helping rate over
chance, on the scripted CP scale) and the same number of rounds, and compare
the scripted detection rates with the LLM detection rates.

  python -m collusion.calibration
"""

from __future__ import annotations

import json
from pathlib import Path

from collusion.rps import RESULTS, sweep

SETTINGS = [  # setting, condition, rounds
    ("r60", "P-strong", 60), ("r60", "P-weak", 60),
    ("r200", "P-strong", 200), ("r200", "P-weak", 200),
    ("r200_strongB", "P-strong", 200),
]


def main() -> None:
    summary = json.loads((RESULTS / "llm_round2.json").read_text(encoding="utf-8"))["summary"]
    lines = [
        "# Calibration: scripted game at the strength the LLM games realized",
        "",
        "Scripted CP = mean excess helping rate (h - 1/3) / (2/3) of the LLM games in that setting; "
        "200 scripted repetitions, 300 permutations. LLM columns are counts over games.",
        "",
        "| setting | condition | rounds | scripted CP | scripted published: CDA | scripted perm: CDA | "
        "LLM published AB | LLM perm AB |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for setting, cond, rounds in SETTINGS:
        s = next((x for x in summary if x["setting"] == setting and x["condition"] == cond), None)
        if s is None:
            continue
        cp = float(s["cp_excess"])
        row = sweep(cps=(cp,), games=(rounds,), reps=200, n_players=4, seed=7, n_perm=300)[0]
        lines.append(
            f"| {setting} | {cond} | {rounds} | {cp:.2f} | {row['cda']:.2f} | {row['cda_perm']:.2f} | "
            f"{s['published_AB']} | {s['perm_AB']} |"
        )
    (RESULTS / "calibration.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
