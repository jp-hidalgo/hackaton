# How a judge should read this artifact

This is a Track 1 (Containment) artifact: a scored control-by-phase matrix plus a one-page v0.1 standard.

**What it claims.** For the July 2026 OpenAI / Hugging Face chain, the cheapest interrupts sit in Zone A (the lab's one permitted egress) and Zone B (the unowned public eval harness). Zone C detections already existed in vendor rule packs and in Hugging Face's own stack; they correlated and did not page. Most CSA AIS-13 evidence is interview-and-document, not outsider-checkable.

**What it does not claim.** It does not certify any lab. Costs are three-band estimates. Incident interrupt verdicts are retrospective readings of the public record. The harness and one local class-agent turn test the rubric, not OpenAI's network. Adoption friction is hypothesized.

**How to grade it in fifteen minutes.**

1. Read [scoring-rubric.md](scoring-rubric.md) (definitions of interrupt, cost, evidence, owner).
2. Skim the 18 rows in [matrix.md](matrix.md). Zone A and Zone B first.
3. Read the eight clauses in [minimum-standard-v0.1.md](minimum-standard-v0.1.md). Each clause points at matrix rows.
4. Check that every "stops" cell cites a public fact.

**Legend (copied onto the matrix).**

- Interrupt: `stops` | `delays` | `detects-only` | `misses`
- Cost: `L` / `M` / `H` for implement and for operate
- Evidence: `outsider-checkable` | `lab-attestable` | `not-externally-verifiable`
- Owner: `lab` | `harness-host` | `victim-platform` | `nobody`
- Confidence: `established` | `asserted` | `guess`
