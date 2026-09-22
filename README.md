# jobfeed

One command → a Markdown list of new-grad and internship roles at companies you choose, with direct apply links.

```bash
git clone <this repo> && cd jobfeed
./run.sh
open jobs.md
```

Edit `companies.py` to change which companies show up. That's the whole interface.

Built to be driven by [Claude Code](https://claude.com/claude-code): open the folder and ask it to "add Stripe" or "refresh the list" — `CLAUDE.md` tells it everything it needs. Works fine by hand too.

Python 3 + `curl`, nothing else. MIT.
