---
name: jobfeed
description: Build or refresh a curated job list (new grad, internships, or senior/experienced) from live sources, add or remove companies, and explain the output. Use when the user says refresh the list, add/remove a company, run the senior feed, or asks what a link marker means.
---

# jobfeed

You are inside the jobfeed repo. Everything is driven by two commands and one config file.

## Commands

| User wants | Run |
|---|---|
| New grad + internship list | `./run.sh` → `jobs.md` (5–10 min) |
| Senior / experienced list | `./run.sh --senior` → `senior.md` (~1 min) |
| Different output path | append it: `./run.sh out.md` / `./run.sh --senior out.md` |

Run them with Bash. They print one line per stage; the last line is `done -> <file>`. Then tell the user the row count from the `written` line and open or send the file.

## Adding or removing a company

Edit `companies.py` only:

1. **`TIER`** — add the company name to the closest bucket (`frontier AI`, `robotics / autonomy`, `space / hard tech`, `silicon / systems`, `elite quant`, `product infra`, `research lab`). **Spelling must match the job board exactly**; if unsure, grep the raw data: `grep -o '"company": *"[^"]*Stripe[^"]*"' newgrad_raw.json intern_raw.json careerin_raw.json | sort -u`.
2. **`FB`** — add a careers-page URL so rows never fall back to a web search.
3. Optionally **`board_tokens.json`** — add `"Company": [["greenhouse","slug"]]` (or `lever` / `ashby`) for exact posting links. The slug is in the URL of the company's job board.

To remove: delete the name from `TIER`. Never delete from `FB`.

Then re-run the relevant command. To check a company is present afterwards: `grep -c "^| Stripe" jobs.md`.

## Tuning the senior feed

`companies.py` → `SENIOR["queries"]`. Each query is one careerin.ai search:

- `type`: `ai_company_jobs` (any role at AI companies) or `ai_jobs` (AI/ML roles at any company)
- `domain`: for `ai_company_jobs` — `software_engineer`, `data_analyst`, `product_management`, `design`; for `ai_jobs` — `all_roles`, `ai_infrastructure`, `ai_researcher`, `robotics`, `computer_vision`, `deep_learning`, `llm`, `nlp`, `foundation_model`, `model_training`, `gen_ai`
- `seniority`: list of codes — 1 intern/new grad, 2 entry, 3 mid, 4 senior, 5 lead/staff, 6 director
- `workModel`: `[]` any, or codes 1 onsite, 2 remote, 3 hybrid

Add a second query to widen; results are merged and deduped. `us_only`, `cap_per_company`, and `exclude_titles` (a regex) are there too.

## Filters — location, work model, salary

`companies.py` → `FILTERS`. Applies to every feed (new grad, internships, senior). Empty means no constraint.

```python
FILTERS={"locations":["Seattle, WA","San Francisco","Remote"],   # substrings; "Remote" allows remote rows
         "work_model":["hybrid","remote"],                       # any subset of onsite / hybrid / remote
         "work_model_keep_unknown":True,                         # keep rows whose work model isn't stated
         "salary_min":150000,                                    # annual USD vs the TOP of the posted range
         "salary_min_strict":False}                              # False = rows with no posted pay are kept
```

When the user says "only remote", "Seattle or SF", "at least 150k": set the matching field, re-run, report the new row count. Don't set `salary_min_strict` unless they say so explicitly — most postings don't list pay, and strict mode deletes all of them. The senior feed has no salary data, so `salary_min` has no effect there.

## Reading the output

- `[apply]` exact posting · `[apply ⌕]` employer careers page · `[apply 🔍]` web search (no ATS or careers URL known). Names are the reliable part; links are best-effort.
- 🆕 = not in the previous version of the same output file. Delete the file to reset.
- 403/429 on Citadel, Tesla, Intel, Blue Origin are bot protection, not dead links.
- A missing company is almost always not in `TIER`, not a lack of openings. Check the raw data before saying a company has nothing.

## Do not

- Do not edit anything but `companies.py`, `board_tokens.json`, and `CLAUDE.md` unless asked to change the pipeline itself.
- Do not commit `*_raw.json`, `boards.json`, `built.json`, `offcycle.json` — they're regenerated and gitignored.
- Do not link to `jobright.ai/jobs/info/...` URLs; the pipeline deliberately re-resolves those to the employer.
