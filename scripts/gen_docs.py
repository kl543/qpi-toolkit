# scripts/gen_docs.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# ---- 仓库信息（GitHub Actions 会自动从 env 取；本地跑用默认值）----
REPO_FULL = os.getenv("GITHUB_REPOSITORY", "kl543/qpi-toolkit")  # 形如 user/repo
BRANCH    = os.getenv("GITHUB_REF_NAME", "main")
OWNER, REPO_NAME = (REPO_FULL.split("/", 1) + [""])[:2]

# ---- 路径 ----
ROOT     = Path(__file__).resolve().parents[1]   # repo root
NB_DIR   = ROOT / "notebooks"                    # 展示 notebook（nbviewer + 下载）
IMG_DIR  = ROOT / "assets" / "img"               # 展示封面图
RES_DIR  = ROOT / "results"                      # （可选）按材料分组的输出
OUT_HTML = ROOT / "index.html"

MAIN_SITE    = "https://kl543.github.io"
PROJECTS_URL = f"{MAIN_SITE}/projects.html"

# ------------------------ 小工具 ------------------------
def q(p: Path | str) -> str:
    if isinstance(p, Path):
        p = p.as_posix()
    return quote(p, safe="/-._")

def h(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )

def nbviewer_url(rel_path: str) -> str:
    return f"https://nbviewer.org/github/{REPO_FULL}/blob/{BRANCH}/{q(rel_path)}"

def raw_url(rel_path: str) -> str:
    return f"https://raw.githubusercontent.com/{REPO_FULL}/{BRANCH}/{q(rel_path)}"

# ------------------------ 页眉 ------------------------
def load_site_header() -> str:
    for p in [ROOT / "_site-header.html", ROOT.parent / "_site-header.html"]:
        if p.exists():
            return p.read_text(encoding="utf-8")
    # fallback header（与 MBE 风格一致）
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>QPI Toolkit — Kaiming Liu</title>
<style>
:root{{--line:#e9e9e9;--muted:#666;--ink:#111}}
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);line-height:1.6}}
header{{background:#111;color:#fff;padding:30px 16px;text-align:center}}
nav{{display:flex;gap:14px;justify-content:center;margin:10px 0 0}}
nav a{{color:#fff;text-decoration:none;opacity:.9}} nav a:hover{{opacity:1}}
.container{{max-width:1040px;margin:24px auto;padding:0 16px}}
.muted{{color:var(--muted)}}
.card{{border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:16px 0;background:#fff}}
h1,h2,h3{{margin:.2rem 0 .6rem}}
.btn{{display:inline-block;border:1px solid var(--line);padding:8px 12px;border-radius:10px;text-decoration:none;margin-right:8px;color:#111}}
.btn:hover{{background:#f6f6f6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
.thumb{{border:1px solid var(--line);border-radius:12px;padding:6px;background:#fff}}
.thumb img{{width:100%;height:auto;display:block;border-radius:8px}}
.center{{text-align:center}}
.run-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-top:8px}}
.tile{{display:block;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;text-decoration:none;color:inherit}}
.tile img{{width:100%;display:block;aspect-ratio:4/3;object-fit:cover}}
.tile .cap{{padding:8px 10px;font-size:13px;color:var(--muted);border-top:1px solid var(--line)}}
</style>
</head>
<body>
<header>
  <h1>QPI from Iso-energy Contours in Altermagnets</h1>
  <div class="muted">JDOS / spin-polarized QPI pipeline</div>
  <div style="margin-top:6px"><a href="{PROJECTS_URL}" style="color:#fff;text-decoration:underline;">Back to Projects</a></div>
  <nav>
    <a href="{MAIN_SITE}/index.html">About</a>
    <a href="{MAIN_SITE}/interests.html">Interests</a>
    <a href="{MAIN_SITE}/projects.html"><b>Projects</b></a>
    <a href="{MAIN_SITE}/coursework.html">Coursework</a>
    <a href="{MAIN_SITE}/contact.html">Contact</a>
  </nav>
</header>
"""

# ------------------------ 内容块 ------------------------
def list_notebooks() -> list[tuple[str, str, str]]:
    items: list[tuple[str, str, str]] = []
    if NB_DIR.exists():
        for nb in sorted(NB_DIR.glob("*.ipynb")):
            rel = nb.relative_to(ROOT).as_posix()
            items.append((rel, nbviewer_url(rel), raw_url(rel)))
    # 根目录 *.ipynb 也一并收
    for nb in sorted(ROOT.glob("*.ipynb")):
        rel = nb.name
        items.append((rel, nbviewer_url(rel), raw_url(rel)))
    # 去重
    seen, uniq = set(), []
    for rel, v, d in items:
        if rel not in seen:
            uniq.append((rel, v, d))
            seen.add(rel)
    return uniq

def list_figs(max_count: int = 24) -> list[str]:
    if not IMG_DIR.exists():
        return []
    imgs = list(IMG_DIR.glob("*.*"))
    imgs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [p.relative_to(ROOT).as_posix() for p in imgs[:max_count]]

def runs_sections() -> str:
    if not RES_DIR.exists():
        return '<div class="muted">No results/ directory.</div>'
    cards = []
    dirs = [d for d in RES_DIR.iterdir() if d.is_dir()]
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for d in dirs:
        imgs = sorted(d.glob("*.png"))
        docs = sorted([*d.glob("*.csv"), *d.glob("*.txt")])
        tiles = "".join(
            f"""
            <a class="tile" href="{q(p.relative_to(ROOT))}" target="_blank" rel="noreferrer">
              <img loading="lazy" src="{q(p.relative_to(ROOT))}" alt="{h(p.name)}">
              <div class="cap">{h(p.name)}</div>
            </a>
            """
            for p in imgs
        )
        dl = "".join(f'<li><a href="{q(p.relative_to(ROOT))}">{h(p.name)}</a></li>' for p in docs)
        empty = "" if (imgs or docs) else '<div class="muted">No plots or logs in this run.</div>'
        cards.append(
            f"""
            <section class="card">
              <h3>{h(d.name)}</h3>
              {'<div class="run-grid">'+tiles+'</div>' if tiles else ''}
              {('<div class="muted" style="margin-top:6px">Downloads</div><ul style="margin:6px 0 0 18px">'+dl+'</ul>') if dl else ''}
              {empty}
            </section>
            """
        )
    return "\n".join(cards)

def build_html() -> str:
    header = load_site_header()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    nbs  = list_notebooks()
    figs = list_figs()

    html = [header, '<main class="container">']

    html.append('<section class="card"><h2>Notebooks</h2>')
    if nbs:
        for rel, view_url, dl_url in nbs:
            label = Path(rel).stem.replace("-", " ")
            html.append('<div style="margin:10px 0;">')
