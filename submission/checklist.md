# Pre-submission checklist

Deadline: Sunday 13 September 2026, 11:59 PM Anywhere on Earth.
Target: submit by 8:00 PM local (UTC-6). AoE midnight is Monday 5:59 AM local.

## You must do (this repo cannot)

- [ ] Join Discord and skim help-desk / announcements: https://discord.gg/XswWBvugYs
- [ ] Download the **current** official report template from the Guidelines tab: https://apartresearch.com/sprints/ai-incident-response-sprint-2026-09-11-to-2026-09-13
- [ ] Confirm the Guidelines-tab template matches [docs/Copy of Apart Research hackathon submission template.docx](../docs/Copy%20of%20Apart%20Research%20hackathon%20submission%20template.docx)
- [ ] Open [submission/report-official.docx](report-official.docx), put your name on it, File > Save As PDF. A standalone 6-page PDF also exists at [submission/report.pdf](report.pdf); prefer the official-template export if the Guidelines file still matches.
- [ ] Read the report once in your own voice; keep claims and citations
- [ ] Submit on the official form on the sprint page
- [ ] Keep the confirmation email (it should echo the project title)
- [ ] If no confirmation: email sprints@apartresearch.com
- [ ] If you catch a mistake: submit again with the **same title**

## Files ready in this repo

- [x] Research report draft: `report/report.md`
- [x] Abstract ≤ 150 words
- [x] Author/affiliation fields present (placeholders)
- [x] Limitations and Dual-Use appendix
- [x] Body aimed at 5–7 pages (max 8 excluding references and appendices)
- [x] Artifact: matrix, rubric, eight-clause standard
- [x] No novel installation recipes; no exploit PoCs
- [x] Optional public GitHub: keep private until you decide; do not publish recipes
- [x] Video: skip

## Suggested submission metadata

- **Title:** Detection existed; kill criteria and outsider-checkable evidence did not: a three-zone control matrix for the July 2026 agent intrusion
- **Track:** 1 — Containment
- **Team:** solo
- **Artifact link:** this repo (matrix + standard), or attach `artifact/` as a zip if the form allows

## Abstract (copy)

OpenAI's July 2026 evaluation escaped through the one network egress its sandbox allowed, rooted a third-party code-eval harness, and spent days in Hugging Face production. I scored eighteen controls against that public chain, in three ownership zones: the lab sandbox, the unowned public harness, and the victim platform. Nine controls would have stopped the published sequence. The cheapest sit before Hugging Face's 17,600 recovered actions: a dated kill switch after the lab's 27 June alert and 5 July Artifactory compromise, and a no-open-internet, no-live-credentials rule for public exploit-confirmation harnesses. Hugging Face correlated the intrusion and did not page. CSA AIS-13 already names isolation and egress; its audit is still interviews and documents. The attached v0.1 standard adds outsider-checkable evidence and an owner for the second hop. The matrix does not certify any lab.
