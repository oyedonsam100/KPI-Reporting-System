import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
from etl.transform import (
    get_total_revenue, get_profit_metrics, get_cac,
    get_customer_status, get_revenue_by_product,
    get_revenue_by_region, get_top_salespeople,
    get_monthly_revenue
)

app = Dash(__name__)

# ── Load Data ───────────────────────────────────────────────
total_revenue  = get_total_revenue()
profit         = get_profit_metrics()
cac            = get_cac()
status         = get_customer_status()
df_product     = get_revenue_by_product()
df_region      = get_revenue_by_region()
df_sales       = get_top_salespeople()
df_monthly     = get_monthly_revenue()

# ── Charts ──────────────────────────────────────────────────
fig_monthly = px.line(
    df_monthly, x="month", y="revenue",
    title="📅 Monthly Revenue Trend",
    markers=True, color_discrete_sequence=["#00b4d8"]
)

fig_product = px.bar(
    df_product, x="product", y="revenue",
    title="📦 Revenue by Product",
    color="product", color_discrete_sequence=px.colors.qualitative.Set2
)

fig_region = px.pie(
    df_region, names="region", values="revenue",
    title="🌍 Revenue by Region",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_sales = px.bar(
    df_sales, x="salesperson", y="revenue",
    title="🏆 Top Salespeople",
    color="salesperson", color_discrete_sequence=px.colors.qualitative.Bold
)

# ── KPI Card Helper ─────────────────────────────────────────
def kpi_card(title, value, color):
    return html.Div([
        html.P(title, style={"margin": "0", "fontSize": "14px", "color": "#666"}),
        html.H2(value, style={"margin": "0", "color": color})
    ], style={
        "background": "white", "borderRadius": "12px",
        "padding": "20px 30px", "flex": "1",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
        "minWidth": "180px", "textAlign": "center"
    })

active     = int(status["active_customers"][0])
churned    = int(status["churned_customers"][0])
total_cust = active + churned
retention  = round((active / total_cust) * 100, 1)

# ── Layout ──────────────────────────────────────────────────
app.layout = html.Div([

    html.H1("📊 KPI Reporting Dashboard",
            style={"textAlign": "center", "color": "white",
                   "padding": "30px 0 10px", "margin": 0}),
    html.P("Sales & Revenue Overview — 2003 to 2005",
           style={"textAlign": "center", "color": "#ccc", "marginBottom": "30px"}),

    # KPI Cards Row
    html.Div([
        kpi_card("💰 Total Revenue",   f"${total_revenue:,.0f}",           "#00b4d8"),
        kpi_card("📈 Total Profit",    f"${profit['total_profit']:,.0f}",   "#06d6a0"),
        kpi_card("📉 Profit Margin",   f"{profit['profit_margin_pct']}%",   "#f77f00"),
        kpi_card("🧲 CAC",             f"${cac:,.2f}",                      "#e63946"),
        kpi_card("✅ Retention Rate",  f"{retention}%",                     "#7209b7"),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap",
              "padding": "0 40px 30px"}),

    # Charts Row 1
    html.Div([
        dcc.Graph(figure=fig_monthly, style={"flex": "2"}),
        dcc.Graph(figure=fig_region,  style={"flex": "1"}),
    ], style={"display": "flex", "gap": "16px", "padding": "0 40px 20px"}),

    # Charts Row 2
    html.Div([
        dcc.Graph(figure=fig_product, style={"flex": "1"}),
        dcc.Graph(figure=fig_sales,   style={"flex": "1"}),
    ], style={"display": "flex", "gap": "16px", "padding": "0 40px 40px"}),

], style={"background": "#1a1a2e", "minHeight": "100vh", "fontFamily": "Segoe UI, sans-serif"})

if __name__ == "__main__":
    app.run(debug=True)