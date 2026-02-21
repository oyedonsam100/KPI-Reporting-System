import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Create data/raw folder if it doesn't exist
os.makedirs("data/raw", exist_ok=True)

# Connect to SQLite database (creates it automatically)
conn = sqlite3.connect("data/raw/sales.db")
cursor = conn.cursor()

# ── Create Tables ──────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    product TEXT,
    region TEXT,
    salesperson TEXT,
    quantity INTEGER,
    unit_price REAL,
    revenue REAL,
    cost REAL,
    profit REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    region TEXT,
    acquisition_date TEXT,
    acquisition_cost REAL,
    is_active INTEGER
)
""")

# ── Generate Dummy Data ─────────────────────────────────────
products    = ["Product A", "Product B", "Product C", "Product D"]
regions     = ["North", "South", "East", "West"]
salespeople = ["Alice", "Bob", "Carol", "David", "Eva"]

random.seed(42)
sales_data = []
start_date = datetime(2024, 1, 1)

for i in range(500):
    date       = start_date + timedelta(days=random.randint(0, 365))
    product    = random.choice(products)
    region     = random.choice(regions)
    salesperson= random.choice(salespeople)
    quantity   = random.randint(1, 50)
    unit_price = round(random.uniform(20, 500), 2)
    revenue    = round(quantity * unit_price, 2)
    cost       = round(revenue * random.uniform(0.4, 0.7), 2)
    profit     = round(revenue - cost, 2)
    sales_data.append((date.strftime("%Y-%m-%d"), product, region,
                       salesperson, quantity, unit_price, revenue, cost, profit))

cursor.executemany("""
INSERT INTO sales (date, product, region, salesperson, quantity, unit_price, revenue, cost, profit)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", sales_data)

# ── Generate Customer Data ──────────────────────────────────
customer_data = []
for i in range(200):
    name       = f"Customer_{i+1}"
    region     = random.choice(regions)
    acq_date   = start_date + timedelta(days=random.randint(0, 365))
    acq_cost   = round(random.uniform(50, 500), 2)
    is_active  = random.choice([1, 1, 1, 0])  # 75% active
    customer_data.append((name, region, acq_date.strftime("%Y-%m-%d"), acq_cost, is_active))

cursor.executemany("""
INSERT INTO customers (name, region, acquisition_date, acquisition_cost, is_active)
VALUES (?, ?, ?, ?, ?)
""", customer_data)

conn.commit()
conn.close()
print("✅ Database created successfully at data/raw/sales.db")
print(f"   → 500 sales records added")
print(f"   → 200 customer records added")