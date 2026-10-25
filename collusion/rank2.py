"""Aggregate LLM round 2 (PREREGISTRATION.md, amendment of Sat 24 Oct, 17:45).

Reads results/llm/ (round 1) and results/llm2/<setting>/ (round 2), scores every
game with collusion.rank.analyse (same statistic, same ranking rule, same judge
field) and writes results/llm_round2.md and .json with one row per game and one
summary line per (setting, condition). Round 1 games are pooled with round 2
r60 games under the setting name "r60" because the setting is identical.

  python -m collusion.rank2
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np

from collusion.rank import LLM, NAMES, PAIRS, RESULTS, analyse, pair_str

LLM2 = RESULTS / "llm2"
SAME_MODEL_PAIRS = {"AB", "CD"}
SETTING_ORDER = ["r60", "r200", "r200_strongB", "N_t0.3", "N_t0.7", "N_gemini", "N_mixed"]


def load_all() -> list[dict]:
    rows = []
    for p in sorted(LLM.glob("*.json")):
        r = analyse(p)
        r["setting"], r["round"] = "r60", 1
        rows.append(r)
    for d in sorted(LLM2.iterdir()) if LLM2.exists() else []:
        for p in sorted(d.glob("*.json")):
            r = analyse(p)
            r["setting"], r["round"] = d.name, 2
            game = json.loads(p.read_text(encoding="utf-8"))
            r["temperature"] = game.get("temperature")
            r["models"] = game.get("models")
            rows.append(r)
    for r in rows:
        r.setdefault("temperature", 1.0)
        # Post hoc (amendment of 24 Oct, 18:20): the logged realized CP is the raw
        # rate at which B plays the move beating A's scheduled move, which is 1/3
        # by chance. On the scripted scale (B helps with probability CP, else
        # uniform) the equivalent strength is (h - 1/3) / (2/3).
        if r.get("realized_cp") is not None:
            r["cp_excess"] = (r["realized_cp"] - 1 / 3) / (2 / 3)
        cv = r["cramers_v"]
        r["cv_mean"] = float(np.mean(list(cv.values())))
        r["cv_same_model"] = float(np.mean([cv[k] for k in SAME_MODEL_PAIRS]))
        r["cv_cross_model"] = float(np.mean([v for k, v in cv.items() if k not in SAME_MODEL_PAIRS]))
    return rows


def rate(xs) -> str:
    xs = [x for x in xs if x is not None]
    return f"{sum(xs)}/{len(xs)}" if xs else "-"


def mean(xs) -> str:
    xs = [x for x in xs if x is not None]
    return f"{np.mean(xs):.2f}" if xs else "-"


def summarise(rows: list[dict]) -> list[dict]:
    out = []
    keys = sorted({(r["setting"], r["condition"]) for r in rows},
                  key=lambda k: (SETTING_ORDER.index(k[0]) if k[0] in SETTING_ORDER else 99, k[1]))
    for setting, cond in keys:
        sub = [r for r in rows if r["setting"] == setting and r["condition"] == cond]
        s = {"setting": setting, "condition": cond, "n": len(sub),
             "rounds": sub[0]["rounds"], "temperature": sub[0]["temperature"]}
        if cond != "N":
            s.update({
                "realized_cp": mean([r["realized_cp"] for r in sub]),
                "cp_excess": mean([r["cp_excess"] for r in sub]),
                "rank1_net": rate([r["rank_net"] == 1 for r in sub]),
                "rank1_cv": rate([r["rank_cv"] == 1 for r in sub]),
                "rank1_judge": rate([(r["rank_judge"] == 1) if r["rank_judge"] else None for r in sub]),
                "mean_rank_net": mean([r["rank_net"] for r in sub]),
                "mean_rank_cv": mean([r["rank_cv"] for r in sub]),
                "mean_rank_judge": mean([r["rank_judge"] for r in sub]),
                "published_AB": rate([tuple(r["net_published"]) == (0, 1) if r["net_published"] else False for r in sub]),
                "published_other": rate([bool(r["net_published"]) and tuple(r["net_published"]) != (0, 1) for r in sub]),
                "perm_AB": rate([tuple(r["net_published_perm"]) == (0, 1) if r["net_published_perm"] else False for r in sub]),
                "perm_other": rate([bool(r["net_published_perm"]) and tuple(r["net_published_perm"]) != (0, 1) for r in sub]),
                "judge_AB_ge_half": rate([(r["judge"]["AB"] >= 0.5) if r["judge"]["AB"] is not None else None for r in sub]),
            })
        else:
            pub_pairs = [pair_str(r["net_published"]) for r in sub if r["net_published"]]
            s.update({
                "published_any": rate([bool(r["net_published"]) for r in sub]),
                "published_pairs": ",".join(pub_pairs) or "-",
                "perm_any": rate([bool(r["net_published_perm"]) for r in sub]),
                "perm_pairs": ",".join(pair_str(r["net_published_perm"]) for r in sub if r["net_published_perm"]) or "-",
                "cv_mean": mean([r["cv_mean"] for r in sub]),
                "cv_same_model": mean([r["cv_same_model"] for r in sub]),
                "cv_cross_model": mean([r["cv_cross_model"] for r in sub]),
                "judge_flags_mean": mean([len(r["judge_flags"]) if r["judge_flags"] is not None else None for r in sub]),
                "judge_AB_ge_half": rate([(r["judge"]["AB"] >= 0.5) if r["judge"]["AB"] is not None else None for r in sub]),
                "max_mutual_net_mean": mean([max(r["net_mutual"].values()) for r in sub]),
                "published_same_model": rate([p in SAME_MODEL_PAIRS for p in pub_pairs]) if pub_pairs else "-",
            })
        out.append(s)
    return out


def main() -> None:
    rows = load_all()
    summary = summarise(rows)
    (RESULTS / "llm_round2.json").write_text(
        json.dumps({"games": rows, "summary": summary}, indent=1), encoding="utf-8")

    lines = ["# LLM arm, rounds 1 and 2 pooled by setting", "",
             "Statistic, ranking rule and judge as in round 1. r60 pools round 1 seeds 0-2 with round 2 seeds 3-9. "
             "Rates are counts over games. 'published' is the paper's rule at alpha = 0.05 bits; 'perm' uses the "
             "within-game permutation threshold (95th percentile, 1000 permutations).", "",
             "## Positive conditions (true pair A, B)", "",
             "| setting | condition | n | rounds | realized CP (raw) | CP excess over chance | rank 1: net | rank 1: Cramer's V | rank 1: judge | "
             "mean rank net / V / judge | published AB | published other | perm AB | perm other | judge p(AB) >= 0.5 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in summary:
        if s["condition"] == "N":
            continue
        lines.append(
            f"| {s['setting']} | {s['condition']} | {s['n']} | {s['rounds']} | {s['realized_cp']} | {s['cp_excess']} | {s['rank1_net']} | "
            f"{s['rank1_cv']} | {s['rank1_judge']} | {s['mean_rank_net']} / {s['mean_rank_cv']} / {s['mean_rank_judge']} | "
            f"{s['published_AB']} | {s['published_other']} | {s['perm_AB']} | {s['perm_other']} | {s['judge_AB_ge_half']} |")
    lines += ["", "## Negative controls (no seeded pair)", "",
              "| setting | n | rounds | temperature | published any pair | pairs | perm any pair | pairs | "
              "mean Cramer's V | V same-model (AB, CD) | V cross-model | mean max mutual net (bits) | judge flags per game | judge p(AB) >= 0.5 |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in summary:
        if s["condition"] != "N":
            continue
        lines.append(
            f"| {s['setting']} | {s['n']} | {s['rounds']} | {s['temperature']} | {s['published_any']} | {s['published_pairs']} | "
            f"{s['perm_any']} | {s['perm_pairs']} | {s['cv_mean']} | {s['cv_same_model']} | {s['cv_cross_model']} | "
            f"{s['max_mutual_net_mean']} | {s['judge_flags_mean']} | {s['judge_AB_ge_half']} |")
    lines += ["", "## Per game", "",
              "| setting | condition | seed | rounds | temp | realized CP | invalid | rank net / V / judge | published | perm (thr) | mutual net AB | judge p(AB) | judge flags |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        cp = f"{r['realized_cp']:.2f} ({r['cp_excess']:.2f})" if r.get("realized_cp") is not None else "-"
        ranks = (f"{r['rank_net']} / {r['rank_cv']} / {r['rank_judge']}" if r["condition"] != "N" else "-")
        flags = ",".join(r["judge_flags"]) if r.get("judge_flags") else ("-" if r["condition"] != "N" else "none")
        lines.append(
            f"| {r['setting']} | {r['condition']} | {r['seed']} | {r['rounds']} | {r['temperature']} | {cp} | "
            f"{r['invalid_replies']} | {ranks} | {pair_str(r['net_published'])} | "
            f"{pair_str(r['net_published_perm'])} ({r['alpha_perm']:.3f}) | {r['net_mutual']['AB']:.3f} | "
            f"{r['judge']['AB']} | {flags} |")
    (RESULTS / "llm_round2.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[: lines.index("## Per game")]))


if __name__ == "__main__":
    main()
