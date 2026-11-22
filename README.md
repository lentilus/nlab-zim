# Zim Archive of the nLab

This repository builds a ZIM archive from the nLab HTML dump. The HTML dump is
the basis for the archive, but static links require resolving redirects
corretly. For that purpose we build a page index from the nLab Markdown dump.

You can just download the `nLab.zim` file, or build an updated one yourself.

## Update the source

Update the git submodules:
```
git submodule update --init --recursive
```

## Dependencies

You need a `python3` installation with `beautifulsoup4`. The latter is used to
manipulate the html source. Furthermore we need `zimwriterfs` from `zimtools`
to build the final `zim`.

If you have nix installed you can just do
```bash
nix-shell -p "python3.withPackages (ps: [ ps.beautifulsoup4 ])" zim-tools
```

## Build

Run all the remaining commands from the repositories root.

Build the page index, respecting redirects from the markdown dump.
```bash
./build_page_index.py ./nlab-content > page-index.csv
```

Prepare the html for use in a reader like `Kiwix`. Do this step before fixing
the links!
```
./clean_html.py ./nlab-content-html ./cleaned-nlab-content-html ./assets/style.css
```

Replace links with their correct static targets from the page index. Unresolved
links are written to `missing.html`.
```
./fix_links.py ./cleaned-nlab-content-html page-index.csv ./missing.html
```

Copy the nlab-favicon over to the `cleaned-nlab-content-html`.
```
cp ./assets/favicon.png ./cleaned-nlab-content-html/
```

Finally use `zimwriterfs` to build the archive.
```
zimwriterfs \
  --welcome=pages/1/0/0/0/1/content.html \
  --illustration=./favicon.png \
  --language="eng" \
  --title="nLab" \
  --description="wiki for mathematical research-level notes, expositions and collaborative work" \
  --creator="nlab contributors" \
  --publisher="ncatlab.org" \
  --name="nLab" \
  ./cleaned-nlab-content-html \
  nLab.zim
```
