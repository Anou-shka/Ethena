-- Q03 · Holder concentration: top-10 / top-100 share for ENA and USDe
-- ---------------------------------------------------------------------------
-- Raw top-holder shares overstate concentration because the largest "holders"
-- are smart contracts (the sUSDe vault, Pendle, Aave, bridges, vesting
-- contracts). The query reports both views:
--   * all addresses, and
--   * externally owned accounts only (addresses with no creation trace).
-- Parameter: {{token}} = 'ENA' or 'USDe'

WITH token AS (
    SELECT CASE '{{token}}'
             WHEN 'ENA'  THEN 0x57e114B691Db790C35207b2e685D4A43181e6061
             WHEN 'USDe' THEN 0x4c9EDD5852cd905f086C759E8383e09bff1E68B3
           END AS addr
),
ledger AS (
    SELECT "to" AS holder, CAST(value AS double) / 1e18 AS amt
    FROM erc20_ethereum.evt_Transfer, token
    WHERE contract_address = token.addr
    UNION ALL
    SELECT "from" AS holder, -CAST(value AS double) / 1e18 AS amt
    FROM erc20_ethereum.evt_Transfer, token
    WHERE contract_address = token.addr
),
balances AS (
    SELECT holder, SUM(amt) AS balance
    FROM ledger
    WHERE holder <> 0x0000000000000000000000000000000000000000
    GROUP BY 1
    HAVING SUM(amt) > 1e-6
),
tagged AS (
    SELECT
        b.holder,
        b.balance,
        (c.address IS NOT NULL) AS is_contract
    FROM balances b
    LEFT JOIN ethereum.creation_traces c ON c.address = b.holder
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY balance DESC)                             AS rank_all,
        ROW_NUMBER() OVER (PARTITION BY is_contract ORDER BY balance DESC)     AS rank_in_class
    FROM tagged
)
SELECT
    '{{token}}'                                                                  AS token,
    COUNT(*)                                                                     AS holders,
    SUM(balance)                                                                 AS supply,
    SUM(CASE WHEN rank_all <= 10  THEN balance END) / SUM(balance)              AS top10_share_all,
    SUM(CASE WHEN rank_all <= 100 THEN balance END) / SUM(balance)              AS top100_share_all,
    SUM(CASE WHEN NOT is_contract AND rank_in_class <= 10  THEN balance END)
        / SUM(CASE WHEN NOT is_contract THEN balance END)                        AS top10_share_eoa,
    SUM(CASE WHEN NOT is_contract AND rank_in_class <= 100 THEN balance END)
        / SUM(CASE WHEN NOT is_contract THEN balance END)                        AS top100_share_eoa,
    SUM(CASE WHEN is_contract THEN balance END) / SUM(balance)                   AS share_in_contracts
FROM ranked
