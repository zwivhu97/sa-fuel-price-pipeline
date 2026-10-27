import json

from load_bronze import connect, load_brent, load_fx, table_count


def write_fx(path, rates):
    payload = {"rates": {day: {"ZAR": rate} for day, rate in rates.items()}}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_fx_load_is_idempotent(tmp_path):
    raw = tmp_path / "usd_zar_2026-10-16.json"
    write_fx(raw, {"2026-10-14": 17.3, "2026-10-15": 17.4})
    con = connect(":memory:")
    load_fx(con, raw)
    load_fx(con, raw)
    assert table_count(con, "fx_usd_zar") == 2


def test_fx_reload_updates_a_revised_rate(tmp_path):
    first = tmp_path / "usd_zar_2026-10-16.json"
    second = tmp_path / "usd_zar_2026-10-17.json"
    write_fx(first, {"2026-10-14": 17.3})
    write_fx(second, {"2026-10-14": 17.5})
    con = connect(":memory:")
    load_fx(con, first)
    load_fx(con, second)
    assert table_count(con, "fx_usd_zar") == 1
    rate = con.execute(
        "SELECT zar_per_usd FROM bronze.fx_usd_zar WHERE rate_date = '2026-10-14'"
    ).fetchone()[0]
    assert rate == "17.5"


def test_brent_load_keeps_missing_marker_untouched(tmp_path):
    raw = tmp_path / "brent_2026-10-16.csv"
    raw.write_text("observation_date,DCOILBRENTEU\n2026-10-12,95.10\n2026-10-13,.\n", encoding="utf-8")
    con = connect(":memory:")
    load_brent(con, raw)
    load_brent(con, raw)
    assert table_count(con, "brent_usd") == 2
    value = con.execute(
        "SELECT price_raw FROM bronze.brent_usd WHERE obs_date = '2026-10-13'"
    ).fetchone()[0]
    assert value == "."
