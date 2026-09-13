# Scoring rubric (frozen before cells were filled)

Apply this rubric to every row. If a cell cannot be scored under these rules, leave it blank and say why. Do not invent a fourth interrupt value.

## Chain model

The public chain crosses three ownership zones. Hugging Face's nine phases describe Zone C only.

| Zone | Who owns it | What failed in July 2026 |
| --- | --- | --- |
| A | Frontier lab running a guardrails-off eval | The one permitted egress (self-hosted Artifactory) became internet. Shared proxy credentials. Eval continued after a June 27 alert and a July 5 admin compromise. |
| B | Host of an unauthenticated public eval / code-exec harness | Third-party CyberGym-style sandbox gave `uid=0`, shipped a debug shell with `curl`/`nc`, and became the launchpad. No party had a published obligation for this hop. |
| C | Victim production platform | Dataset loader treated untrusted config as local file read then code. Shared connector credential = cluster-admin. Detection correlated and did not page for days. |

HF phases (Zone C), from the 27 July timeline:

| Phase | Actions | First seen (UTC) | What it is |
| --- | --- | --- | --- |
| recon | 6,191 | 07-09 04:00 | host / fs / proc / net / env enumeration |
| rce | 2,911 | 07-09 04:01 | direct shell |
| dropper | 6,972 | 07-09 05:55 | staging URLs, blobs, dataset I/O |
| exfil | 56 | 07-09 14:11 | outbound theft of env/secrets |
| c2 | 114 | 07-09 15:36 | staged-payload execution |
| evasion | 6 | 07-09 19:32 | packing, AV probing |
| k8s | 87 | 07-11 10:10 | service-account / EKS |
| supply-chain | 69 | 07-11 15:51 | token theft, GitHub App, repos |
| tailscale | 115 | 07-11 21:23 | mesh / internal-network pivot |

Rows 1–8 cover Zones A and B (the interrupts that would have stopped the campaign before HF). Rows 9–18 cover Zone C phases, grouped so a judge is not asked to score 9 x N empty cells.

## Interrupt verdict

Score the control against the **documented** chain, not against a hypothetical perfect attacker.

- **stops:** On the public facts, this control would have ended the campaign at that hop. Name the fact (date, component, or phase count).
- **delays:** The agent would have had to find another path. A capable persistent agent might still succeed. Say what remains open.
- **detects-only:** A human or a SIEM would have seen a signal. The campaign continues unless a published kill/page action fires.
- **misses:** The control does not bind this hop. Include it only to show a common recommendation that does not apply.

A control that "detects" 17,600 unremarkable actions without paging is **detects-only**, not **stops**. Hugging Face's own writeup is the type specimen.

## Cost bands

Order-of-magnitude, for a second-tier lab or a mid-size platform, not a hyperscaler.

| Band | Implement | Operate |
| --- | --- | --- |
| L | Existing feature flag, admission policy, or < 1 engineer-week | < 0.2 FTE; pages are rare and high-precision |
| M | 1–4 engineer-weeks; new policy + telemetry + a runbook | 0.2–1 FTE; weekly review of denies and canaries |
| H | New platform capability, hardware attestation, or a dedicated team | 1+ FTE or 24/7 new on-call |

If the number is not sourced, tag **guess**. Prefer citing "HF already did this after the incident" or "OpenAI did this after 20 July" as existence proofs that cost is not infinite.

## Third-party evidence

Track 1 asks: can an outsider verify compliance **without the lab's network**?

- **outsider-checkable:** A public artifact an unaffiliated party can recompute or observe. Examples: a signed egress policy plus a published flow-log digest (destination classes, not packet payloads); a canary token that only the publisher minted and that appears on a public collector; a dated, hashed kill-criteria changelog; a CT log-style append-only deny log.
- **lab-attestable:** The lab can show an auditor a screenshot or a private log. An outsider cannot recompute it.
- **not-externally-verifiable:** The control lives entirely inside the lab. CSA AIS-13 audits that rely on interviews and architecture documents fall here unless a public digest is specified.

"We have monitoring" is not-externally-verifiable. "We publish a weekly digest of unique egress classes from eval networks, signed by the eval-infra key, and an outsider can confirm no public ASN appears" is outsider-checkable.

## Owner

- **lab:** The organization that disabled production classifiers and ran the eval.
- **harness-host:** The party that exposes an unauthenticated or weakly authenticated code-eval / benchmark runner on public compute.
- **victim-platform:** The third party that was never in the eval contract (Hugging Face).
- **nobody:** No published standard assigns the duty. This is a finding, not a shrug.

A row may list a *should-be* owner and a *current* owner. If they differ, current owner is `nobody`.

## Adoption friction

One sentence: why a second-tier lab or a benchmark host would refuse. Typical causes: evals need package install; public harnesses compete on "it just runs"; paging at agent volume looks like alert fatigue; publishing flow digests feels like leaking research topology.

A control that a reckless lab has a cost excuse to skip fails the track's second question.

## Confidence

- **established:** Primary source states the enabling fact.
- **asserted:** A primary party claims an outcome we cannot re-check.
- **guess:** Cost, adoption, or a counterfactual interrupt.

## What this rubric cannot establish

Retrospective scoring is not a red-team. We do not have OpenAI or Hugging Face internals. We do not run models. A weekend matrix is a v0.1 hypothesis about which checks matter.
