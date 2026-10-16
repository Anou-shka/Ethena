-- Q02 · Share of USDe staked in sUSDe, daily
-- ---------------------------------------------------------------------------
-- Staked USDe = USDe balance held by the sUSDe ERC-4626 vault.
-- Note: the vault balance includes rewards that are still vesting (8-hour
-- linear vest) and EXCLUDES USDe sitting in the cooldown silo. Both effects
-- are small relative to the totals, and are called out in the report.
-- A low ratio means fewer holders share the protocol yield, which mechanically
-- raises the sUSDe APY (Figure 6).

WITH usde AS (
    SELECT evt_block_time, "from", "to", value / 1e18 AS amt
    FROM erc20_ethereum.evt_Transfer
    WHERE contract_address = 0x4c9EDD5852cd905f086C759E8383e09bff1E68B3 -- USDe
),
daily AS (
    SELECT
        date_trunc('day', evt_block_time) AS day,
        SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amt
                 WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN -amt ELSE 0 END) AS supply_delta,
        SUM(CASE WHEN "to"   = 0x9D39A5DE30e57443BfF2A8307A4256c8797A3497 THEN amt
                 WHEN "from" = 0x9D39A5DE30e57443BfF2A8307A4256c8797A3497 THEN -amt ELSE 0 END) AS staked_delta
    FROM usde
    GROUP BY 1
),
running AS (
    SELECT
        day,
        SUM(supply_delta) OVER (ORDER BY day) AS usde_supply,
        SUM(staked_delta) OVER (ORDER BY day) AS usde_in_susde
    FROM daily
)
SELECT
    day,
    usde_supply,
    usde_in_susde,
    usde_in_susde / NULLIF(usde_supply, 0) AS staking_ratio
FROM running
WHERE day >= DATE '2024-02-19'
ORDER BY day
