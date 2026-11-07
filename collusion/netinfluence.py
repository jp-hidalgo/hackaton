"""Pairwise net influence (Bonjour, Aggarwal and Bhargava, UAI 2022).

Implements, from the paper:
  - individual influence gamma(i; j) = I(A_i; A_j | S)        (Eq. 5 / Eq. 6)
  - net influence Gamma(i; j) = gamma(i; j) - max_k gamma(k; j) (Eq. 3)
  - the published decision rule: exactly one pair with both
    directions >= alpha                                        (Eq. 4, Alg. 1)

New in this sprint (not in the paper; see PREREGISTRATION.md):
  - a permutation null that gives a sample-size-adjusted threshold
  - a multi-pair variant that drops the exactly-one-pair gate

Conventions
-----------
actions: integer array of shape (T, n). Row t is round t, column i is agent
i's action, coded 0..K-1.
states: optional integer array of shape (T,). If None, a single constant
state is used (the pre-registered primary analysis).
All information quantities are in bits (log base 2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

import numpy as np

ALPHA = 0.05  # collusion threshold used throughout Bonjour et al.


def _mi_from_counts(joint: np.ndarray) -> float:
    """Plug-in mutual information in bits from a 2-D contingency table."""
    total = joint.sum()
    if total == 0:
        return 0.0
    p = joint / total
    px = p.sum(axis=1, keepdims=True)
    py = p.sum(axis=0, keepdims=True)
    mask = p > 0
    return float((p[mask] * np.log2(p[mask] / (px @ py)[mask])).sum())


def conditional_mi(
    a: np.ndarray, b: np.ndarray, states: np.ndarray | None, n_actions: int
) -> float:
    """I(A; B | S) by plug-in counts. gamma(i; j) of the paper (Eq. 5)."""
    a = np.asarray(a)
    b = np.asarray(b)
    if states is None:
        joint = np.zeros((n_actions, n_actions))
        np.add.at(joint, (a, b), 1)
        return _mi_from_counts(joint)
    states = np.asarray(states)
    total = len(a)
    out = 0.0
    for s in np.unique(states):
        sel = states == s
        joint = np.zeros((n_actions, n_actions))
        np.add.at(joint, (a[sel], b[sel]), 1)
        out += sel.sum() / total * _mi_from_counts(joint)
    return float(out)


def influence_matrix(
    actions: np.ndarray, states: np.ndarray | None = None, n_actions: int | None = None
) -> np.ndarray:
    """n x n matrix of gamma(i; j). Symmetric for a simultaneous game."""
    actions = np.asarray(actions)
    T, n = actions.shape
    if n_actions is None:
        n_actions = int(actions.max()) + 1
    gamma = np.zeros((n, n))
    for i, j in combinations(range(n), 2):
        g = conditional_mi(actions[:, i], actions[:, j], states, n_actions)
        gamma[i, j] = gamma[j, i] = g
    return gamma


def net_influence_matrix(gamma: np.ndarray) -> np.ndarray:
    """Gamma(i; j) = gamma(i; j) - max_{k != i, j} gamma(k; j)   (Eq. 3)."""
    n = gamma.shape[0]
    net = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            others = [gamma[k, j] for k in range(n) if k not in (i, j)]
            net[i, j] = gamma[i, j] - (max(others) if others else 0.0)
    return net


def mutual_net(net: np.ndarray) -> dict[tuple[int, int], float]:
    """min(Gamma(i; j), Gamma(j; i)) for every unordered pair."""
    n = net.shape[0]
    return {(i, j): float(min(net[i, j], net[j, i])) for i, j in combinations(range(n), 2)}


def published_rule(net: np.ndarray, alpha: float = ALPHA) -> tuple[int, int] | None:
    """Algorithm 1 of Bonjour et al.: exactly one pair with both directions >= alpha."""
    hits = [pair for pair, v in mutual_net(net).items() if v >= alpha]
    return hits[0] if len(hits) == 1 else None


def multi_pair_rule(net: np.ndarray, alpha: float = ALPHA) -> list[tuple[int, int]]:
    """Sprint addition: every pair with both directions >= alpha, no gate."""
    return [pair for pair, v in mutual_net(net).items() if v >= alpha]


def permutation_threshold(
    actions: np.ndarray,
    states: np.ndarray | None = None,
    n_perm: int = 1000,
    quantile: float = 0.95,
    rng: np.random.Generator | None = None,
) -> float:
    """Sprint addition: 95th percentile of max-over-pairs mutual net influence
    when every agent's action sequence is permuted independently."""
    rng = rng or np.random.default_rng(0)
    actions = np.asarray(actions)
    n_actions = int(actions.max()) + 1
    maxima = np.empty(n_perm)
    for b in range(n_perm):
        shuffled = np.column_stack(
            [rng.permutation(actions[:, i]) for i in range(actions.shape[1])]
        )
        net = net_influence_matrix(influence_matrix(shuffled, states, n_actions))
        maxima[b] = max(mutual_net(net).values())
    return float(np.quantile(maxima, quantile))


@dataclass
class Detection:
    gamma: np.ndarray
    net: np.ndarray
    mutual: dict[tuple[int, int], float]
    published: tuple[int, int] | None
    multi: list[tuple[int, int]]
    alpha: float = ALPHA
    alpha_perm: float | None = None
    published_perm: tuple[int, int] | None = None
    multi_perm: list[tuple[int, int]] = field(default_factory=list)

    def ranking(self) -> list[tuple[tuple[int, int], float]]:
        return sorted(self.mutual.items(), key=lambda kv: -kv[1])


def detect(
    actions: np.ndarray,
    states: np.ndarray | None = None,
    alpha: float = ALPHA,
    n_actions: int | None = None,
    permutation: int = 0,
    rng: np.random.Generator | None = None,
) -> Detection:
    """Run the full pipeline. permutation > 0 also computes alpha_perm."""
    actions = np.asarray(actions)
    gamma = influence_matrix(actions, states, n_actions)
    net = net_influence_matrix(gamma)
    det = Detection(
        gamma=gamma,
        net=net,
        mutual=mutual_net(net),
        published=published_rule(net, alpha),
        multi=multi_pair_rule(net, alpha),
        alpha=alpha,
    )
    if permutation > 0:
        det.alpha_perm = permutation_threshold(actions, states, permutation, rng=rng)
        det.published_perm = published_rule(net, det.alpha_perm)
        det.multi_perm = multi_pair_rule(net, det.alpha_perm)
    return det


def cramers_v(a: np.ndarray, b: np.ndarray, n_actions: int) -> float:
    """Cramér's V between two categorical sequences. Baseline 'ordinary
    action correlation' used in the ranking comparison."""
    joint = np.zeros((n_actions, n_actions))
    np.add.at(joint, (np.asarray(a), np.asarray(b)), 1)
    T = joint.sum()
    if T == 0:
        return 0.0
    expected = np.outer(joint.sum(axis=1), joint.sum(axis=0)) / T
    mask = expected > 0
    chi2 = ((joint[mask] - expected[mask]) ** 2 / expected[mask]).sum()
    k = min(n_actions, n_actions) - 1
    return float(np.sqrt(chi2 / (T * k))) if k > 0 else 0.0


def cramers_v_matrix(actions: np.ndarray, n_actions: int | None = None) -> np.ndarray:
    actions = np.asarray(actions)
    n = actions.shape[1]
    if n_actions is None:
        n_actions = int(actions.max()) + 1
    out = np.zeros((n, n))
    for i, j in combinations(range(n), 2):
        out[i, j] = out[j, i] = cramers_v(actions[:, i], actions[:, j], n_actions)
    return out


def format_matrix(m: np.ndarray, names: list[str], digits: int = 3) -> str:
    """Markdown table for a square matrix."""
    head = "| | " + " | ".join(names) + " |"
    sep = "|---|" + "---|" * len(names)
    rows = []
    for i, name in enumerate(names):
        cells = [
            "-" if i == j else f"{m[i, j]:.{digits}f}" for j in range(len(names))
        ]
        rows.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join([head, sep, *rows])
