-- FRED marks holidays with ".", which becomes NULL here. Any other bad value fails loudly.
CREATE OR REPLACE TABLE silver.brent_daily AS
SELECT
    CAST(obs_date AS DATE) AS obs_date,
    CASE WHEN TRIM(price_raw) IN ('', '.') THEN NULL ELSE CAST(price_raw AS DOUBLE) END AS brent_usd
FROM bronze.brent_usd;
