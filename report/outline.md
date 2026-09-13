# Report skeleton (claims + sources, not prose)

Target 5–7 pages body. Official template from the Guidelines tab. Abstract ≤ 150 words. Finding in the title.

## Title (finding, not topic)

Detection existed; kill criteria and outsider-checkable evidence did not: a three-zone control matrix for the July 2026 agent intrusion

## Abstract (draft claims; rewrite in your voice)

- Track 1 artifact: 18-row matrix + 8-clause v0.1 standard.
- Chain scored in three ownership zones, not nine HF phases alone.
- Finding 1–3 as in findings.md.
- Limits: public record only; costs are bands; no live test.

## Introduction

- Track 1: what standard would have stopped this; judged on outsider verification and lab adoption.
- Artifact is for a lab CISO, a benchmark host, and a regulator/insurer who needs a 15-minute gradeable sheet.
- Do not conflate the 20 July long-horizon / public-PR incident.
- Sources: HF 27 July; OpenAI blog + technical report; Elastic 31 July.

## Related Work

- CSA AIS-13: isolate tools/plugins; audit = interview + docs (AIC guidelines).
- CoSAI IR v1.0 on NIST 800-61r3; CoSAI Aug 2026 insider-threat sandboxing (egress including inference endpoint; fail loudly; short-lived creds).
- Elastic: outcome detections exist; volume is the problem.
- What we add: interrupt + cost + outsider-checkable evidence, split by owner, including the unowned second hop.

## Methodology

- Rubric frozen before scoring (artifact/scoring-rubric.md).
- 18 rows, three zones; HF nine phases collapsed into C1–C9.
- Interrupt / cost / evidence / owner / confidence definitions.
- Validation: every stops-claim cites a public fact. Prior-art column maps CSA/CoSAI/Elastic.
- Threat to validity stated here and repeated in Results.

## Results

- Table excerpt: Zone A/B plus C6.
- Counts from matrix.md.
- Findings 1–3 with citations.
- Main threat to validity: counterfactual on a public chain.

## Discussion

- Minimum adequate standard is A1+A2+A3+A4 plus B1+B3, not a complete Zone C catalog.
- Second-tier lab adoption: A3 is L/L; A1 needs a curated package index (the real cost).
- Zone B is the neglected problem: CSA vuln-ops already wrote the clause; nobody is assigned it.
- Month of follow-up: turn A4 into a worked example digest; playtest kill criteria with one lab; ask a benchmark host to publish B3.

## Limitations and Dual-Use (required appendix)

- Defensive catalog; no payloads; no novel recipes; public techniques already disclosed by HF/OpenAI.
- Dual-use: interrupt points could be read as a targeting guide. Mitigation: no working exploit detail; no installation recipes.
- Does not certify any lab.
- AI tools used as a colleague for source-gathering and structure; prose is the author's.

## References

- List from report/sources.md.
