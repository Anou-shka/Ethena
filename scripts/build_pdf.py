"""Render report/ethena_due_diligence.md to a print-quality PDF.

    python scripts/build_pdf.py

Markdown -> HTML (python-markdown) -> PDF (headless Chromium via Playwright).
Also writes report/ethena_due_diligence.html, which is handy for a website.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "report" / "ethena_due_diligence.md"
HTML = ROOT / "report" / "ethena_due_diligence.html"
PDF = ROOT / "report" / "Ethena_Due_Diligence_Report.pdf"

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm; }
:root { --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --rule:#e1e0d9; --accent:#2a78d6; --warm:#eb6834; --wash:#f3f2ee; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: Inter, system-ui, sans-serif; color: var(--ink); font-size: 9.6pt; line-height: 1.5; margin: 0; background:#fff; }
.cover { height: 257mm; display:flex; flex-direction:column; justify-content:space-between; padding: 8mm 0 0; page-break-after: always; }
.cover .eyebrow { font-size: 9pt; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); font-weight: 600; }
.cover h1 { font-size: 40pt; line-height: 1.05; margin: 10mm 0 4mm; letter-spacing: -.02em; border: 0; }
.cover .sub { font-size: 15pt; color: var(--ink2); max-width: 140mm; }
.cover .verdict { display:flex; gap: 6mm; margin-top: 14mm; }
.cover .pill { border:1px solid var(--rule); border-radius: 10px; padding: 5mm 6mm; flex:1; background: var(--wash); }
.cover .pill b { display:block; font-size: 20pt; margin-top: 1mm; }
.cover .pill.med b { color: #c98500; } .cover .pill.high b { color: #d03b3b; }
.cover .pill span { font-size: 8.5pt; color: var(--ink2); text-transform: uppercase; letter-spacing: .08em; }
.cover .stats { display:grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; border-top: 1px solid var(--rule); padding-top: 6mm; }
.cover .stats div { font-size: 8.3pt; color: var(--ink2); } .cover .stats b { display:block; font-size: 16pt; color: var(--ink); }
.cover .foot { font-size: 8pt; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 4mm; }
h1 { font-size: 19pt; letter-spacing: -.01em; margin: 0 0 4mm; padding-bottom: 2mm; border-bottom: 2px solid var(--ink); }
h2 { font-size: 12.5pt; margin: 6mm 0 2mm; color: var(--ink); break-after: avoid; page-break-after: avoid; }
p { margin: 0 0 2.6mm; }
ul, ol { margin: 0 0 3mm; padding-left: 5mm; } li { margin-bottom: 1.2mm; }
a { color: var(--accent); text-decoration: none; }
strong { font-weight: 650; }
table { width: 100%; border-collapse: collapse; margin: 2mm 0 4mm; font-size: 8.3pt; line-height: 1.4; page-break-inside: avoid; }
th { text-align: left; font-weight: 600; color: var(--ink2); border-bottom: 1.5px solid var(--ink); padding: 1.6mm 2mm; vertical-align: bottom; }
td { border-bottom: 1px solid var(--rule); padding: 1.6mm 2mm; vertical-align: top; }
tbody tr:nth-child(even) td { background: #fafaf8; }
img { display:block; max-width: 100%; max-height: 82mm; margin: 2mm auto 4mm; page-break-inside: avoid; }
blockquote { margin: 0 0 4mm; padding: 2.5mm 4mm; background: var(--wash); border-left: 3px solid var(--accent); color: var(--ink2); }
blockquote p { margin: 0; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; background: var(--wash); padding: 0 1mm; border-radius: 2px; }
.pagebreak { page-break-after: always; }
.cover-meta { display: none; }
em { color: var(--ink2); }
"""

COVER = """
<section class="cover">
  <div>
    <div class="eyebrow">Due diligence report · October 2026</div>
    <h1>Ethena<br>USDe &amp; ENA</h1>
    <div class="sub">A risk assessment of crypto's largest synthetic dollar: funding-rate dependence, custody concentration, peg resilience and token supply.</div>
    <div class="verdict">
      <div class="pill med"><span>USDe / sUSDe holders</span><b>Medium risk</b></div>
      <div class="pill high"><span>ENA token holders</span><b>High risk</b></div>
    </div>
  </div>
  <div>
    <div class="stats">
      <div><b>$4.76B</b>USDe supply<br>(12 Oct 2026)</div>
      <div><b>−68%</b>from Oct 2025<br>all-time high</div>
      <div><b>~5.0%</b>sUSDe 7-day APY<br>(30 Sep 2026)</div>
      <div><b>$7.5B</b>USDe supply needed<br>to start ENA buybacks</div>
    </div>
    <p class="foot" style="margin-top:8mm">Independent research. Not investment advice. Data as of 12–16 October 2026; sources in Appendix A.
    Charts and on-chain queries are reproducible from the accompanying repository.</p>
  </div>
</section>
"""


def render_html() -> str:
    text = SRC.read_text()
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)  # strip front matter
    body = markdown.markdown(text, extensions=["tables", "md_in_html", "sane_lists"])
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Ethena Due Diligence</title>"
        f"<style>{CSS}</style></head><body>{COVER}{body}</body></html>"
    )


def main() -> None:
    HTML.write_text(render_html())
    print(f"wrote {HTML.relative_to(ROOT)}")

    from playwright.sync_api import sync_playwright

    launch = {}
    if Path("/opt/pw-browsers/chromium").exists() and not os.environ.get("PLAYWRIGHT_CHROMIUM"):
        launch["executable_path"] = "/opt/pw-browsers/chromium"
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch)
        page = browser.new_page()
        page.goto(HTML.resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(PDF),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=(
                "<div style='font-family:Inter,sans-serif;font-size:7pt;color:#898781;width:100%;"
                "padding:0 17mm;display:flex;justify-content:space-between'>"
                "<span>Ethena (USDe / ENA) · Due Diligence · October 2026</span>"
                "<span class='pageNumber'></span></div>"
            ),
            margin={"top": "16mm", "bottom": "18mm", "left": "17mm", "right": "17mm"},
        )
        browser.close()
    print(f"wrote {PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
