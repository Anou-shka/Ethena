# Dune queries

Five DuneSQL (Trino) queries behind the on-chain section of the report. Each one
is self-contained: paste it into a new query at [dune.com](https://dune.com),
run it, and add a visualisation.

| # | Query | Answers | Suggested chart |
|---|-------|---------|-----------------|
| 01 | [`01_usde_supply_daily.sql`](01_usde_supply_daily.sql) | How has USDe supply grown and contracted? | Area: `usde_supply`; bar: `net_change_30d` |
| 02 | [`02_susde_staking_ratio.sql`](02_susde_staking_ratio.sql) | What share of USDe is staked for yield? | Line: `staking_ratio` |
| 03 | [`03_holder_concentration.sql`](03_holder_concentration.sql) | How concentrated are ENA and USDe? (parameter `token`) | Counter / table |
| 04 | [`04_ena_exchange_flows_unlocks.sql`](04_ena_exchange_flows_unlocks.sql) | Does ENA move to exchanges after unlocks? | Bar: avg `net_inflow` by `days_from_unlock` |
| 05 | [`05_usde_mint_redeem_weekly.sql`](05_usde_mint_redeem_weekly.sql) | How much gross churn sits under net supply? | Stacked bar: `minted` vs `-redeemed` |

## Contract addresses (Ethereum mainnet)

| Contract | Address |
|----------|---------|
| USDe | [`0x4c9EDD5852cd905f086C759E8383e09bff1E68B3`](https://etherscan.io/token/0x4c9EDD5852cd905f086C759E8383e09bff1E68B3) |
| sUSDe (staked USDe, ERC-4626) | [`0x9D39A5DE30e57443BfF2A8307A4256c8797A3497`](https://etherscan.io/token/0x9D39A5DE30e57443BfF2A8307A4256c8797A3497) |
| ENA | [`0x57e114B691Db790C35207b2e685D4A43181e6061`](https://etherscan.io/token/0x57e114B691Db790C35207b2e685D4A43181e6061) |

Always confirm addresses against Ethena's official documentation
(`docs.ethena.fi` → Key Addresses) before relying on results.

## Design notes

- **Supply from transfer events, not `totalSupply()` calls.** Mints are transfers
  from `0x0`, burns are transfers to `0x0`. This reproduces supply at any date
  using only decoded event tables.
- **Mainnet = total supply.** USDe on other chains uses a LayerZero OFT adapter
  that locks mainnet tokens, so mainnet supply already counts bridged USDe.
- **Contracts vs people.** The largest "holders" of USDe are protocols (the sUSDe
  vault, Pendle, Aave, bridges). Q03 splits concentration into all addresses vs
  externally owned accounts, because a top-10 share of 80% means something
  very different if eight of the ten are DeFi contracts.
- **CEX labels are a lower bound.** Q04 depends on Spellbook's `cex.addresses`,
  which misses unlabelled deposit wallets. Inflows are under-counted, never
  over-counted.

## Status

These queries were written for DuneSQL and reviewed against the Spellbook schema
(`erc20_ethereum.evt_Transfer`, `ethereum.creation_traces`, `cex.addresses`).
They have not yet been run against Dune. When you publish them, add the query
links to the table above and replace the approximate points in
`data/usde_supply_snapshots.csv` with the Q01 output.
