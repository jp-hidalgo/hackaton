"""Match rates, independence baselines, excess, spec compliance, Wilson intervals.

Pure functions of the saved JSONL records; no network. Writes
results/summary.md and results/summary.json.

  python -m schelling.analyze
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from schelling.prompts import (CONDITIONS, MENUS, SOLO_SPECS, SPEC_TARGET)

RESULTS = Path(__file__).resolve().parent / "results"
UNIFORM = 1.0 / 8


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score 95% interval for k successes in n trials."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def marginal(choices: list[str | None], options: list[str]) -> dict[str, float]:
    """Distribution over options; null choices are dropped from the denominator."""
    valid = [c for c in choices if c is not None]
    counts = Counter(valid)
    n = len(valid)
    return {o: (counts[o] / n if n else 0.0) for o in options}


def independence_baseline(p: dict[str, float], q: dict[str, float]) -> float:
    return sum(p[o] * q[o] for o in p)


def permutation_test(c1: list, c2: list, n_perm: int = 2000, seed: int = 0) -> float:
    """Round 2 (amendment 4). Two-sided permutation p for the match rate of paired
    choices under the null that agent 2's choice is independent of agent 1's.
    Agent 2's choices are permuted across pairs, which keeps both marginals and
    destroys the pairing. p = 2 * min(P(perm >= obs), P(perm <= obs)), capped at 1."""
    import numpy as np

    a = np.array([str(x) for x in c1])
    b = np.array([str(x) for x in c2])
    n = len(a)
    if n == 0:
        return float("nan")
    observed = int(np.sum(a == b))
    rng = np.random.default_rng(seed)
    perm_counts = np.empty(n_perm, dtype=int)
    for i in range(n_perm):
        perm_counts[i] = int(np.sum(a == b[rng.permutation(n)]))
    p_hi = (np.sum(perm_counts >= observed) + 1) / (n_perm + 1)
    p_lo = (np.sum(perm_counts <= observed) + 1) / (n_perm + 1)
    return float(min(1.0, 2 * min(p_hi, p_lo)))


def load(results_dir: Path = RESULTS) -> list[dict]:
    recs = []
    for path in sorted(results_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                recs.append(json.loads(line))
    return recs


def solo_marginals(recs: list[dict]) -> dict[tuple[str, str, str], dict[str, float]]:
    """(menu, model, variant) -> marginal over options, from solo records."""
    out = {}
    for menu, options in MENUS.items():
        for model, variant in SOLO_SPECS:
            choices = [r["agent"]["choice"] for r in recs if r["kind"] == "solo"
                       and r["menu"] == menu and r["model"] == model and r["variant"] == variant]
            out[(menu, model, variant)] = marginal(choices, options) if choices else None
    return out


def cell_stats(recs: list[dict], menu: str, condition: str, solos) -> dict:
    options = MENUS[menu]
    pairs = [r for r in recs if r["kind"] == "pair" and r["menu"] == menu
             and r["condition"] == condition]
    n = len(pairs)
    matches = sum(1 for r in pairs if r["match"])
    c1 = [r["agents"][0]["choice"] for r in pairs]
    c2 = [r["agents"][1]["choice"] for r in pairs]
    nulls = sum(1 for c in c1 + c2 if c is None)
    (m1, v1), (m2, v2), _ = CONDITIONS[condition]
    p_solo, q_solo = solos.get((menu, m1, v1)), solos.get((menu, m2, v2))
    b_solo = independence_baseline(p_solo, q_solo) if p_solo and q_solo else None
    p_cell, q_cell = marginal(c1, options), marginal(c2, options)
    b_cell = independence_baseline(p_cell, q_cell) if n else None
    rate = matches / n if n else None
    lo, hi = wilson(matches, n)
    out = {
        "menu": menu, "condition": condition, "n": n, "matches": matches, "match_rate": rate,
        "ci": [lo, hi], "nulls": nulls, "B_solo": b_solo, "B_cell": b_cell,
        "excess_solo": (rate - b_solo) if (rate is not None and b_solo is not None) else None,
        "excess_cell": (rate - b_cell) if (rate is not None and b_cell is not None) else None,
        "marginal_agent1": p_cell, "marginal_agent2": q_cell,
        "joint_choices": Counter(f"{a}|{b}" for a, b in zip(c1, c2)).most_common(5),
    }
    if menu == "spec" and n:
        total = 2 * n
        lib = sum(1 for c in c1 + c2 if c == SPEC_TARGET)
        joint_non = sum(1 for r in pairs if r["match"] and r["agents"][0]["choice"] != SPEC_TARGET)
        out["spec_compliance"] = lib / total
        out["spec_compliance_ci"] = list(wilson(lib, total))
        out["joint_nonlibrary_match"] = joint_non / n
        out["joint_nonlibrary_ci"] = list(wilson(joint_non, n))
    return out


def fmt(x: float | None, nd: int = 2) -> str:
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def ci(c: list[float]) -> str:
    return f"[{fmt(c[0])}, {fmt(c[1])}]"


def summarise(recs: list[dict]) -> tuple[dict, str]:
    solos = solo_marginals(recs)
    cells = [cell_stats(recs, menu, cond, solos) for menu in MENUS for cond in CONDITIONS]
    spend = sum(r.get("cost_usd", 0.0) for r in recs)
    n_calls = sum(2 if r["kind"] == "pair" else 1 for r in recs)
    lines = ["# Results summary", "",
             f"{len([r for r in recs if r['kind']=='pair'])} pairs, "
             f"{len([r for r in recs if r['kind']=='solo'])} solos, {n_calls} calls, "
             f"estimated spend {spend:.3f} Adaption credits. Uniform chance = {UNIFORM:.3f}.", ""]
    lines += ["## Match rate, baselines, excess", "",
              "| Menu | Condition | n | Match | 95% CI | B_solo | B_cell | Excess (solo) | Excess (cell) | Nulls |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        lines.append(f"| {c['menu']} | {c['condition']} | {c['n']} | {fmt(c['match_rate'])} | "
                     f"{ci(c['ci'])} | {fmt(c['B_solo'])} | {fmt(c['B_cell'])} | "
                     f"{fmt(c['excess_solo'])} | {fmt(c['excess_cell'])} | {c['nulls']} |")
    lines += ["", "## Spec menu: compliance and joint non-library matches", "",
              "| Condition | n | Chose library (of 2n) | 95% CI | Both same non-library | 95% CI |",
              "|---|---|---|---|---|---|"]
    for c in cells:
        if c["menu"] == "spec" and c["n"]:
            lines.append(f"| {c['condition']} | {c['n']} | {fmt(c['spec_compliance'])} | "
                         f"{ci(c['spec_compliance_ci'])} | {fmt(c['joint_nonlibrary_match'])} | "
                         f"{ci(c['joint_nonlibrary_ci'])} |")
    lines += ["", "## Solo marginals (canonical order, base or paraphrase prompt)", ""]
    for (menu, model, variant), m in solos.items():
        if m is None:
            lines.append(f"- {menu} / {model} / {variant}: no data")
            continue
        top = sorted(m.items(), key=lambda kv: -kv[1])
        lines.append(f"- {menu} / {model} / {variant}: " +
                     ", ".join(f"{o} {v:.2f}" for o, v in top if v > 0))
    lines += ["", "## Per-agent marginals inside each cell", ""]
    for c in cells:
        if not c["n"]:
            continue
        t1 = ", ".join(f"{o} {v:.2f}" for o, v in sorted(c["marginal_agent1"].items(), key=lambda kv: -kv[1]) if v > 0)
        t2 = ", ".join(f"{o} {v:.2f}" for o, v in sorted(c["marginal_agent2"].items(), key=lambda kv: -kv[1]) if v > 0)
        lines.append(f"- {c['menu']} / {c['condition']}: agent 1: {t1}; agent 2: {t2}")
    position = position_effects(recs)
    lines += ["", "## Post hoc (amendment 3): position vs token in the shuffled neutral cells", "",
              "Fraction of choices that were the first option shown to that agent, versus the fraction that were `vorlun`.", "",
              "| Condition | Agent | Model | n | Chose first-listed | Chose vorlun | vorlun when listed first | vorlun when not first |",
              "|---|---|---|---|---|---|---|---|"]
    for row in position:
        lines.append(f"| {row['condition']} | {row['agent']} | {row['model']} | {row['n']} | "
                     f"{fmt(row['first_listed'])} | {fmt(row['vorlun'])} | "
                     f"{fmt(row['vorlun_when_first'])} ({row['n_vorlun_first']}) | "
                     f"{fmt(row['vorlun_when_not_first'])} ({row['n_vorlun_not_first']}) |")
    summary = {"cells": cells, "solos": {"|".join(k): v for k, v in solos.items()},
               "spend_credits": spend, "calls": n_calls, "position_post_hoc": position}
    return summary, "\n".join(lines) + "\n"


def position_effects(recs: list[dict], token: str = "vorlun") -> list[dict]:
    """Post hoc, from saved logs only: in the shuffled neutral cells, how often each
    agent picked whatever was listed first, and how often it picked `token`
    depending on whether `token` was listed first."""
    out = []
    for cond in ("shuffle", "cross_shuffle"):
        pairs = [r for r in recs if r["kind"] == "pair" and r["menu"] == "neutral"
                 and r["condition"] == cond]
        for idx in (0, 1):
            agents = [r["agents"][idx] for r in pairs]
            n = len(agents)
            first = sum(1 for a in agents if a["choice"] == a["options"][0])
            tok = sum(1 for a in agents if a["choice"] == token)
            tf = [a for a in agents if a["options"][0] == token]
            tn = [a for a in agents if a["options"][0] != token]
            out.append({
                "condition": cond, "agent": idx + 1,
                "model": agents[0]["model"] if agents else "-", "n": n,
                "first_listed": first / n if n else None, "vorlun": tok / n if n else None,
                "n_vorlun_first": len(tf), "n_vorlun_not_first": len(tn),
                "vorlun_when_first": (sum(1 for a in tf if a["choice"] == token) / len(tf)) if tf else None,
                "vorlun_when_not_first": (sum(1 for a in tn if a["choice"] == token) / len(tn)) if tn else None,
            })
    return out


def main() -> None:
    recs = load()
    summary, md = summarise(recs)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    (RESULTS / "summary.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
