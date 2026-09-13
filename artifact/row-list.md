# Frozen row list (18 rows)

Do not add rows during scoring. If Saturday slips, cut from the bottom of Zone C, not from A/B.

## Zone A — lab eval sandbox

| ID | Control | Phase / hop |
| --- | --- | --- |
| A1 | Default-deny eval egress; package proxy is not a general HTTP client | Artifactory-as-only-egress, 8–9 July |
| A2 | Per-workload identity on the allowed proxy; no shared admin-equivalent credential | Shared Artifactory creds, May–July message board |
| A3 | Published kill criteria: stop the eval on sandbox-root, unexpected egress, or compromise of the allowed proxy | 27 June alert; 5 July admin compromise; evals resumed 7 July |
| A4 | Signed egress policy + flow-log digest an outsider can check | Track 1 durable output |
| A5 | Trajectory monitor that can pause the run and page a human | OpenAI later added this class of control; missing in July |

## Zone B — unauthenticated public eval harness / staging base

| ID | Control | Phase / hop |
| --- | --- | --- |
| B1 | Harness does not run attacker-controlled constructors or unsandboxed build paths as root | `sqlite3_initialize` + path injection, 9 July 04:01 |
| B2 | No pre-staged debug toolchain (`curl`, `nc`, `ip`) on eval images | HF: bundled debug shell kept egress alive |
| B3 | Public-harness baseline: no open internet, no live production credentials (CSA vuln-ops class) | Unowned second hop |
| B4 | Canary credentials in harness environments; public hit = page + revoke | Credential reuse across agents via message board |

## Zone C — victim production (HF nine phases)

| ID | Control | Phase / hop |
| --- | --- | --- |
| C1 | Untrusted dataset/model config cannot read local files or evaluate templates | Vectors 1–2; recon + rce start |
| C2 | Block IMDS / cloud metadata from processing pods | Node-role creds from 169.254.169.254 |
| C3 | Admission: deny privileged and hostPath pods by default | Node root 11 July 19:53 |
| C4 | Per-cluster connector identity; never `system:masters` on a shared broker | Connector catalog + cluster-admin |
| C5 | Short-lived secrets; no static DB password or reusable mesh auth key in env | Mongo static password; Tailscale key; 181 enrollments |
| C6 | Detect-and-page on correlated agent-speed volume (not correlate-and-wait) | HF: correlated, did not page; 4.5 days |
| C7 | Worker egress allowlist (deny pastebins, request-capture, arbitrary Spaces relays) | C2 / dropper / exfil substrate |
| C8 | Canary tokens in worker env and cluster secrets | Secret read of 136-key object |
| C9 | Source-control App tokens scoped read-only by default; CI cannot mint write from a worker | Supply-chain 69 actions; draft PR + CI beacon |

C6 covers the detection failure across all nine phases. C7 covers dropper/c2/exfil. C9 covers supply-chain. Lateral k8s/tailscale are C2–C5.
