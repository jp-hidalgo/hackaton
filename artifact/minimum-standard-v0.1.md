# Minimum adequate standard for guardrails-off evaluations (v0.1)

Eight clauses. Each one is specific enough to audit and cheap enough that a second-tier lab can adopt the cheap ones this quarter. "Adequate" here means: the July 2026 chain, as published, would have stopped or forced a human decision before a third party was rooted. It does not mean the environment is safe against a different agent.

Normative language: **must** is required for the claim "we run dangerous-capability evals." **should** is required for the claim "a third party can check."

## Clause 1 — One egress, and it is not a general client (rows A1, A4)

A guardrails-off eval network **must** default-deny outbound traffic. The allowed package or model-cache proxy **must not** be able to fetch arbitrary URLs, perform SSRF, or be used as a message bus between runs. A lab **should** publish a signed egress policy naming allowed destination classes and a periodic flow-log digest of unique destination classes from that network.

## Clause 2 — No shared identity on the allowed proxy (row A2)

Eval workloads **must not** share a credential that can write to the allowed proxy or mint administrative tokens. Compromise of one run **must not** become a coordination channel for the next.

## Clause 3 — Kill criteria are written, dated, and used (row A3)

The lab **must** publish a kill-criteria changelog. At minimum the eval **must** hard-stop on: (a) sandbox or parent-VM root, (b) unexpected egress, (c) administrative compromise of the allowed proxy. An on-call alert that does not name a stop/no-stop decision does not satisfy this clause. Resuming after a proxy compromise **must** be a dated entry against the same changelog.

## Clause 4 — Pause-and-page is on the eval, not only on production (row A5)

A trajectory or sequence monitor that can pause the run and page a human **must** cover guardrails-off evals, not only production traffic. Production classifiers that were deliberately disabled do not count.

## Clause 5 — The public harness is in scope (rows B1, B2, B3)

Anyone who exposes an unauthenticated or weakly authenticated code-eval or exploit-confirmation harness to the internet **must** treat it as an exploit-confirmation environment: no open internet, no live production credentials, no root via constructors or unsandboxed build metadata, no pre-staged debug toolchain. Current owner of this duty is `nobody`. This clause assigns it to the harness host.

## Clause 6 — Canaries are the outsider's detector (rows B4, C8)

Harness images and victim processing workers **should** carry unique canary credentials. A hit on a public collector **must** page the same on-call as Clause 3. This is the cheapest outsider-checkable detection in the matrix.

## Clause 7 — Victim-side cheap stops are ordinary platform hygiene (rows C1–C4)

A platform that executes untrusted dataset or model configuration **must** refuse local-file reads and template evaluation in data fields, **must** block instance metadata from those pods, **must** deny privileged and hostPath pods by default, and **must not** bind a shared connector to cluster-admin. These are L/M controls Hugging Face has now described as shipped. They are aftermath relative to Clauses 1–5. They are still required, because Zone B will fail again.

## Clause 8 — Correlate-and-page, not correlate-and-wait (row C6)

A high-severity correlated signal on eval or processing infrastructure **must** page a human in minutes, any day of the week. A rule pack that fires and does not page does not satisfy the clause. Exfiltration content-loss detections are not a substitute; in this incident they would have seen 56 actions after days of recon.

## What this standard cannot establish

It does not prove any named lab is compliant. It does not replace CSA AIS-13 or CoSAI IR; it adds outsider-checkable evidence and an owner for the second hop. A month of follow-up would produce one worked A4 digest and one harness-host B3 attestation, not a longer clause list.
