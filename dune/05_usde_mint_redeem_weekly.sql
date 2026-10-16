-- Q05 · USDe gross mints vs redemptions, weekly
-- ---------------------------------------------------------------------------
-- Net supply hides the churn underneath. A week with large gross redemptions
-- is a stress test of the redemption path: the October 2025 drawdown
-- ($14.8B -> $6.4B) was absorbed through this path without an on-chain depeg.
-- Pair with weekly average BTC/ETH funding (scripts/fetch_data.py) to show the
-- funding -> redemptions link.

SELECT
    date_trunc('week', evt_block_time)                                                         AS week,
    SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN value END) / 1e18    AS minted,
    SUM(CASE WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN value END) / 1e18    AS redeemed,
    (COALESCE(SUM(CASE WHEN "from" = 0x0000000000000000000000000000000000000000 THEN value END), 0)
   - COALESCE(SUM(CASE WHEN "to"   = 0x0000000000000000000000000000000000000000 THEN value END), 0)) / 1e18 AS net
FROM erc20_ethereum.evt_Transfer
WHERE contract_address = 0x4c9EDD5852cd905f086C759E8383e09bff1E68B3 -- USDe
  AND ("from" = 0x0000000000000000000000000000000000000000
       OR "to" = 0x0000000000000000000000000000000000000000)
GROUP BY 1
ORDER BY 1
