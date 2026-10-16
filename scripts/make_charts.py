"""Render every figure used in the report from the CSVs in data/.

    python scripts/make_charts.py          # writes charts/*.png

All numbers come from data/*.csv (see data/SOURCES.md for provenance). The two
model figures (yield sensitivity, reserve-fund runway) are calculations whose
assumptions are printed on the chart itself.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "charts"

# ---- design tokens (validated categorical palette, light mode) -------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
BLUE_LIGHT = "#cde2fb"
STATUS = {"good": "#0ca30c", "warning": "#fab219", "serious": "#ec835a", "critical": "#d03b3b"}

for f in font_manager.findSystemFonts():
    if "Inter" in Path(f).name:
        font_manager.fontManager.addfont(f)
FAMILY = "Inter" if any("Inter" in f.name for f in font_manager.fontManager.ttflist) else "DejaVu Sans"

plt.rcParams.update(
    {
        "font.family": FAMILY,
        "font.size": 10,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titleweight": "semibold",
        "axes.titlesize": 13,
        "axes.titlelocation": "left",
        "axes.titlepad": 26,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
        "legend.frameon": False,
        "legend.labelcolor": INK_2,
        "text.parse_math": False,
        "axes.axisbelow": True,
    }
)


def read(name: str) -> list[dict]:
    with (DATA / name).open() as f:
        return list(csv.DictReader(f))


def subtitle(ax, text: str) -> None:
    ax.text(0, 1.02, text, transform=ax.transAxes, color=INK_2, fontsize=9.5, va="bottom")


def source(fig, text: str, y: float = -0.03) -> None:
    fig.text(0.01, y, text, color=MUTED, fontsize=7.5, ha="left", va="top")


def save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("wrote charts/" + name)


# ---- 1. mechanism ----------------------------------------------------------
def fig_mechanism() -> None:
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")

    def box(x, y, w, h, title, body, fill):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.6",
                                    fc=fill, ec=AXIS, lw=0.8))
        ax.text(x + w / 2, y + h - 2.6, title, ha="center", va="top", fontsize=10, weight="semibold", color=INK)
        ax.text(x + w / 2, y + h - 7.2, body, ha="center", va="top", fontsize=8.2, color=INK_2, linespacing=1.35)

    def arrow(x1, y1, x2, y2, label="", dy=1.4, rad=0.0):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
                                     color=INK_2, lw=1.0, connectionstyle=f"arc3,rad={rad}"))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, label, ha="center", va="bottom", fontsize=7.8, color=INK_2)

    box(1, 30, 17, 16, "Whitelisted\nminter", "deposits BTC, ETH,\nLSTs or USDT/USDC", "#f3f2ee")
    box(27, 30, 20, 16, "Ethena minting\ncontract", "mints USDe 1:1\nagainst delivered\ncollateral", BLUE_LIGHT)
    box(56, 30, 19, 16, "Off-exchange\ncustodians", "Copper, Ceffu (Binance)\nhold spot collateral;\nmirrored to venues", "#f3f2ee")
    box(81, 30, 18, 16, "Perp venues", "short perpetuals\nsized to the spot\n= delta ~ 0", "#fde6dc")
    box(27, 3, 20, 17, "USDe holder", "stake into sUSDe\n(ERC-4626 vault,\n7-day cooldown)", BLUE_LIGHT)
    box(56, 3, 19, 17, "Yield sources", "1 perp funding\n2 LST staking yield\n3 reserve/RWA yield", "#ddf3ea")
    box(81, 3, 18, 17, "Reserve fund", "absorbs negative\nfunding; backstop\nfor sUSDe yield", "#fdf0d0")

    arrow(18.6, 38, 26.4, 38, "collateral")
    arrow(26.4, 34, 18.6, 34, "USDe", dy=-4.2)
    arrow(47.6, 38, 55.4, 38, "spot assets")
    arrow(75.6, 38, 80.4, 38, "hedge")
    arrow(90, 29.4, 75.6, 18, "funding", rad=-0.15, dy=0.5)
    arrow(55.4, 11, 47.6, 11, "yield", dy=-4.6)
    arrow(75.6, 7, 80.4, 7)
    arrow(37, 20.6, 37, 29.4, "", dy=0)
    ax.text(38, 24.2, "redeem", fontsize=7.8, color=INK_2)
    ax.text(0, 50, "How USDe stays dollar-neutral", fontsize=13, weight="semibold", color=INK, va="bottom")
    source(fig, "Diagram: author, from Ethena documentation. Custodian list per Aave governance review (Ceffu + Copper hold ~90-95% of backing).")
    save(fig, "fig01_mechanism.png")


# ---- 2. USDe supply --------------------------------------------------------
def fig_usde_supply() -> None:
    rows = read("usde_supply_snapshots.csv")
    d = [datetime.fromisoformat(r["date"]) for r in rows]
    v = [float(r["usde_supply_usd_bn"]) for r in rows]
    hi = [r["confidence"] != "low" for r in rows]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.fill_between(d, v, color=BLUE, alpha=0.08, lw=0)
    ax.plot(d, v, color=BLUE, lw=2, solid_capstyle="round")
    ax.scatter([x for x, h in zip(d, hi) if h], [y for y, h in zip(v, hi) if h], s=34, color=BLUE,
               edgecolor=SURFACE, lw=1.6, zorder=3, label="Sourced data point")
    ax.scatter([x for x, h in zip(d, hi) if not h], [y for y, h in zip(v, hi) if not h], s=30,
               facecolor=SURFACE, edgecolor=BLUE, lw=1.4, zorder=3, label="Approximate (replace with Dune Q01)")

    notes = {
        "2024-07-05": ("2024 peak $3.6B", 10, 22),
        "2024-09-30": ("Funding compresses:\n-31% to $2.5B", 14, -42),
        "2025-04-30": ("Risk-off, funding\nnear zero", -40, -48),
        "2025-10-04": ("ATH $14.8B (4 Oct 2025)", -150, 4),
        "2025-11-30": ("10 Oct crash then\n-52% in 2 months", 14, 12),
        "2026-10-12": ("$4.76B\n(12 Oct 2026)", -40, 34),
    }
    for r, x, y in zip(rows, d, v):
        if r["date"] in notes:
            t, dx, dy = notes[r["date"]]
            ax.annotate(t, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=8.3, color=INK_2,
                        arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.8))
    ax.axvline(datetime(2025, 10, 10), color=STATUS["critical"], lw=1, ls=(0, (3, 3)))
    ax.text(datetime(2025, 10, 14), 0.4, "10 Oct 2025", color=INK_2, fontsize=7.8)
    ax.set_ylim(0, 16.5)
    ax.set_ylabel("USDe supply (US$ bn)")
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("USDe supply: three boom-bust cycles in 32 months")
    subtitle(ax, "Supply tracks the funding-rate regime: it expands when the basis is rich and contracts when it compresses.")
    source(fig, "Sources: DefiLlama, CoinGecko, CoinMarketCap via 21Shares, Yahoo Finance, Cointelegraph, Ethena governance. See data/usde_supply_snapshots.csv.")
    save(fig, "fig02_usde_supply.png")


# ---- 3. ENA allocation -----------------------------------------------------
def fig_allocation() -> None:
    rows = read("ena_allocation.csv")[::-1]
    names = [r["group"] for r in rows]
    pct = [float(r["share_pct"]) for r in rows]
    insider = {"Core Contributors", "Investors"}
    colors = [ORANGE if n in insider else BLUE for n in names]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    bars = ax.barh(names, pct, color=colors, height=0.62)
    for b, p, r in zip(bars, pct, rows):
        ax.text(b.get_width() + 0.6, b.get_y() + b.get_height() / 2,
                f"{p:.0f}%  ·  {float(r['tokens_bn']):.2f}B ENA", va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 40)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Share of 15B total supply (%)")
    ax.tick_params(axis="y", length=0)
    ax.set_title("ENA allocation: 55% to insiders")
    subtitle(ax, "Orange = Core Contributors + Investors (cliff + linear vesting). Blue = Foundation-controlled or fully liquid.")
    source(fig, "Source: Ethena documentation (tokenomics). Values fixed at genesis.")
    save(fig, "fig03_ena_allocation.png")


# ---- 4. ENA unlocks --------------------------------------------------------
def fig_unlocks() -> None:
    rows = read("ena_unlock_schedule.csv")
    d = [datetime.fromisoformat(r["date"]) for r in rows]
    core = [int(r["core_contributors"]) / 1e6 for r in rows]
    inv = [int(r["investors"]) / 1e6 for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    w = 22
    ax.bar(d, core, width=w, color=ORANGE, label="Core Contributors", edgecolor=SURFACE, lw=0.8)
    ax.bar(d, inv, width=w, bottom=core, color=BLUE, label="Investors", edgecolor=SURFACE, lw=0.8)
    today = datetime(2026, 10, 16)
    ax.axvline(today, color=INK_2, lw=1, ls=(0, (3, 3)))
    ax.text(today, 1650, "  today", color=INK_2, fontsize=8.5, va="top")
    ax.annotate("5 Oct 2026: remaining investor\ntranches pulled forward\n(1.41B ENA, 9.4% of supply)",
                (datetime(2026, 10, 5), 1500), xytext=(-210, -20), textcoords="offset points", fontsize=8.3,
                color=INK_2, arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.8))
    ax.annotate("2 Apr 2025 cliff\n2.06B ENA", (datetime(2025, 4, 2), 2062), xytext=(18, -14),
                textcoords="offset points", fontsize=8.3, color=INK_2,
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.8))
    ax.annotate("Nov 2026 - Mar 2028: team only,\n93.75M ENA/month (0.63%)", (datetime(2027, 6, 5), 100),
                xytext=(-40, 60), textcoords="offset points", fontsize=8.3, color=INK_2,
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.8))
    ax.set_ylim(0, 2300)
    ax.set_ylabel("ENA unlocked (millions)")
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right", fontsize=8.5)
    ax.set_title("ENA unlocks: the investor overhang is gone; the team tail remains")
    subtitle(ax, "Scheduled Core Contributor and Investor unlocks. Ecosystem and Foundation releases are discretionary and not shown.")
    source(fig, "Model: scripts/build_unlock_schedule.py, from Ethena docs; reconciled to Tokenomist (171.875M monthly; 1,406.25M on 5 Oct 2026).")
    save(fig, "fig04_ena_unlocks.png")


# ---- 5. ENA supply status --------------------------------------------------
def fig_supply_status() -> None:
    released, team_locked, other_locked = 10.651, 1.594, 0.731
    unscheduled = 15 - released - team_locked - other_locked
    parts = [("Released per schedule", released, BLUE),
             ("Locked: team (Nov 26 - Mar 28)", team_locked, ORANGE),
             ("Locked: other scheduled", other_locked, YELLOW),
             ("Not yet scheduled", unscheduled, "#d6d5cf")]
    fig, ax = plt.subplots(figsize=(10, 3.0))
    left = 0.0
    for i, (name, v, c) in enumerate(parts):
        ax.barh([0], [v], left=left, color=c, height=0.5, edgecolor=SURFACE, lw=2,
                label=f"{name}: {v:.2f}B ({100*v/15:.1f}%)")
        if i == 0:
            ax.text(v / 2, 0, f"{name}\n{v:.2f}B · {100*v/15:.1f}%", ha="center", va="center",
                    fontsize=9, color="white", weight="semibold")
        left += v
    ax.plot([13.4, 13.4], [-0.3, 0.45], color=INK, lw=1.4)
    ax.text(13.4, 0.5, "CoinGecko-implied\ncirculating ~13.4B", ha="center", va="bottom", fontsize=8.3, color=INK_2)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2, fontsize=8.5)
    ax.set_xlim(0, 15)
    ax.set_ylim(-0.4, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("ENA (billions)")
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_title("ENA supply status, October 2026")
    subtitle(ax, "Trackers disagree by ~2.7B ENA on what counts as circulating; Foundation-held tokens are the gap.")
    source(fig, "Sources: Tokenomist (7 Oct 2026); OKX market cap $2.80B at $0.209 (14 Oct 2026). Team-locked split from the vesting model.", y=-0.42)
    save(fig, "fig05_ena_supply_status.png")


# ---- 6. yield sensitivity --------------------------------------------------
def fig_yield_sensitivity() -> None:
    xs = [i / 10 for i in range(-20, 81)]  # protocol yield on total backing, % p.a.
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for ratio, c in [(0.25, ORANGE), (0.50, BLUE), (0.75, AQUA)]:
        ax.plot(xs, [x / ratio for x in xs], color=c, lw=2, label=f"{int(ratio*100)}% of USDe staked")
        ax.text(8.1, 8 / ratio, f"{int(ratio*100)}% staked", color=INK_2, fontsize=8.5, va="center")
    obs_ratio = 1.26 / 4.9
    obs_apy = 5.0
    ax.scatter([obs_apy * obs_ratio], [obs_apy], s=60, color=INK, zorder=4, edgecolor=SURFACE, lw=1.6)
    ax.annotate(f"30 Sep 2026: 5.0% APY with {obs_ratio:.0%} staked\nimplies ~{obs_apy*obs_ratio:.1f}% net yield on all backing",
                (obs_apy * obs_ratio, obs_apy), xytext=(-60, 95), textcoords="offset points", fontsize=8.5,
                color=INK_2, arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.8))
    ax.axhline(0, color=AXIS, lw=1)
    ax.axvspan(-2, 0, color=STATUS["critical"], alpha=0.06, lw=0)
    ax.text(-1.9, 22, "negative net yield:\nreserve fund pays", fontsize=8, color=INK_2)
    ax.set_xlim(-2, 9.2)
    ax.set_ylim(-8, 33)
    ax.set_xlabel("Net protocol yield on total USDe backing (% p.a.)")
    ax.set_ylabel("sUSDe APY (%)")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("sUSDe yield is leveraged by the staking ratio")
    subtitle(ax, "All backing earns yield, but only staked USDe receives it: APY = net yield on backing / share staked.")
    source(fig, "Model: author. Observed point from Ethena Q3 2026 governance update ($1.26B staked; 7-day APY 5.0%; supply ~$4.9B).")
    save(fig, "fig06_yield_sensitivity.png")


# ---- 7. reserve fund runway ------------------------------------------------
def fig_reserve_runway() -> None:
    reserve = 61e6
    notional = [n / 10 * 1e9 for n in range(5, 49)]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for f, c in [(-0.05, AQUA), (-0.10, BLUE), (-0.20, ORANGE)]:
        weeks = [reserve / (n * -f / 52) for n in notional]
        ax.plot([n / 1e9 for n in notional], weeks, color=c, lw=2, label=f"funding {int(f*100)}% p.a.")
        ax.text(4.85, weeks[-1], f"{int(f*100)}%", color=INK_2, fontsize=8.5, va="center")
    ax.axhline(8, color=STATUS["critical"], lw=1, ls=(0, (3, 3)))
    ax.text(0.55, 8.6, "8-week trigger used in the conclusion", color=INK_2, fontsize=8.3)
    ax.set_yscale("log")
    ax.set_yticks([2, 4, 8, 16, 32, 64, 128])
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlim(0.5, 5.2)
    ax.set_xlabel("Hedged (short-perp) notional, US$ bn")
    ax.set_ylabel("Weeks of negative funding absorbed")
    ax.legend(loc="upper right", fontsize=8.5)
    ax.set_title("How long can the reserve fund absorb negative funding?")
    subtitle(ax, "Conservative: assumes a ~$61M reserve and ignores offsetting yield from LSTs, stablecoins and RWAs.")
    source(fig, "Model: author. Reserve fund size ~$61M (Mar 2026) is from a secondary source and NOT verified against Ethena's dashboard.")
    save(fig, "fig07_reserve_runway.png")


# ---- 8. risk matrix --------------------------------------------------------
def fig_risk_matrix() -> None:
    rows = read("risk_register.csv")
    fig, ax = plt.subplots(figsize=(7.4, 5.6))
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            c = STATUS["good"] if s <= 4 else STATUS["warning"] if s <= 9 else STATUS["serious"] if s <= 14 else STATUS["critical"]
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, fc=c, alpha=0.16, ec=SURFACE, lw=2))
    offsets: dict[tuple[int, int], int] = {}
    for r in rows:
        x, y = int(r["likelihood"]), int(r["impact"])
        k = offsets.get((x, y), 0)
        offsets[(x, y)] = k + 1
        ax.scatter([x], [y + 0.22 - 0.36 * k], s=330, color=INK, zorder=3, edgecolor=SURFACE, lw=1.6)
        ax.text(x, y + 0.22 - 0.36 * k, r["id"], color=SURFACE, ha="center", va="center", fontsize=7.5,
                weight="bold", zorder=4)
        ax.text(x + 0.2, y + 0.22 - 0.36 * k, r["risk"], color=INK, va="center", fontsize=7.6, zorder=4)
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6), ["Rare", "Unlikely", "Possible", "Likely", "Near-certain"])
    ax.set_yticks(range(1, 6), ["Minimal", "Minor", "Moderate", "Major", "Severe"])
    ax.set_xlabel("Likelihood (12-month horizon)")
    ax.set_ylabel("Impact on USDe holders")
    ax.grid(False)
    ax.set_title("Risk map")
    subtitle(ax, "Shading = likelihood x impact score. Scores in data/risk_register.csv.")
    save(fig, "fig08_risk_matrix.png")


# ---- 9. competitive --------------------------------------------------------
def fig_competitive() -> None:
    rows = read("stablecoin_comparison.csv")[::-1]
    names = [r["asset"] for r in rows]
    v = [float(r["supply_usd_bn"]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 3.2))
    bars = ax.barh(names, v, color=[ORANGE if "USDe" in n else BLUE for n in names], height=0.6)
    for b, val, r in zip(bars, v, rows):
        ax.text(b.get_width() * 1.08, b.get_y() + b.get_height() / 2, f"${val:,.1f}B  ·  yield: {r['yield_to_holder']}",
                va="center", fontsize=8.6, color=INK)
    ax.set_xscale("log")
    ax.set_xlim(1, 4000)
    ax.set_xticks([1, 10, 100, 1000], ["$1B", "$10B", "$100B", "$1,000B"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("Supply, US$ bn (log scale)")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    ax.set_title("USDe is ~1.6% of a $303B stablecoin market")
    subtitle(ax, "Log scale: USDT is ~39x the size of USDe. USDe competes on yield, not on payments liquidity.")
    source(fig, "Sources: Stablecoin Beat / CoinGecko (15 Oct 2026); Sky governance; Ethena governance (12 Oct 2026).", y=-0.06)
    save(fig, "fig09_competitive.png")


def main() -> None:
    fig_mechanism()
    fig_usde_supply()
    fig_allocation()
    fig_unlocks()
    fig_supply_status()
    fig_yield_sensitivity()
    fig_reserve_runway()
    fig_risk_matrix()
    fig_competitive()


if __name__ == "__main__":
    main()
