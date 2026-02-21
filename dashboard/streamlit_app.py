import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.express as px
from etl.transform import (
    get_total_revenue, get_profit_metrics, get_cac,
    get_customer_status, get_revenue_by_product,
    get_revenue_by_region, get_top_salespeople,
    get_monthly_revenue
)

st.set_page_config(page_title="KPI Dashboard", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1a1a2e; }
    .metric-card {
        background: #16213e;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 KPI Reporting Dashboard")
st.markdown("**Sales & Revenue Overview — 2003 to 2005**")
st.divider()

# ── KPI Cards ───────────────────────────────────────────────
total_revenue = get_total_revenue()
profit        = get_profit_metrics()
cac           = get_cac()
status        = get_customer_status()
active        = int(status["active_customers"][0])
churned       = int(status["churned_customers"][0])
total         = active + churned
retention     = round((active / total) * 100, 1) if total > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Revenue",  f"${total_revenue:,.0f}")
col2.metric("📈 Total Profit",   f"${profit['total_profit']:,.0f}")
col3.metric("📉 Profit Margin",  f"{profit['profit_margin_pct']}%")
col4.metric("🧲 CAC",            f"${cac:,.2f}")
col5.metric("🔁 Retention Rate", f"{retention}%")

st.divider()

# ── Charts Row 1 ────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    df_monthly = get_monthly_revenue()
    fig = px.line(df_monthly, x="month", y="revenue",
                  title="📅 Monthly Revenue Trend",
                  markers=True, color_discrete_sequence=["#00b4d8"])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_region = get_revenue_by_region()
    fig = px.pie(df_region.head(8), names="region", values="revenue",
                 title="🌍 Revenue by Region",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 2 ────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    df_product = get_revenue_by_product()
    fig = px.bar(df_product, x="product", y="revenue",
                 title="📦 Revenue by Product",
                 color="product",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_sales = get_top_salespeople()
    fig = px.bar(df_sales, x="salesperson", y="revenue",
                 title="🏆 Top Customers by Revenue",
                 color="salesperson",
                 color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(f"Data sourced from SQL Server • Auto-generated KPI Reporting System")