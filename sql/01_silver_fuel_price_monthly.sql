-- silver: one row per month, typed and trimmed. Blank optional fields become NULL.
CREATE OR REPLACE TABLE silver.fuel_price_monthly AS
SELECT
    CAST(TRIM("date") AS DATE) AS effective_date,
    CAST(DATE_TRUNC('month', CAST(TRIM("date") AS DATE)) AS DATE) AS price_month,
    CAST(TRIM(pump_price_rands) AS DOUBLE) AS pump_price_rands,
    TRY_CAST(NULLIF(TRIM(pump_price_cents), '') AS DOUBLE) AS pump_price_cents,
    TRY_CAST(NULLIF(TRIM(BFP), '') AS DOUBLE) AS basic_fuel_price_cents,
    TRY_CAST(NULLIF(TRIM(fuel_tax), '') AS DOUBLE) AS fuel_tax_cents,
    TRY_CAST(NULLIF(TRIM(slate_levy), '') AS DOUBLE) AS slate_levy_cents,
    TRY_CAST(NULLIF(TRIM(crude_oil_usd), '') AS DOUBLE) AS dept_crude_oil_usd,
    TRY_CAST(NULLIF(TRIM(exchange_rate), '') AS DOUBLE) AS dept_exchange_rate
FROM bronze.fuel_petrol95_inland
WHERE TRIM("date") <> '';
