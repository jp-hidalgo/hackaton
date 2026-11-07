"""Unit checks for collusion.netinfluence (written during the October 2026 sprint)."""

import unittest

import numpy as np

from collusion.netinfluence import (
    ALPHA,
    conditional_mi,
    cramers_v,
    detect,
    influence_matrix,
    multi_pair_rule,
    net_influence_matrix,
    permutation_threshold,
    published_rule,
)


class TestNetInfluence(unittest.TestCase):
    def test_independent_agents_score_near_zero(self):
        rng = np.random.default_rng(1)
        actions = rng.integers(0, 3, size=(2000, 4))
        det = detect(actions)
        self.assertLess(det.gamma.max(), 0.01)
        self.assertIsNone(det.published)
        self.assertEqual(det.multi, [])

    def test_perfect_mutual_pair_clears_alpha_both_directions(self):
        rng = np.random.default_rng(2)
        a = rng.integers(0, 3, size=500)
        b = (a + 2) % 3  # deterministic function of a
        c = rng.integers(0, 3, size=500)
        d = rng.integers(0, 3, size=500)
        actions = np.column_stack([a, b, c, d])
        det = detect(actions)
        self.assertGreaterEqual(det.net[0, 1], ALPHA)
        self.assertGreaterEqual(det.net[1, 0], ALPHA)
        self.assertEqual(det.published, (0, 1))
        self.assertAlmostEqual(det.gamma[0, 1], np.log2(3), places=0)

    def test_gamma_is_symmetric(self):
        rng = np.random.default_rng(3)
        actions = rng.integers(0, 3, size=(300, 4))
        gamma = influence_matrix(actions)
        np.testing.assert_allclose(gamma, gamma.T)

    def test_two_pairs_return_no_collusion_under_published_rule(self):
        rng = np.random.default_rng(4)
        a = rng.integers(0, 3, size=500)
        c = rng.integers(0, 3, size=500)
        actions = np.column_stack([a, (a + 2) % 3, c, (c + 1) % 3])
        net = net_influence_matrix(influence_matrix(actions))
        self.assertIsNone(published_rule(net))
        self.assertEqual(sorted(multi_pair_rule(net)), [(0, 1), (2, 3)])

    def test_conditioning_on_state_removes_common_cause(self):
        rng = np.random.default_rng(5)
        T = 3000
        s = rng.integers(0, 3, size=T)
        actions = np.column_stack(
            [np.where(rng.random(T) < 0.8, s, rng.integers(0, 3, size=T)) for _ in range(4)]
        )
        unconditional = conditional_mi(actions[:, 0], actions[:, 1], None, 3)
        conditional = conditional_mi(actions[:, 0], actions[:, 1], s, 3)
        self.assertGreater(unconditional, 0.3)
        self.assertLess(conditional, 0.02)

    def test_permutation_threshold_is_small_and_positive(self):
        rng = np.random.default_rng(6)
        actions = rng.integers(0, 3, size=(200, 4))
        thr = permutation_threshold(actions, n_perm=200, rng=rng)
        self.assertGreater(thr, 0.0)
        self.assertLess(thr, 0.05)

    def test_cramers_v_bounds(self):
        rng = np.random.default_rng(7)
        a = rng.integers(0, 3, size=500)
        self.assertAlmostEqual(cramers_v(a, a, 3), 1.0, places=6)
        self.assertLess(cramers_v(a, rng.integers(0, 3, size=500), 3), 0.15)


if __name__ == "__main__":
    unittest.main()
