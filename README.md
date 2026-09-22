# jobs-skill

A Claude Code skill that builds a curated job list from live sources — new grad, internships (including off-cycle), or senior/experienced — into one Markdown file with employer-direct links.

## Use it in Claude Code

```
/plugin marketplace add anshulkc/jobs-skill
/plugin install jobfeed@jobs-skill
```

Or clone and open the folder — the skill is picked up automatically. Then:

> `/jobfeed` run the senior feed
> `/jobfeed` only remote or hybrid, Seattle or San Francisco
> `/jobfeed` add Waymo

## Use it by hand

```bash
git clone https://github.com/anshulkc/jobs-skill && cd jobs-skill
./run.sh --senior     # senior / experienced engineers  →  senior.md   (~1 min)
./run.sh              # new grad + internships          →  jobs.md     (5–10 min)
```

Python 3 and `curl`. No pip installs, no API keys.

**`companies.py` is the only file to edit** — which companies appear (`TIER`), location / remote / salary (`FILTERS`), and what the senior feed searches (`SENIOR`). Re-run after any change; new rows since last time are marked 🆕.

## Layout

```
skills/jobfeed/SKILL.md        the skill — what Claude reads
skills/jobfeed/scripts/        the pipeline (black boxes; run.sh --help)
skills/jobfeed/references/     endpoints, config fields, how to read the output
companies.py                   your config
run.sh                         shim → skills/jobfeed/scripts/run.sh
data/                          regenerated each run, gitignored
```

Follows the [Agent Skills spec](https://agentskills.io/specification); validates with `skills-ref validate skills/jobfeed`.

## Sources

SimplifyJobs (public) and two unofficial Jobright endpoints — documented in [`references/endpoints.md`](skills/jobfeed/references/endpoints.md). They can change without notice. Every link is re-resolved to the employer's own job page; none route through Jobright. Roughly 40% of postings turn over every two weeks, so re-running is the point.

MIT.
