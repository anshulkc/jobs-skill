# jobfeed

One command → a Markdown list of jobs at companies you choose, with apply links. Two feeds:

```bash
git clone <this repo> && cd jobfeed
./run.sh --senior     # senior / experienced engineers  →  senior.md   (~1 min)
./run.sh              # new grad + internships          →  jobs.md     (5–10 min)
```

Python 3 and `curl`. Nothing to install, no API keys.

**Everything you'd change is in `companies.py`:**

- `TIER` — which companies appear, and under which heading
- `FILTERS` — location, remote / hybrid / onsite, minimum salary
- `SENIOR` — what the senior feed searches for (role area, seniority level)

Re-running is the point: roughly 40% of postings turn over every two weeks. New rows since the last run are marked 🆕.

**Built for [Claude Code](https://claude.com/claude-code).** Open the folder and type `/jobfeed` — then "run the senior feed", "only remote, Seattle or SF", or "add Waymo". The skill in `.claude/skills/jobfeed/` and `CLAUDE.md` tell it everything. Works fine by hand too.

Sources are SimplifyJobs (public) and two Jobright front-ends (unofficial — may change without notice). Every link is re-resolved to the employer's own job page; none go through Jobright. MIT.
