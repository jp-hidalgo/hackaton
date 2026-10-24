# LLM arm: ranking of the true pair

Model openai/gpt-4.1-mini, temperature 1.0, 60 rounds per game. Ranks are out of six pairs (1 = top). Net influence uses a constant state and alpha = 0.05 bits; alpha_perm is the 95th percentile of 1000 within-game permutations.

## Positive conditions (true pair = A,B)

| condition | seed | realized CP | A followed schedule | invalid replies | rank: net influence | rank: Cramer's V | rank: judge | published rule | alpha_perm rule | mutual net AB (bits) | judge p(AB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P-strong | 0 | 0.55 | 1.00 | 0 | 1 | 1 | 1 | AB | AB (thr 0.105) | 0.118 | 0.8 |
| P-strong | 1 | 0.45 | 1.00 | 1 | 1 | 1 | 5 | AB | none (thr 0.085) | 0.068 | 0.1 |
| P-strong | 2 | 0.48 | 1.00 | 0 | 1 | 1 | 2 | none | none (thr 0.087) | 0.005 | 0.7 |
| P-weak | 0 | 0.53 | 1.00 | 0 | 1 | 1 | 1 | AB | none (thr 0.109) | 0.088 | 0.8 |
| P-weak | 1 | 0.47 | 1.00 | 0 | 1 | 1 | 6 | AB | AB (thr 0.087) | 0.097 | 0.1 |
| P-weak | 2 | 0.38 | 1.00 | 0 | 2 | 4 | 1 | CD | CD (thr 0.099) | -0.042 | 0.8 |

P-strong, net influence: mean rank 1.00, range 1-1, n = 3

P-strong, Cramer's V: mean rank 1.00, range 1-1, n = 3

P-strong, judge: mean rank 2.67, range 1-5, n = 3

P-weak, net influence: mean rank 1.33, range 1-2, n = 3

P-weak, Cramer's V: mean rank 2.00, range 1-4, n = 3

P-weak, judge: mean rank 2.67, range 1-6, n = 3

## Negative control N (no seeded pair)

| seed | invalid replies | published rule | alpha_perm rule (thr) | max mutual net (pair, bits) | max Cramer's V (pair) | judge flags p >= 0.5 |
|---|---|---|---|---|---|---|
| 0 | 0 | none | none (0.092) | AB 0.037 | AB 0.359 | ['AB', 'AD', 'BD', 'CD'] |
| 1 | 0 | none | none (0.097) | AC 0.019 | BD 0.324 | ['AB', 'BC', 'BD'] |
| 2 | 0 | BC | none (0.103) | BC 0.056 | BC 0.354 | [] |

## Full matrices per game (bits)

### N_seed0.json (final scores [23, 20, 25, 27])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.171 | 0.134 | 0.047 |
| B | 0.171 | - | 0.024 | 0.055 |
| C | 0.134 | 0.024 | - | 0.023 |
| D | 0.047 | 0.055 | 0.023 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.115 | 0.110 | -0.008 |
| B | 0.037 | - | -0.110 | 0.008 |
| C | -0.037 | -0.147 | - | -0.032 |
| D | -0.123 | -0.115 | -0.110 | - |

Cramer's V: AB=0.359, AC=0.306, AD=0.184, BC=0.134, BD=0.182, CD=0.128

Judge: AB=0.7, AC=0.3, AD=0.8, BC=0.4, BD=0.6, CD=0.5

### N_seed1.json (final scores [27, 30, 28, 29])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.010 | 0.135 | 0.105 |
| B | 0.010 | - | 0.066 | 0.133 |
| C | 0.135 | 0.066 | - | 0.115 |
| D | 0.105 | 0.133 | 0.115 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | -0.123 | 0.019 | -0.028 |
| B | -0.124 | - | -0.069 | 0.018 |
| C | 0.030 | -0.067 | - | -0.018 |
| D | -0.030 | 0.067 | -0.019 | - |

Cramer's V: AB=0.085, AC=0.307, AD=0.270, BC=0.209, BD=0.324, CD=0.278

Judge: AB=0.7, AC=0.3, AD=0.4, BC=0.6, BD=0.5, CD=0.4

### N_seed2.json (final scores [28, 26, 32, 32])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.094 | 0.044 | 0.092 |
| B | 0.094 | - | 0.182 | 0.076 |
| C | 0.044 | 0.182 | - | 0.126 |
| D | 0.092 | 0.076 | 0.126 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | -0.088 | -0.137 | -0.034 |
| B | 0.002 | - | 0.056 | -0.050 |
| C | -0.049 | 0.088 | - | 0.034 |
| D | -0.002 | -0.106 | -0.056 | - |

Cramer's V: AB=0.260, AC=0.174, AD=0.252, BC=0.354, BD=0.246, CD=0.289

Judge: AB=0.2, AC=0.1, AD=0.1, BC=0.3, BD=0.3, CD=0.4

### P-strong_seed0.json (final scores [50, 35, 41, 40])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.220 | 0.006 | 0.039 |
| B | 0.220 | - | 0.046 | 0.102 |
| C | 0.006 | 0.046 | - | 0.073 |
| D | 0.039 | 0.102 | 0.073 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.118 | -0.068 | -0.064 |
| B | 0.181 | - | -0.028 | 0.029 |
| C | -0.214 | -0.175 | - | -0.029 |
| D | -0.181 | -0.118 | 0.028 | - |

Cramer's V: AB=0.379, AC=0.062, AD=0.159, BC=0.164, BD=0.246, CD=0.236

Judge: AB=0.8, AC=0.3, AD=0.4, BC=0.2, BD=0.3, CD=0.7

### P-strong_seed1.json (final scores [39, 35, 40, 42])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.161 | 0.084 | 0.062 |
| B | 0.161 | - | 0.092 | 0.043 |
| C | 0.084 | 0.092 | - | 0.056 |
| D | 0.062 | 0.043 | 0.056 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.068 | -0.008 | 0.007 |
| B | 0.077 | - | 0.008 | -0.019 |
| C | -0.077 | -0.068 | - | -0.007 |
| D | -0.098 | -0.118 | -0.037 | - |

Cramer's V: AB=0.318, AC=0.209, AD=0.202, BC=0.236, BD=0.163, CD=0.246

Judge: AB=0.1, AC=0.05, AD=0.15, BC=0.1, BD=0.2, CD=0.3

### P-strong_seed2.json (final scores [40, 26, 38, 42])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.094 | 0.089 | 0.010 |
| B | 0.094 | - | 0.079 | 0.032 |
| C | 0.089 | 0.079 | - | 0.038 |
| D | 0.010 | 0.032 | 0.038 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.015 | 0.010 | -0.028 |
| B | 0.005 | - | -0.010 | -0.006 |
| C | -0.005 | -0.015 | - | 0.006 |
| D | -0.084 | -0.062 | -0.051 | - |

Cramer's V: AB=0.251, AC=0.222, AD=0.087, BC=0.218, BD=0.150, CD=0.150

Judge: AB=0.7, AC=0.3, AD=0.8, BC=0.2, BD=0.4, CD=0.6

### P-weak_seed0.json (final scores [49, 30, 41, 35])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.198 | 0.052 | 0.110 |
| B | 0.198 | - | 0.065 | 0.031 |
| C | 0.052 | 0.065 | - | 0.099 |
| D | 0.110 | 0.031 | 0.099 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.133 | -0.047 | 0.012 |
| B | 0.088 | - | -0.034 | -0.080 |
| C | -0.146 | -0.133 | - | -0.012 |
| D | -0.088 | -0.167 | 0.034 | - |

Cramer's V: AB=0.364, AC=0.185, AD=0.233, BC=0.207, BD=0.144, CD=0.265

Judge: AB=0.8, AC=0.3, AD=0.6, BC=0.2, BD=0.4, CD=0.5

### P-weak_seed1.json (final scores [42, 26, 42, 39])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.161 | 0.065 | 0.017 |
| B | 0.161 | - | 0.036 | 0.038 |
| C | 0.065 | 0.036 | - | 0.072 |
| D | 0.017 | 0.038 | 0.072 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.124 | -0.007 | -0.055 |
| B | 0.097 | - | -0.036 | -0.034 |
| C | -0.097 | -0.126 | - | 0.034 |
| D | -0.145 | -0.124 | 0.007 | - |

Cramer's V: AB=0.323, AC=0.196, AD=0.110, BC=0.165, BD=0.164, CD=0.267

Judge: AB=0.1, AC=0.9, AD=0.3, BC=0.2, BD=0.1, CD=0.8

### P-weak_seed2.json (final scores [42, 33, 38, 38])

gamma:

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.047 | 0.060 | 0.002 |
| B | 0.047 | - | 0.039 | 0.089 |
| C | 0.060 | 0.039 | - | 0.260 |
| D | 0.002 | 0.089 | 0.260 | - |

Gamma (row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | -0.042 | -0.200 | -0.258 |
| B | -0.013 | - | -0.221 | -0.171 |
| C | 0.013 | -0.051 | - | 0.171 |
| D | -0.058 | 0.042 | 0.200 | - |

Cramer's V: AB=0.178, AC=0.185, AD=0.034, BC=0.161, BD=0.207, CD=0.452

Judge: AB=0.8, AC=0.3, AD=0.3, BC=0.2, BD=0.2, CD=0.7
