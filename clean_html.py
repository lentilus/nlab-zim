#!/usr/bin/env python3
"""
Strips the nLab HTML export and injects minimal stylesheet

Removes:
- all <script> tags and external/local <link rel="stylesheet"> tags
- the top navigation bar (Home Page / All Pages / ...) and its search form
- the footer navigation (Edit / History / Cite / Print / Source / ...)
- the "Last revised on" block
- the sidebar TOCs (rightHandSide + toc clickDown)
- the "Edit this sidebar" links
- the trailing category property block
- 'hide' wrappers — content is made visible unconditionally
- 'clickDown' class and tabindex — no JS behaviour needed
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup

HTML_ROOT = Path(sys.argv[1]).resolve()
RESULT_ROOT = Path(sys.argv[2])
CSS_FILE = Path(sys.argv[3])

INLINE_CSS = CSS_FILE.read_text()

def clean_file(source: Path, target: Path) -> None:
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")

    # scripts and stylesheets
    for tag in soup.find_all("script"):
        tag.decompose()

    # everything prepended to the page title
    h1 = soup.find("h1", id="pageName")
    if h1 is not None:
        for span in h1.find_all("span", recursive=False):
            span.decompose()

    for tag in soup.find_all("link", rel="stylesheet"):
        tag.decompose()

    # navigation bars
    for tag in soup.find_all("div", class_="navigation"):
        tag.decompose()

    # search form
    for tag in soup.find_all("form"):
        tag.decompose()

    # footer metadata and edit/history chrome
    for tag in soup.find_all("div", class_="revisedby"):
        tag.decompose()

    # sidebar TOCs
    for tag in soup.find_all("div", class_="rightHandSide"):
        tag.decompose()

    # any remaining "Edit this sidebar" links
    for a in soup.find_all("a", href=True):
        if "/nlab/edit/" in a["href"]:
            a.decompose()

    # category property block at the bottom
    for tag in soup.find_all("div", class_="property"):
        tag.decompose()

    # reveal anything still wrapped in 'hide'
    for tag in soup.find_all(class_="hide"):
        tag.unwrap()

    # drop clickDown class and tabindex from anything left
    for tag in soup.find_all(class_="clickDown"):
        tag["class"] = [c for c in tag.get("class", []) if c != "clickDown"]
        if not tag["class"]:
            del tag["class"]
        tag.attrs.pop("tabindex", None)

    # flatten the nested <html>/<head>/<body>
    revision = soup.find("div", id="revision")
    if revision is not None:
        inner_body = revision.find("body")
        if inner_body is not None:
            for child in list(inner_body.children):
                revision.append(child.extract())
            for tag in revision.find_all(["html", "head", "body"]):
                tag.decompose()
        # drop any stray inner <title> that would override the outer one
        for t in revision.find_all("title"):
            t.decompose()

    # inject stylesheet into the outer <head>
    head = soup.find("head")
    if head is not None:
        style = soup.new_tag("style")
        style.string = INLINE_CSS
        head.append(style)

    target.write_text(str(soup), encoding="utf-8")


n = 0

for html in HTML_ROOT.rglob("content.html"):
    relative = os.path.relpath(html, HTML_ROOT)
    result = RESULT_ROOT / relative

    if not os.path.exists(result.parent):
       os.makedirs(result.parent)

    clean_file(html, result)
    n += 1

print(f"cleaned {n} files")
