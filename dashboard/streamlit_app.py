import streamlit as st
import plotly.express as px
import pandas as pd
import os

st.set_page_config(page_title="KPI Dashboard", page_icon="📊", layout="wide")

# ── Load CSV ────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/sales_data_sample.csv", encoding="latin1")
    df.columns = df.columns.str.strip()
    df["SALES"] = pd.to_numeric(df["SALES"], errors="coerce")
    df["PRICEEACH"] = pd.to_numeric(df["PRICEEACH"], errors="coerce")
    df["QUANTITYORDERED"] = pd.to_numeric(df["QUANTITYORDERED"], errors="coerce")
    df["PROFIT"] = df["SALES"] * 0.45
    return df

df = load_data()

# ── KPI Calculations ─────────────────────────────────────────
total_revenue  = round(df["SALES"].sum(), 2)
total_profit   = round(df["PROFIT"].sum(), 2)
profit_margin  = round((total_profit / total_revenue) * 100, 2)

customers_2004 = set(df[df["YEAR_ID"] == 2004]["CUSTOMERNAME"])
customers_2005 = set(df[df["YEAR_ID"] == 2005]["CUSTOMERNAME"])
retained       = len(customers_2004 & customers_2005)
churned        = len(customers_2004 - customers_2005)
total_cust     = len(customers_2004)
retention      = round((retained / total_cust) * 100, 1) if total_cust > 0 else 0
cac            = round(500 / df["CUSTOMERNAME"].nunique() * 100, 2)

# ── Revenue by Product ───────────────────────────────────────
df_product = df.groupby("PRODUCTLINE").agg(
    revenue=("SALES", "sum"),
    profit=("PROFIT", "sum")
).reset_index().rename(columns={"PRODUCTLINE": "product"}).sort_values("revenue", ascending=False)

# ── Revenue by Region ────────────────────────────────────────
df_region = df.groupby("COUNTRY").agg(
    revenue=("SALES", "sum"),
    profit=("PROFIT", "sum")
).reset_index().rename(columns={"COUNTRY": "region"}).sort_values("revenue", ascending=False)

# ── Top Customers ────────────────────────────────────────────
df_sales = df.groupby("CUSTOMERNAME").agg(
    revenue=("SALES", "sum"),
    total_sales=("ORDERNUMBER", "count")
).reset_index().rename(columns={"CUSTOMERNAME": "salesperson"}).sort_values("revenue", ascending=False).head(10)

# ── Monthly Trend ────────────────────────────────────────────
df["month"] = df["YEAR_ID"].astype(str) + "-" + df["MONTH_ID"].astype(str).str.zfill(2)
df_monthly  = df.groupby("month").agg(
    revenue=("SALES", "sum"),
    profit=("PROFIT", "sum")
).reset_index().sort_values("month")

# ── Page Header ──────────────────────────────────────────────
st.title("📊 KPI Reporting Dashboard")
st.markdown("**Sales & Revenue Overview — 2003 to 2005**")
st.divider()

# ── KPI Cards ────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Revenue",  f"${total_revenue:,.0f}")
col2.metric("📈 Total Profit",   f"${total_profit:,.0f}")
col3.metric("📉 Profit Margin",  f"{profit_margin}%")
col4.metric("🧲 CAC",            f"${cac:,.2f}")
col5.metric("🔁 Retention Rate", f"{retention}%")

st.divider()

# ── Charts Row 1 ─────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    fig = px.line(df_monthly, x="month", y="revenue",
                  title="📅 Monthly Revenue Trend",
                  markers=True, color_discrete_sequence=["#00b4d8"])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.pie(df_region.head(8), names="region", values="revenue",
                 title="🌍 Revenue by Region",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 2 ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(df_product, x="product", y="revenue",
                 title="📦 Revenue by Product",
                 color="product",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(df_sales, x="salesperson", y="revenue",
                 title="🏆 Top Customers by Revenue",
                 color="salesperson",
                 color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data sourced from Sales Dataset • Auto-generated KPI Reporting System")