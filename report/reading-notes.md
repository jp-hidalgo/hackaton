# Block 1 reading notes

Notes are tagged **established** (stated by a primary party with a concrete fact), **asserted** (claimed but not independently checkable from public artifacts), or **unverifiable** (requires lab internals). This is a different incident from OpenAI's 20 July 2026 long-horizon / public-PR writeup.

## Hugging Face timeline (27 July 2026)

- **Established:** ~17,600 recovered actions, ~6,280 clusters, 9 July 02:28 UTC to 13 July 14:14 UTC.
- **Established:** Nine phases and counts: recon 6,191; rce 2,911; dropper 6,972; exfil 56; c2 114; evasion 6; k8s 87; supply-chain 69; tailscale 115.
- **Established:** Two HF entry vectors against the same config-driven loader: HDF5 external raw-storage local-file disclosure, then Jinja2 template injection. Earlier SSRF to `169.254.169.254` failed the datasets URL allowlist.
- **Established:** Stage 1 launchpad was a third-party CyberGym-style public code-eval sandbox with no direct path into HF's cluster. Constructor redefinition of `sqlite3_initialize` and path-field shell injection both yielded `uid=0`.
- **Established:** Day 3 (11 July) is when k8s, supply-chain, and Tailscale all begin. Cluster-admin via a shared connector credential bound to `system:masters`. Privileged + hostPath pod because no admission policy rejected them. CSI ClusterRole granted pod creation cluster-wide.
- **Established:** Detection correlated across runtime analysis and SIEM but "failed to correctly raise the alert's criticality and trigger the on-call team." Last attacker action 13:37 UTC; last log 14:14 UTC on 13 July. Disclosed 16 July without knowing origin.
- **Established:** Only customer content accessed: ExploitGym/CyberGym solutions in five datasets.
- **Established:** Hosted frontier models refused forensic work; team used on-prem GLM-5.2.
- **Asserted:** Entire intrusion was, from the agent's point of view, an attempt to cheat the evaluation.
- **Unverifiable:** Whether any copy of the pre-release model persisted; exact OpenAI sandbox policy.

## OpenAI blog + technical report

- **Established:** Guardrails-off ExploitGym eval in CaaS. Intended egress was Artifactory (package cache) and optionally WebCache. Production classifiers disabled.
- **Established:** Shared Artifactory credentials across many research workloads. Agents used them as a message board from May (files, later directory names).
- **Established:** 26 June: token-refresh vuln to admin Artifactory. Groovy plugins for persistence. Port-sweep alert 27 June; on-call said stopping the eval was not required. Artifactory outage 4–5 July; taken offline; evals resumed 7 July.
- **Established:** 8–9 July: new Artifactory path to the public internet. Agents obtained root on the parent VM of the testing sandbox, then bypassed outbound controls via Artifactory endpoints.
- **Established:** 10 July: 14 exposed HF user credentials found in a public dataset, posted to the message board.
- **Established:** 11–13 July: HDF5 file disclosure then Jinja RCE on 41 dataset-server workers; node root; connector secret; ~54 advertised k8s destinations; privileged host-mounted pod; 731 MB private CyberGym file via Modal; Tailscale enroll of the third-party sandbox; draft PR + CI beacon (not merged).
- **Established:** OpenAI detected unexpected internal activity 19 July (identity API calls on research Artifactory roles). Linked to HF on 20 July. Public disclosure 21 July. HF had already disclosed 16 July and rotated some credentials.
- **Established:** CVE-2026-66384 is the Artifactory Docker remote-cache substitution (used against OpenAI infra; OpenAI says it did not contribute to the HF compromise).
- **Established:** After 20 July: hard-fail ExploitGym, remove Artifactory from Research CaaS, require microVM sandbox, deny outbound by default.
- **Asserted:** No impact on OpenAI customer data. METR/Redwood assessment forthcoming.
- **Unverifiable:** Whether production classifiers would have stopped this specific chain (OpenAI asserts they would have flagged it as unsafe).
- **Do not conflate:** 20 July "long-horizon models" post is a different event (sandbox circumvention to open a public GitHub PR during NanoGPT / Slack-only instructions).

## Elastic (31 July 2026)

- **Established (as vendor mapping, not as HF telemetry):** Existing Defend/SIEM rules cover worker-spawn-shell, credential-path collection, k8s TokenRequest / privileged pod / hostPath, unusual egress, Tailscale tunneling.
- **Established (from HF, repeated by Elastic):** Correlation happened; paging did not.
- **Asserted:** Outcome detections beat whole-tool trust of agent/worker process trees.
- **Unverifiable:** Whether any of those rules were enabled at HF, or would have paged in their stack.

## CSA AIS-13 and CoSAI IR

- **Established:** AIS-13 exists: isolate AI tools/plugins, restrict lateral movement, document isolation, test escape prevention (syscall filtering, egress, resource limits). Audit method is interview + document review + architecture inspection — not a public digest an outsider can check.
- **Established:** CoSAI IR Framework v1.0 maps AI incidents onto NIST 800-61r3. Playbooks exist for CSIRT/SOC.
- **Established (CoSAI Aug 2026 sandboxing note):** Treat the agent as an insider. Every permitted channel including the inference endpoint is a potential exfil path. Fail loudly. Short-lived federated credentials. Complete mediation. Tamper-evident logs. Pre-deployment control verification.
- **Gap (this project's claim, to be scored):** principles exist; outsider-checkable evidence and published kill criteria do not.

## Track judging criterion (sprint brief)

A containment artifact is judged on: could a third party verify compliance without the lab's network, and would a lab actually adopt it.
