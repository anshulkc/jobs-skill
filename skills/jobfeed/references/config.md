# companies.py — the only file a user edits

Lives at the repo root. Four settings.

## `TIER` — which companies appear, under which heading
```python
TIER={"frontier AI":["OpenAI","Anthropic",...], "robotics / autonomy":[...], "space / hard tech":[...],
      "silicon / systems":[...], "elite quant":[...], "product infra":[...], "research lab":[...]}
```
- **Names must match the job board's spelling exactly.** Several firms appear under 2–3 spellings ("Five Rings" / "Five Rings Capital", "Akuna Capital University"). Add each variant; use `NAME` to collapse them for display.
- To find the exact spelling: `grep -oh '"company": *"[^"]*Stripe[^"]*"' data/*_raw.json | sort -u`
- A company **not** in `TIER` is absent from the curated sections (Parts 1–3 and the senior "curated" block). It can still appear in the off-cycle section (Part 3a) and the senior "everything else" block, which don't require it.
- Remove a company by deleting it from `TIER`. Don't delete it from `FB`.

## `NAME` — display overrides
`{"The D. E. Shaw Group": "D. E. Shaw"}`

## `FB` — careers-page URL per company
Used when no exact posting can be matched. Add one whenever you add a company, or its rows fall back to a web-search link. `{q}` is replaced with the job title.

## `FILTERS` — applies to every feed
```python
FILTERS={"locations":["Seattle, WA","San Francisco","Remote"],  # substrings; "Remote" admits remote rows
         "work_model":["hybrid","remote"],                      # subset of onsite / hybrid / remote; [] = any
         "work_model_keep_unknown":True,                        # keep rows that don't state a work model
         "salary_min":150000,                                   # annual USD vs the TOP of the posted range
         "salary_min_strict":False}                             # False = rows with no posted pay are KEPT
```
Most postings list no pay; `salary_min_strict=True` deletes all of them. The senior source has no salary field, so `salary_min` doesn't affect `senior.md`.

## `SENIOR` — what the senior feed searches
```python
SENIOR={"queries":[{"type":"ai_company_jobs","domain":"software_engineer","seniority":[4,5],"workModel":[]}],
        "us_only":True, "cap_per_company":6, "max_per_query":4000,
        "exclude_titles": r"engineering manager|\bmanager,|head of|vp\b|sales|marketing|..."}
```
Add queries to widen (e.g. `{"type":"ai_jobs","domain":"ai_infrastructure","seniority":[4,5]}`); results merge and dedupe. Codes are in [endpoints.md](endpoints.md). `exclude_titles` is a regex over titles; set it to `r""` to keep everything.

## `scripts/board_tokens.json` — exact posting links
`{"Stripe": [["greenhouse","stripe"]], "Notion": [["ashby","notion"]]}`. Optional; without it a company's rows use `FB`. Find the slug in the URL of the company's job board.
