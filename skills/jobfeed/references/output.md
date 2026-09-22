# Reading the output

## jobs.md — new grad + internships
| Part | What | Gate |
|---|---|---|
| 1 | New grad, SimplifyJobs | `TIER` — every link a direct posting |
| 2 | New grad, Jobright | `TIER` |
| 3a | Off-cycle internships (winter / spring / fall / co-op) | **loose** — only non-engineering titles and non-tech employers excluded |
| 3 | Internships, all terms | `TIER` |

Header shows counts vs the previous `jobs.md` and marks new rows 🆕. Delete `jobs.md` to reset the diff.

## senior.md
Curated-list companies grouped by theme, then everything else grouped by employer size (largest first) — promote any by adding it to `TIER`. Columns include seniority label, min years, company size, and posted-ago.

## Link markers
- `[apply]` — exact posting on the employer's ATS (title matched with level/season/year/state checks)
- `[apply ⌕]` — the employer's careers page or search; find the role there
- `[apply 🔍]` — no ATS or careers URL known; a web search for company + title

Names are the reliable part. Links are best-effort and never route through Jobright.

## Things that look like bugs but aren't
- **403 / 429 when checking links by script** — Citadel, Tesla, Intel, Blue Origin block automation; they open in a browser.
- **A big company is missing** — it isn't in `TIER`. Check the raw data before concluding it has no openings.
- **Rows with no pay** — kept on purpose. Pay is shown, never gated, unless `salary_min_strict`.
- **~40% of rows change every two weeks** — re-run rather than read a stale file.
