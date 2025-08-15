#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

REPO_FULL = os.getenv("GITHUB_REPOSITORY", "kl543/qpi-toolkit")
BRANCH    = os.getenv("GITHUB_REF_NAME", "main")
OWNER, REPO_NAME = (REPO_FULL.split("/", 1) + [""])[:2]

ROOT     = Path(__file__).resolve().parents[1]
NB_DIR   = ROOT / "notebooks"
IMG_DIR  = ROOT / "assets" / "img"
RES_DIR  = ROOT / "results"          # 可不存在
OUT_HTML = ROOT / "index.html"
MAIN    = "https://kl543.github.io"
PROJ    = f"{MAIN}/projects.html"

def q(p): return quote(p if isinstance(p, str) else p.as_posix(), safe="/-._")
def h(s): return (s.replace("&","&amp;").replace("<","&lt;")
                   .replace(">","&gt;").replace('"',"&quot;"))

def nbv(rel): return f"https://nbviewer.org/github/{REPO_FULL}/blob/{BRANCH}/{q(rel)}"
def raw(rel): return f"https://raw.githubusercontent.com/{REPO_FULL}/{BRANCH}/{q(rel)}"

def header():
    try:
        for p in [ROOT/"_site-header.html", ROOT.parent/"_site-header.html"]:
            if p.exists(): return p.read_text(encoding="utf-8")
    except Exception:  # 兜底
        pass
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>QPI Toolkit — Kaiming Liu</title>
<style>
:root{{--line:#e9e9e9;--muted:#666;--ink:#111}}
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);line-height:1.6}}
header{{background:#111;color:#fff;padding:30px 16px;text-align:center}}
nav{{display:flex;gap:14px;justify-content:center;margin:10px 0 0}}
nav a{{color:#fff;text-decoration:none;opacity:.9}} nav a:hover{{opacity:1}}
.container{{max-width:1040px;margin:24px auto;padding:0 16px}}
.card{{border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:16px 0;background:#fff}}
.muted{{color:var(--muted)}} h1,h2,h3{{margin:.2rem 0 .6rem}}
.btn{{display:inline-block;border:1px solid var(--line);padding:8px 12px;border-radius:10px;text-decoration:none;margin-right:8px;color:#111}}
.btn:hover{{background:#f6f6f6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
.thumb{{border:1px solid var(--line);border-radius:12px;padding:6px;background:#fff}}
.thumb img{{width:100%;display:block;border-radius:8px}}
.run-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-top:8px}}
.tile{{display:block;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;text-decoration:none;color:inherit}}
.tile img{{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}}
.tile .cap{{padding:8px 10px;font-size:13px;color:var(--muted);border-top:1px solid var(--line)}}
.center{{text-align:center}}
</style></head><body>
<header>
  <h1>QPI from Iso-energy Contours in Altermagnets</h1>
  <div class="muted">JDOS / spin-polarized QPI pipeline</div>
  <div style="margin-top:6px"><a href="{PROJ}" style="color:#fff;text-decoration:underline;">Back to Projects</a></div>
  <nav>
    <a href="{MAIN}/index.html">About</a>
    <a href="{MAIN}/interests.html">Interests</a>
    <a href="{MAIN}/projects.html"><b>Projects</b></a>
    <a href="{MAIN}/coursework.html">Coursework</a>
    <a href="{MAIN}/contact.html">Contact</a>
  </nav>
</header>
"""

def list_notebooks():
    items = []
    try:
        if NB_DIR.exists():
            for nb in sorted(NB_DIR.glob("*.ipynb")):
                rel = nb.relative_to(ROOT).as_posix()
                items.append((rel, nbv(rel), raw(rel)))
        for nb in sorted(ROOT.glob("*.ipynb")):
            rel = nb.name
            items.append((rel, nbv(rel), raw(rel)))
    except Exception:
        pass
    # 去重
    seen, out = set(), []
    for rel, v, d in items:
        if rel not in seen:
            out.append((rel, v, d)); seen.add(rel)
    return out

def list_figs(max_n=24):
    try:
        if not IMG_DIR.exists(): return []
        imgs = sorted(IMG_DIR.glob("*.*"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [p.relative_to(ROOT).as_posix() for p in imgs[:max_n]]
    except Exception:
        return []

def runs_sections():
    try:
        if not RES_DIR.exists(): return '<div class="muted">No results/ directory.</div>'
        cards, dirs = [], sorted([d for d in RES_DIR.iterdir() if d.is_dir()],
                                 key=lambda p: p.stat().st_mtime, reverse=True)
        for d in dirs:
            imgs = sorted(d.glob("*.png"))
            docs = sorted([*d.glob("*.csv"), *d.glob("*.txt")])
            tiles = "".join(
                f'<a class="tile" href="{q(p.relative_to(ROOT))}" target="_blank" rel="noreferrer">'
                f'<img loading="lazy" src="{q(p.relative_to(ROOT))}"><div class="cap">{h(p.name)}</div></a>'
                for p in imgs)
            dls = "".join(f'<li><a href="{q(f.relative_to(ROOT))}">{h(f.name)}</a></li>' for f in docs)
            cards.append(
                f'<section class="card"><h3>{h(d.name)}</h3>'
                f'{"<div class=run-grid>"+tiles+"</div>" if tiles else ""}'
                f'{("<div class=muted style=margin-top:6px>Downloads</div><ul style=margin:6px 0 0 18px>"+dls+"</ul>") if dls else ""}'
                f'{"" if (imgs or docs) else "<div class=muted>No plots or logs in this run.</div>"}'
                f'</section>'
            )
        return "\n".join(cards)
    except Exception:
        return '<div class="muted">Failed to read results/.</div>'

def build():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    nbs, figs = list_notebooks(), list_figs()
    html = [header(), '<main class="container">']

    html += ['<section class="card"><h2>Notebooks</h2>']
    if nbs:
        for rel, view_url, dl_url in nbs:
            label = Path(rel).stem.replace("-", " ")
            html += [f'<div style="margin:10px 0;"><b>{h(label)}</b><br/>'
                     f'<a class="btn" href="{view_url}" target="_blank" rel="noreferrer">View (nbviewer)</a>'
                     f'<a class="btn" href="{dl_url}" target="_blank" rel="noreferrer">Download (.ipynb)</a></div>']
    else:
        html += ['<div class="muted">No notebooks yet.</div>']
    html += ['</section>']

    html += ['<section class="card"><h2>Selected Figures</h2>']
    if figs:
        html += ['<div class="grid">'] + [f'<div class="thumb"><img src="{f}" loading="lazy"></div>' for f in figs] + ['</div>']
    else:
        html += ['<div class="muted">No figures yet.</div>']
    html += ['</section>']

    html += ['<section class="card"><h2>Recent Results</h2>', runs_sections(), '</section>']
    html += [f'<div class="center muted" style="margin:24px 0;">Last updated: {now} — {OWNER}/{REPO_NAME}@{BRANCH}</div>',
             '</main></body></html>']
    return "\n".join(html)

if __name__ == "__main__":
    OUT_HTML.write_text(build(), encoding="utf-8")
    print(f"[qpi-toolkit] wrote {OUT_HTML}")
