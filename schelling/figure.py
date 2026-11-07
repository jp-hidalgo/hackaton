"""Figure 1: match rate per condition and menu with Wilson intervals and the
within-cell independence baseline. Reads results/summary.json.

  python -m schelling.figure
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from schelling.prompts import CONDITION_ORDER, MENU_ORDER

RESULTS = Path(__file__).resolve().parent / "results"


def main() -> None:
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    cells = {(c["menu"], c["condition"]): c for c in summary["cells"]}
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.2), sharey=True)
    for ax, menu in zip(axes, MENU_ORDER):
        xs = range(len(CONDITION_ORDER))
        rates = [cells[(menu, c)]["match_rate"] for c in CONDITION_ORDER]
        lo = [cells[(menu, c)]["match_rate"] - cells[(menu, c)]["ci"][0] for c in CONDITION_ORDER]
        hi = [cells[(menu, c)]["ci"][1] - cells[(menu, c)]["match_rate"] for c in CONDITION_ORDER]
        b_cell = [cells[(menu, c)]["B_cell"] for c in CONDITION_ORDER]
        ax.bar(xs, rates, color="0.55", width=0.6, label="match rate (Wilson 95%)")
        ax.errorbar(xs, rates, yerr=[lo, hi], fmt="none", ecolor="black", capsize=3, lw=1)
        ax.scatter(xs, b_cell, marker="_", s=400, color="black", zorder=3,
                   label="independence baseline B_cell")
        ax.axhline(1 / 8, ls=":", color="0.3", lw=1, label="uniform chance 1/8")
        ax.set_xticks(list(xs))
        ax.set_xticklabels([c.replace("_", "\n") for c in CONDITION_ORDER], fontsize=8)
        ax.set_title(f"{menu} menu", fontsize=10)
        ax.set_ylim(0, 1.05)
    axes[0].set_ylabel("pair match rate")
    axes[1].legend(fontsize=7, loc="upper right", frameon=False)
    fig.tight_layout()
    out = RESULTS / "fig_match_rates.png"
    fig.savefig(out, dpi=200)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
