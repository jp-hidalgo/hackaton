"""Build a submission-ready PDF from report/report.md.

Paste into the official Apart template before the upload if that template
differs. This file exists so there is a PDF in-repo tonight.
"""

from __future__ import annotations

import re
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "report" / "report.md"
OUT = ROOT / "submission" / "report.pdf"
FONT = Path(r"C:\Windows\Fonts\times.ttf")
FONT_B = Path(r"C:\Windows\Fonts\timesbd.ttf")
FONT_I = Path(r"C:\Windows\Fonts\timesi.ttf")
FONT_BI = Path(r"C:\Windows\Fonts\timesbi.ttf")


class ReportPDF(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Body", "I", 9)
        self.set_text_color(80, 80, 80)
        self.cell(
            0,
            8,
            "Detection existed; kill criteria and outsider-checkable evidence did not",
            align="L",
        )
        self.ln(12)
        self.set_text_color(0, 0, 0)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Body", "I", 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, str(self.page_no()), align="C")
        self.set_text_color(0, 0, 0)


def write_inline(pdf: ReportPDF, text: str, size: int = 11) -> None:
    parts = re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\[[0-9,\s]+\])", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("Body", "B", size)
            pdf.write(5.5, part[2:-2])
        elif part.startswith("`") and part.endswith("`"):
            pdf.set_font("Courier", size=9)
            pdf.write(5.5, part[1:-1])
        else:
            pdf.set_font("Body", "", size)
            pdf.write(5.5, part)
    pdf.ln(6.5)


def build() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    pdf = ReportPDF(format="A4")
    pdf.add_font("Body", "", str(FONT))
    pdf.add_font("Body", "B", str(FONT_B))
    pdf.add_font("Body", "I", str(FONT_I))
    pdf.add_font("Body", "BI", str(FONT_BI))
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.set_margins(22, 20, 22)
    pdf.add_page()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        i += 1
        if not line:
            continue
        if line.startswith("# "):
            pdf.set_font("Body", "B", 16)
            pdf.multi_cell(0, 8, line[2:])
            pdf.ln(1)
            continue
        if line.startswith("**") and line.endswith("**") and line.count("**") == 2:
            pdf.set_font("Body", "I", 12)
            pdf.multi_cell(0, 6, line.strip("*"))
            pdf.ln(2)
            continue
        if line.startswith("## "):
            pdf.ln(3)
            pdf.set_font("Body", "B", 13)
            pdf.multi_cell(0, 7, line[3:])
            pdf.ln(2)
            continue
        if line.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Body", "B", 12)
            pdf.multi_cell(0, 6, line[4:])
            pdf.ln(1)
            continue
        write_inline(pdf, line)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"Wrote {OUT} ({pdf.page_no()} pages)")


if __name__ == "__main__":
    build()
