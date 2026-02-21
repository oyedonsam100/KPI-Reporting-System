import pandas as pd
import pyodbc
import numpy as np

# ── Load CSV ────────────────────────────────────────────────
df = pd.read_csv(
    r"C:\Users\USER\Desktop\Data Analysis Tutorial\kpi-reporting-system\data\sales_data_sample.csv",
    encoding="latin1",
    dtype=str
)

df.columns = df.columns.str.strip()
df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

# ── Force ALL NaN/None/empty to Python None ─────────────────
def clean(val):
    if val is None:
        return None
    if isinstance(val, float) and np.isnan(val):
        return None
    s = str(val).strip()
    if s.lower() in ("nan", "none", "null", ""):
        return None
    return s

for col in df.columns:
    df[col] = df[col].apply(clean)

def to_int(val):
    try:
        return int(float(val)) if val is not None else None
    except:
        return None

def to_float(val):
    try:
        return float(val) if val is not None else None
    except:
        return None

print(f"✅ CSV loaded and cleaned: {len(df)} rows")

# ── Connect ──────────────────────────────────────────────────
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-FHDJ2FC\\SQLEXPRESS;"
    "DATABASE=sales_db;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

cursor.execute("DELETE FROM sales")
conn.commit()
print("🗑️  Cleared existing table data")

# ── Insert Rows ──────────────────────────────────────────────
inserted  = 0
errors    = 0
error_log = []

for idx, row in df.iterrows():
    try:
        cursor.execute("""
            INSERT INTO sales (
                ORDERNUMBER, QUANTITYORDERED, PRICEEACH, ORDERLINENUMBER,
                SALES, ORDERDATE, STATUS, QTR_ID, MONTH_ID, YEAR_ID,
                PRODUCTLINE, MSRP, PRODUCTCODE, CUSTOMERNAME, PHONE,
                ADDRESSLINE1, ADDRESSLINE2, CITY, STATE, POSTALCODE,
                COUNTRY, TERRITORY, CONTACTLASTNAME, CONTACTFIRSTNAME, DEALSIZE
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            to_int(row["ORDERNUMBER"]),
            to_int(row["QUANTITYORDERED"]),
            to_float(row["PRICEEACH"]),
            to_int(row["ORDERLINENUMBER"]),
            to_float(row["SALES"]),
            row["ORDERDATE"],
            row["STATUS"],
            to_int(row["QTR_ID"]),
            to_int(row["MONTH_ID"]),
            to_int(row["YEAR_ID"]),
            row["PRODUCTLINE"],
            to_int(row["MSRP"]),
            row["PRODUCTCODE"],
            row["CUSTOMERNAME"],
            row["PHONE"],
            row["ADDRESSLINE1"],
            row["ADDRESSLINE2"],
            row["CITY"],
            row["STATE"],
            row["POSTALCODE"],
            row["COUNTRY"],
            row["TERRITORY"],
            row["CONTACTLASTNAME"],
            row["CONTACTFIRSTNAME"],
            row["DEALSIZE"]
        )
        inserted += 1

        if inserted % 200 == 0:
            conn.commit()
            print(f"   ⏳ {inserted} rows inserted...")

    except Exception as e:
        errors += 1
        if errors <= 3:
            error_log.append(
                f"\nRow {idx}:\n"
                f"  POSTALCODE={repr(row['POSTALCODE'])}\n"
                f"  STATE={repr(row['STATE'])}\n"
                f"  TERRITORY={repr(row['TERRITORY'])}\n"
                f"  DEALSIZE={repr(row['DEALSIZE'])}\n"
                f"  ERROR: {str(e)}\n"
            )

conn.commit()
conn.close()

print(f"\n✅ Import complete!")
print(f"   → {inserted} rows inserted successfully")
print(f"   → {errors} rows skipped due to errors")

if error_log:
    print("\n⚠️  Sample errors:")
    for err in error_log:
        print(err)