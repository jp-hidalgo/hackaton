"""Offline tests for the Schelling-copies sprint code. No network."""

import math
import unittest
from pathlib import Path

from schelling import analyze, prompts, protocol
from schelling.run import parse_choice

ROOT = Path(__file__).resolve().parents[1]


def pair(menu, cond, c1, c2, k=0):
    return {"kind": "pair", "menu": menu, "condition": cond, "pair": k,
            "agents": [{"choice": c1}, {"choice": c2}],
            "match": c1 is not None and c1 == c2, "cost_usd": 0.0}


def solo(menu, model, variant, choice, k=0):
    return {"kind": "solo", "menu": menu, "model": model, "variant": variant, "index": k,
            "agent": {"choice": choice}, "cost_usd": 0.0}


class TestPrompts(unittest.TestCase):
    def test_prompts_frozen_in_preregistration(self):
        text = (ROOT / "schelling" / "PREREGISTRATION.md").read_text(encoding="utf-8")
        for p in prompts.PROMPTS.values():
            self.assertIn(p, text)
        for menu in prompts.MENUS.values():
            self.assertIn(", ".join(menu), text)

    def test_menus_have_eight_distinct_options(self):
        for menu in prompts.MENUS.values():
            self.assertEqual(len(menu), 8)
            self.assertEqual(len(set(menu)), 8)
        self.assertIn(prompts.SPEC_TARGET, prompts.MENUS["spec"])

    def test_shuffle_is_deterministic_and_independent_per_agent(self):
        a = prompts.option_order("spec", "shuffle", 3, 1, True)
        b = prompts.option_order("spec", "shuffle", 3, 1, True)
        c = prompts.option_order("spec", "shuffle", 3, 2, True)
        self.assertEqual(a, b)
        self.assertEqual(sorted(a), sorted(prompts.MENUS["spec"]))
        self.assertNotEqual(a, c)
        self.assertEqual(prompts.option_order("spec", "same", 3, 1, False), prompts.MENUS["spec"])

    def test_render_inserts_options_in_given_order(self):
        order = ["gym", "library"] + [o for o in prompts.MENUS["spec"] if o not in ("gym", "library")]
        text = prompts.render("spec", "base", order)
        self.assertIn("Places: gym, library,", text)


class TestRound2(unittest.TestCase):
    def test_ladder_and_menus_frozen_in_preregistration(self):
        text = (ROOT / "schelling" / "PREREGISTRATION.md").read_text(encoding="utf-8")
        for level in ("L1", "L2", "L3"):
            self.assertIn(prompts.PROMPTS[("spec", level)], text)
        for menu in ("neutralB", "neutralC", "neutralD"):
            self.assertIn(", ".join(prompts.MENUS[menu]), text)
            self.assertEqual(len(set(prompts.MENUS[menu])), 8)
        self.assertEqual(prompts.PROMPTS[("spec", "L0")], prompts.PROMPTS[("spec", "base")])

    def test_neutral_menus_share_prompt_text(self):
        a = prompts.render("neutralB", "base", prompts.MENUS["neutralB"])
        self.assertIn("Tokens: morvash, kelint,", a)
        self.assertTrue(a.startswith("You are one of two AI agents."))

    def test_option_order2_seeding(self):
        a = prompts.option_order2("neutral", "shuffle", 5, 1, True)
        self.assertEqual(a, prompts.option_order2("neutral", "shuffle", 5, 1, True))
        self.assertNotEqual(a, prompts.option_order2("neutral", "shuffle", 5, 2, True))
        self.assertNotEqual(a, prompts.option_order2("neutral", "other_cell", 5, 1, True))
        self.assertEqual(sorted(a), sorted(prompts.MENUS["neutral"]))
        self.assertEqual(prompts.option_order2("neutral", "same", 5, 1, False), prompts.MENUS["neutral"])

    def test_round2_job_keys_unique_and_counts(self):
        from schelling import round2
        jobs = []
        for b in ("A", "C", "D", "E"):
            jobs += round2.BLOCKS[b]()
        keys = [j["key"] for j in jobs]
        # solos shared across blocks are deduplicated by jobs_for, not within a block list
        dedup = round2.jobs_for(["A", "C", "D", "E"])
        self.assertEqual(len({j["key"] for j in dedup}), len(dedup))
        pairs_a = [j for j in round2.block_a() if j["kind"] == "pair2"]
        self.assertEqual(len(pairs_a), 5 * 100 + 3 * 3 * 50)
        pairs_d = [j for j in round2.block_d() if j["kind"] == "pair2"]
        self.assertEqual(len(pairs_d), 4 * 2 * 60)
        self.assertTrue(all(j["menu"] == "spec" for j in pairs_d))
        c_default = [j for j in round2.block_c() if j["kind"] == "pair2" and j["agents"][0]["reasoning"] == "default"]
        self.assertEqual(len(c_default), 3 * 2 * 50)
        self.assertEqual(round2.max_tokens(c_default[0]["agents"][0]), round2.REASONING_MAX_TOKENS)

    def test_permutation_test(self):
        import random
        rng = random.Random(0)
        opts = ["a", "b", "c", "d"]
        c1 = [rng.choice(opts) for _ in range(60)]
        dependent = list(c1)
        p_dep = analyze.permutation_test(c1, dependent, n_perm=500, seed=1)
        self.assertLess(p_dep, 0.05)
        independent = [rng.choice(opts) for _ in range(60)]
        p_ind = analyze.permutation_test(c1, independent, n_perm=500, seed=1)
        self.assertGreater(p_ind, 0.05)
        self.assertLessEqual(p_ind, 1.0)


class TestParse(unittest.TestCase):
    def test_json_choice(self):
        opts = prompts.MENUS["spec"]
        self.assertEqual(parse_choice('{"choice": "Library"}', opts), "library")
        self.assertEqual(parse_choice('```json\n{"choice": "town square"}\n```', opts), "town square")

    def test_models_named_in_preregistration(self):
        text = (ROOT / "schelling" / "PREREGISTRATION.md").read_text(encoding="utf-8")
        self.assertIn(f"COPY_MODEL = {prompts.COPY_MODEL}", text)
        self.assertIn(f"OTHER_MODEL = {prompts.OTHER_MODEL}", text)
        self.assertNotEqual(prompts.COPY_MODEL, prompts.OTHER_MODEL)

    def test_output_text_fallback(self):
        from schelling.run import output_text
        resp = {"output": [{"type": "reasoning"},
                           {"type": "message", "content": [{"type": "output_text", "text": "a"},
                                                           {"type": "output_text", "text": "b"}]}]}
        self.assertEqual(output_text(resp), "ab")
        self.assertEqual(output_text({"output_text": "x"}), "x")

    def test_last_valid_choice_wins(self):
        opts = ["red", "green", "blue"]
        text = 'reply in the form {"choice": "<colour>"}. I pick blue. {"choice": "blue"}'
        self.assertEqual(parse_choice(text, opts), "blue")

    def test_fallback_unique_mention(self):
        opts = prompts.MENUS["neutral"]
        self.assertEqual(parse_choice("I pick brimmoth.", opts), "brimmoth")
        self.assertIsNone(parse_choice("brimmoth or vorlun", opts))
        self.assertIsNone(parse_choice('{"choice": "castle"}', opts))


class TestAnalyze(unittest.TestCase):
    def test_wilson_bounds(self):
        lo, hi = analyze.wilson(0, 30)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)
        lo, hi = analyze.wilson(30, 30)
        self.assertEqual(hi, 1.0)
        lo, hi = analyze.wilson(15, 30)
        self.assertTrue(lo < 0.5 < hi)
        self.assertTrue(math.isnan(analyze.wilson(0, 0)[0]))

    def test_marginal_and_baseline(self):
        opts = ["a", "b", "c"]
        p = analyze.marginal(["a", "a", "b", None], opts)
        self.assertAlmostEqual(p["a"], 2 / 3)
        self.assertAlmostEqual(analyze.independence_baseline(p, p), (2 / 3) ** 2 + (1 / 3) ** 2)

    def test_cell_stats_and_excess(self):
        gpt, gem = prompts.COPY_MODEL, prompts.OTHER_MODEL
        recs = []
        recs += [solo("spec", gpt, "base", "library", k) for k in range(8)]
        recs += [solo("spec", gpt, "base", "gym", k) for k in range(8, 10)]
        recs += [solo("spec", gem, "base", "library", k) for k in range(10)]
        recs += [pair("spec", "same", "library", "library", k) for k in range(8)]
        recs += [pair("spec", "same", "gym", "gym", 8), pair("spec", "same", "gym", "library", 9)]
        solos = analyze.solo_marginals(recs)
        c = analyze.cell_stats(recs, "spec", "same", solos)
        self.assertEqual(c["n"], 10)
        self.assertAlmostEqual(c["match_rate"], 0.9)
        self.assertAlmostEqual(c["B_solo"], 0.64 + 0.04)
        self.assertAlmostEqual(c["excess_solo"], 0.9 - 0.68)
        self.assertAlmostEqual(c["spec_compliance"], 17 / 20)
        self.assertAlmostEqual(c["joint_nonlibrary_match"], 0.1)
        self.assertEqual(c["nulls"], 0)
        summary, md = analyze.summarise(recs)
        self.assertIn("| spec | same | 10 | 0.90 |", md)


class TestProtocol(unittest.TestCase):
    def test_policy_counts(self):
        recs = [pair("spec", "same", "library", "library", 0),
                pair("spec", "same", "library", "gym", 1),
                pair("spec", "same", "gym", "gym", 2),
                pair("spec", "same", "gym", "library", 3),
                pair("spec", "same", None, "library", 4)]
        s = protocol.policy_stats(recs, "spec", "same")
        self.assertEqual(s["worker_offspec"], 2)
        self.assertEqual(s["offspec_approved"], 1)
        self.assertAlmostEqual(s["offspec_approved_rate"], 0.5)
        self.assertEqual(s["worker_onspec"], 2)
        self.assertEqual(s["onspec_flagged"], 1)
        self.assertAlmostEqual(s["flag_rate"], 3 / 5)


if __name__ == "__main__":
    unittest.main()
