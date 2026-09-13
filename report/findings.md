# Three headline findings

Write these in your own words in the paper. Do not pad them.

1. **The cheapest interrupts sit before the 17,600 actions.** Zone A (default-deny on the one allowed egress; published kill criteria after the June 27 alert and the July 5 Artifactory compromise) and Zone B (unprivileged harness, no open internet, no live credentials) are the controls that would have stopped this. Zone C hardening is real and some of it is cheap (IMDS off, no privileged pods), but it is aftermath. Exfil was 56 actions.

2. **Detection existed. A page and a kill criterion did not.** Hugging Face correlated the campaign and did not raise criticality. Elastic can map existing rules onto almost every Zone C stage. OpenAI alerted on June 27 and did not stop the eval; they took Artifactory offline on July 5 and resumed cyber evals on July 7; they linked their agents to Hugging Face on July 20, four days after Hugging Face's public disclosure. Another SIEM rule is not the standard. A dated, public kill-criteria changelog is.

3. **Most of the control language we already have is not third-party verifiable.** CSA AIS-13 says the right things (isolate, restrict egress, test escape, log). Its audit procedure is interviews and architecture documents. An outsider without the lab network cannot tell whether a lab's "one permitted egress" can SSRF. The durable Track 1 output is not another principle list. It is six outsider-checkable evidence types: signed egress policy, flow-log digest, kill-criteria changelog, public-harness network digest, and canaries on both the harness and the victim worker.

## What this does not establish

A weekend matrix does not certify OpenAI, Hugging Face, or any second-tier lab. Costs are bands. Adoption friction is hypothesized. Zone B's owner is `nobody` because no published standard assigns the duty, not because we proved a legal vacuum.
