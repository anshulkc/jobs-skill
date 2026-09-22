#!/bin/bash
# ./run.sh [out.md]            new grad + internships  (default jobs.md)
# ./run.sh --senior [out.md]   senior / experienced, from careerin.ai (default senior.md); filters in companies.py -> SENIOR
set -e; cd "$(dirname "$0")"
if [ "$1" = "--senior" ]; then
  OUT="${2:-senior.md}"
  echo "1/3 pulling careerin.ai";                  python3 pull_careerin.py
  [ -f boards.json ] || { echo "2/3 fetching ATS boards"; python3 getboards.py; } && echo "2/3 boards cached"
  echo "3/3 assembling $OUT";                      python3 gen_senior.py "$OUT"
  echo "done -> $OUT"; exit 0
fi
OUT="${1:-jobs.md}"
echo "1/5 pulling sources";            python3 pull.py
echo "2/5 fetching ATS boards";        python3 getboards.py
echo "3/5 building curated lists";     python3 gen.py
echo "4/5 building off-cycle intern list"; python3 offcycle.py
echo "5/5 assembling $OUT";            python3 finalize.py "$OUT"
echo "done -> $OUT"
