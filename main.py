import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime

def print_banner():
    print("=" * 50)
    print("   📊 KPI REPORTING SYSTEM")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

def show_menu():
    print("\nWhat would you like to do?\n")
    print("  [1] 📊 View KPI Summary in Terminal")
    print("  [2] 📄 Generate PDF Report")
    print("  [3] 📧 Send KPI Email Report")
    print("  [4] 🌐 Launch Live Dashboard")
    print("  [5] ⏰ Start Automated Scheduler")
    print("  [6] 🚪 Exit")
    print()

def run():
    print_banner()

    while True:
        show_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            print("\n📊 Loading KPI Summary...\n")
            from etl.transform import (
                get_total_revenue, get_profit_metrics, get_cac,
                get_customer_status, get_revenue_by_product,
                get_revenue_by_region, get_top_salespeople,
                get_monthly_revenue
            )
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
            print("\n🏆 Top Salespeople:")
            print(get_top_salespeople().to_string(index=False))
            print("\n📅 Monthly Revenue Trend:")
            print(get_monthly_revenue().to_string(index=False))

        elif choice == "2":
            print("\n📄 Generating PDF Report...")
            from reports.pdf_report import generate_pdf
            generate_pdf()

        elif choice == "3":
            print("\n📧 Sending KPI Email Report...")
            from reports.email_report import send_kpi_email
            send_kpi_email()

        elif choice == "4":
            print("\n🌐 Launching Dashboard...")
            print("Open your browser and go to: http://127.0.0.1:8050")
            print("Press Ctrl+C to stop the dashboard and return to menu\n")
            from dashboard.app import app
            app.run(debug=False)

        elif choice == "5":
            print("\n⏰ Starting Automated Scheduler...")
            print("Press Ctrl+C to stop\n")
            import schedule
            import time
            from reports.email_report import send_kpi_email

            def job():
                print(f"\n🕐 Running scheduled report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                send_kpi_email()
                print("✅ Job complete. Waiting for next run...\n")

            schedule.every().day.at("08:00").do(job)
            print("📅 Scheduler running — report will send daily at 08:00 AM")
            print("─" * 45)

            while True:
                schedule.run_pending()
                time.sleep(60)

        elif choice == "6":
            print("\n👋 Goodbye! KPI Reporting System shutting down.\n")
            break

        else:
            print("\n⚠️  Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    run()