-- gold: fuel price per month next to the PREVIOUS month's average oil price and exchange rate,
-- because each month's price reflects the preceding review period.
CREATE OR REPLACE TABLE gold.fuel_drivers_monthly AS
WITH fx AS (
    SELECT DATE_TRUNC('month', rate_date) AS month_start, AVG(zar_per_usd) AS avg_zar_per_usd
    FROM silver.fx_usd_zar_daily
    GROUP BY 1
),
brent AS (
    SELECT DATE_TRUNC('month', obs_date) AS month_start, AVG(brent_usd) AS avg_brent_usd
    FROM silver.brent_daily
    WHERE brent_usd IS NOT NULL
    GROUP BY 1
)
SELECT
    f.price_month,
    f.pump_price_rands,
    f.pump_price_rands - LAG(f.pump_price_rands) OVER (ORDER BY f.price_month) AS pump_price_change_rands,
    f.basic_fuel_price_cents,
    f.fuel_tax_cents,
    f.slate_levy_cents,
    ROUND(fx.avg_zar_per_usd, 4) AS prev_month_avg_zar_per_usd,
    ROUND(brent.avg_brent_usd, 2) AS prev_month_avg_brent_usd
FROM silver.fuel_price_monthly AS f
LEFT JOIN fx ON fx.month_start = CAST(f.price_month - INTERVAL 1 MONTH AS DATE)
LEFT JOIN brent ON brent.month_start = CAST(f.price_month - INTERVAL 1 MONTH AS DATE);
