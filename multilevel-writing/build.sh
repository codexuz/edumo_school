#!/usr/bin/env bash
# Build "A Complete Guide to Multilevel Writing": HTML -> A4 PDF (cover + body).
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/check.py
python3 scripts/build.py
node scripts/render.js
rm -f dist/cover.html dist/body.html
