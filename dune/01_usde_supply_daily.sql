-- Q01 · USDe circulating supply, daily (Ethereum mainnet)
-- ---------------------------------------------------------------------------
-- Supply = cumulative mints (transfers from 0x0) minus burns (transfers to 0x0).
-- USDe on L2s/alt-L1s is bridged via LayerZero OFT: mainnet tokens are locked
-- in the adapter and mirrored elsewhere, so mainnet supply = total supply.
-- Output feeds Figure 2 (replace the approximate points in
-- data/usde_supply_snapshots.csv with this series).
-- Engine: DuneSQL (Trino)

WITH flows AS (
    SELECT
        date_trunc('day', evt_block_time) AS day,
        SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN value ELSE 0 END) / 1e18 AS minted,
        SUM(CASE WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN value ELSE 0 END) / 1e18 AS burned
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = 0x4c9EDD5852cd905f086C759E8383e09bff1E68B3 -- USDe
      AND ("from" = 0x0000000000000000000000000000000000000000
           OR "to" = 0x0000000000000000000000000000000000000000)
    GROUP BY 1
),
days AS (
    SELECT day
    FROM UNNEST(sequence(DATE '2024-02-19', CURRENT_DATE, INTERVAL '1' DAY)) AS t(day)
)
SELECT
    d.day,
    COALESCE(f.minted, 0)                                               AS minted,
    COALESCE(f.burned, 0)                                               AS burned,
    SUM(COALESCE(f.minted, 0) - COALESCE(f.burned, 0)) OVER (ORDER BY d.day) AS usde_supply,
    -- 30-day change: the contraction signal to line up against funding rates
    SUM(COALESCE(f.minted, 0) - COALESCE(f.burned, 0)) OVER (ORDER BY d.day ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
                                                                        AS net_change_30d
FROM days d
LEFT JOIN flows f ON f.day = CAST(d.day AS timestamp)
ORDER BY 1
