"""Executive PDF report — KPI summary + top-vendor table."""
from __future__ import annotations
from pathlib import Path
from datetime import date
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def build_pdf(path: Path, *, kpis: dict, scorecard: pd.DataFrame) -> Path:
    doc = SimpleDocTemplate(str(path), pagesize=A4, title="SAP P2P Weekly Report")
    styles = getSampleStyleSheet()
    flow = [
        Paragraph("SAP Procure-to-Pay — Weekly Executive Report", styles["Title"]),
        Paragraph(f"Generated: {date.today():%B %d, %Y}", styles["Italic"]),
        Spacer(1, 18),
        Paragraph("Key Performance Indicators", styles["Heading2"]),
    ]

    kpi_rows = [["Metric", "Value"]] + [[k.replace("_", " ").title(), str(v)] for k, v in kpis.items()]
    t = Table(kpi_rows, hAlign="LEFT", colWidths=[200, 200])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0FAAFF")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",       (0, 0), (-1, -1), 0.4, colors.grey),
    ]))
    flow += [t, Spacer(1, 18), Paragraph("Top Vendors by Spend (EUR)", styles["Heading2"])]

    if not scorecard.empty:
        top = scorecard.head(10)
        rows = [list(top.columns)] + top.values.tolist()
        t2 = Table(rows, hAlign="LEFT")
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0FAAFF")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID",       (0, 0), (-1, -1), 0.3, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        flow.append(t2)

    doc.build(flow)
    return path
