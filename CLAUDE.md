# jobs-skill

This repo *is* a Claude Code skill. The operating manual is `skills/jobfeed/SKILL.md` — read it and follow it; `/jobfeed` loads it automatically (via the `.claude/skills/jobfeed` symlink).

- Build: `./run.sh` (new grad + interns) or `./run.sh --senior`. Both are shims to `skills/jobfeed/scripts/run.sh`.
- Config: `companies.py` at the root. That's the only file to edit for results.
- Data: `data/` is regenerated every run and gitignored.
- Install elsewhere: `/plugin marketplace add anshulkc/jobs-skill` then `/plugin install jobfeed@jobs-skill`.

Keep `SKILL.md` under 500 lines; put detail in `skills/jobfeed/references/`.
