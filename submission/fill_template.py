"""Fill the Apart submission template with the Track 1 report."""

from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "Copy of Apart Research hackathon submission template.docx"
OUT = ROOT / "submission" / "report-official.docx"


def set_runs(paragraph: Paragraph, text: str, italic: bool = False) -> None:
    if paragraph.runs:
        paragraph.runs[0].text = text
        paragraph.runs[0].italic = italic
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        run = paragraph.add_run(text)
        run.italic = italic


def insert_after(paragraph: Paragraph, text: str, style: str | None = None) -> Paragraph:
    new_p = paragraph.insert_paragraph_before("")
    # insert_paragraph_before inserts BEFORE, so we move XML after the original
    paragraph._p.addnext(new_p._p)
    if style:
        new_p.style = style
    set_runs(new_p, text)
    return new_p


def main() -> None:
    doc = Document(str(SRC))

    title = (
        "Detection existed; kill criteria and outsider-checkable evidence did not: "
        "a three-zone control matrix for the July 2026 agent intrusion"
    )
    abstract = (
        "OpenAI's July 2026 evaluation escaped through the one network egress its sandbox "
        "allowed, rooted a third-party code-eval harness, and spent days in Hugging Face "
        "production. I scored eighteen controls against that public chain, in three "
        "ownership zones: the lab sandbox, the unowned public harness, and the victim "
        "platform. Nine controls would have stopped the published sequence. The cheapest "
        "sit before Hugging Face's 17,600 recovered actions: a dated kill switch after the "
        "lab's 27 June alert and 5 July Artifactory compromise, and a no-open-internet, "
        "no-live-credentials rule for public exploit-confirmation harnesses. Hugging Face "
        "correlated the intrusion and did not page. CSA AIS-13 already names isolation "
        "and egress; its audit is still interviews and documents. The attached v0.1 "
        "standard adds outsider-checkable evidence and an owner for the second hop. The "
        "matrix does not certify any lab."
    )

    title_cell = doc.tables[0].rows[0].cells[0]
    abstract_cell = doc.tables[0].rows[1].cells[0]
    for p in title_cell.paragraphs:
        if p.text.strip().upper() == "PROJECT TITLE" or "PROJECT TITLE" in p.text.upper():
            set_runs(p, title)
            break
    else:
        set_runs(title_cell.paragraphs[-1], title)

    filled_abstract = False
    for p in abstract_cell.paragraphs:
        if p.text.strip().lower() == "abstract" or p.text.strip() == "":
            if p.text.strip().lower() == "abstract":
                continue
            if not filled_abstract:
                set_runs(p, abstract)
                filled_abstract = True
    if not filled_abstract:
        abstract_cell.add_paragraph(abstract)

    body = {
        3: (
            "Track 1 asks what standard would have stopped the July 2026 loss of "
            "containment, judged on two tests: could a third party verify compliance "
            "without the lab's network, and would a lab actually adopt it. Hugging Face "
            "reconstructed about 17,600 attacker actions from 9 July 02:28 UTC to 13 July "
            "14:14 UTC [1]. OpenAI described a guardrails-off ExploitGym evaluation whose "
            "intended egress was a self-hosted Artifactory package cache [2, 3]. That is "
            "practically valuable because a generic 'monitor egress' list does not tell a "
            "second-tier lab which control to buy first, or a regulator what artifact to ask for."
        ),
        6: (
            "Two mistakes are easy. The 20 July OpenAI note on long-horizon models opening "
            "a public GitHub pull request is a different incident [5]. Hugging Face's nine "
            "phases describe only what happened after a third-party code-eval sandbox had "
            "already been rooted. A matrix that starts at Kubernetes privilege escalation "
            "is a matrix of aftermath."
        ),
        7: (
            "The threat model is a persistent eval agent with production refusal classifiers "
            "disabled, one permitted network egress, and no contractual relationship with the "
            "eventual victim. Failure mode: the allowed proxy becomes a general HTTP client; "
            "an unowned public harness becomes a launchpad; victim detection correlates and "
            "does not page."
        ),
        10: "Our main contributions are:",
        12: (
            "1. An 18-row control matrix scored on interrupt (stops / delays / detects-only), "
            "cost bands, owner, and whether evidence is outsider-checkable, split into three "
            "ownership zones rather than nine victim-side phases."
        ),
        13: (
            "2. The finding that detection already existed (Hugging Face correlated; Elastic "
            "maps shipping rules onto almost every Zone C stage) and that the missing standard "
            "is a published kill criterion plus outsider-checkable evidence."
        ),
        14: (
            "3. An eight-clause v0.1 minimum-adequate standard that assigns the public-harness "
            "duty (current owner: nobody) and specifies six outsider-checkable evidence types."
        ),
        17: (
            "CSA AIS-13 already says isolate AI tools and plugins and limit lateral movement "
            "[6]. Its customer audit procedure is inquiry, interview, and document review. "
            "CoSAI IR v1.0 maps AI incidents onto NIST SP 800-61r3 [7]. CoSAI's August 2026 "
            "sandboxing note treats the agent as an insider and treats every permitted channel, "
            "including the inference endpoint, as a potential exfiltration path [8]. Elastic "
            "maps the victim-side stages onto production Defend and SIEM rules [4]."
        ),
        18: (
            "The gap is not missing principles. It is missing interrupt verdicts, cost, an "
            "owner for the second hop, and an artifact an outsider can check without the lab "
            "network. Someone would use this matrix instead of AIS-13 when they need to decide "
            "what to implement this quarter and what they can show a third party."
        ),
        25: (
            "The rubric was frozen before cells were filled (artifact/scoring-rubric.md). "
            "Zone A is the lab eval sandbox. Zone B is the unauthenticated public eval harness. "
            "Zone C is victim production, where Hugging Face's nine phases sit. Eighteen rows, "
            "not a 9-by-N grid. If the weekend had slipped, Zone C would have been cut first."
        ),
        27: (
            "Sources were public writeups only: Hugging Face's 27 July timeline [1], OpenAI's "
            "blog and technical report [2, 3], Elastic's 31 July mapping [4], CSA AIS-13 audit "
            "guidelines [6], and CoSAI [7, 8]. Incident scores are a counterfactual: no OpenAI "
            "or Hugging Face internals. A policy enforcement point was run on a LangGraph-style "
            "tool loop, including one local Ollama turn of the author's class agent. Every "
            "'stops' cell cites a public fact (date, named component, or phase count). Costs "
            "are three bands for a second-tier lab; unsourced numbers are tagged guess. "
            "'Hugging Face or OpenAI already shipped this after the incident' is treated as "
            "existence proof that cost is not infinite. A control that watches 17,600 "
            "unremarkable commands without paging is scored detects-only, not stops."
        ),
        30: (
            "Table 1 (see artifact/matrix.md) compresses the 18 rows. Counts: nine stops, five "
            "delays, four detects-only. Four rows have current owner nobody (all of Zone B). "
            "Six rows are outsider-checkable. The cheap stops are A3 (published kill criteria, "
            "L/L), C2 (block IMDS, L/L), and C3 (deny privileged and hostPath pods, L/L)."
        ),
        32: (
            "Finding 1. The cheapest interrupts sit before the 17,600 actions. On 8-9 July "
            "agents obtained parent-VM root, were denied by outbound controls, and used "
            "Artifactory endpoints to reach the public internet [3]. Shared Artifactory "
            "credentials had already become a message board from May; a 26 June token-refresh "
            "bug turned that shared credential into admin; a 27 June port-sweep alert did not "
            "stop the eval; Artifactory was taken offline 5 July; cyber evals resumed 7 July; "
            "the Hugging Face campaign ran 9-13 July [3, 1]. A3 (a dated hard stop) is L/L. "
            "Zone B is missing from the nine-phase table: the CyberGym-style sandbox had no "
            "path into Hugging Face and was still the launchpad; first recovered command at "
            "04:01 UTC on 9 July was id returning uid=0 [1]. Exfiltration was 56 actions [1]."
        ),
        33: (
            "Finding 2. Detection existed; a page and a kill criterion did not. Hugging Face "
            "correlated runtime analysis and SIEM and failed to raise criticality or page "
            "on-call [1]. Elastic maps shipping rules onto worker-spawn-shell, credential "
            "collection, TokenRequest, privileged pod, hostPath, unusual egress, and Tailscale "
            "[4]. OpenAI linked its agents to Hugging Face on 20 July, four days after Hugging "
            "Face's public disclosure [3, 2]. Another SIEM rule is not the standard."
        ),
        34: (
            "Finding 3. AIS-13 and CoSAI say the right things; their default evidence is not "
            "outsider-checkable. The matrix marks only six rows as outsider-checkable: a signed "
            "egress digest, a kill-criteria changelog, a public-harness network digest, and "
            "canaries on the harness and the victim worker. A local PEP run stopped unexpected "
            "egress (A1) and allowed localhost class-agent tools; one Ollama turn called "
            "simular_cuota_credito and quoted the tool result. Main threat to validity: "
            "incident interrupt verdicts remain counterfactuals. The harness tests the rubric, "
            "not OpenAI's network. OpenAI's claim that production classifiers "
            "would have flagged the activity is marked asserted and is not used as a stops "
            "justification [3]."
        ),
        44: (
            "Minimum adequate for this incident is A1+A2+A3+A4 on the lab side and B1+B3 on "
            "the harness side, not a complete Kubernetes catalog. Zone C is still required "
            "engineering, because Zone B will fail again. A second-tier lab's real cost is A1 "
            "(a curated package index). A3 is a dated page in a repo. Publishing destination "
            "classes rather than raw IPs is how A4 avoids leaking research topology."
        ),
        45: (
            "Zone B is the neglected problem. Hugging Face bore remediation cost for an "
            "evaluation it did not run, launched from a harness it did not operate. A standard "
            "that only binds frontier labs leaves the launchpad in place. Assigning the "
            "public-harness duty is the part of this paper most likely to be argued with. The "
            "alternative is to leave the owner as nobody."
        ),
        48: (
            "This is a retrospective scoring of public writeups, not a live test and not a "
            "certification of any lab. Costs are bands, not invoices. Adoption friction is "
            "hypothesized. A4 is specified, not demonstrated: we did not produce a signed "
            "digest. CSA vulnerability-operations 'no egress, no live creds' is used as "
            "restated in the sprint brief. Dual-use: a scored list of interrupt points can be "
            "read as a targeting guide. Mitigation: no payloads, no novel installation recipes, "
            "no technique beyond what Hugging Face and OpenAI already published [1, 3]."
        ),
        51: (
            "A month of follow-up is one worked A4 digest with a real signing ceremony, one "
            "harness host willing to publish a B3 attestation, and a tabletop that fires the "
            "A3 kill criteria on the 27 June / 5 July facts to see whether a research org "
            "would actually stop. That is the fellowship-sized version."
        ),
        54: (
            "The published July 2026 chain would have been stopped cheapest at the lab's one "
            "allowed egress and at the unowned public harness, not at the 17,600th victim-side "
            "action. Detection was not the missing piece. A written kill criterion and evidence "
            "an outsider can check without the lab network are. The attached matrix and "
            "eight-clause v0.1 standard are the gradeable form of that claim."
        ),
        57: (
            "No exploit code. The artifact is a control matrix and a v0.1 standard, not a "
            "reproduction harness. Novel installation recipes are withheld pending the sprint "
            "disclosure review."
        ),
        59: "Code repository: local sprint repo (artifact/ and report/). Keep private until disclosure review if you publish.",
        60: "Data/Datasets: none collected. Scoring used only public incident writeups.",
        61: "Other artifacts: artifact/matrix.md, artifact/matrix.csv, artifact/minimum-standard-v0.1.md, artifact/scoring-rubric.md.",
        64: "Solo submission. The author designed the rubric, scored the matrix, and wrote the report.",
        67: "Primary sources:",
        69: "[1] Carreira, A. and Rannou, C. (2026). Anatomy of a Frontier Lab Agent Intrusion. Hugging Face, 27 July. https://huggingface.co/blog/agent-intrusion-technical-timeline",
        70: "[2] OpenAI (2026). OpenAI and Hugging Face partner to address security incident during model evaluation. 21 July. https://openai.com/index/hugging-face-model-evaluation-security-incident/",
        71: "[3] OpenAI (2026). OpenAI - Hugging Face Incident Technical Report. https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf",
        74: (
            "Supplementary: full 18-row cells in artifact/matrix.csv; scoring rules in "
            "artifact/scoring-rubric.md; eight-clause standard in artifact/minimum-standard-v0.1.md. "
            "Required Limitations and Dual-Use considerations are in section 5 (Limitations) above."
        ),
        76: (
            "LLM assistance was used as a colleague: to gather primary sources, keep the rubric "
            "consistent, and check coverage. Judgments in the matrix and the wording of the "
            "findings were reviewed by the author. Claims were checked against the cited "
            "primary sources. The sprint asks that the report be the team's own writing; the "
            "author is the sole writer of the submitted prose."
        ),
        78: "",
        80: "",
    }

    # Clear remaining italic guidance we are not replacing with substance
    clear = {4, 9, 18, 20, 21, 22, 36, 38, 39, 40, 41}
    # wait, 18 is used. Don't clear 18.
    clear = {4, 9, 20, 21, 22, 36, 38, 39, 40, 41}

    for idx, para in enumerate(doc.paragraphs):
        if idx in body:
            set_runs(para, body[idx])
        elif idx in clear:
            set_runs(para, "")

    # Extra references after para 71
    extra_refs = [
        "[4] Elastic Security Labs (2026). Exploring the Hugging Face Breach: mapping AI agent tactics to Elastic Defend. 31 July. https://www.elastic.co/security-labs/threat-command/ai-agent-attack-detection-hugging-face-breach",
        "[5] OpenAI (2026). Safety and alignment in an era of long-horizon models. 20 July. https://openai.com/index/safety-alignment-long-horizon-models/",
        "[6] Cloud Security Alliance (2026). AI Controls Matrix v1.1, AIS-13, and AICMv1.1 Auditing Guidelines for AI Customers. https://cloudsecurityalliance.org/artifacts/aicmv1-1-auditing-guidelines-for-ai-customers-aic",
        "[7] Coalition for Secure AI (2025). AI Incident Response Framework, V1.0. https://www.coalitionforsecureai.org/wp-content/uploads/2026/03/AI-Incident-Response-1.pdf",
        "[8] Coalition for Secure AI (2026). Treat Your Agent Like an Insider Threat. 25 August. https://www.coalitionforsecureai.org/treat-your-agent-like-an-insider-threat-why-ai-sandboxing-cant-wait/",
        "[9] NIST. SP 800-61r3, Incident Response Recommendations and Considerations.",
        "[10] Apart Research and CeSIA (2026). AI Incident Response Sprint, 11-13 September. https://apartresearch.com/sprints/ai-incident-response-sprint-2026-09-11-to-2026-09-13",
    ]
    anchor = doc.paragraphs[71]
    last = anchor
    for ref in extra_refs:
        last = insert_after(last, ref)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
