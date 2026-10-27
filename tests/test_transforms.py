from load_bronze import connect, load_brent
from run_transforms import run_all


def build_fuel(con):
    con.execute(
        """
        CREATE OR REPLACE TABLE bronze.fuel_petrol95_inland AS
        SELECT * FROM (VALUES
            ('269', '2006-01-01 ', '5.49', '549', '', '116', '15', '', ''),
            ('283', '2006-02-01 ', '5.63', '563', '', '116', '15', '', '')
        ) AS t(BFP, "date", pump_price_rands, pump_price_cents, crude_oil_usd, fuel_tax, slate_levy, exchange_rate, _source_file)
        """
    )


def test_fuel_dates_are_trimmed_and_blanks_become_null():
    con = connect(":memory:")
    build_fuel(con)
    run_all(con)
    row = con.execute(
        "SELECT price_month, pump_price_rands, dept_crude_oil_usd FROM silver.fuel_price_monthly ORDER BY price_month LIMIT 1"
    ).fetchone()
    assert str(row[0]) == "2006-01-01"
    assert row[1] == 5.49
    assert row[2] is None


def test_brent_missing_marker_becomes_null(tmp_path):
    raw = tmp_path / "brent_2026-10-16.csv"
    raw.write_text("observation_date,DCOILBRENTEU\n2026-10-12,95.10\n2026-10-13,.\n", encoding="utf-8")
    con = connect(":memory:")
    build_fuel(con)
    load_brent(con, raw)
    run_all(con)
    rows = con.execute("SELECT obs_date, brent_usd FROM silver.brent_daily ORDER BY obs_date").fetchall()
    assert rows[0][1] == 95.10
    assert rows[1][1] is None


def test_gold_has_one_row_per_fuel_month():
    con = connect(":memory:")
    build_fuel(con)
    run_all(con)
    count = con.execute("SELECT COUNT(*) FROM gold.fuel_drivers_monthly").fetchone()[0]
    assert count == 2
