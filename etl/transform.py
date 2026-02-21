import pandas as pd
from sqlalchemy import create_engine

def get_connection():
    engine = create_engine(
        "mssql+pyodbc://DESKTOP-FHDJ2FC\\SQLEXPRESS/sales_db"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&trusted_connection=yes"
    )
    return engine.connect()

# ── KPI 1: Total Revenue ────────────────────────────────────
def get_total_revenue():
    conn = get_connection()
    df = pd.read_sql("SELECT SUM(SALES) as total_revenue FROM sale", conn)
    conn.close()
    return round(df["total_revenue"][0], 2)

# ── KPI 2: Total Profit & Profit Margin ────────────────────
def get_profit_metrics():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            SUM(SALES) as total_revenue,
            SUM(SALES * 0.45) as total_profit
        FROM sale
    """, conn)
    conn.close()
    total_profit  = round(df["total_profit"][0], 2)
    profit_margin = round((total_profit / df["total_revenue"][0]) * 100, 2)
    return {"total_profit": total_profit, "profit_margin_pct": profit_margin}

# ── KPI 3: Revenue by Product ───────────────────────────────
def get_revenue_by_product():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            PRODUCTLINE as product,
            SUM(SALES) as revenue,
            SUM(SALES * 0.45) as profit
        FROM sale
        GROUP BY PRODUCTLINE
        ORDER BY revenue DESC
    """, conn)
    conn.close()
    return df

# ── KPI 4: Revenue by Region ────────────────────────────────
def get_revenue_by_region():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            COUNTRY as region,
            SUM(SALES) as revenue,
            SUM(SALES * 0.45) as profit
        FROM sale
        GROUP BY COUNTRY
        ORDER BY revenue DESC
    """, conn)
    conn.close()
    return df

# ── KPI 5: Top Customers by Revenue ────────────────────────
def get_top_salespeople():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT TOP 10
            CUSTOMERNAME as salesperson,
            SUM(SALES) as revenue,
            COUNT(ORDERNUMBER) as total_sales
        FROM sale
        GROUP BY CUSTOMERNAME
        ORDER BY revenue DESC
    """, conn)
    conn.close()
    return df

# ── KPI 6: Monthly Revenue Trend ───────────────────────────
def get_monthly_revenue():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            CAST(YEAR_ID AS VARCHAR) + '-' + 
            RIGHT('0' + CAST(MONTH_ID AS VARCHAR), 2) as month,
            SUM(SALES) as revenue,
            SUM(SALES * 0.45) as profit
        FROM sale
        GROUP BY YEAR_ID, MONTH_ID
        ORDER BY YEAR_ID, MONTH_ID
    """, conn)
    conn.close()
    return df

# ── KPI 7: Customer Acquisition Cost (CAC) ─────────────────
def get_cac():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT COUNT(DISTINCT CUSTOMERNAME) as total_customers
        FROM sale
    """, conn)
    conn.close()
    total_customers = df["total_customers"][0]
    return round(500 / total_customers * 100, 2)

# ── KPI 8: Active vs Churned Customers ─────────────────────
def get_customer_status():
    conn = get_connection()

    df_2003 = pd.read_sql("SELECT DISTINCT CUSTOMERNAME FROM sale WHERE YEAR_ID = 2003", conn)
    df_2004 = pd.read_sql("SELECT DISTINCT CUSTOMERNAME FROM sale WHERE YEAR_ID = 2004", conn)
    df_2005 = pd.read_sql("SELECT DISTINCT CUSTOMERNAME FROM sale WHERE YEAR_ID = 2005", conn)

    conn.close()

    customers_2003 = set(df_2003["CUSTOMERNAME"])
    customers_2004 = set(df_2004["CUSTOMERNAME"])
    customers_2005 = set(df_2005["CUSTOMERNAME"])

    # Year over year: who bought in 2004 came back in 2005?
    retained = len(customers_2004 & customers_2005)
    churned  = len(customers_2004 - customers_2005)
    total    = len(customers_2004)

    result = pd.DataFrame([{
        "active_customers":  retained,
        "total_customers":   total,
        "churned_customers": churned
    }])
    return result

# ── Run All KPIs ────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 45)
    print("         📊 KPI SUMMARY REPORT")
    print("=" * 45)

    print(f"\n💰 Total Revenue:      ${get_total_revenue():,.2f}")

    profit = get_profit_metrics()
    print(f"📈 Total Profit:       ${profit['total_profit']:,.2f}")
    print(f"📉 Profit Margin:      {profit['profit_margin_pct']}%")
    print(f"\n🧲 Cust. Acq. Cost:   ${get_cac():,.2f}")

    status = get_customer_status()
    print(f"✅ Active Customers:   {status['active_customers'][0]}")
    print(f"❌ Churned Customers:  {status['churned_customers'][0]}")

    print("\n📦 Revenue by Product:")
    print(get_revenue_by_product().to_string(index=False))

    print("\n🌍 Revenue by Region:")
    print(get_revenue_by_region().to_string(index=False))

    print("\n🏆 Top Customers by Revenue:")
    print(get_top_salespeople().to_string(index=False))

    print("\n📅 Monthly Revenue Trend:")
    print(get_monthly_revenue().to_string(index=False))