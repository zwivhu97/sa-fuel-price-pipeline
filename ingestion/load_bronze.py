import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "warehouse.duckdb"
PARQUET_DIR = ROOT / "data" / "bronze"


def latest_file(source, pattern):
    files = sorted((RAW / source).glob(pattern))
    if not files:
        raise FileNotFoundError(f"no raw files in data/raw/{source} matching {pattern}")
    return files[-1]


def connect(db_path=DB_PATH):
    if str(db_path) != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS bronze.fx_usd_zar (
            rate_date VARCHAR PRIMARY KEY,
            zar_per_usd VARCHAR NOT NULL,
            _source_file VARCHAR,
            _loaded_at TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS bronze.brent_usd (
            obs_date VARCHAR PRIMARY KEY,
            price_raw VARCHAR,
            _source_file VARCHAR,
            _loaded_at TIMESTAMP
        )
        """
    )
    return con


def load_fx(con, path):
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    loaded_at = datetime.now(timezone.utc)
    rows = [
        (day, str(values["ZAR"]), path.name, loaded_at)
        for day, values in payload["rates"].items()
    ]
    con.executemany("INSERT OR REPLACE INTO bronze.fx_usd_zar VALUES (?, ?, ?, ?)", rows)
    return len(rows)


def load_brent(con, path):
    loaded_at = datetime.now(timezone.utc)
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # header: read columns by position, as FRED has renamed them before
        rows = [(r[0], r[1], path.name, loaded_at) for r in reader if len(r) >= 2]
    con.executemany("INSERT OR REPLACE INTO bronze.brent_usd VALUES (?, ?, ?, ?)", rows)
    return len(rows)


def load_fuel(con, path):
    """Snapshot file: replace the whole table each run."""
    sql_path = path.as_posix().replace("'", "''")
    con.execute(
        f"""
        CREATE OR REPLACE TABLE bronze.fuel_petrol95_inland AS
        SELECT * EXCLUDE (filename),
               parse_filename(filename) AS _source_file,
               now() AS _loaded_at
        FROM read_csv('{sql_path}', header = true, all_varchar = true, filename = true)
        """
    )
    return con.execute("SELECT COUNT(*) FROM bronze.fuel_petrol95_inland").fetchone()[0]


def export_parquet(con):
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    for table in ("fx_usd_zar", "brent_usd", "fuel_petrol95_inland"):
        target = (PARQUET_DIR / f"{table}.parquet").as_posix()
        con.execute(f"COPY bronze.{table} TO '{target}' (FORMAT parquet)")


def table_count(con, table):
    return con.execute(f"SELECT COUNT(*) FROM bronze.{table}").fetchone()[0]


def main():
    con = connect()
    load_fx(con, latest_file("fx", "usd_zar_*.json"))
    load_brent(con, latest_file("brent", "brent_*.csv"))
    load_fuel(con, latest_file("fuel", "petrol95_inland_outlier_*.csv"))
    export_parquet(con)
    for table in ("fx_usd_zar", "brent_usd", "fuel_petrol95_inland"):
        print(f"bronze.{table}: {table_count(con, table)} rows")
    con.close()


if __name__ == "__main__":
    main()