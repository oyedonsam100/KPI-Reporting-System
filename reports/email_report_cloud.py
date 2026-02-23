import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

load_dotenv()

EMAIL_SENDER    = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVERS = [
    os.getenv("EMAIL_RECEIVER"),
    os.getenv("EMAIL_RECEIVER2"),
    os.getenv("EMAIL_RECEIVER3"),
]
EMAIL_RECEIVERS = [e for e in EMAIL_RECEIVERS if e]

DASHBOARD_URL = "https://kpi-reporting-system-ifxehqzoojyy5g6qcsvob8.streamlit.app/"
CSV_PATH      = "data/sales_data_sample.csv"

# ── Load & Calculate KPIs from CSV ──────────────────────────
def load_kpis():
    df = pd.read_csv(CSV_PATH, encoding="latin1")
    df.columns = df.columns.str.strip()
    df["SALES"]  = pd.to_numeric(df["SALES"],  errors="coerce")
    df["PROFIT"] = df["SALES"] * 0.45

    total_revenue = round(df["SALES"].sum(), 2)
    total_profit  = round(df["PROFIT"].sum(), 2)
    profit_margin = round((total_profit / total_revenue) * 100, 2)
    num_customers = df["CUSTOMERNAME"].nunique()
    cac           = round(500 / num_customers * 100, 2)

    c2004     = set(df[df["YEAR_ID"] == 2004]["CUSTOMERNAME"])
    c2005     = set(df[df["YEAR_ID"] == 2005]["CUSTOMERNAME"])
    retained  = len(c2004 & c2005)
    retention = round((retained / len(c2004)) * 100, 1) if len(c2004) > 0 else 0

    top_product     = df.groupby("PRODUCTLINE")["SALES"].sum().idxmax()
    top_country     = df.groupby("COUNTRY")["SALES"].sum().idxmax()
    top_country_rev = df.groupby("COUNTRY")["SALES"].sum().max()

    return {
        "total_revenue":   total_revenue,
        "total_profit":    total_profit,
        "profit_margin":   profit_margin,
        "cac":             cac,
        "retention":       retention,
        "top_product":     top_product,
        "top_country":     top_country,
        "top_country_rev": top_country_rev,
        "num_customers":   num_customers,
    }

# ── Generate PDF from CSV ────────────────────────────────────
def generate_pdf(kpis, output_path="data/processed/kpi_report.pdf"):
    os.makedirs("data/processed", exist_ok=True)

    df = pd.read_csv(CSV_PATH, encoding="latin1")
    df.columns = df.columns.str.strip()
    df["SALES"]  = pd.to_numeric(df["SALES"],  errors="coerce")
    df["PROFIT"] = df["SALES"] * 0.45

    doc    = SimpleDocTemplate(output_path, pagesize=A4,
                               rightMargin=2*cm, leftMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    title_style = ParagraphStyle(
        "title", parent=styles["Title"],
        fontSize=24, textColor=colors.HexColor("#1a1a2e"), spaceAfter=6
    )
    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"],
        fontSize=11, textColor=colors.grey, spaceAfter=20
    )
    section_style = ParagraphStyle(
        "section", parent=styles["Heading2"],
        fontSize=14, textColor=colors.HexColor("#00b4d8"),
        spaceBefore=16, spaceAfter=8
    )

    story.append(Paragraph("KPI Summary Report", title_style))
    story.append(Paragraph(
        f"Sales & Revenue Overview — Generated {datetime.now().strftime('%B %d, %Y')}",
        sub_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#00b4d8")))
    story.append(Spacer(1, 0.4*cm))

    # KPI Summary Table
    story.append(Paragraph("Key Performance Indicators", section_style))
    kpi_data = [
        ["Metric", "Value"],
        ["Total Revenue",       f"${kpis['total_revenue']:,.2f}"],
        ["Total Profit",        f"${kpis['total_profit']:,.2f}"],
        ["Profit Margin",       f"{kpis['profit_margin']}%"],
        ["Cust. Acq. Cost",     f"${kpis['cac']:,.2f}"],
        ["Retention Rate",      f"{kpis['retention']}%"],
        ["Top Product Line",    kpis['top_product']],
        ["Top Country",         f"{kpis['top_country']} — ${kpis['top_country_rev']:,.0f}"],
    ]
    kpi_table = Table(kpi_data, colWidths=[9*cm, 7*cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 12),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#f0f9ff"), colors.white]),
        ("FONTSIZE",      (0,1), (-1,-1), 11),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING",       (0,0), (-1,-1), 10),
        ("ALIGN",         (1,0), (1,-1), "RIGHT"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.5*cm))

    # Revenue by Product
    story.append(Paragraph("Revenue by Product Line", section_style))
    df_prod = df.groupby("PRODUCTLINE").agg(
        revenue=("SALES", "sum"),
        profit=("PROFIT", "sum")
    ).reset_index().sort_values("revenue", ascending=False)
    prod_data = [["Product Line", "Revenue", "Profit"]] + [
        [row["PRODUCTLINE"], f"${row['revenue']:,.2f}", f"${row['profit']:,.2f}"]
        for _, row in df_prod.iterrows()
    ]
    prod_table = Table(prod_data, colWidths=[7*cm, 5*cm, 5*cm])
    prod_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#00b4d8")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#f0f9ff"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING",       (0,0), (-1,-1), 9),
        ("ALIGN",         (1,0), (-1,-1), "RIGHT"),
    ]))
    story.append(prod_table)
    story.append(Spacer(1, 0.5*cm))

    # Revenue by Country
    story.append(Paragraph("Revenue by Country (Top 10)", section_style))
    df_country = df.groupby("COUNTRY").agg(
        revenue=("SALES", "sum")
    ).reset_index().sort_values("revenue", ascending=False).head(10)
    country_data = [["Country", "Revenue"]] + [
        [row["COUNTRY"], f"${row['revenue']:,.2f}"]
        for _, row in df_country.iterrows()
    ]
    country_table = Table(country_data, colWidths=[9*cm, 7*cm])
    country_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#06d6a0")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#f0fff8"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("PADDING",       (0,0), (-1,-1), 9),
        ("ALIGN",         (1,0), (-1,-1), "RIGHT"),
    ]))
    story.append(country_table)

    # Footer
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Auto-generated by KPI Reporting System • {datetime.now().strftime('%Y-%m-%d %H:%M')} • Built by Samuel Oyedokun",
        ParagraphStyle("footer", parent=styles["Normal"],
                       fontSize=9, textColor=colors.grey, alignment=1)
    ))

    doc.build(story)
    print(f"✅ PDF generated: {output_path}")
    return output_path

# ── Send Email ───────────────────────────────────────────────
def send_kpi_email():
    kpis     = load_kpis()
    pdf_path = generate_pdf(kpis)

    msg = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = ", ".join(EMAIL_RECEIVERS)
    msg["Subject"] = f"KPI Report — {datetime.now().strftime('%B %d, %Y')}"

    body = f"""
<html><body style="font-family: Arial, sans-serif; color: #333; margin:0; padding:0; background:#f4f6f9;">
<div style="max-width:620px; margin:auto; background:white; border-radius:12px; overflow:hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
    <div style="background:#0D1421; padding:36px 40px; text-align:center;">
        <h1 style="color:white; margin:0; font-size:22px; font-weight:700;">KPI Summary Report</h1>
        <p style="color:#64748B; margin:8px 0 0; font-size:13px;">Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
    </div>
    <div style="height:3px; background:linear-gradient(90deg,#63B3ED,#4FD1C5,#F6AD55);"></div>
    <div style="padding:36px 40px;">
        <p style="font-size:15px; color:#334155; margin-top:0;">Hello,</p>
        <p style="font-size:14px; color:#475569; line-height:1.7;">
            Your automated <strong>KPI Summary Report</strong> for the sales period
            <strong>2003-2005</strong> is ready. The full PDF is attached.
        </p>
        <div style="text-align:center; margin:28px 0;">
            <a href="{DASHBOARD_URL}"
               style="background:linear-gradient(135deg,#63B3ED,#4FD1C5); color:white;
                      text-decoration:none; padding:14px 32px; border-radius:8px;
                      font-size:14px; font-weight:600; display:inline-block;">
                View Live Dashboard
            </a>
        </div>
        <div style="background:#F8FAFC; border-radius:10px; padding:20px 24px; margin-bottom:24px;">
            <h3 style="color:#1E293B; font-size:14px; margin:0 0 14px; text-transform:uppercase;">KPI Highlights</h3>
            <table style="width:100%; border-collapse:collapse;">
                <tr><td style="padding:8px 0; font-size:13px; color:#475569; border-bottom:1px solid #E2E8F0;">Total Revenue</td>
                    <td style="padding:8px 0; font-size:13px; font-weight:600; text-align:right; border-bottom:1px solid #E2E8F0;">${kpis['total_revenue']:,.2f}</td></tr>
                <tr><td style="padding:8px 0; font-size:13px; color:#475569; border-bottom:1px solid #E2E8F0;">Total Profit</td>
                    <td style="padding:8px 0; font-size:13px; font-weight:600; text-align:right; border-bottom:1px solid #E2E8F0;">${kpis['total_profit']:,.2f}</td></tr>
                <tr><td style="padding:8px 0; font-size:13px; color:#475569; border-bottom:1px solid #E2E8F0;">Profit Margin</td>
                    <td style="padding:8px 0; font-size:13px; font-weight:600; text-align:right; border-bottom:1px solid #E2E8F0;">{kpis['profit_margin']}%</td></tr>
                <tr><td style="padding:8px 0; font-size:13px; color:#475569; border-bottom:1px solid #E2E8F0;">Retention Rate</td>
                    <td style="padding:8px 0; font-size:13px; font-weight:600; text-align:right; border-bottom:1px solid #E2E8F0;">{kpis['retention']}%</td></tr>
                <tr><td style="padding:8px 0; font-size:13px; color:#475569; border-bottom:1px solid #E2E8F0;">Top Product</td>
                    <td style="padding:8px 0; font-size:13px; font-weight:600; text-align:right; border-bottom:1px solid #E2E8F0;">{kpis['top_product']}</td></tr>
                <tr><td style="padding:8px 0; font-size:13px; color:#475569;">Top Country</td>
                    <td style="padding:8px 0; font-size:13px; font-weight:600; text-align:right;">{kpis['top_country']} - ${kpis['top_country_rev']:,.0f}</td></tr>
            </table>
        </div>
        <div style="background:#EFF6FF; border-left:4px solid #63B3ED; padding:12px 16px; border-radius:4px;">
            <p style="margin:0; font-size:13px; color:#3B82F6;">Full PDF report is attached to this email.</p>
        </div>
    </div>
    <div style="background:#F8FAFC; padding:20px 40px; text-align:center; border-top:1px solid #E2E8F0;">
        <p style="color:#94A3B8; font-size:12px; margin:0;">
            KPI Reporting System · Auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · Built by Samuel Oyedokun
        </p>
    </div>
</div>
</body></html>
"""
    msg.attach(MIMEText(body, "html"))

    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",
                        f"attachment; filename=kpi_report_{datetime.now().strftime('%Y%m%d')}.pdf")
        msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVERS, msg.as_string())
        print(f"✅ Email sent successfully to:")
        for e in EMAIL_RECEIVERS:
            print(f"   -> {e}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    send_kpi_email()