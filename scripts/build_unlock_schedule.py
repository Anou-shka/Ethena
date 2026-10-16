"""Reconstruct the ENA vesting schedule for Core Contributors and Investors.

The model is built from Ethena's published terms and reconciled against two
independently reported figures:

  * the combined monthly unlock of 171,875,000 ENA (e.g. 5 March 2026), and
  * the accelerated investor release of 1,406,250,000 ENA on 5 October 2026.

Terms (Ethena docs): 25% of each allocation unlocks at a 1-year cliff after the
2 April 2024 TGE; the remaining 75% vests in 36 equal monthly tranches. Working
backwards from the two figures above, the monthly tranches fall on the 5th of
each month from April 2025 through March 2028.

Ecosystem Development and Foundation allocations are released at the
Foundation's discretion and are not modelled month by month here.

Output: data/ena_unlock_schedule.csv
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

TOTAL_SUPPLY = 15_000_000_000
CORE = 0.30 * TOTAL_SUPPLY
INVESTORS = 0.25 * TOTAL_SUPPLY
CLIFF_SHARE = 0.25
MONTHLY_TRANCHES = 36

TGE = date(2024, 4, 2)
CLIFF = date(2025, 4, 2)
ACCELERATION = date(2026, 10, 5)  # remaining investor tranches pulled forward

OUT = Path(__file__).resolve().parents[1] / "data" / "ena_unlock_schedule.csv"


def month_iter(start: date, n: int):
    y, m = start.year, start.month
    for _ in range(n):
        yield date(y, m, 5)
        m += 1
        if m == 13:
            y, m = y + 1, 1


def build() -> list[dict]:
    core_monthly = CORE * (1 - CLIFF_SHARE) / MONTHLY_TRANCHES
    inv_monthly = INVESTORS * (1 - CLIFF_SHARE) / MONTHLY_TRANCHES

    events: list[dict] = [
        {"date": CLIFF, "core": CORE * CLIFF_SHARE, "investors": INVESTORS * CLIFF_SHARE, "note": "1-year cliff"},
    ]
    accelerated = 0.0
    for d in month_iter(date(2025, 4, 5), MONTHLY_TRANCHES):
        if d < ACCELERATION:
            events.append({"date": d, "core": core_monthly, "investors": inv_monthly, "note": ""})
        elif d == ACCELERATION:
            accelerated += inv_monthly
            events.append({"date": d, "core": core_monthly, "investors": 0.0, "note": "investor acceleration"})
        else:
            accelerated += inv_monthly
            events.append({"date": d, "core": core_monthly, "investors": 0.0, "note": ""})

    for e in events:
        if e["date"] == ACCELERATION:
            e["investors"] = accelerated

    cum = 0.0
    rows = []
    for e in sorted(events, key=lambda e: e["date"]):
        total = e["core"] + e["investors"]
        cum += total
        rows.append(
            {
                "date": e["date"].isoformat(),
                "core_contributors": round(e["core"]),
                "investors": round(e["investors"]),
                "total": round(total),
                "pct_of_supply": round(100 * total / TOTAL_SUPPLY, 3),
                "cumulative_core_investor": round(cum),
                "note": e["note"],
            }
        )
    return rows


def main() -> None:
    rows = build()
    # Reconciliation checks against reported figures.
    by_date = {r["date"]: r for r in rows}
    assert by_date["2026-03-05"]["total"] == 171_875_000, by_date["2026-03-05"]
    assert by_date["2026-10-05"]["investors"] == 1_406_250_000, by_date["2026-10-05"]
    assert rows[-1]["cumulative_core_investor"] == round(CORE + INVESTORS)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    remaining = sum(r["total"] for r in rows if r["date"] > "2026-10-16")
    print(f"wrote {OUT.relative_to(OUT.parents[1])} ({len(rows)} events)")
    print(f"core/investor ENA still to unlock after 16 Oct 2026: {remaining/1e9:.3f}B "
          f"({100*remaining/TOTAL_SUPPLY:.1f}% of supply)")


if __name__ == "__main__":
    main()
