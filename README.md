# Zim Archive of the nLab

Update git submodules.

Make sure the python scripts dependencies are available.
```bash
nix-shell -p "python3.withPackages (ps: [ ps.beautifulsoup4 ])" zim-tools
```

We want to use the html-dump as a basis for the zim archive but in order to
have working static links, we need to resolve redirects correctly. We can build
a page index respecting redirects using the markdown dump of the nlab.
```bash
./build_page_index.py ./nlab-content > page-index.csv
```

The html dump contains a bunch of elements that we don't want/need in the
static archive. The below line removes the unnecessary bits from the dump.
```
./clean_html.py ./nlab-content-html ./cleaned-nlab-content-html ./assets/style.css
```

Lastly we make sure that all links resolve correctly by replacing them with the
correct static target from the page index.
```
./fix_links.py ./cleaned-nlab-content-html page-index.csv ./missing.html
```

Copy the favicon over.
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
