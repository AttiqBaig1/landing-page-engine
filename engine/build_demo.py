# -*- coding: utf-8 -*-
"""
build_demo.py
-------------
Builds a static demo gallery: one sample landing page per niche plus an
index.html that links them all, with each niche's colour palette shown.
GitHub Actions runs this on every push and publishes the result to
GitHub Pages (see .github/workflows/pages.yml).

Usage:
    python build_demo.py --out ../site
"""
import argparse
import html
import shutil
from pathlib import Path

from generate_site import build_site
from niche_content import NICHE_CONTENT
from theme import get_theme

CITIES = ["Fresno, CA", "Round Rock, TX", "Columbus, OH", "Tampa, FL", "Denver, CO",
          "Charlotte, NC", "Nashville, TN", "Phoenix, AZ", "Raleigh, NC", "Kitchener, ON",
          "Calgary, AB", "Highland Park, IL"]


def build(out: Path):
    if out.exists():
        shutil.rmtree(out)
    demos = out / "demo"
    demos.mkdir(parents=True)

    cards = []
    for i, key in enumerate(sorted(NICHE_CONTENT)):
        c = NICHE_CONTENT[key]
        label = key.replace("_", " ").title()
        path = build_site(f"Summit {label}", CITIES[i % len(CITIES)], f"(555) 555-{1000 + i:04d}",
                          key, out_dir=str(demos), warn=lambda m: None)
        # build_site names the folder after the business; rename to the niche key
        target = demos / key
        if target.exists():
            shutil.rmtree(target)
        path.parent.rename(target)
        T = get_theme(c["theme"])
        cards.append(
            f'<a class="card" href="demo/{key}/" style="--bg:{T["bg"]};--acc:{T["accent"]};--acc2:{T["accent2"]}">'
            f'<span class="dot"></span><strong>{html.escape(label)}</strong>'
            f'<small>{html.escape(c["theme"])} · {html.unescape(c["h1_keyword"])}</small></a>')
        print(f"[{i + 1}/{len(NICHE_CONTENT)}] {key}")

    (out / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Landing Page Engine — {len(cards)} Niche Demos</title>
<style>
body{{margin:0;font-family:Inter,system-ui,sans-serif;background:#0f1115;color:#e8e8e8}}
header{{padding:48px 24px 24px;max-width:1200px;margin:auto}}
h1{{margin:0 0 8px;font-size:32px}} p{{color:#9aa0a6;margin:0}}
input{{margin-top:20px;width:100%;max-width:420px;padding:12px 14px;border-radius:10px;border:1px solid #2a2f37;background:#171a20;color:#fff;font-size:15px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;padding:0 24px 64px;max-width:1200px;margin:auto}}
.card{{display:flex;flex-direction:column;gap:6px;padding:18px;border-radius:14px;text-decoration:none;color:#fff;
background:var(--bg);border:1px solid color-mix(in srgb,var(--acc) 35%,transparent);transition:transform .15s}}
.card:hover{{transform:translateY(-2px);border-color:var(--acc2)}}
.dot{{width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,var(--acc),var(--acc2))}}
small{{color:var(--acc2);font-size:12px}}
</style></head><body>
<header><h1>Landing Page Engine</h1>
<p>{len(cards)} niches — one sample page each, every niche with its own colour palette and tinted background.</p>
<input id="q" placeholder="Search niches..." oninput="for(const c of document.querySelectorAll('.card'))c.style.display=c.textContent.toLowerCase().includes(this.value.toLowerCase())?'':'none'">
</header>
<main class="grid">{''.join(cards)}</main>
</body></html>""", encoding="utf-8")
    (out / ".nojekyll").write_text("")
    print(f"Gallery written to {out / 'index.html'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).parent.parent / "site"))
    build(Path(ap.parse_args().out))
