from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "data" / "serving" / "fuel_drivers_monthly.csv"

st.set_page_config(page_title="South African petrol price drivers", layout="wide")
st.title("South African petrol price (inland 95)")
st.caption(
    "Sources: Department of Mineral and Petroleum Resources via Data Desk; "
    "USD/ZAR from the ECB via Frankfurter; Brent from the EIA via FRED."
)


@st.cache_data
def load():
    df = pd.read_csv(DATA, parse_dates=["price_month"])
    df["brent_zar_per_barrel"] = df["prev_month_avg_brent_usd"] * df["prev_month_avg_zar_per_usd"]
    return df.set_index("price_month")


df = load()
latest = df.iloc[-1]
previous = df.iloc[-2]

col1, col2, col3 = st.columns(3)
col1.metric(
    "Latest price (R per litre)",
    f"{latest['pump_price_rands']:.2f}",
    f"{latest['pump_price_rands'] - previous['pump_price_rands']:+.2f}",
)
col2.metric("Month", latest.name.strftime("%B %Y"))
col3.metric("Months of data", len(df))

st.subheader("Pump price since 2006")
st.line_chart(df["pump_price_rands"])

st.subheader("Price components (cents per litre)")
st.area_chart(df[["basic_fuel_price_cents", "fuel_tax_cents", "slate_levy_cents"]])

st.subheader("What drives the price? (2020 onwards)")
recent = df.loc["2020-02-01":]
left, right = st.columns(2)
left.caption("Previous month average USD/ZAR")
left.line_chart(recent["prev_month_avg_zar_per_usd"])
right.caption("Previous month average Brent (USD per barrel)")
right.line_chart(recent["prev_month_avg_brent_usd"])

changes = pd.DataFrame(
    {
        "pump": recent["pump_price_rands"].pct_change(),
        "brent_rand": recent["brent_zar_per_barrel"].pct_change(),
    }
).dropna()
corr = changes["pump"].corr(changes["brent_rand"])
st.metric("Correlation: monthly % change in pump price vs Brent in rand", f"{corr:.2f}")
st.caption(
    "Brent is a proxy: the official formula uses refined product prices, not crude. "
    "Correlation is not causation."
)
