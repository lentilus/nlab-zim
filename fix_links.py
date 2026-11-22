#!/usr/bin/env python3
"""
Rewrite nlab/show/ links in the HTML export to local relative paths.

Handles:
- /nlab/show/Name   (Instiki uses '+' for spaces, %XX for special chars)
- relative links (Name#frag) — they resolve to /nlab/show/Name live
- preserves #fragment anchors
- skips external http(s) links and in-page fragments

Wanted pages (not found in index) route to <HTML_ROOT>/missing.html.
"""

import csv
import os
import sys
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
from bs4 import BeautifulSoup

HTML_ROOT = Path(sys.argv[1]).resolve()
INDEX_CSV = Path(sys.argv[2])
MISSING   = Path(sys.argv[3])

# ---------- load the index ----------
index: dict[str, Path] = {}
with INDEX_CSV.open(newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        raw = row["name"].strip()
        target = HTML_ROOT / row["dirpath"] / "content.html"
        # store both raw and underscore-normalised keys as a safety net
        index[raw] = target
        index[raw.replace("_", " ")] = target

# ---------- helpers ----------
def local_target(page_name: str) -> Path | None:
    t = index.get(page_name)
    return t if t is not None and t.exists() else None

def extract_page_name(parsed) -> str | None:
    """Return the nLab page name for a link, or None if it's not a page."""
    path = parsed.path
    if "/nlab/show/" in path:
        rest = path.split("/nlab/show/", 1)[1].rstrip("/")
        # sub-views: /show/diff/PageName, /show/PageName/cite, /show/PageName/print
        if rest.startswith("diff/") or rest.endswith(("/cite", "/print")):
            return None
        return unquote_plus(rest)
    # relative link: no scheme, no leading slash, no known asset prefix
    if path and not path.startswith("/") and not parsed.scheme:
        if path.startswith(("stylesheets/", "javascripts/", "files/")):
            return None
        return unquote_plus(path)
    return None

def rewrite_file(path: Path) -> None:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    changed = False
    for a in soup.find_all("a", href=True):
        parsed = urlparse(a["href"])
        name = extract_page_name(parsed)
        if name is None:
            continue
        target = local_target(name) or MISSING
        rel = os.path.relpath(target, path.parent)
        if parsed.fragment:
            rel += "#" + parsed.fragment
        a["href"] = rel
        changed = True
    if changed:
        path.write_text(str(soup), encoding="utf-8")

n = 0
for html in HTML_ROOT.rglob("content.html"):
    rewrite_file(html)
    n += 1
print(f"rewrote links in {n} files")
