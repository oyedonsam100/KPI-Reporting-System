import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from etl.transform import (
    get_total_revenue, get_profit_metrics, get_cac,
    get_customer_status, get_revenue_by_product,
    get_revenue_by_region, get_top_salespeople,
    get_monthly_revenue
)
from dotenv import load_dotenv
load_dotenv()

SHEET_ID   = os.getenv("GOOGLE_SHEET_ID")
CREDS_FILE = "config/google_credentials.json"
SCOPES     = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet_client():
    creds  = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)

def clear_and_write(worksheet, data):
    worksheet.clear()
    worksheet.update(range_name="A1", values=data)

def sync_to_sheets():
    print("🔄 Connecting to Google Sheets...")
    spreadsheet = get_sheet_client()

    # ── Tab 1: KPI Summary ──────────────────────────────────
    try:
        ws1 = spreadsheet.worksheet("KPI Summary")
    except:
        ws1 = spreadsheet.add_worksheet("KPI Summary", rows=20, cols=5)

    profit    = get_profit_metrics()
    cac       = get_cac()
    status    = get_customer_status()
    active    = int(status["active_customers"][0])
    churned   = int(status["churned_customers"][0])
    total     = active + churned
    retention = round((active / total) * 100, 1) if total > 0 else 0

    kpi_data = [
        ["📊 KPI SUMMARY", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
        [""],
        ["Metric", "Value"],
        ["💰 Total Revenue",    f"${get_total_revenue():,.2f}"],
        ["📈 Total Profit",     f"${profit['total_profit']:,.2f}"],
        ["📉 Profit Margin",    f"{profit['profit_margin_pct']}%"],
        ["🧲 Cust. Acq. Cost", f"${cac:,.2f}"],
        ["✅ Active Customers", str(active)],
        ["❌ Churned Customers",str(churned)],
        ["🔁 Retention Rate",   f"{retention}%"],
    ]
    clear_and_write(ws1, kpi_data)
    print("✅ KPI Summary tab updated")

    # ── Tab 2: Revenue by Product ───────────────────────────
    try:
        ws2 = spreadsheet.worksheet("By Product")
    except:
        ws2 = spreadsheet.add_worksheet("By Product", rows=20, cols=5)

    df_product   = get_revenue_by_product()
    product_data = [["Product", "Revenue", "Profit"]] + [
        [row["product"], round(row["revenue"], 2), round(row["profit"], 2)]
        for _, row in df_product.iterrows()
    ]
    clear_and_write(ws2, product_data)
    print("✅ By Product tab updated")

    # ── Tab 3: Revenue by Region ────────────────────────────
    try:
        ws3 = spreadsheet.worksheet("By Region")
    except:
        ws3 = spreadsheet.add_worksheet("By Region", rows=30, cols=5)

    df_region   = get_revenue_by_region()
    region_data = [["Region", "Revenue", "Profit"]] + [
        [row["region"], round(row["revenue"], 2), round(row["profit"], 2)]
        for _, row in df_region.iterrows()
    ]
    clear_and_write(ws3, region_data)
    print("✅ By Region tab updated")

    # ── Tab 4: Top Customers ────────────────────────────────
    try:
        ws4 = spreadsheet.worksheet("Top Customers")
    except:
        ws4 = spreadsheet.add_worksheet("Top Customers", rows=20, cols=5)

    df_sales   = get_top_salespeople()
    sales_data = [["Customer", "Revenue", "Total Orders"]] + [
        [row["salesperson"], round(row["revenue"], 2), int(row["total_sales"])]
        for _, row in df_sales.iterrows()
    ]
    clear_and_write(ws4, sales_data)
    print("✅ Top Customers tab updated")

    # ── Tab 5: Monthly Trend ────────────────────────────────
    try:
        ws5 = spreadsheet.worksheet("Monthly Trend")
    except:
        ws5 = spreadsheet.add_worksheet("Monthly Trend", rows=40, cols=5)

    df_monthly   = get_monthly_revenue()
    monthly_data = [["Month", "Revenue", "Profit"]] + [
        [row["month"], round(row["revenue"], 2), round(row["profit"], 2)]
        for _, row in df_monthly.iterrows()
    ]
    clear_and_write(ws5, monthly_data)
    print("✅ Monthly Trend tab updated")

    print(f"\n🎉 All tabs synced successfully!")
    print(f"   View your sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}")

if __name__ == "__main__":
    sync_to_sheets()