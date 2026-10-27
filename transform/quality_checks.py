import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"

# Each check returns the number of bad rows. Zero means pass.
CHECKS = {
    "fuel: price_month is unique": "SELECT COUNT(*) - COUNT(DISTINCT price_month) FROM silver.fuel_price_monthly",
    "fuel: pump price is between R3 and R60": "SELECT COUNT(*) FROM silver.fuel_price_monthly WHERE pump_price_rands NOT BETWEEN 3 AND 60",
    "fuel: no missing months between first and last": "SELECT DATEDIFF('month', MIN(price_month), MAX(price_month)) + 1 - COUNT(*) FROM silver.fuel_price_monthly",
    "fx: rate_date is unique": "SELECT COUNT(*) - COUNT(DISTINCT rate_date) FROM silver.fx_usd_zar_daily",
    "fx: ZAR per USD is between 5 and 40": "SELECT COUNT(*) FROM silver.fx_usd_zar_daily WHERE zar_per_usd NOT BETWEEN 5 AND 40",
    "brent: obs_date is unique": "SELECT COUNT(*) - COUNT(DISTINCT obs_date) FROM silver.brent_daily",
    "brent: price is between 5 and 200 when present": "SELECT COUNT(*) FROM silver.brent_daily WHERE brent_usd IS NOT NULL AND brent_usd NOT BETWEEN 5 AND 200",
    "gold: FX and Brent present for every month from Feb 2020": "SELECT COUNT(*) FROM gold.fuel_drivers_monthly WHERE price_month >= DATE '2020-02-01' AND (prev_month_avg_zar_per_usd IS NULL OR prev_month_avg_brent_usd IS NULL)",
    "gold: one row per fuel month (no join fan-out)": "SELECT ABS((SELECT COUNT(*) FROM gold.fuel_drivers_monthly) - (SELECT COUNT(*) FROM silver.fuel_price_monthly))",
}


def run_checks(con):
    failures = 0
    for name, sql in CHECKS.items():
        bad_rows = con.execute(sql).fetchone()[0]
        status = "PASS" if bad_rows == 0 else "FAIL"
        print(f"{status}  {name} ({bad_rows} bad rows)")
        if bad_rows:
            failures += 1
    return failures


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    failures = run_checks(con)
    con.close()
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()


