import json,re,sys,os,collections,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from gen import section,table
from companies import TITLE
TODAY=datetime.date.today().isoformat()
B=json.load(open("built.json")); OC=json.load(open("offcycle.json"))
def key(c,t): return (re.sub(r'\W','',c.lower())[:12],re.sub(r'\W','',t.lower())[:26])
seen=set(); dropped=0
for part in ["p1","p2","p3"]:
    kept=[]
    for r in B[part]:
        k=key(r["name"],r["title"])
        if k in seen: dropped+=1; continue
        seen.add(k); kept.append(r)
    B[part]=kept
OUT=sys.argv[1] if len(sys.argv)>1 else "jobs.md"
old=open(OUT).read() if os.path.exists(OUT) else ""
prev_date=(re.search(r'Refreshed (\d{4}-\d{2}-\d{2})',old) or [None,"?"])[1]
oldrows={key(c,re.sub(r'\s*\*\(PhD\)\*','',t)) for c,t in re.findall(r'^\| ([^|🆕]+?)(?: 🆕)? \| ([^|]+) \|.*\[apply',old,re.M)}
allrows=[r for p in B for r in B[p]]+OC
for r in allrows: r["new"]=key(r["name"],r["title"]) not in oldrows
newk={key(r["name"],r["title"]) for r in allrows}
gone=len(oldrows-newk); added=sum(r["new"] for r in allrows)
tot=len(allrows); ats=sum(1 for r in allrows if r["src"]=="ats")
offc=sum(1 for r in B["p3"] if re.search(r'fall|winter|spring|january',(r.get("season","")+r["title"]),re.I))
topnew=collections.Counter(r["name"] for r in allrows if r["new"]).most_common(10)
def oc_season(r):
    s=(r["season"]+" "+r["title"]).lower()
    if "winter" in s or "january" in s: return "Winter 2027 (Jan start)"
    if "spring" in s: return "Spring 2027"
    if "fall" in s or "autumn" in s: return "Fall 2026"
    return "Co-op (rolling / multi-term)"
ORDER=["Winter 2027 (Jan start)","Spring 2027","Fall 2026","Co-op (rolling / multi-term)"]
groups={k:[r for r in OC if oc_season(r)==k] for k in ORDER}
for k in groups: groups[k].sort(key=lambda z:(not z["inmap"],z["days"]))
oc_body="".join(f"\n### {k} — {len(groups[k])}\n\n{table(groups[k])}\n" for k in ORDER if groups[k])
nats=sum(r["src"]=="ats" for r in OC); nsr=sum(r["src"]=="search" for r in OC); nweb=sum(r["src"]=="web" for r in OC)
ng=len(json.load(open("newgrad_raw.json"))); it=len(json.load(open("intern_raw.json")))
prev_counts=re.search(r'\| Roles listed \| (\d[\d,]*) \| (\d[\d,]*) \|',old)
prev_tot=prev_counts.group(2) if prev_counts else "?"
prev_ng=(re.search(r'New grad postings in source \| [\d,]+ \| ([\d,]+)',old) or [None,"?"])[1]
prev_it=(re.search(r'Internship postings in source \| [\d,]+ \| ([\d,]+)',old) or [None,"?"])[1]
prev_ats=(re.search(r'Direct req links \| [\d,]+ \| ([\d,]+)',old) or [None,"?"])[1]
if old:
    CHANGES=f"""## What changed since {prev_date}

| | {prev_date} | {TODAY} |
|---|---|---|
| Roles listed | {prev_tot} | {tot} |
| New grad postings in source | {prev_ng} | {ng:,} |
| Internship postings in source | {prev_it} | {it:,} |
| Direct req links | {prev_ats} | {ats} |

**{added} roles are new** (marked 🆕) and **{gone} from the previous list are gone** — filled, expired, or pulled. {offc} of the curated internships are off-cycle.

Biggest additions: {", ".join(f"{c} ({n})" for c,n in topnew)}.
"""
else:
    CHANGES=f"""**First run — {tot} roles, {ats} with direct posting links.** Re-run later and this section becomes a diff: new roles get marked 🆕 and the header reports what came and went.
"""
    for r in allrows: r["new"]=False
doc=f"""# {TITLE}

*Refreshed {TODAY}.{" Previous pull was "+prev_date+"." if old else ""}*

Three sources, one selection method: roles picked on the work — frontier AI, robotics, space and hard tech, silicon, elite quant, serious product infrastructure — rather than on a salary threshold. Edit `companies.py` to change which companies appear.

- **Part 1** — new grad, SimplifyJobs repo (every link a direct ATS req)
- **Part 2** — new grad, Jobright API (wider net; carries companies SimplifyJobs doesn't)
- **Part 3a** — off-cycle internships (winter, spring, fall, co-op), looser gate
- **Part 3** — internships, all terms, curated companies

{CHANGES}
---

# Part 1 — New grad, from SimplifyJobs

`listings.json`, `active` and posted within 90 days, US only. Links are the strongest in the file: SimplifyJobs stores the employer ATS URL directly, so nothing needs resolving.
{section(B["p1"],pay=False)}
---

# Part 2 — New grad, from Jobright

`POST https://jobright.ai/swan/mini-sites/list` with `{{"category":"newgrad:us:swe"}}`, plus `ml_ai` and `data_engineer`. {ng:,} unique postings. Pay shown where listed, **—** where not; it is never a filter.
{section(B["p2"])}
---

# Part 3a — Off-cycle internships: Winter, Spring, Fall, Co-op

**{len(OC)} roles.** Deliberately looser gate than the rest of the file: only non-engineering titles and clearly non-tech employers are excluded, no company-list requirement. Amazon/AWS rows excluded. Curated-list companies sort first within each term.

- **[apply]** — direct link to the exact req ({nats})  ·  **[apply ⌕]** — employer careers page or search ({nsr})  ·  **[apply 🔍]** — web search, no ATS or careers URL known ({nweb})
{oc_body}
---

# Part 3 — Internships

Same endpoint, `intern:us:*`. {it:,} unique postings. Off-cycle seasons are **bolded**.
{section(B["p3"],season=True)}
---

"""
i=old.find("# Audit —")
doc+=old[i:] if i>=0 else "# Notes\n\nSee CLAUDE.md for how this file is built and what the link markers mean.\n"
open(OUT,"w").write(doc)
print(f"written: {tot} roles | new {added} | gone {gone} | direct {ats} | cross-part dupes removed {dropped}")
print("top new:",topnew)
