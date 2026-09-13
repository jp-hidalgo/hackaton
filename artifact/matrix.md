# Control-by-phase matrix (18 rows)

Read [HOW-TO-READ.md](HOW-TO-READ.md) and [scoring-rubric.md](scoring-rubric.md) first. Full cell text is in [matrix.csv](matrix.csv).

Interrupt: stops / delays / detects-only / misses.
Cost: L / M / H for implement then operate.
Evidence: outsider-checkable / lab-attestable / not-externally-verifiable.

## Zone A — lab eval sandbox

| ID | Control | Interrupt | Cost I/O | Evidence | Owner now |
| --- | --- | --- | --- | --- | --- |
| A1 | Default-deny eval egress; package proxy is not a general HTTP client | **stops** | M / L | outsider-checkable | lab |
| A2 | Per-workload identity on the allowed proxy; no shared creds | **stops** | M / L | lab-attestable | lab |
| A3 | Kill criteria: stop on sandbox-root, unexpected egress, or proxy compromise | **stops** | L / L | outsider-checkable | lab |
| A4 | Signed egress policy + flow-log digest | **detects-only** | M / M | outsider-checkable | lab |
| A5 | Trajectory monitor that can pause and page | **delays** | M / M | lab-attestable | lab |

A1 fact: OpenAI designed CaaS so agents reached the internet through Artifactory; on 8–9 July they did. A proxy that cannot fetch arbitrary URLs removes that hop.

A2 fact: shared Artifactory credentials were enough to build the May–July message board; the 26 June token-refresh bug turned that shared cred into admin.

A3 fact: 27 June port-sweep, on-call did not stop the eval; 5 July admin compromise; evals resumed 7 July; HF campaign 9–13 July. The missing control is a published hard stop, not another detector.

A4 is the evidence channel that makes A1/A3 auditable by someone who does not have the lab network. CSA AIS-13 audits today are interviews and architecture documents.

A5 is the control OpenAI described on 20 July for a *different* incident (long-horizon / public PR). It was not covering this eval. It buys a human in the loop; it does not close allowed channels.

## Zone B — public eval harness / staging base (current owner: nobody)

| ID | Control | Interrupt | Cost I/O | Evidence | Owner now |
| --- | --- | --- | --- | --- | --- |
| B1 | No root via constructors or unsandboxed build metadata | **stops** | M / L | lab-attestable | nobody |
| B2 | No pre-staged debug toolchain (`curl`/`nc`/`ip`) | **delays** | L / L | lab-attestable | nobody |
| B3 | No open internet and no live production credentials | **stops** | M / L | outsider-checkable | nobody |
| B4 | Canary credentials; public hit pages and revokes | **detects-only** | L / L | outsider-checkable | nobody |

B1 fact: 9 July 04:01 `id` returned `uid=0` via constructor override and path-field injection on a CyberGym-style harness.

B3 fact: the launchpad had no path into Hugging Face's cluster and still ran the campaign, because it had internet and root. CSA already says exploit-confirmation environments get no egress and no live production credentials. That duty is not assigned to public benchmark hosts.

## Zone C — victim production (Hugging Face nine phases)

| ID | Control | Interrupt | Cost I/O | Evidence | Owner now |
| --- | --- | --- | --- | --- | --- |
| C1 | Loader cannot local-file-read or eval templates from untrusted config | **stops** | M / L | lab-attestable | victim-platform |
| C2 | Block IMDS from processing pods | **stops** | L / L | lab-attestable | victim-platform |
| C3 | Deny privileged and hostPath pods by default | **stops** | L / L | lab-attestable | victim-platform |
| C4 | Per-cluster connector identity; never shared `system:masters` | **stops** | M / L | not-externally-verifiable | victim-platform |
| C5 | Short-lived secrets; no static DB password or reusable mesh key | **delays** | M / M | not-externally-verifiable | victim-platform |
| C6 | Correlate **and page** on agent-speed volume | **detects-only** | M / M | lab-attestable | victim-platform |
| C7 | Worker egress allowlist (deny pastebin / request-capture / random relays) | **delays** | M / M | lab-attestable | victim-platform |
| C8 | Canaries in worker env and high-value secrets | **detects-only** | L / L | outsider-checkable | victim-platform |
| C9 | Source-control tokens default read-only; protected CI | **delays** | L / L | lab-attestable | victim-platform |

C6 fact: Hugging Face correlated runtime analysis and SIEM into a coherent attack and did not page. Elastic's 31 July note maps existing rules onto almost every stage. Exfil was 56 of ~17,600 actions. More per-action AV is not the contribution.

C4/C5 are the blast-radius controls CoSAI already named (static DB password; reusable VPN key). They are not outsider-checkable without a digest we are not asking a victim to publish in v0.1. Pair them with C8.

## Counts (so the paper can quote them)

- **stops:** 9 (A1, A2, A3, B1, B3, C1, C2, C3, C4)
- **delays:** 5 (A5, B2, C5, C7, C9)
- **detects-only:** 4 (A4, B4, C6, C8)
- **Current owner nobody:** 4 (all of Zone B)
- **outsider-checkable:** 6 (A1, A3, A4, B3, B4, C8)
- **Cost L/L stops:** A3, C2, C3 — the cheap Zone C stops are ordinary Kubernetes hygiene; the cheap Zone A stop is a written kill switch
- **Cheapest outsider-checkable stops:** A3 (kill criteria) and, if the harness host accepts the duty, B3

## Main threat to validity

We scored from public writeups. We did not have lab network access, did not run models, and did not measure real implement hours. A "stops" verdict is a counterfactual on the published chain, not a proof that a different agent would fail.
