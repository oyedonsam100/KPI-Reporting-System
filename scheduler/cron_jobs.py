import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import schedule
import time
from datetime import datetime
from reports.email_report import send_kpi_email

def job():
    print(f"\n⏰ Scheduler triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    send_kpi_email()
    print("✅ Job complete. Waiting for next run...\n")

# ── Schedule Options (uncomment the one you want) ───────────

# Every day at 8:00 AM
schedule.every().day.at("08:00").do(job)

# Every Monday at 9:00 AM
# schedule.every().monday.at("09:00").do(job)

# Every hour
# schedule.every().hour.do(job)

# Every 30 minutes (good for testing)
# schedule.every(30).minutes.do(job)

print("🚀 KPI Report Scheduler started!")
print(f"   Next report will be sent at 08:00 daily")
print("   Press Ctrl+C to stop\n")

# ── Run immediately once for testing ────────────────────────
print("📤 Running once immediately for testing...")
job()

# ── Keep Running ─────────────────────────────────────────────
while True:
    schedule.run_pending()
    time.sleep(60)