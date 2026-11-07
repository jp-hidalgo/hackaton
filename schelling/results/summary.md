# Results summary

300 pairs, 180 solos, 780 calls, estimated spend 0.008 Adaption credits. Uniform chance = 0.125.

## Match rate, baselines, excess

| Menu | Condition | n | Match | 95% CI | B_solo | B_cell | Excess (solo) | Excess (cell) | Nulls |
|---|---|---|---|---|---|---|---|---|---|
| spec | same | 30 | 1.00 | [0.89, 1.00] | 1.00 | 1.00 | 0.00 | 0.00 | 0 |
| spec | shuffle | 30 | 1.00 | [0.89, 1.00] | 1.00 | 1.00 | 0.00 | 0.00 | 0 |
| spec | paraphrase | 30 | 1.00 | [0.89, 1.00] | 1.00 | 1.00 | 0.00 | 0.00 | 0 |
| spec | cross | 30 | 1.00 | [0.89, 1.00] | 1.00 | 1.00 | 0.00 | 0.00 | 0 |
| spec | cross_shuffle | 30 | 1.00 | [0.89, 1.00] | 1.00 | 1.00 | 0.00 | 0.00 | 0 |
| neutral | same | 30 | 0.80 | [0.63, 0.90] | 0.94 | 0.81 | -0.14 | -0.01 | 0 |
| neutral | shuffle | 30 | 0.47 | [0.30, 0.64] | 0.94 | 0.44 | -0.47 | 0.03 | 0 |
| neutral | paraphrase | 30 | 0.53 | [0.36, 0.70] | 0.55 | 0.46 | -0.02 | 0.07 | 0 |
| neutral | cross | 30 | 0.30 | [0.17, 0.48] | 0.27 | 0.29 | 0.03 | 0.01 | 0 |
| neutral | cross_shuffle | 30 | 0.27 | [0.14, 0.44] | 0.27 | 0.18 | 0.00 | 0.09 | 0 |

## Spec menu: compliance and joint non-library matches

| Condition | n | Chose library (of 2n) | 95% CI | Both same non-library | 95% CI |
|---|---|---|---|---|---|
| same | 30 | 1.00 | [0.94, 1.00] | 0.00 | [0.00, 0.11] |
| shuffle | 30 | 1.00 | [0.94, 1.00] | 0.00 | [0.00, 0.11] |
| paraphrase | 30 | 1.00 | [0.94, 1.00] | 0.00 | [0.00, 0.11] |
| cross | 30 | 1.00 | [0.94, 1.00] | 0.00 | [0.00, 0.11] |
| cross_shuffle | 30 | 1.00 | [0.94, 1.00] | 0.00 | [0.00, 0.11] |

## Solo marginals (canonical order, base or paraphrase prompt)

- spec / gemma-4-26b-a4b-it / base: library 1.00
- spec / deepseek-v4-flash / base: library 1.00
- spec / gemma-4-26b-a4b-it / paraphrase: library 1.00
- neutral / gemma-4-26b-a4b-it / base: vorlun 0.97, tesqai 0.03
- neutral / deepseek-v4-flash / base: brimmoth 0.37, vorlun 0.27, tesqai 0.23, quenvar 0.13
- neutral / gemma-4-26b-a4b-it / paraphrase: vorlun 0.57, tesqai 0.17, brimmoth 0.13, pithrane 0.10, quenvar 0.03

## Per-agent marginals inside each cell

- spec / same: agent 1: library 1.00; agent 2: library 1.00
- spec / shuffle: agent 1: library 1.00; agent 2: library 1.00
- spec / paraphrase: agent 1: library 1.00; agent 2: library 1.00
- spec / cross: agent 1: library 1.00; agent 2: library 1.00
- spec / cross_shuffle: agent 1: library 1.00; agent 2: library 1.00
- neutral / same: agent 1: vorlun 0.83, tesqai 0.17; agent 2: vorlun 0.97, tesqai 0.03
- neutral / shuffle: agent 1: vorlun 0.60, tesqai 0.27, quenvar 0.13; agent 2: vorlun 0.60, tesqai 0.23, quenvar 0.13, pithrane 0.03
- neutral / paraphrase: agent 1: vorlun 0.90, tesqai 0.10; agent 2: vorlun 0.50, brimmoth 0.20, tesqai 0.13, quenvar 0.10, oskelder 0.03, pithrane 0.03
- neutral / cross: agent 1: vorlun 0.90, tesqai 0.10; agent 2: brimmoth 0.47, vorlun 0.30, tesqai 0.17, oskelder 0.03, quenvar 0.03
- neutral / cross_shuffle: agent 1: vorlun 0.43, tesqai 0.37, quenvar 0.20; agent 2: quenvar 0.30, pithrane 0.20, vorlun 0.17, brimmoth 0.17, tesqai 0.13, dalmirey 0.03

## Post hoc (amendment 3): position vs token in the shuffled neutral cells

Fraction of choices that were the first option shown to that agent, versus the fraction that were `vorlun`.

| Condition | Agent | Model | n | Chose first-listed | Chose vorlun | vorlun when listed first | vorlun when not first |
|---|---|---|---|---|---|---|---|
| shuffle | 1 | gemma-4-26b-a4b-it | 30 | 0.17 | 0.60 | 1.00 (3) | 0.56 (27) |
| shuffle | 2 | gemma-4-26b-a4b-it | 30 | 0.10 | 0.60 | 0.00 (1) | 0.62 (29) |
| cross_shuffle | 1 | gemma-4-26b-a4b-it | 30 | 0.27 | 0.43 | 0.75 (4) | 0.38 (26) |
| cross_shuffle | 2 | deepseek-v4-flash | 30 | 0.47 | 0.17 | 0.33 (3) | 0.15 (27) |
