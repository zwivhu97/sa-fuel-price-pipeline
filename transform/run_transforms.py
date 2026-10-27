from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
DB_PATH = ROOT / "data" / "warehouse.duckdb"


def run_all(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute("CREATE SCHEMA IF NOT EXISTS gold")
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        con.execute(sql_file.read_text(encoding="utf-8"))
        print(f"ran {sql_file.name}")


def main():
    con = duckdb.connect(str(DB_PATH))
    run_all(con)
    con.close()


if __name__ == "__main__":
    main()
