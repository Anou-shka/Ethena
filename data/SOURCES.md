# Data provenance

Every curated CSV in this folder carries a `source` column, and the time series
also carry a `confidence` column:

| confidence | meaning |
|---|---|
| `high` | Taken from a primary source (Ethena governance, docs) or from two or more consistent secondary sources |
| `medium` | One credible source, or derived from one |
| `low` | Approximate or conflicting. Shown with hollow markers on the charts and flagged in the report |

| File | What it holds | Main sources |
|---|---|---|
| `usde_supply_snapshots.csv` | USDe supply at key dates, Feb 2024 to Oct 2026 | Ethena governance updates, 21Shares, Yahoo Finance/CoinGecko, Cointelegraph/CoinMarketCap, stablecoininsider |
| `ena_allocation.csv` | ENA genesis allocation and vesting terms | Ethena documentation |
| `ena_unlock_schedule.csv` | **Generated** by `scripts/build_unlock_schedule.py` | Model reconciled to Tokenomist |
| `key_metrics.csv` | Headline figures used in the report | See row-level `source` |
| `stablecoin_comparison.csv` | Competitive landscape | Stablecoin Beat, CoinGecko, Sky governance, Ethena governance |
| `risk_register.csv` | Likelihood and impact scores | Author judgement (rationale in report Section 4) |

`data/raw/` (git-ignored) is written by `scripts/fetch_data.py` from the
DefiLlama, CoinGecko and Binance public APIs.
