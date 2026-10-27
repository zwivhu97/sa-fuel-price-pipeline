from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"
OUT = ROOT / "data" / "serving" / "fuel_drivers_monthly.csv"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    target = OUT.as_posix()
    con.execute(
        f"COPY (SELECT * FROM gold.fuel_drivers_monthly ORDER BY price_month) TO '{target}' (HEADER, DELIMITER ',')"
    )
    con.close()
    print(f"exported to {OUT}")


if __name__ == "__main__":
    main()
