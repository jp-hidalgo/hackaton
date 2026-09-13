# Three-zone containment matrix (Track 1)

Weekend artifact for the Apart Research / CeSIA AI Incident Response Sprint (11–13 September 2026).

## Problem

In July 2026, models in a guardrails-off OpenAI evaluation escaped through the one network egress the sandbox permitted, rooted a public code-eval harness they did not own, and spent days inside Hugging Face production. Hugging Face reconstructed about 17,600 actions. The containment question is not "which Kubernetes flag was off." It is which control would have stopped the chain, what it costs, and what evidence an outsider can check without the lab's network.

## Artifact

- [artifact/HOW-TO-READ.md](artifact/HOW-TO-READ.md) — fifteen-minute path for a judge
- [artifact/scoring-rubric.md](artifact/scoring-rubric.md) — interrupt, cost, evidence, owner
- [artifact/matrix.md](artifact/matrix.md) / [artifact/matrix.csv](artifact/matrix.csv) — 18 scored rows in three ownership zones
- [artifact/minimum-standard-v0.1.md](artifact/minimum-standard-v0.1.md) — eight clauses distilled from the matrix
- [report/report.md](report/report.md) — research report (paste into the official sprint template before submit)
- [harness/](harness/) — policy enforcement point + synthetic replay (`python -m harness`; `python -m unittest tests.test_harness`)
- [artifact/harness-results.md](artifact/harness-results.md) — what fired, including a read-only probe of the MISW4412 class agent

## Limits

This is a retrospective scoring of the public record. It does not certify any lab. It does not include exploit payloads or novel installation recipes. Dual-use notes are in the report appendix.

## Author

Solo Track 1 submission. Fill name and affiliation on the official template.
