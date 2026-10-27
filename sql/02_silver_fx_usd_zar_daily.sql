CREATE OR REPLACE TABLE silver.fx_usd_zar_daily AS
SELECT
    CAST(rate_date AS DATE) AS rate_date,
    CAST(zar_per_usd AS DOUBLE) AS zar_per_usd
FROM bronze.fx_usd_zar;
