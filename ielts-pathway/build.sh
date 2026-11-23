#!/usr/bin/env bash
# Build IELTS Pathway books: ./build.sh a1 [sb|wb] [--units 1,2] [--title "..."]
# Validates the level, then writes <level>/dist/<book>.pdf (both books if none is given).
set -euo pipefail
cd "$(dirname "$0")"
level=${1:?level, e.g. a1}; shift
books="sb wb"
if [[ ${1:-} == sb || ${1:-} == wb ]]; then books=$1; shift; fi
python3 scripts/validate.py "$level"
for b in $books; do
  python3 scripts/build.py "$level" "$b" "$@"
  HTML="$level/dist/$b.html" PDF="$level/dist/$b.pdf" node scripts/render.js
done
