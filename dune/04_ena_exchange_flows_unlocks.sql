-- Q04 · ENA net flows to centralised exchanges around unlock dates
-- ---------------------------------------------------------------------------
-- Tests the "unlock -> sell" hypothesis: does ENA move onto exchanges in the
-- days after each scheduled unlock? Positive net_inflow = ENA moving onto
-- exchanges (potential sell pressure).
-- Exchange wallets come from Spellbook's cex.addresses label set, which is
-- incomplete; treat results as a lower bound.

WITH unlocks AS (
    -- 2 Apr 2025 cliff, then monthly tranches on the 5th; 5 Oct 2026 is the
    -- accelerated investor release (see scripts/build_unlock_schedule.py)
    SELECT CAST(d AS date) AS unlock_date
    FROM UNNEST(ARRAY[DATE '2025-04-02']) AS t(d)
    UNION ALL
    SELECT CAST(d AS date)
    FROM UNNEST(sequence(DATE '2025-04-05', DATE '2026-10-05', INTERVAL '1' MONTH)) AS t(d)
),
cex AS (
    SELECT DISTINCT address, cex_name
    FROM cex.addresses
    WHERE blockchain = 'ethereum'
),
ena_daily AS (
    SELECT
        CAST(date_trunc('day', t.evt_block_time) AS date) AS day,
        SUM(CASE WHEN cto.address IS NOT NULL AND cfrom.address IS NULL THEN t.value ELSE 0 END) / 1e18 AS to_cex,
        SUM(CASE WHEN cfrom.address IS NOT NULL AND cto.address IS NULL THEN t.value ELSE 0 END) / 1e18 AS from_cex
    FROM erc20_ethereum.evt_Transfer t
    LEFT JOIN cex cto   ON cto.address   = t."to"
    LEFT JOIN cex cfrom ON cfrom.address = t."from"
    WHERE t.contract_address = 0x57e114B691Db790C35207b2e685D4A43181e6061 -- ENA
      AND t.evt_block_time >= TIMESTAMP '2025-03-01'
    GROUP BY 1
)
SELECT
    u.unlock_date,
    date_diff('day', u.unlock_date, e.day) AS days_from_unlock,
    e.to_cex,
    e.from_cex,
    e.to_cex - e.from_cex                  AS net_inflow
FROM unlocks u
JOIN ena_daily e
  ON e.day BETWEEN u.unlock_date - INTERVAL '7' DAY AND u.unlock_date + INTERVAL '7' DAY
ORDER BY u.unlock_date, days_from_unlock
