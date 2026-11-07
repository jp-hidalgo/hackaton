# Schelling copies, no channel

Do two copies of one model pick the same option from a menu with no channel between them, beyond what their shared marginal preference predicts, and does a shuffled menu, a paraphrased prompt or a second model family break the match? Built for the Apart Research Swarm Alignment Hackathon, 6-8 November 2026, Track 4.

## Provenance

Everything in `schelling/`, `tests/test_schelling.py` and `report-schelling/` was written during the hackathon weekend. The following directories are preexisting work from earlier sprints and are not part of this submission: `collusion/`, `report-collusion/`, `submission-collusion/` (October 2026, pairwise net influence), and `harness/`, `artifact/`, `report/`, `submission/` (September 2026, containment matrix). No code is imported from them.

## What is here

| File | Purpose |
|---|---|
| `PREREGISTRATION.md` | Menus, prompt texts, conditions, n, metrics, predictions, spend cap, timestamped amendments |
| `prompts.py` | Frozen menus, prompts, conditions, seeded option permutation |
| `run.py` | One call per agent via OpenRouter; resumable JSONL logs with every raw reply |
| `analyze.py` | Match rate, independence baselines, excess, spec compliance, Wilson intervals; writes `results/summary.md` |
| `protocol.py` | Simulated flag-on-disagreement policy from the saved pairs; writes `results/protocol.md` |
| `results/` | Raw records (`records_w*.jsonl`), smoke run, summary tables |

## Reproduce

```
pip install numpy openai python-dotenv
python -m unittest tests.test_schelling          # offline
```

LLM runs need `OPENROUTER_API_KEY` in a `.env` file at the repository root.

```
python -m schelling.run --smoke                   # one pair and one solo, results/smoke/
python -m schelling.run --worker 0 --workers 2    # run workers 0 and 1 in two shells
python -m schelling.analyze
python -m schelling.protocol
```

Report: `report-schelling/report.md`, built into the official template with `python report-schelling/build_docx.py`.
