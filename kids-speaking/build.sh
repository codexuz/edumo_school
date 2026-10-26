#!/usr/bin/env bash
# Build a Talk Time! book.  Usage: ./build.sh [1|2]   (default: both)
set -euo pipefail
cd "$(dirname "$0")"
books=("$@"); [ ${#books[@]} -eq 0 ] && books=(1 2)
for b in "${books[@]}"; do
  python3 scripts/check.py "$b"
  python3 scripts/build.py "$b"
  node scripts/render.js "$b"
done
