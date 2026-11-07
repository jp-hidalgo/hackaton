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


def round2_figures() -> None:
    """Figures 2-4 from results/round2/summary2.json (amendment 4)."""
    import numpy as np
    from schelling.prompts import FAMILY, LADDER

    out_dir = RESULTS / "round2"
    s = json.loads((out_dir / "summary2.json").read_text(encoding="utf-8"))
    cells = s["cells"]

    # Figure 2: model matrix heatmap
    b = [c for c in cells if c["block"] == "B"]
    models = s["block_b_models"]
    short = {m: m.replace("-a4b-it", "").replace("-it", "").replace("-flash", "-fl") for m in models}
    mat = np.full((len(models), len(models)), np.nan)
    pm = np.full((len(models), len(models)), np.nan)
    for c in b:
        i, j = models.index(c["models"][0]), models.index(c["models"][1])
        mat[i, j] = mat[j, i] = c["match_rate"]
        pm[i, j] = pm[j, i] = c["perm_p"]
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    im = ax.imshow(mat, cmap="Greys", vmin=0, vmax=1)
    ax.set_xticks(range(len(models)))
    ax.set_yticks(range(len(models)))
    ax.set_xticklabels([short[m] for m in models], rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels([short[m] for m in models], fontsize=8)
    for i in range(len(models)):
        for j in range(len(models)):
            if not np.isnan(mat[i, j]):
                ax.text(j, i, f"{mat[i, j]:.2f}\np={pm[i, j]:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if mat[i, j] > 0.55 else "black")
    fig.colorbar(im, ax=ax, fraction=0.046, label="pair match rate")
    ax.set_title("Neutral menu A, canonical order, n = 50 per cell", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_dir / "fig2_model_matrix.png", dpi=200)

    # Figure 3: ladder
    d = {c["cell"]: c for c in cells if c["block"] == "D"}
    if d:
        fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.2))
        xs = range(len(LADDER))
        for kind, marker in (("same", "o"), ("cross", "s")):
            comp = [d[f"{l}_{kind}"]["compliance_agent1"] if f"{l}_{kind}" in d else np.nan for l in LADDER]
            axes[0].plot(list(xs), comp, marker=marker, color="black", ls="-" if kind == "same" else "--",
                         label=f"worker compliance ({kind} cell)")
            appr = [d[f"{l}_{kind}"]["offspec_approved_rate"] if f"{l}_{kind}" in d and d[f"{l}_{kind}"]["offspec_approved_rate"] is not None else np.nan for l in LADDER]
            lo = [appr[k] - d[f"{l}_{kind}"]["offspec_approved_ci"][0] if not np.isnan(appr[k]) else 0 for k, l in enumerate(LADDER)]
            hi = [d[f"{l}_{kind}"]["offspec_approved_ci"][1] - appr[k] if not np.isnan(appr[k]) else 0 for k, l in enumerate(LADDER)]
            axes[1].errorbar(list(xs), appr, yerr=[lo, hi], marker=marker, color="black", capsize=3,
                             ls="-" if kind == "same" else "--", label=f"{'copy' if kind == 'same' else 'cross'} reviewer")
        for ax in axes:
            ax.set_xticks(list(xs))
            ax.set_xticklabels(LADDER)
            ax.set_ylim(-0.02, 1.05)
        axes[0].set_ylabel("fraction choosing library")
        axes[0].set_title("Compliance by pressure level", fontsize=9)
        axes[1].set_ylabel("off-spec worker choices approved")
        axes[1].set_title("Flag-on-disagreement: approval of off-spec choices", fontsize=9)
        axes[0].legend(fontsize=7, frameon=False)
        axes[1].legend(fontsize=7, frameon=False)
        fig.tight_layout()
        fig.savefig(out_dir / "fig3_ladder.png", dpi=200)

    # Figure 4: reasoning on/off
    cc = [c for c in cells if c["block"] == "C"]
    if cc:
        rmodels = sorted({c["cell"].split("__")[0] for c in cc})
        fig, ax = plt.subplots(figsize=(7, 3.2))
        width = 0.2
        for k, (reason, kind) in enumerate((("reason_none", "same"), ("reason_default", "same"),
                                            ("reason_none", "shuffle"), ("reason_default", "shuffle"))):
            vals, los, his = [], [], []
            for m in rmodels:
                c = next((c for c in cc if c["cell"] == f"{m}__{reason}__{kind}"), None)
                v = c["match_rate"] if c else np.nan
                vals.append(v)
                los.append(v - c["ci"][0] if c else 0)
                his.append(c["ci"][1] - v if c else 0)
            xs = np.arange(len(rmodels)) + (k - 1.5) * width
            ax.bar(xs, vals, width=width, color=["0.75", "0.35", "0.75", "0.35"][k],
                   hatch="" if kind == "same" else "//",
                   label=f"{kind}, reasoning {'off' if reason == 'reason_none' else 'on'}")
            ax.errorbar(xs, vals, yerr=[los, his], fmt="none", ecolor="black", capsize=2, lw=0.8)
        ax.set_xticks(range(len(rmodels)))
        ax.set_xticklabels(rmodels, fontsize=8)
        ax.set_ylabel("self-pair match rate")
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=7, frameon=False, ncol=2)
        fig.tight_layout()
        fig.savefig(out_dir / "fig4_reasoning.png", dpi=200)
    print(f"wrote round 2 figures to {out_dir}")


def main() -> None:
    import sys
    if "--round2" in sys.argv:
        round2_figures()
        return
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
