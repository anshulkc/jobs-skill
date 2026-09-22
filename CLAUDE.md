# jobfeed

A curated new-grad and internship job list, rebuilt from live sources in one command. Output is a single Markdown file (`jobs.md`) with direct application links.

## Run it

```bash
./run.sh                 # new grad + internships → jobs.md (5–10 min, mostly network)
./run.sh --senior        # senior / experienced → senior.md (~1 min)
./run.sh out.md          # either form takes an output path
```

There is also a Claude Code skill in `.claude/skills/jobfeed/` — inside this folder, `/jobfeed` knows all of the below.

Needs only Python 3 and `curl`. No pip installs, no API keys.

Re-running is safe and expected: it re-pulls everything, marks roles that weren't in the previous `jobs.md` with 🆕, and reports how many roles came and went in the header.

## Customize — this is the only file to edit

`companies.py` holds three things:

- **`TIER`** — which companies appear, grouped into theme buckets (`frontier AI`, `robotics / autonomy`, `space / hard tech`, `silicon / systems`, `elite quant`, `product infra`, `research lab`). **A company not in `TIER` will not appear in Parts 1–3.** Add a name exactly as the job board spells it.
- **`NAME`** — display-name overrides (`"The D. E. Shaw Group": "D. E. Shaw"`).
- **`FB`** — a careers-page URL per company, used when no exact posting link can be found. Add one whenever you add a company; otherwise its rows fall back to a web search.
- **`TITLE`** — the heading of the output file.

- **`FILTERS`** — location substrings (add `"Remote"` to allow remote), work model as any subset of `onsite`/`hybrid`/`remote`, and `salary_min` in annual USD. Empty = no constraint. Rows with no posted pay are kept unless `salary_min_strict`. Applies to every feed.

Optionally `board_tokens.json` maps a company to its Greenhouse / Lever / Ashby board slug so rows get exact posting links. To find a slug: the company's careers page usually links to `boards.greenhouse.io/<slug>`, `jobs.lever.co/<slug>`, or `jobs.ashbyhq.com/<slug>`.

When asked to add a company: add it to `TIER` (pick the closest bucket), add an `FB` URL, and if you can find its board slug, add it to `board_tokens.json`. Then re-run.

## Senior mode — a different source

`--senior` doesn't use the new-grad sources at all. It queries **careerin.ai**, another Jobright front-end whose search endpoint carries a real seniority label per posting:

```
POST https://www.careerin.ai/swan/ai-site/search/jobs?position=0&count=100
{"type":"ai_company_jobs","domain":"software_engineer","seniority":[4,5],"workModel":[],"city":"","radiusRange":50}
```

Page by `position` in steps of 100 until an empty page (~2,500 rows for senior+lead SWE at AI companies; `count` above ~200 returns 500s). Codes and domains are listed in `companies.py` next to `SENIOR`. Every `applyLink` it returns is a `jobright.ai` redirect, so `gen_senior.py` re-resolves against the employer exactly as the new-grad path does. Output groups curated-list companies by theme first, then everything else by employer size.

## What the output means

Four parts. Parts 1–3 are gated on the `TIER` list; Part 3a is deliberately looser.

| Part | What | Source |
|---|---|---|
| 1 | New grad | SimplifyJobs GitHub repo — every link is a direct posting |
| 2 | New grad | Jobright — wider net, includes companies SimplifyJobs doesn't index |
| 3a | **Off-cycle internships** (winter / spring / fall / co-op) | Jobright — company list **not** required, only junk excluded |
| 3 | Internships, all terms | Jobright — curated companies |

Link markers on every row:

- `[apply]` — exact posting, matched on title with level / season / year / US-state checks
- `[apply ⌕]` — the employer's careers page or search; find the role there
- `[apply 🔍]` — no ATS or careers URL known; a web search for company + title

Pay is shown when the posting lists it and is **never a filter**. Rows with no pay listed are kept.

## How the pieces fit

```
pull.py       → newgrad_raw.json, intern_raw.json, listings_dev.json   (sources)
getboards.py  → boards.json                                             (live ATS boards, from board_tokens.json)
gen.py        → built.json                                              (Parts 1–3, curated)
offcycle.py   → offcycle.json                                           (Part 3a, loose gate, auto-discovers boards)
finalize.py   → jobs.md                                                 (dedupe across parts, diff vs previous, write)
lib.py                                                                  (title matching + ATS fetch helpers)
```

Everything in `.gitignore` is regenerated each run. Nothing is cached between runs except `jobs.md` (for the diff).

## Sources, honestly

- **SimplifyJobs** (`github.com/SimplifyJobs/New-Grad-Positions`) — public, community-curated, US new grad. Clean.
- **Jobright** — an undocumented endpoint (`POST jobright.ai/swan/mini-sites/list`) that their partner sites embed. Not an official API; it can change or block without notice. The original apply URL is gated behind login, so this tool never uses Jobright's links — it re-resolves every posting against the employer's own ATS. If Jobright breaks, Parts 2, 3, and 3a go empty and Part 1 still works.

## Things that look like bugs but aren't

- **Some links return 403 / 429 to scripts** — Citadel, Tesla, Intel, Blue Origin and a few others block automated requests. They open normally in a browser.
- **A big company is missing** — it's almost certainly not in `TIER`. Add it; don't assume it has no openings.
- **Turnover is ~40% every two weeks.** A `jobs.md` older than that is stale. Re-run rather than reading an old one.
- **`qualifications` text from Jobright is truncated** at ~270 characters, so nothing in this tool scores on it.
