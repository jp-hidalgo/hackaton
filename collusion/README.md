# Pairwise net influence on LLM agents (sprint question 1.4)

Implementation and test of the collusion statistic of Bonjour, Aggarwal and Bhargava (UAI 2022), applied for the first time to language-model agents. Built during the Apart Research AI Collusion Research Sprint, 23-25 October 2026.

## Provenance

Everything in `collusion/` and `tests/test_netinfluence.py` was written during the sprint. The directories `harness/`, `artifact/`, `report/` and `submission/` at the repository root are preexisting work from a September 2026 sprint on a different topic and are not part of this submission.

## What is here

| File | Purpose |
|---|---|
| `PREREGISTRATION.md` | Definition, frozen rules, predicted anti-example outputs, LLM conditions, ranking rule, amendments with timestamps |
| `netinfluence.py` | gamma (conditional MI), Gamma (net influence), published rule, permutation threshold, multi-pair variant, Cramér's V |
| `rps.py` | Scripted 3- and 4-player iterated RPS with assistant collusion; CP x games sweep; Bonjour Table 2 replication |
| `anti_examples.py` | Two pairs, lagged one-way copying, same-round one-way copying, shared marginal, common cause |
| `llm_game.py` | Four `openai/gpt-4.1-mini` agents via OpenRouter; conditions P-strong, P-weak, N; full transcripts |
| `judge.py` | Frozen action-log-only LLM judge, one call per game |
| `rank.py` | Ranks the six pairs under net influence, Cramér's V and the judge; writes `results/llm_ranking.md` |
| `results/` | Every CSV, JSON, transcript, table and figure referenced in the report |

## Reproduce

```
pip install numpy matplotlib openai python-dotenv
python -m unittest tests.test_netinfluence
python -m collusion.rps              # about 2 minutes, writes results/sweep_results.md and the figure
python -m collusion.anti_examples    # about 30 seconds, writes results/anti_examples.md
```

LLM arm (needs `OPENROUTER_API_KEY` in a `.env` file at the repository root; total cost for the runs reported was under USD 2):

```
python -m collusion.llm_game --smoke
python -m collusion.llm_game --condition P-strong --seed 0 --rounds 60   # seeds 0,1,2; also N
python -m collusion.judge collusion/results/llm/*.json
python -m collusion.rank
```

All information quantities are in bits. The threshold alpha = 0.05 follows the paper.
