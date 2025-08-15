#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

REPO_FULL = os.getenv("GITHUB_REPOSITORY", "kl543/qpi-toolkit")
BRANCH    = os.getenv("GITHUB_REF_NAME", "main")

ROOT    = Path(__file__).resolve().parents[1]
NB_DIR  = ROOT / "notebooks"
IMG_DIR = ROOT / "assets" / "img"
RES_DIR = ROOT / "results"
OUT     = ROOT / "index.html"

MAIN   = "https://kl543.github.io"
PROJ   = f"{MAIN}/projects.html"

def q(p): 
    return quote(p if isinstance(p, str) else p.as_posix(), safe="/-._")
def h(s): 
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")
def nbv(rel): 
    return f"https://nbviewer.org/github/{REPO_FULL}/blob/{BRANCH}/{q(rel)}"
def raw(rel): 
    return f"https://raw.githubusercontent.com/{REPO_FULL}/{BRANCH}/{q(rel)}"

def header():
    # 复用主站头（可放到 _site-header.html），无则兜底
    for p in [ROOT/"_site-header.html", ROOT.parent/"_site-header.html"]:
        if p.exists(): return p.read_text(encoding="utf-8")
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>QPI from Iso-energy Contours — Kaiming Liu</title>
<style>
:root{{--line:#e9e9e9;--muted:#666;--ink:#111}}
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.6;color:var(--ink)}}
header{{background:#111;color:#fff;text-align:center;padding:30px 16px}}
.container{{max-width:1040px;margin:24px auto;padding:0 16px}}
.card{{border:1px solid var(--line);border-radius:16px;background:#fff;padding:16px 18px;margin:16px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
.thumb{{border:1px solid var(--line);border-radius:12px;padding:6px;background:#fff}}
.thumb img{{width:100%;display:block;border-radius:8px}}
.btn{{display:inline-block;border:1px solid var(--line);padding:8px 12px;border-radius:10px;text-decoration:none;margin-right:8px;color:#111}}
.btn:hover{{background:#f6f6f6}}
.run-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-top:8px}}
.tile{{display:block;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;text-decoration:none;color:inherit}}
.tile img{{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}}
.tile .cap{{padding:8px 10px;font-size:13px;color:var(--muted);border-top:1px solid var(--line)}}
.center{{text-align:center}} .muted{{color:var(--muted)}}
</style></head><body>
<header>
  <h1>QPI from Iso-energy Contours in Altermagnets</h1>
  <div class="muted">JDOS / spin-polarized QPI pipeline</div>
  <div style="margin-top:6px;"><a href="{PROJ}" style="color:#fff;text-decoration:underline;">Back to Projects</a></div>
</header>
"""

def list_notebooks():
    items = []
    if NB_DIR.exists():
        for nb in sorted(NB_DIR.glob("*.ipynb")):
            rel = nb.relative_to(ROOT).as_posix()
            items.append((Path(rel).stem.replace("-"," "), nbv(rel), raw(rel)))
    return items

def list_figs(max_n=24):
    if not IMG_DIR.exists(): return []
    imgs = sorted(IMG_DIR.glob("*.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [p.relative_to(ROOT).as_posix() for p in imgs[:max_n]]

def list_runs():
    if not RES_DIR.exists(): return []
    dirs = sorted([d for d in RES_DIR.iterdir() if d.is_dir()],
                  key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for d in dirs:
        pngs = sorted(d.glob("*.png"))
        docs = sorted([*d.glob("*.csv"), *d.glob("*.txt")])
        tiles = "".join(
            f'<a class="tile" href="{q(p.relative_to(ROOT))}" target="_blank" rel="noreferrer">'
            f'<img loading="lazy" src="{q(p.relative_to(ROOT))}"><div class="cap">{h(p.name)}</div></a>'
            for p in pngs)
        dls = "".join(f'<li><a href="{q(f.relative_to(ROOT))}">{h(f.name)}</a></li>' for f in docs)
        out.append(
            f'<section class="card"><h3>{h(d.name)}</h3>'
            f'{"<div class=run-grid>"+tiles+"</div>" if tiles else "<div class=muted>No images</div>"}'
            f'{("<div class=muted style=margin-top:6px>Downloads</div><ul style=margin:6px 0 0 18px>"+dls+"</ul>") if dls else ""}'
            f'</section>'
        )
    return "\n".join(out)

def build():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    nbs = list_notebooks()
    figs = list_figs()
    runs = list_runs()
    html = [header(), '<main class="container">']

    html += ['<section class="card"><h2>Notebooks</h2>']
    if nbs:
        for label, v, d in nbs:
            html += [f'<div style="margin:10px 0;"><b>{h(label)}</b><br/>'
                     f'<a class="btn" href="{v}" target="_blank" rel="noreferrer">View (nbviewer)</a>'
                     f'<a class="btn" href="{d}" target="_blank" rel="noreferrer">Download (.ipynb)</a></div>']
    else:
        html += ['<div class="muted">No notebooks yet.</div>']
    html += ['</section>']

    html += ['<section class="card"><h2>Selected Figures</h2>']
    if figs:
        html += ['<div class="grid">'] + [f'<div class="thumb"><img src="{f}" loading="lazy"></div>' for f in figs] + ['</div>']
    else:
        html += ['<div class="muted">No figures yet.</div>']
    html += ['</section>']

    html += ['<section class="card"><h2>Recent Results</h2>', runs or '<div class="muted">No results yet.</div>', '</section>']

    html += [f'<div class="center muted" style="margin:24px 0;">Last updated: {now}</div>',
             '</main></body></html>']
    return "\n".join(html)

if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"[qpi-toolkit] wrote {OUT}")
