import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from datetime import datetime
from etl.transform import (
    get_total_revenue, get_profit_metrics, get_cac,
    get_customer_status, get_revenue_by_product,
    get_revenue_by_region, get_top_salespeople,
    get_monthly_revenue
)

def generate_pdf(output_path="data/processed/kpi_report.pdf"):
    os.makedirs("data/processed", exist_ok=True)

    doc  = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    # ── Custom Styles ───────────────────────────────────────
    title_style = ParagraphStyle("title", parent=styles["Title"],
                                  fontSize=24, textColor=colors.HexColor("#1a1a2e"),
                                  spaceAfter=6)
    sub_style   = ParagraphStyle("sub", parent=styles["Normal"],
                                  fontSize=11, textColor=colors.grey, spaceAfter=20)
    section_style = ParagraphStyle("section", parent=styles["Heading2"],
                                    fontSize=14, textColor=colors.HexColor("#00b4d8"),
                                    spaceBefore=16, spaceAfter=8)

    # ── Header ──────────────────────────────────────────────
    story.append(Paragraph("📊 KPI Summary Report", title_style))
    story.append(Paragraph(f"Sales & Revenue Overview — Generated {datetime.now().strftime('%B %d, %Y')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#00b4d8")))
    story.append(Spacer(1, 0.4*cm))

    # ── KPI Cards Table ─────────────────────────────────────
    total_revenue = get_total_revenue()
    profit        = get_profit_metrics()
    cac           = get_cac()
    status        = get_customer_status()
    active        = int(status["active_customers"][0])
    churned       = int(status["churned_customers"][0])
    retention     = round((active / (active + churned)) * 100, 1)

    story.append(Paragraph("Key Performance Indicators", section_style))

    kpi_data = [
        ["Metric", "Value"],
        ["💰 Total Revenue",    f"${total_revenue:,.2f}"],
        ["📈 Total Profit",     f"${profit['total_profit']:,.2f}"],
        ["📉 Profit Margin",    f"{profit['profit_margin_pct']}%"],
        ["🧲 Cust. Acq. Cost", f"${cac:,.2f}"],
        ["✅ Active Customers", f"{active}"],
        ["❌ Churned Customers",f"{churned}"],
        ["🔁 Retention Rate",   f"{retention}%"],
    ]

    kpi_table = Table(kpi_data, colWidths=[9*cm, 7*cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0), 12),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f9ff"), colors.white]),
        ("FONTSIZE",     (0,1), (-1,-1), 11),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING",      (0,0), (-1,-1), 10),
        ("ALIGN",        (1,0), (1,-1), "RIGHT"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Revenue by Product ──────────────────────────────────
    story.append(Paragraph("Revenue by Product", section_style))
    df_product = get_revenue_by_product()
    prod_data  = [["Product", "Revenue", "Profit"]] + [
        [row["product"], f"${row['revenue']:,.2f}", f"${row['profit']:,.2f}"]
        for _, row in df_product.iterrows()
    ]
    prod_table = Table(prod_data, colWidths=[7*cm, 5*cm, 5*cm])
    prod_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#00b4d8")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f9ff"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING",       (0,0), (-1,-1), 9),
        ("ALIGN",         (1,0), (-1,-1), "RIGHT"),
    ]))
    story.append(prod_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Top Salespeople ─────────────────────────────────────
    story.append(Paragraph("Top Salespeople", section_style))
    df_sales  = get_top_salespeople()
    sales_data = [["Salesperson", "Revenue", "Total Sales"]] + [
        [row["salesperson"], f"${row['revenue']:,.2f}", str(row["total_sales"])]
        for _, row in df_sales.iterrows()
    ]
    sales_table = Table(sales_data, colWidths=[7*cm, 5*cm, 5*cm])
    sales_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#06d6a0")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0fff8"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING",       (0,0), (-1,-1), 9),
        ("ALIGN",         (1,0), (-1,-1), "RIGHT"),
    ]))
    story.append(sales_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Monthly Revenue ─────────────────────────────────────
    story.append(Paragraph("Monthly Revenue Trend", section_style))
    df_monthly  = get_monthly_revenue()
    monthly_data = [["Month", "Revenue", "Profit"]] + [
        [row["month"], f"${row['revenue']:,.2f}", f"${row['profit']:,.2f}"]
        for _, row in df_monthly.iterrows()
    ]
    monthly_table = Table(monthly_data, colWidths=[5*cm, 6*cm, 6*cm])
    monthly_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#f77f00")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#fff8f0"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING",       (0,0), (-1,-1), 9),
        ("ALIGN",         (1,0), (-1,-1), "RIGHT"),
    ]))
    story.append(monthly_table)

    # ── Footer ──────────────────────────────────────────────
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Auto-generated by KPI Reporting System • {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ParagraphStyle("footer", parent=styles["Normal"],
                       fontSize=9, textColor=colors.grey, alignment=1)
    ))

    doc.build(story)
    print(f"✅ PDF report generated: {output_path}")

if __name__ == "__main__":
    generate_pdf()