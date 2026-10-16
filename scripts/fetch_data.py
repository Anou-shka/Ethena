"""Refresh market data from public APIs (no keys required).

    python scripts/fetch_data.py            # writes data/raw/*.csv

Pulls:
  * USDe circulating supply history          - DefiLlama stablecoins API
  * ENA / USDe price, market cap, supply     - CoinGecko public API
  * BTC and ETH perpetual funding history    - Binance USD-M futures API

The report's figures use the curated, source-annotated CSVs in data/. Run this
script to check those numbers against live data, or to extend the funding-rate
comparison in Section 4.
"""

from __future__ import annotations

import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
TIMEOUT = 30
HEADERS = {"User-Agent": "ethena-dd-report/1.0"}


def get(url: str, **params):
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 429:
                time.sleep(2 ** (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as exc:
            if attempt == 3:
                raise
            print(f"  retry {attempt + 1} after {exc}", file=sys.stderr)
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}")


def write(name: str, rows: list[dict]) -> None:
    if not rows:
        print(f"  no rows for {name}")
        return
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / name
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote data/raw/{name} ({len(rows)} rows)")


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()


def usde_supply() -> None:
    print("DefiLlama: USDe supply")
    listing = get("https://stablecoins.llama.fi/stablecoins")["peggedAssets"]
    usde = next(a for a in listing if a["symbol"] == "USDe")
    chart = get("https://stablecoins.llama.fi/stablecoincharts/all", stablecoin=usde["id"])
    write(
        "usde_supply_defillama.csv",
        [
            {"date": iso(int(p["date"])), "usde_supply_usd": p.get("totalCirculatingUSD", {}).get("peggedUSD")}
            for p in chart
        ],
    )


def coingecko() -> None:
    print("CoinGecko: ENA and USDe market data")
    data = get(
        "https://api.coingecko.com/api/v3/coins/markets",
        vs_currency="usd",
        ids="ethena,ethena-usde,ethena-staked-usde",
    )
    write(
        "coingecko_snapshot.csv",
        [
            {
                "id": c["id"],
                "price": c["current_price"],
                "market_cap": c["market_cap"],
                "circulating_supply": c["circulating_supply"],
                "total_supply": c["total_supply"],
                "volume_24h": c["total_volume"],
                "as_of": c["last_updated"],
            }
            for c in data
        ],
    )
    hist = get("https://api.coingecko.com/api/v3/coins/ethena/market_chart", vs_currency="usd", days=365)
    write("ena_price_365d.csv", [{"date": iso(t / 1000), "price": p} for t, p in hist["prices"]])


def funding(symbol: str, start: str = "2024-02-01") -> None:
    print(f"Binance: {symbol} funding history")
    start_ms = int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp() * 1000)
    rows: list[dict] = []
    while True:
        batch = get("https://fapi.binance.com/fapi/v1/fundingRate", symbol=symbol, startTime=start_ms, limit=1000)
        if not batch:
            break
        for b in batch:
            rate = float(b["fundingRate"])
            rows.append(
                {
                    "time": datetime.fromtimestamp(b["fundingTime"] / 1000, tz=timezone.utc).isoformat(),
                    "funding_rate_8h": rate,
                    "annualised_pct": round(rate * 3 * 365 * 100, 3),
                }
            )
        start_ms = batch[-1]["fundingTime"] + 1
        if len(batch) < 1000:
            break
        time.sleep(0.3)
    write(f"funding_{symbol.lower()}.csv", rows)


def main() -> None:
    steps = [usde_supply, coingecko, lambda: funding("BTCUSDT"), lambda: funding("ETHUSDT")]
    failed = 0
    for step in steps:
        try:
            step()
        except Exception as exc:  # keep going so one dead API doesn't block the rest
            failed += 1
            print(f"  FAILED: {exc}", file=sys.stderr)
    sys.exit(1 if failed == len(steps) else 0)


if __name__ == "__main__":
    main()
