#!/bin/bash
# One command, start to finish. Output: jobs.md (or pass a path). Takes ~5-10 min, mostly network.
set -e; cd "$(dirname "$0")"
OUT="${1:-jobs.md}"
echo "1/5 pulling sources";            python3 pull.py
echo "2/5 fetching ATS boards";        python3 getboards.py
echo "3/5 building curated lists";     python3 gen.py
echo "4/5 building off-cycle intern list"; python3 offcycle.py
echo "5/5 assembling $OUT";            python3 finalize.py "$OUT"
echo "done -> $OUT"
