#!/bin/bash
# jobfeed — build a curated job list. Run from anywhere; outputs land in the repo root.
#   run.sh                 new grad + internships   -> jobs.md    (5–10 min)
#   run.sh --senior        senior / experienced      -> senior.md  (~1 min)
#   run.sh [--senior] OUT  choose the output path
#   run.sh --help
set -e
# resolve symlinks so the root ./run.sh shim finds the real scripts dir
SRC="$0"; while [ -L "$SRC" ]; do D="$(cd "$(dirname "$SRC")" && pwd)"; SRC="$(readlink "$SRC")"; [ "${SRC#/}" = "$SRC" ] && SRC="$D/$SRC"; done
HERE="$(cd "$(dirname "$SRC")" && pwd)"; ROOT="$(cd "$HERE/../../.." && pwd)"; cd "$ROOT"
case "$1" in
  -h|--help) sed -n '2,6p' "$0"; exit 0;;
  --senior)
    OUT="$(cd "$(dirname "${2:-senior.md}")" && pwd)/$(basename "${2:-senior.md}")"
    echo "1/3 pulling careerin.ai";                 python3 "$HERE/pull_careerin.py"
    if [ -f data/boards.json ]; then echo "2/3 ATS boards cached (delete data/boards.json to refresh)"; else echo "2/3 fetching ATS boards"; python3 "$HERE/getboards.py"; fi
    echo "3/3 assembling $(basename "$OUT")";        python3 "$HERE/gen_senior.py" "$OUT"
    echo "done -> $OUT"; exit 0;;
esac
OUT="$(cd "$(dirname "${1:-jobs.md}")" && pwd)/$(basename "${1:-jobs.md}")"
echo "1/5 pulling sources";               python3 "$HERE/pull.py"
echo "2/5 fetching ATS boards";           python3 "$HERE/getboards.py"
echo "3/5 building curated lists";        python3 "$HERE/gen.py"
echo "4/5 building off-cycle intern list"; python3 "$HERE/offcycle.py"
echo "5/5 assembling $(basename "$OUT")"; python3 "$HERE/finalize.py" "$OUT"
echo "done -> $OUT"
