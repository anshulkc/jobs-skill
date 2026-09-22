---
name: jobfeed
description: Builds and refreshes a curated job list — new grad, internships (including off-cycle), or senior/experienced — from live sources into one Markdown file with employer-direct links, and tunes it by company, location, work model, and salary. Use when the user wants a job list built or refreshed, asks to add or remove a company, wants only remote/hybrid/onsite or specific cities, asks why a company or role is missing, or asks what a link marker (⌕ 🔍 🆕) means.
license: MIT
compatibility: Requires Python 3 and curl, and network access to github.com, jobright.ai, careerin.ai, and public ATS boards (Greenhouse, Lever, Ashby).
metadata:
  author: anshulkc
  version: "1.0"
---

# jobfeed

One script, one config file. `scripts/run.sh` builds the list; `companies.py` at the repo root decides what's in it. Treat the scripts as black boxes — run `scripts/run.sh --help` rather than reading their source.

## Quick reference

| User says | Do |
|---|---|
| "refresh the list", "new grad / internships" | `scripts/run.sh` → `jobs.md` (5–10 min) |
| "senior roles", "experienced", "for my dad" | `scripts/run.sh --senior` → `senior.md` (~1 min) |
| "add Waymo" | find the exact spelling in `data/*_raw.json`, add to `TIER` and `FB` in `companies.py`, re-run |
| "remove X" | delete from `TIER` only, re-run |
| "only remote / hybrid", "Seattle or SF", "at least 150k" | set `FILTERS` in `companies.py`, re-run, report the new count |
| "why isn't X here?" | check `TIER` first; then `grep -c "X" data/*_raw.json` |
| "what does ⌕ / 🔍 / 🆕 mean?" | answer from [references/output.md](references/output.md) |

After a run, read the `written …` line for the row count and hand the user the output file.

## Rules

- **Only edit `companies.py`** (and `scripts/board_tokens.json` for exact links). Field-by-field guide: [references/config.md](references/config.md).
- **Company names must match the job board's spelling.** Wrong spelling = silently absent. Grep the raw data first.
- **Never set `salary_min_strict` unless the user says so.** Most postings list no pay; strict mode deletes them all.
- **Never link `jobright.ai/jobs/info/...` URLs.** The pipeline re-resolves every posting to the employer on purpose.
- **Don't commit `data/`, `jobs.md`, or `senior.md`.** They regenerate.

## Reading results

`[apply]` exact posting · `[apply ⌕]` employer careers page · `[apply 🔍]` web search. 🆕 = new since the previous run of that file; on a first run nothing is marked (there's nothing to compare against — don't describe that as "no turnover"). 403/429 on Citadel, Tesla, Intel, Blue Origin are bot protection, not dead links. Details: [references/output.md](references/output.md).

## Common mistakes

- Declaring a company has no openings because it's absent — it's almost always missing from `TIER`.
- Filtering by pay: pay is display-only by design; unpriced rows stay.
- Reading a `jobs.md` older than two weeks — ~40% of rows turn over; re-run instead.
- Editing pipeline scripts to change results — every knob is in `companies.py`.

## Sources

SimplifyJobs (public) plus two unofficial Jobright endpoints, documented with field codes in [references/endpoints.md](references/endpoints.md). If Jobright breaks, Part 1 of `jobs.md` still works; `senior.md` does not.
