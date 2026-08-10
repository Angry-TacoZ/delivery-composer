import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output" / "pdf"
sys.path.insert(0, str(PROJECT_ROOT / "api"))

from app.mock_briefs import MOCK_BRIEFS  # noqa: E402

INK = colors.HexColor("#1D2023")
MUTED = colors.HexColor("#666B70")
ACCENT = colors.HexColor("#238B98")
PALE = colors.HexColor("#E8EFF0")


def _page_frame(canvas, document) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, height - 27 * mm, width, 27 * mm, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, height - 28.5 * mm, width, 1.5 * mm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(23 * mm, 16 * mm, "SYNTHETIC DEMONSTRATION DOCUMENT")
    canvas.drawRightString(width - 23 * mm, 16 * mm, f"PAGE {document.page}")
    canvas.restoreState()


def generate() -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    label = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=10,
        textColor=ACCENT,
        spaceAfter=3,
        uppercase=True,
    )
    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Times-Roman",
        fontSize=29,
        leading=32,
        textColor=INK,
        alignment=0,
        spaceAfter=12,
    )
    metadata = ParagraphStyle(
        "Metadata",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=MUTED,
        borderColor=PALE,
        borderWidth=0.8,
        borderPadding=8,
        spaceAfter=18,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=INK,
        spaceAfter=14,
    )
    marker = ParagraphStyle(
        "Marker",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=MUTED,
        alignment=TA_RIGHT,
    )

    generated: list[Path] = []
    for brief in MOCK_BRIEFS:
        output_path = OUTPUT_DIR / f"{brief['slug']}.pdf"
        document = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=23 * mm,
            leftMargin=23 * mm,
            topMargin=43 * mm,
            bottomMargin=27 * mm,
            title=brief["title"],
            author="Delivery Composer synthetic demo",
            subject="Synthetic client brief for evaluator demonstration",
        )
        story = [
            Paragraph("CLIENT BRIEF / DELIVERY COMPOSER", label),
            Paragraph(brief["title"], title),
            Paragraph(
                f"REFERENCE&nbsp;&nbsp; {brief['reference']}<br/>"
                f"SECTOR&nbsp;&nbsp; {brief['sector']}<br/>"
                "CLASSIFICATION&nbsp;&nbsp; Synthetic demo data only",
                metadata,
            ),
            Paragraph("ENGAGEMENT REQUIREMENT", label),
            Paragraph(brief["brief"], body),
            Spacer(1, 8 * mm),
            Paragraph("Evaluation instruction", label),
            Paragraph(
                "Use recorded constraints before semantic relevance. Show the evidence for "
                "each proposed consultant and leave the final decision with a human delivery leader.",
                body,
            ),
            Spacer(1, 5 * mm),
            Paragraph("NOT A REAL CLIENT DOCUMENT", marker),
        ]
        document.build(story, onFirstPage=_page_frame, onLaterPages=_page_frame)
        generated.append(output_path)
    return generated


if __name__ == "__main__":
    for generated_path in generate():
        print(generated_path.relative_to(PROJECT_ROOT))
