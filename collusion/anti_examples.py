"""Frozen anti-examples for pairwise net influence.

Predictions were written in PREREGISTRATION.md before this file was run.
Each case is simulated with 200 repetitions of 400 rounds (and 100 rounds,
to show the small-sample behaviour); we report how often the published rule
and the multi-pair variant return each outcome, plus the mean influence
matrices from one 400-round realisation.

  python -m collusion.anti_examples
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np

from collusion.netinfluence import detect, format_matrix
from collusion.rps import beats, simulate

RESULTS = Path(__file__).resolve().parent / "results"
NAMES = ["A", "B", "C", "D"]


def ae1_two_pairs(T: int, rng: np.random.Generator):
    """(A, B) and (C, D) both assistant-collude at CP 0.8."""
    return simulate(T, 0.8, 4, rng, pairs=[(0, 1), (2, 3)]), None


def ae2_one_way_copy(T: int, rng: np.random.Generator):
    """B copies A's previous-round action with probability 0.8. Constant state."""
    actions = rng.integers(0, 3, size=(T + 1, 4))
    copy = rng.random(T) < 0.8
    actions[1:, 1] = np.where(copy, actions[:-1, 0], actions[1:, 1])
    return actions[1:], None


def ae2b_one_way_same_round(T: int, rng: np.random.Generator):
    """Exploratory addition: B sees A's current move and copies it with
    probability 0.8. A does not depend on B."""
    actions = rng.integers(0, 3, size=(T, 4))
    copy = rng.random(T) < 0.8
    actions[copy, 1] = actions[copy, 0]
    return actions, None


def ae3_shared_marginal(T: int, rng: np.random.Generator):
    """All four draw independently from the same skewed marginal."""
    return rng.choice(3, size=(T, 4), p=[0.6, 0.3, 0.1]), None


def ae4_common_cause(T: int, rng: np.random.Generator, condition: bool):
    """Public state s each round; every agent plays s with probability 0.8."""
    s = rng.integers(0, 3, size=T)
    actions = np.column_stack(
        [np.where(rng.random(T) < 0.8, s, rng.integers(0, 3, size=T)) for _ in range(4)]
    )
    return actions, (s if condition else None)


CASES = {
    "AE1 two pairs (A,B),(C,D) CP 0.8": lambda T, rng: ae1_two_pairs(T, rng),
    "AE2 one-way copying B<-A(t-1) p 0.8": lambda T, rng: ae2_one_way_copy(T, rng),
    "AE2b one-way copying B<-A(t) p 0.8 (exploratory)": lambda T, rng: ae2b_one_way_same_round(T, rng),
    "AE3 shared skewed marginal, independent": lambda T, rng: ae3_shared_marginal(T, rng),
    "AE4 common cause, constant state": lambda T, rng: ae4_common_cause(T, rng, False),
    "AE4 common cause, conditioned on state": lambda T, rng: ae4_common_cause(T, rng, True),
}

PREDICTIONS = {
    "AE1 two pairs (A,B),(C,D) CP 0.8": ("no collusion", "both pairs"),
    "AE2 one-way copying B<-A(t-1) p 0.8": ("(A,B)", "(A,B)"),
    "AE2b one-way copying B<-A(t) p 0.8 (exploratory)": ("(A,B), post-hoc", "(A,B), post-hoc"),
    "AE3 shared skewed marginal, independent": ("no collusion", "none"),
    "AE4 common cause, constant state": ("no collusion (gate fires)", "all six pairs"),
    "AE4 common cause, conditioned on state": ("no collusion", "none"),
}


def pair_name(p):
    return "(" + ",".join(NAMES[i] for i in p) + ")"


def run(reps: int = 200, rounds=(100, 400), seed: int = 11) -> dict:
    rng = np.random.default_rng(seed)
    out = {}
    for name, fn in CASES.items():
        out[name] = {}
        for T in rounds:
            pub = Counter()
            multi = Counter()
            for _ in range(reps):
                actions, states = fn(T, rng)
                det = detect(actions, states=states, n_actions=3)
                pub[pair_name(det.published) if det.published else "none"] += 1
                multi[",".join(pair_name(p) for p in det.multi) or "none"] += 1
            actions, states = fn(T, np.random.default_rng(seed + T))
            det = detect(actions, states=states, n_actions=3, permutation=500,
                         rng=np.random.default_rng(seed))
            out[name][T] = {
                "published": dict(pub),
                "multi": dict(multi),
                "example_gamma": det.gamma.tolist(),
                "example_net": det.net.tolist(),
                "example_alpha_perm": det.alpha_perm,
                "example_published_perm": det.published_perm,
            }
            print(f"{name} T={T}: published={dict(pub)} multi={dict(multi)}")
    return out


def main() -> None:
    results = run()
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "anti_examples.json").write_text(json.dumps(results, indent=1), encoding="utf-8")

    lines = [
        "# Anti-examples",
        "",
        "Predictions were frozen in PREREGISTRATION.md before running. 200 repetitions "
        "per case; alpha = 0.05 bits; published rule = exactly one pair with both directions "
        ">= alpha; multi-pair variant = every such pair. Counts are repetitions out of 200.",
        "",
        "| Case | rounds | predicted (published / multi) | published rule output | multi-pair output |",
        "|---|---|---|---|---|",
    ]
    for name, by_T in results.items():
        pred = PREDICTIONS[name]
        for T, r in by_T.items():
            pub = ", ".join(f"{k}: {v}" for k, v in sorted(r["published"].items(), key=lambda kv: -kv[1]))
            mul = ", ".join(f"{k}: {v}" for k, v in sorted(r["multi"].items(), key=lambda kv: -kv[1]))
            lines.append(f"| {name} | {T} | {pred[0]} / {pred[1]} | {pub} | {mul} |")
    lines += ["", "## Example influence matrices (one 400-round realisation per case, bits)", ""]
    for name, by_T in results.items():
        r = by_T[400]
        lines += [
            f"### {name}",
            "",
            "gamma (individual influence):",
            "",
            format_matrix(np.array(r["example_gamma"]), NAMES),
            "",
            "Gamma (net influence, row influences column):",
            "",
            format_matrix(np.array(r["example_net"]), NAMES),
            "",
            f"Permutation threshold for this realisation: {r['example_alpha_perm']:.3f} bits; "
            f"published rule with that threshold returns "
            f"{pair_name(r['example_published_perm']) if r['example_published_perm'] else 'none'}.",
            "",
        ]
    (RESULTS / "anti_examples.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:20]))


if __name__ == "__main__":
    main()
