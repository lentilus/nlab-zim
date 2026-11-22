#!/usr/bin/env python3

import csv
import re
import sys
from pathlib import Path

REPO = Path(sys.argv[1])

# detects instiki style redirects
REDIRECT_RE = re.compile(r"\[\[!redirects?\s+([^\]]+)\]\]")


def parse_redirects(text: str) -> list[str]:
    aliases: list[str] = []
    for m in REDIRECT_RE.finditer(text):
        for part in m.group(1).split(","):
            part = part.strip()
            if part:
                aliases.append(part)
    return aliases


def main() -> None:
    pages_root = REPO / "pages"
    rows: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for name_file in sorted(pages_root.rglob("name")):
        content_file = name_file.with_name("content.md")
        if not content_file.exists():
            continue

        page_name = name_file.read_text(encoding="utf-8").strip()
        if not page_name:
            continue

        rel = str(name_file.parent.relative_to(REPO))

        # add page itself to index
        if (page_name, rel) not in seen:
            seen.add((page_name, rel))
            rows.append((page_name, rel))

        # add all redirects to index
        text = content_file.read_text(encoding="utf-8", errors="replace")
        for alias in parse_redirects(text):
            if (alias, rel) not in seen:
                seen.add((alias, rel))
                rows.append((alias, rel))

    writer = csv.writer(sys.stdout)
    writer.writerow(["name", "dirpath"])
    writer.writerows(rows)

if __name__ == "__main__":
    main()
