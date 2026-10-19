#!/usr/bin/env bash
# Build "A Complete Guide to Multilevel Writing": interior + cover, merged into one PDF.
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/check.py
python3 scripts/build.py
node scripts/render.js
python3 scripts/cover.py
node scripts/cover_render.js
python3 scripts/merge.py
rm -f dist/cover_pages.html dist/cover_spread.html dist/body.html dist/cover.html dist/interior.pdf
