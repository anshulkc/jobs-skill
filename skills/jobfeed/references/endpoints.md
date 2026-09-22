# Sources and endpoints

All three are public-but-unofficial. If one breaks, the others still work.

## SimplifyJobs (new grad) — clean, public
`https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json` — ~20k listings, fields `company_name, title, url, locations, active, date_posted, category`. Every `url` is the employer's ATS. Used by Part 1.

## Jobright minisite API (new grad + internships)
Powers `newgrad-jobs.com` and `intern-list.com` (both are Webflow shells iframing Jobright).
```
POST https://jobright.ai/swan/mini-sites/list?position=0&count=50
{"category": "newgrad:us:swe"}
```
- `category` = `type:country:area`. Types `newgrad`, `intern`. Countries `us`, `ca`. Areas include `swe`, `ml_ai`, `data_engineer`, `cyber_security`, `product_management`.
- Page by `position` until an empty `jobList`. `count` up to 50.
- Useful fields: `properties.title/company/location/salary/hireTime/workModel/h1bSponsored`, `postedAt` (ms). `hireTime` carries the term (`2027-Spring`, `2026-Fall`).
- `qualifications` is truncated at ~270 chars — don't score on it. `salary` mixes `/hr`, `/wk`, `/mo`, `/yr`.
- `applyUrl` is a `jobright.ai` redirect gated behind login. Never link it; resolve against the employer instead.

## careerin.ai search (senior / experienced)
Another Jobright front-end, with a real seniority label per posting.
```
POST https://www.careerin.ai/swan/ai-site/search/jobs?position=0&count=100
{"type":"ai_company_jobs","domain":"software_engineer","seniority":[4,5],"workModel":[],"city":"","radiusRange":50}
```
| field | values |
|---|---|
| `type` | `ai_company_jobs` (any role at AI companies) · `ai_jobs` (AI/ML roles anywhere) |
| `domain` under `ai_company_jobs` | `software_engineer`, `data_analyst`, `product_management`, `design`, `customer_success`, `sales`, `marketing`, `finance`, `human_resources` |
| `domain` under `ai_jobs` | `all_roles`, `ai_framework`, `ai_infrastructure`, `ai_researcher`, `robotics`, `computer_vision`, `deep_learning`, `foundation_model`, `gen_ai`, `llm`, `model_training`, `nlp`, `prompt_engineer` |
| `seniority` | list of codes: 1 intern/new grad · 2 entry · 3 mid · 4 senior · 5 lead/staff · 6 director |
| `workModel` | list: 1 onsite · 2 remote · 3 hybrid (empty = any) |
| `city` + `radiusRange` | geo filter; the only text field the server honors |

Page by `position` in steps of 100 until empty. `count` ≥ ~200 returns HTTP 500. ~2,500 rows for senior+lead SWE. No salary field. Params like `keyword`, `sort`, `companyId` are silently ignored. `applyLink` is a jobright redirect — resolve against the employer.

## Employer ATS boards (link resolution)
Public JSON, no auth:
- Greenhouse `https://boards-api.greenhouse.io/v1/boards/<slug>/jobs`
- Lever `https://api.lever.co/v0/postings/<slug>?mode=json`
- Ashby `https://api.ashbyhq.com/posting-api/job-board/<slug>`

Slugs live in `scripts/board_tokens.json`. Titles are matched with a level / season / year / US-state gate (`lib.compatible`) — similarity alone links interns to full-time reqs and Fall to Winter. Workday tenants can be queried at `<tenant>.wdN.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs` but rate-limit hard; not used by default. Big boards (SpaceX, 2.5k postings) need a long timeout.
