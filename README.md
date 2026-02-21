# 📊 KPI Intelligence Center — Automated Sales Reporting System

A production-grade, fully automated business intelligence pipeline built with Python, SQL Server, and Streamlit. Extracts 2,800+ real sales transactions, calculates executive-level KPIs, generates PDF reports, and delivers them via scheduled email — all from a single command.

## 🔗 Live Dashboard
👉 **[View Live Dashboard](https://kpi-reporting-system-ifxehqzoojyy5g6qcsvob8.streamlit.app/)**

> Interactive 5-tab analytics dashboard with real-time filters, YoY comparisons, heatmaps, choropleth maps, and deal analysis — accessible from any device, anywhere.

---

## 🚀 Features

- **5-Tab Interactive Dashboard** — Overview, Products, Regions, Trends & YoY, Deal Analysis
- **Dynamic Sidebar Filters** — Filter all charts simultaneously by Year, Product Line, and Deal Size
- **Year-over-Year Analysis** — Revenue growth comparison across 2003, 2004, and 2005
- **Seasonality Heatmap** — Monthly revenue patterns visualized across all years
- **World Choropleth Map** — Geographic revenue distribution across 19 countries
- **Deal Size Intelligence** — Small, Medium, and Large deal performance breakdown
- **Analyst Insights** — Auto-generated strategic observations from the data
- **PDF Report Generation** — Professional multi-page formatted reports via ReportLab
- **Automated Email Delivery** — HTML emails with dashboard link + PDF to multiple recipients
- **ETL Pipeline** — Extract, Transform, Load architecture using Pandas & SQL Server
- **Job Scheduler** — Fully automated daily report delivery via schedule library

---

## 📊 Dashboard Tabs & Analysis

### 📈 Overview Tab
- Monthly Revenue & Profit trend (area line chart)
- Deal size revenue split (donut chart)
- Top 10 customers by revenue with margin & order count table

### 📦 Products Tab
- Revenue by product line (horizontal bar)
- Profit margin comparison by product (horizontal bar)
- Product line performance over time (multi-line chart)

### 🌍 Regions Tab
- World choropleth map — revenue by country
- Top 10 countries ranked by revenue
- Territory scorecards (NA, EMEA, APAC) with margin & orders

### 📈 Trends & YoY Tab
- Year-over-year monthly revenue comparison (2003 vs 2004 vs 2005)
- Annual revenue + growth rate combo chart
- Monthly seasonality heatmap
- Auto-generated analyst insights & strategic recommendations

### 💼 Deal Analysis Tab
- Small / Medium / Large deal scorecards with revenue, orders, avg value, margin
- Deal size mix by year (grouped bar)
- Deal size by product line (stacked bar)
- Order status conversion funnel

---

## 🔢 KPIs Tracked

| KPI | Description |
|-----|-------------|
| 💰 Total Revenue | Sum of all sales across filtered period |
| 📈 Total Profit | Revenue × 45% profit margin |
| 📉 Profit Margin % | Profit as percentage of revenue |
| 📦 Avg Order Value | Revenue divided by total unique orders |
| 🧲 Customer Acq. Cost | Estimated cost to acquire each customer |
| 🔁 Retention Rate | % of 2004 customers who returned in 2005 |
| 🌍 Revenue by Country | Sales performance across 19 countries |
| 🏆 Top Customers | Top 10 customers ranked by revenue |
| 📅 Monthly Trends | Revenue & profit by month across all years |
| 📊 YoY Growth | Year-over-year revenue growth percentage |
| 💼 Deal Size Split | Revenue breakdown by Small/Medium/Large deals |
| 🗺️ Territory Performance | NA, EMEA, APAC revenue & margin comparison |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| Pandas | Data transformation & KPI calculations |
| Microsoft SQL Server | Production database (2,823 records) |
| pyodbc & SQLAlchemy | SQL Server connectivity |
| Plotly | Interactive charts & visualizations |
| Streamlit | Web dashboard & online deployment |
| ReportLab | Professional PDF report generation |
| smtplib | Automated HTML email delivery |
| schedule | Daily job scheduling |
| python-dotenv | Secure environment configuration |
| Git & GitHub | Version control & code hosting |

---

## 📁 Project Structure

```
kpi-reporting-system/
├── etl/
│   ├── extract.py          # SQLite dummy data generator
│   ├── transform.py        # KPI calculations from SQL Server
│   └── load.py             # Google Sheets sync (optional)
├── reports/
│   ├── pdf_report.py       # Multi-page PDF report generator
│   └── email_report.py     # HTML email with PDF to multiple recipients
├── dashboard/
│   └── streamlit_app.py    # 5-tab live web dashboard
├── scheduler/
│   └── cron_jobs.py        # Automated daily scheduler
├── data/
│   └── sales_data_sample.csv  # 2,823 real sales transactions
├── config/
│   └── config.yaml         # App configuration
├── main.py                 # Central CLI menu (run everything)
└── requirements.txt        # All dependencies
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/oyedonsam100/KPI-Reporting-System.git
cd KPI-Reporting-System
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```
DB_URL=mssql+pyodbc://SERVER/sales_db?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
EMAIL_SENDER=your@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_RECEIVER=recipient@gmail.com
```

### 5. Run the System
```bash
python main.py
```

### 6. Or Run the Dashboard Directly
```bash
streamlit run dashboard/streamlit_app.py
```

---

## 📧 Email Automation

The system sends professional HTML emails containing:
- Executive KPI summary table
- Clickable **Live Dashboard** button
- PDF report attachment
- Supports **multiple recipients** simultaneously

---

## 📅 Scheduler

The system runs automatically every day at 08:00 AM:
```
🚀 KPI Scheduler Started
📅 Report scheduled: Every day at 08:00 AM
✅ Email sent to all recipients
```

---

## 🔒 Security Note

All credentials are stored in `.env` and excluded via `.gitignore`.
The `config/google_credentials.json` service account file is also excluded.
No secrets are ever committed to GitHub.

---

## 📂 Data Source

**Dataset:** Sample Sales Data (Kaggle)
- **2,823 transactions** across 3 years (2003–2005)
- **19 countries** across NA, EMEA, and APAC territories
- **7 product lines** including Classic Cars, Motorcycles, Planes, Ships, and more
- **92 unique customers** with deal sizes ranging from Small to Large

---

## 👤 Author

**Samuel Oyedokun**
[GitHub](https://github.com/oyedonsam100) · [Live Dashboard](https://kpi-reporting-system-ifxehqzoojyy5g6qcsvob8.streamlit.app/)
