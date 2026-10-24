# Anti-examples

Predictions were frozen in PREREGISTRATION.md before running. 200 repetitions per case; alpha = 0.05 bits; published rule = exactly one pair with both directions >= alpha; multi-pair variant = every such pair. Counts are repetitions out of 200.

| Case | rounds | predicted (published / multi) | published rule output | multi-pair output |
|---|---|---|---|---|
| AE1 two pairs (A,B),(C,D) CP 0.8 | 100 | no collusion / both pairs | none: 200 | (A,B),(C,D): 200 |
| AE1 two pairs (A,B),(C,D) CP 0.8 | 400 | no collusion / both pairs | none: 200 | (A,B),(C,D): 200 |
| AE2 one-way copying B<-A(t-1) p 0.8 | 100 | (A,B) / (A,B) | none: 183, (C,D): 6, (A,B): 4, (B,D): 3, (A,D): 2, (B,C): 2 | none: 183, (C,D): 6, (A,B): 4, (B,D): 3, (A,D): 2, (B,C): 2 |
| AE2 one-way copying B<-A(t-1) p 0.8 | 400 | (A,B) / (A,B) | none: 200 | none: 200 |
| AE2b one-way copying B<-A(t) p 0.8 (exploratory) | 100 | (A,B), post-hoc / (A,B), post-hoc | (A,B): 198, none: 2 | (A,B): 198, (A,B),(C,D): 2 |
| AE2b one-way copying B<-A(t) p 0.8 (exploratory) | 400 | (A,B), post-hoc / (A,B), post-hoc | (A,B): 200 | (A,B): 200 |
| AE3 shared skewed marginal, independent | 100 | no collusion / none | none: 182, (C,D): 5, (B,C): 4, (A,D): 3, (B,D): 3, (A,C): 2, (A,B): 1 | none: 182, (C,D): 5, (B,C): 4, (A,D): 3, (B,D): 3, (A,C): 2, (A,B): 1 |
| AE3 shared skewed marginal, independent | 400 | no collusion / none | none: 200 | none: 200 |
| AE4 common cause, constant state | 100 | no collusion (gate fires) / all six pairs | none: 100, (B,D): 22, (A,D): 21, (C,D): 19, (A,B): 14, (B,C): 12, (A,C): 12 | none: 98, (B,D): 22, (A,D): 21, (C,D): 19, (A,B): 14, (B,C): 12, (A,C): 12, (A,C),(B,D): 2 |
| AE4 common cause, constant state | 400 | no collusion (gate fires) / all six pairs | none: 166, (B,D): 11, (B,C): 8, (C,D): 7, (A,C): 5, (A,D): 2, (A,B): 1 | none: 166, (B,D): 11, (B,C): 8, (C,D): 7, (A,C): 5, (A,D): 2, (A,B): 1 |
| AE4 common cause, conditioned on state | 100 | no collusion / none | none: 170, (C,D): 8, (A,B): 7, (B,D): 6, (A,D): 4, (B,C): 3, (A,C): 2 | none: 170, (C,D): 8, (A,B): 7, (B,D): 6, (A,D): 4, (B,C): 3, (A,C): 2 |
| AE4 common cause, conditioned on state | 400 | no collusion / none | none: 200 | none: 200 |

## Example influence matrices (one 400-round realisation per case, bits)

### AE1 two pairs (A,B),(C,D) CP 0.8

gamma (individual influence):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 1.038 | 0.002 | 0.003 |
| B | 1.038 | - | 0.011 | 0.009 |
| C | 0.002 | 0.011 | - | 0.862 |
| D | 0.003 | 0.009 | 0.862 | - |

Gamma (net influence, row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 1.027 | -0.860 | -0.859 |
| B | 1.035 | - | -0.851 | -0.853 |
| C | -1.036 | -1.027 | - | 0.853 |
| D | -1.035 | -1.029 | 0.851 | - |

Permutation threshold for this realisation: 0.014 bits; published rule with that threshold returns none.

### AE2 one-way copying B<-A(t-1) p 0.8

gamma (individual influence):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.005 | 0.002 | 0.004 |
| B | 0.005 | - | 0.012 | 0.004 |
| C | 0.002 | 0.012 | - | 0.017 |
| D | 0.004 | 0.004 | 0.017 | - |

Gamma (net influence, row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | -0.007 | -0.015 | -0.013 |
| B | 0.001 | - | -0.005 | -0.013 |
| C | -0.003 | 0.007 | - | 0.013 |
| D | -0.001 | -0.008 | 0.005 | - |

Permutation threshold for this realisation: 0.013 bits; published rule with that threshold returns none.

### AE2b one-way copying B<-A(t) p 0.8 (exploratory)

gamma (individual influence):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.847 | 0.002 | 0.004 |
| B | 0.847 | - | 0.005 | 0.011 |
| C | 0.002 | 0.005 | - | 0.018 |
| D | 0.004 | 0.011 | 0.018 | - |

Gamma (net influence, row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.835 | -0.016 | -0.014 |
| B | 0.842 | - | -0.013 | -0.007 |
| C | -0.845 | -0.841 | - | 0.007 |
| D | -0.842 | -0.835 | 0.013 | - |

Permutation threshold for this realisation: 0.015 bits; published rule with that threshold returns (A,B).

### AE3 shared skewed marginal, independent

gamma (individual influence):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.001 | 0.002 | 0.004 |
| B | 0.001 | - | 0.002 | 0.001 |
| C | 0.002 | 0.002 | - | 0.006 |
| D | 0.004 | 0.001 | 0.006 | - |

Gamma (net influence, row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | -0.001 | -0.004 | -0.002 |
| B | -0.003 | - | -0.004 | -0.005 |
| C | -0.002 | 0.001 | - | 0.002 |
| D | 0.002 | -0.001 | 0.004 | - |

Permutation threshold for this realisation: 0.015 bits; published rule with that threshold returns none.

### AE4 common cause, constant state

gamma (individual influence):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.545 | 0.496 | 0.566 |
| B | 0.545 | - | 0.528 | 0.567 |
| C | 0.496 | 0.528 | - | 0.635 |
| D | 0.566 | 0.567 | 0.635 | - |

Gamma (net influence, row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | -0.022 | -0.139 | -0.069 |
| B | -0.021 | - | -0.107 | -0.068 |
| C | -0.070 | -0.039 | - | 0.068 |
| D | 0.021 | 0.022 | 0.107 | - |

Permutation threshold for this realisation: 0.014 bits; published rule with that threshold returns (C,D).

### AE4 common cause, conditioned on state

gamma (individual influence):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | 0.021 | 0.019 | 0.025 |
| B | 0.021 | - | 0.024 | 0.020 |
| C | 0.019 | 0.024 | - | 0.038 |
| D | 0.025 | 0.020 | 0.038 | - |

Gamma (net influence, row influences column):

| | A | B | C | D |
|---|---|---|---|---|
| A | - | -0.003 | -0.019 | -0.013 |
| B | -0.004 | - | -0.013 | -0.018 |
| C | -0.006 | 0.003 | - | 0.013 |
| D | 0.004 | -0.005 | 0.013 | - |

Permutation threshold for this realisation: 0.023 bits; published rule with that threshold returns none.
