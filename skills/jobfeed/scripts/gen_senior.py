import json,re,sys,os,time,collections,datetime,urllib.parse
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..'))
sys.path[:0]=[os.path.dirname(os.path.abspath(__file__)),ROOT]
os.makedirs(os.path.join(ROOT,'data'),exist_ok=True); os.chdir(os.path.join(ROOT,'data'))
from lib import resolve
from companies import CO2T,NAME,FB,TITLE,SENIOR,FILTERS
from filters import passes
OUT=sys.argv[1] if len(sys.argv)>1 else "senior.md"
J=json.load(open("careerin_raw.json")); boards=json.load(open("boards.json")) if os.path.exists("boards.json") else {}
US=re.compile(r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|DC)\b|United States|USA\b')
BORING=re.compile(SENIOR.get("exclude_titles",r'engineering manager|\bmanager,|head of|vp\b|vice president|sales|marketing|recruit|account (exec|manag)|customer success|solutions? (engineer|architect|consultant)|functional analyst|program manag|project manag|finance|accounting|legal|hr\b|talent|support engineer|technical writer|instructor|clinical'),re.I)
rows=[]
for x in J:
    j,c=x["jobResult"],x["companyResult"]; loc=j.get("jobLocation") or ""; co=c.get("companyName") or "?"
    if SENIOR.get("us_only",True) and not (US.search(loc) or j.get("isRemote")): continue
    if BORING.search(j.get("jobTitle","")): continue
    if not passes(loc,j.get("workModel"),j.get("isRemote"),"")[0]: continue
    rows.append(dict(co=co,name=NAME.get(co,co),title=j["jobTitle"],loc=loc,remote=j.get("isRemote"),wm=j.get("workModel"),
        sen=j.get("jobSeniority"),yrs=j.get("minYearsOfExperience"),size=(c.get("companySize") or "").replace(" employees",""),
        stage=c.get("fundraisingCurrentStage") or "",posted=j.get("publishTimeDesc") or "",ts=j.get("publishTime") or "",
        jid=j["jobId"],summary=(j.get("jobSummary") or "")[:160],inmap=co in CO2T,tier=CO2T.get(co)))
# auto-discover boards for companies with no cached board and no fallback URL (slugified-name guesses)
from lib import board
from concurrent.futures import ThreadPoolExecutor
need=sorted({r["co"] for r in rows if r["co"] not in boards and r["co"] not in FB})
def slugs(co):
    b=re.sub(r'\b(inc|llc|corp|corporation|company|co|technologies|technology|labs|group|us|usa|ai)\b\.?','',co.lower())
    return list(dict.fromkeys([re.sub(r'[^a-z0-9]','',b),re.sub(r'[^a-z0-9]','',co.lower())]))
def disc(co):
    for sl in slugs(co):
        if not sl: continue
        for k in ("greenhouse","lever","ashby"):
            b=board(k,sl)
            if b and len(b)>=2: return co,b
    return co,None
found=0
with ThreadPoolExecutor(max_workers=12) as ex:
    for co,b in ex.map(disc,need):
        if b: boards[co]=b; found+=1
if found: json.dump(boards,open("boards.json","w"))
print(f"auto-discovered boards for {found} of {len(need)} unmapped companies")
# dedupe (company,title,loc), cap per company
seen=set(); cap=collections.Counter(); keep=[]
for r in sorted(rows,key=lambda z:z["ts"],reverse=True):
    k=(r["co"],re.sub(r'\W','',r["title"].lower())[:36],r["loc"][:12])
    if k in seen or cap[r["co"]]>=SENIOR.get("cap_per_company",6): continue
    seen.add(k); cap[r["co"]]+=1
    u=resolve(boards,r["co"],r["title"],r["loc"]); src="ats"
    if not u and r["co"] in FB: u,src=FB[r["co"]].replace("{q}",urllib.parse.quote(r["title"][:45])),"search"
    if not u: u,src="https://www.google.com/search?q="+urllib.parse.quote(f'{r["co"]} {r["title"]}'),"web"
    r.update(url=u,src=src); keep.append(r)
old=open(OUT).read() if os.path.exists(OUT) else ""
oldids=set(re.findall(r'<!--(\w{24})-->',old))
for r in keep: r["new"]=bool(old) and r["jid"] not in oldids
def table(l):
    o=["| Company | Role | Location | Level | Yrs | Size | Posted | Link |","|---|---|---|---|---|---|---|---|"]
    for r in l:
        tag={"ats":"","search":" ⌕","web":" 🔍"}[r["src"]]
        o.append(f"| {r['name']}{' 🆕' if r['new'] else ''} | {r['title'].replace('|','/')[:60]} | {r['loc'][:22]}{' (remote)' if r['remote'] else ''} | {r['sen'] or '—'} | {r['yrs'] if r['yrs'] is not None else '—'} | {r['size'] or '—'} | {r['posted']} | [apply{tag}]({r['url']})<!--{r['jid']}--> |")
    return "\n".join(o)
THEMES=[("frontier AI","Frontier AI / ML systems"),("robotics / autonomy","Robotics & autonomy"),("space / hard tech","Space & hard tech"),("silicon / systems","Silicon & systems"),("elite quant","Elite quant"),("product infra","Product & infrastructure"),("research lab","Research labs")]
curated=[r for r in keep if r["inmap"]]; rest=[r for r in keep if not r["inmap"]]
SIZEORD={"10001+":0,"5001-10000":1,"1001-5000":2,"501-1000":3,"201-500":4,"51-200":5,"11-50":6,"2-10":7}
rest.sort(key=lambda r:(SIZEORD.get(r["size"],9),r["ts"]),reverse=False)
by_size=collections.OrderedDict()
for r in rest: by_size.setdefault(r["size"] or "unknown",[]).append(r)
TODAY=datetime.date.today().isoformat()
q=SENIOR["queries"][0]
doc=f"""# {TITLE} — senior

*Refreshed {TODAY}.* Source: careerin.ai search (`type={q['type']}`, `domain={q['domain']}`, seniority codes {q['seniority']}). {len(J):,} postings pulled, {len(keep)} after US/remote filter, title exclusions, and a cap of {SENIOR.get('cap_per_company',6)} per company. {sum(r['new'] for r in keep)} new since the previous run (🆕).

Link markers: **[apply]** exact posting on the employer's ATS · **[apply ⌕]** employer careers page · **[apply 🔍]** web search. Every source link here is a jobright.ai redirect, so links are re-resolved against the employer; names are the reliable part.

## Companies on the curated list — {len(curated)}
"""
for k,lab in THEMES:
    g=[r for r in curated if r["tier"]==k]
    if g: doc+=f"\n### {lab} — {len(g)}\n\n{table(sorted(g,key=lambda r:r['ts'],reverse=True))}\n"
doc+=f"\n## Everything else, by company size — {len(rest)}\n\nNot on the curated list; sorted largest employer first. Add any of these to `companies.py` to promote them.\n"
for sz,g in by_size.items(): doc+=f"\n### {sz} — {len(g)}\n\n{table(g)}\n"
open(OUT,"w").write(doc)
print(f"written {OUT}: {len(keep)} rows | curated {len(curated)} | other {len(rest)} | ats {sum(r['src']=='ats' for r in keep)} | careers {sum(r['src']=='search' for r in keep)} | web {sum(r['src']=='web' for r in keep)} | new {sum(r['new'] for r in keep)}")
