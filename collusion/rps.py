"""Scripted iterated Rock-Paper-Scissors with assistant collusion.

Actions: 0 = Rock, 1 = Paper, 2 = Scissors. Action x beats (x + 2) % 3 and
loses to (x + 1) % 3.

Roles (Bonjour et al. Section 5.1, "manual collusion"):
  A (index 0): primary colluder, plays uniformly at random.
  B (index 1): assistant. With probability CP plays the action A's action
               beats, so A scores regardless of the others. Otherwise uniform.
  Others:      uniform at random.

Payoff (per round):
  all actions identical            -> everyone 0
  all three distinct actions occur -> everyone 1
  exactly two distinct actions     -> holders of the winning action get 1
For three players this reproduces the paper's Table 1.

Run as a script to produce the CP x games sweep used in the report:
  python -m collusion.rps
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from collusion.netinfluence import ALPHA, detect

RESULTS = Path(__file__).resolve().parent / "results"
MOVE_NAMES = ["R", "P", "S"]


def beats(x: np.ndarray | int) -> np.ndarray | int:
    """The action that x beats."""
    return (x + 2) % 3


def payoffs(actions: np.ndarray) -> np.ndarray:
    """Vectorised payoff. actions: (T, n) -> (T, n) of 0/1."""
    T, n = actions.shape
    out = np.zeros((T, n), dtype=int)
    present = np.stack([(actions == k).any(axis=1) for k in range(3)], axis=1)
    n_distinct = present.sum(axis=1)
    out[n_distinct == 3] = 1
    two = np.where(n_distinct == 2)[0]
    for t in two:
        acts = np.unique(actions[t])
        x, y = acts
        winner = x if beats(x) == y else y
        out[t] = actions[t] == winner
    return out


def simulate(
    n_rounds: int,
    cp: float,
    n_players: int = 4,
    rng: np.random.Generator | None = None,
    pairs: list[tuple[int, int]] | None = None,
) -> np.ndarray:
    """One game log of shape (n_rounds, n_players).

    pairs: list of (primary, assistant) index pairs that collude with
    probability cp. Default [(0, 1)].
    """
    rng = rng or np.random.default_rng()
    pairs = pairs if pairs is not None else [(0, 1)]
    actions = rng.integers(0, 3, size=(n_rounds, n_players))
    for primary, assistant in pairs:
        help_mask = rng.random(n_rounds) < cp
        actions[help_mask, assistant] = beats(actions[help_mask, primary])
    return actions


def prev_joint_state(actions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Exploratory state definition: the previous round's joint action,
    encoded as a single integer. Returns (actions[1:], states)."""
    n = actions.shape[1]
    weights = 3 ** np.arange(n)[::-1]
    states = actions[:-1] @ weights
    return actions[1:], states


def sweep(
    cps=(0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0),
    games=(50, 100, 200, 400, 1000),
    reps: int = 200,
    n_players: int = 4,
    seed: int = 0,
    alpha: float = ALPHA,
    state_mode: str = "constant",
    n_perm: int = 0,
) -> list[dict]:
    """CDA and false-positive rate for the published rule. Also records the
    mean mutual net influence of the true pair.

    state_mode: "constant" (pre-registered primary) or "prev_joint"
    (exploratory; see PREREGISTRATION.md Amendments).
    n_perm > 0 also evaluates the rule with the permutation threshold.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for cp in cps:
        for g in games:
            hits = 0
            any_pair = 0
            hits_perm = 0
            any_perm = 0
            mutual_ab = []
            alpha_perms = []
            for _ in range(reps):
                actions = simulate(g + (state_mode == "prev_joint"), cp, n_players, rng)
                states = None
                if state_mode == "prev_joint":
                    actions, states = prev_joint_state(actions)
                det = detect(actions, states=states, alpha=alpha, n_actions=3,
                             permutation=n_perm, rng=rng)
                hits += det.published == (0, 1)
                any_pair += det.published is not None
                if n_perm:
                    hits_perm += det.published_perm == (0, 1)
                    any_perm += det.published_perm is not None
                    alpha_perms.append(det.alpha_perm)
                mutual_ab.append(det.mutual[(0, 1)])
            row = {
                "n_players": n_players,
                "state_mode": state_mode,
                "cp": cp,
                "games": g,
                "reps": reps,
                "alpha": alpha,
                "cda": hits / reps,
                "any_pair_rate": any_pair / reps,
                "mean_mutual_net_AB": float(np.mean(mutual_ab)),
                "sd_mutual_net_AB": float(np.std(mutual_ab)),
            }
            if n_perm:
                row.update(
                    {
                        "n_perm": n_perm,
                        "mean_alpha_perm": float(np.mean(alpha_perms)),
                        "cda_perm": hits_perm / reps,
                        "any_pair_rate_perm": any_perm / reps,
                    }
                )
            rows.append(row)
            extra = (
                f" | perm: alpha={row['mean_alpha_perm']:.3f} CDA={row['cda_perm']:.3f} "
                f"any={row['any_pair_rate_perm']:.3f}" if n_perm else ""
            )
            print(
                f"n={n_players} {state_mode} cp={cp:.1f} games={g:5d} CDA={hits / reps:.3f} "
                f"any={any_pair / reps:.3f} mutualAB={np.mean(mutual_ab):.4f}{extra}"
            )
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def cda_table(rows: list[dict]) -> str:
    cps = sorted({r["cp"] for r in rows})
    games = sorted({r["games"] for r in rows})
    head = "| CP \\ games | " + " | ".join(str(g) for g in games) + " |"
    sep = "|---|" + "---|" * len(games)
    lines = [head, sep]
    for cp in cps:
        cells = []
        for g in games:
            r = next(x for x in rows if x["cp"] == cp and x["games"] == g)
            cells.append(f"{r['cda']:.2f}" if cp > 0 else f"FP {r['any_pair_rate']:.2f}")
        lines.append(f"| {cp:.1f} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def plot(rows: list[dict], path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cps = sorted({r["cp"] for r in rows})
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for cp in cps:
        sub = sorted((r for r in rows if r["cp"] == cp), key=lambda r: r["games"])
        y = [r["cda"] if cp > 0 else r["any_pair_rate"] for r in sub]
        label = f"CP={cp:.1f}" + (" (false-positive rate)" if cp == 0 else "")
        ax.plot([r["games"] for r in sub], y, marker="o", label=label,
                linestyle="--" if cp == 0 else "-")
    ax.set_xscale("log")
    ax.set_xlabel("games used for detection")
    ax.set_ylabel("detection accuracy (fraction of 200 reps)")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=2, loc="lower right")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)


# Bonjour et al. 2022, Table 2 (three players, manual collusion, alpha 0.05).
BONJOUR_TABLE2 = {
    0.3: {50: 21.9, 100: 37.1, 200: 48.3, 400: 82.8, 1000: 100.0},
    0.4: {50: 31.2, 100: 58.4, 200: 79.2, 400: 99.3, 1000: 100.0},
}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    rows4 = sweep(n_players=4, seed=0)
    write_csv(rows4, RESULTS / "sweep_4player.csv")
    plot(rows4, RESULTS / "fig_cda_4player.png",
         "Four-player RPS, published rule, alpha = 0.05")

    games3 = (50, 100, 200, 400, 1000)
    rows3 = sweep(cps=(0.0, 0.3, 0.4), games=games3, n_players=3, seed=1)
    write_csv(rows3, RESULTS / "sweep_3player_constant.csv")
    rows3p = sweep(cps=(0.0, 0.3, 0.4), games=games3, n_players=3, seed=1,
                   state_mode="prev_joint")
    write_csv(rows3p, RESULTS / "sweep_3player_prevjoint.csv")

    comparison = [
        "| CP | games | Bonjour Table 2 CDA (%) | constant state CDA (%) | prev-round joint state CDA (%) |",
        "|---|---|---|---|---|",
    ]
    for r, rp in zip(rows3, rows3p):
        if r["cp"] == 0.0:
            continue
        ref = BONJOUR_TABLE2[r["cp"]][r["games"]]
        comparison.append(
            f"| {r['cp']:.1f} | {r['games']} | {ref:.1f} | {100 * r['cda']:.1f} | {100 * rp['cda']:.1f} |"
        )
    fp_rows = ["| games | constant state FP | prev-round joint state FP |", "|---|---|---|"]
    for r, rp in zip(rows3, rows3p):
        if r["cp"] == 0.0:
            fp_rows.append(f"| {r['games']} | {r['any_pair_rate']:.2f} | {rp['any_pair_rate']:.2f} |")

    # Sprint addition: permutation threshold versus fixed alpha, small samples.
    rows_perm = sweep(cps=(0.0, 0.3, 0.5), games=(50, 100, 200), reps=100,
                      n_players=4, seed=2, n_perm=300)
    write_csv(rows_perm, RESULTS / "sweep_4player_permutation.csv")
    perm_table = [
        "| CP | games | mean alpha_perm (bits) | fixed alpha: CDA / any-pair | alpha_perm: CDA / any-pair |",
        "|---|---|---|---|---|",
    ]
    for r in rows_perm:
        perm_table.append(
            f"| {r['cp']:.1f} | {r['games']} | {r['mean_alpha_perm']:.3f} | "
            f"{r['cda']:.2f} / {r['any_pair_rate']:.2f} | {r['cda_perm']:.2f} / {r['any_pair_rate_perm']:.2f} |"
        )

    md = [
        "# Scripted sweep results",
        "",
        "Generated by `python -m collusion.rps`. 200 repetitions per cell unless stated. "
        "Published rule (exactly one pair, both directions >= alpha = 0.05 bits). Cells at CP = 0 "
        "report the false-positive rate (any pair returned).",
        "",
        "## Four players, constant state (pre-registered primary analysis)",
        "",
        "A and B collude at probability CP; C and D are independent.",
        "",
        cda_table(rows4),
        "",
        "![CDA](fig_cda_4player.png)",
        "",
        "## Three players, comparison with Bonjour et al. (2022) Table 2",
        "",
        "Constant state is the pre-registered analysis. The previous-round joint state "
        "(27 states) is an exploratory analysis added after the first run, because the "
        "constant-state implementation detected faster than the paper's Table 2 (see "
        "PREREGISTRATION.md, Amendments). The paper does not state which state it conditions on "
        "for iterated RPS, nor the logarithm base.",
        "",
        *comparison,
        "",
        "False-positive rate at CP = 0 (any pair returned), three players. Not reported in the paper.",
        "",
        *fp_rows,
        "",
        "## Permutation threshold versus fixed alpha (sprint addition), four players, 100 reps, 300 permutations",
        "",
        *perm_table,
    ]
    (RESULTS / "sweep_results.md").write_text("\n".join(md), encoding="utf-8")
    (RESULTS / "sweep_summary.json").write_text(
        json.dumps(
            {"four_player": rows4, "three_player_constant": rows3,
             "three_player_prevjoint": rows3p, "four_player_permutation": rows_perm},
            indent=1,
        ),
        encoding="utf-8",
    )
    print("\n".join(md))


if __name__ == "__main__":
    main()
