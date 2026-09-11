from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _text(value):
    """Convert model output to safe, readable PDF text."""
    return escape(str(value or "")).replace("\n", "<br/>")


def _items(values):
    if isinstance(values, str):
        return [values] if values.strip() else []
    return [str(value) for value in (values or []) if str(value).strip()]


def _bullet_list(values, style):
    return [Paragraph(f"&#8226; {_text(value)}", style) for value in _items(values)]


def _section_heading(title, style):
    return [Spacer(1, 0.16 * inch), Paragraph(_text(title), style)]


def _footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d9e2ec"))
    canvas.line(0.65 * inch, 0.52 * inch, 7.85 * inch, 0.52 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(0.65 * inch, 0.34 * inch, "Smart AI Resume Analyzer")
    canvas.drawRightString(7.85 * inch, 0.34 * inch, f"Page {document.page}")
    canvas.restoreState()


def generate_ai_report(analysis, role="", filename="resume"):
    """Return a PDF report for a completed AI resume analysis."""
    analysis = analysis or {}
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.68 * inch,
        title=f"AI Resume Analysis - {filename}",
        author="Smart AI Resume Analyzer",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=22, leading=27, textColor=colors.HexColor("#12304a"),
        alignment=TA_CENTER, spaceAfter=5,
    )
    subtitle = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], fontSize=10, leading=14,
        textColor=colors.HexColor("#64748b"), alignment=TA_CENTER,
    )
    heading = ParagraphStyle(
        "ReportHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=13, leading=16, textColor=colors.HexColor("#12304a"),
        spaceBefore=8, spaceAfter=7,
    )
    body = ParagraphStyle(
        "ReportBody", parent=styles["BodyText"], fontSize=9.5, leading=14,
        textColor=colors.HexColor("#243b53"), spaceAfter=4,
    )
    bullet = ParagraphStyle(
        "ReportBullet", parent=body, leftIndent=10, firstLineIndent=-8,
        spaceAfter=5,
    )
    small = ParagraphStyle(
        "ReportSmall", parent=body, fontSize=8.5, leading=12,
        textColor=colors.HexColor("#52606d"),
    )

    score = analysis.get("ai_overall_score", analysis.get("ats_score", 0))
    keyword_score = analysis.get("keyword_match_percent", 0)
    verdict = analysis.get("ai_verdict", "")
    story = [
        Paragraph("AI Resume Analysis Report", title),
        Paragraph(
            f"{_text(filename)}{f' &bull; {_text(role)}' if role else ''}",
            subtitle,
        ),
        Spacer(1, 0.22 * inch),
    ]

    score_table = Table(
        [
            [
                Paragraph(f"<b>{_text(score)}</b><br/><font size=8>OVERALL SCORE</font>", body),
                Paragraph(f"<b>{_text(keyword_score)}%</b><br/><font size=8>KEYWORD MATCH</font>", body),
                Paragraph(f"<b>{_text(verdict) or 'Analysis complete'}</b><br/><font size=8>VERDICT</font>", body),
            ]
        ],
        colWidths=[2.25 * inch] * 3,
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e8f1f8")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#b8c9d9")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b8c9d9")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(score_table)

    summary = analysis.get("ai_summary") or analysis.get("summary")
    if summary:
        story.extend(_section_heading("AI Summary", heading))
        story.append(Paragraph(_text(summary), body))

    story.extend(_section_heading("Strengths", heading))
    story.extend(_bullet_list(analysis.get("strengths"), bullet) or [Paragraph("No strengths provided.", small)])

    story.extend(_section_heading("Areas to Improve", heading))
    story.extend(_bullet_list(analysis.get("weaknesses"), bullet) or [Paragraph("No weaknesses provided.", small)])

    found = _items(analysis.get("found_keywords"))
    missing = _items(analysis.get("missing_keywords"))
    story.extend(_section_heading("Keyword Coverage", heading))
    keyword_rows = [[Paragraph("<b>Found keywords</b>", body), Paragraph("<b>Missing keywords</b>", body)]]
    keyword_rows.append([
        Paragraph("<br/>".join(f"&#8226; {_text(item)}" for item in found) or "None identified.", small),
        Paragraph("<br/>".join(f"&#8226; {_text(item)}" for item in missing) or "None identified.", small),
    ])
    keyword_table = Table(keyword_rows, colWidths=[3.55 * inch, 3.55 * inch])
    keyword_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(keyword_table)

    section_feedback = analysis.get("section_feedback") or {}
    if section_feedback:
        story.extend(_section_heading("Section Feedback", heading))
        feedback_rows = [[Paragraph("<b>Section</b>", body), Paragraph("<b>Feedback</b>", body)]]
        feedback_rows.extend([
            Paragraph(_text(section.replace("_", " ").title()), small),
            Paragraph(_text(feedback), small),
        ] for section, feedback in section_feedback.items())
        feedback_table = Table(feedback_rows, colWidths=[1.5 * inch, 5.6 * inch], repeatRows=1)
        feedback_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(feedback_table)

    story.extend(_section_heading("Action Plan", heading))
    action_items = _items(analysis.get("ats_tips")) + _items(analysis.get("recommended_additions"))
    story.extend(_bullet_list(action_items, bullet) or [Paragraph("No action items provided.", small)])

    rewrites = analysis.get("bullet_rewrites") or []
    if rewrites:
        story.extend(_section_heading("AI Bullet Rewrites", heading))
        rewrite_rows = [[Paragraph("<b>Original</b>", body), Paragraph("<b>Suggested rewrite</b>", body)]]
        for rewrite in rewrites:
            if isinstance(rewrite, dict):
                rewrite_rows.append([
                    Paragraph(_text(rewrite.get("original")), small),
                    Paragraph(_text(rewrite.get("improved")), small),
                ])
        rewrite_table = Table(rewrite_rows, colWidths=[3.55 * inch, 3.55 * inch], repeatRows=1)
        rewrite_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(KeepTogether(rewrite_table))

    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer