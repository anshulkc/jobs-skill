import json,re,sys,os,time,collections,urllib.parse
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..'))
sys.path[:0]=[os.path.dirname(os.path.abspath(__file__)),ROOT]
os.makedirs(os.path.join(ROOT,'data'),exist_ok=True); os.chdir(os.path.join(ROOT,'data'))
from lib import board,resolve
from companies import CO2T,NAME,FB
from filters import passes
from concurrent.futures import ThreadPoolExecutor
J=json.load(open("intern_raw.json")); boards=json.load(open("boards.json"))
OFF=re.compile(r'winter|spring|fall|autumn|off.?cycle|co-?op|january|q1',re.I)
BORING=re.compile(r'\bIT\b|help desk|technical support|marketing|sales|recruit|business analyst|accounting|audit|legal|communications|social media|content|ux |data entry|field service|technician|data collection|data label|operator|survey|program manag|product manag|project manag|supply chain|procurement|finance|hr\b|human resources|customer|clinical|nurse|pharmac|construction|civil|mechanical|electrical (design|power)|hvac|quality assurance|manufactur|logistics|analyst\b',re.I)
ENG=re.compile(r'software|swe\b|engineer|developer|machine learning|\bml\b|\bai\b|data science|research|robotic|autonom|embedded|firmware|compiler|systems|infrastructure|backend|full.?stack|security|quant',re.I)
FLUFF=re.compile(r'data annotation|transcription|survey participant|crowdsourc|labeling task|no experience|native speaker|residents -|unpaid|volunteer',re.I)
JUNK=re.compile(r'amtrak|medpace|fifth third|kinder morgan|phillips edison|ducharme|southwest airline|delta air|sanofi|wave life|rbc\b|fab2|hasana|parsonskellogg|university|college|school district|county|city of|state of|department of|bank\b|insurance|fidelity|bcbs|healthcare|health system|medical center|benefit solutions|cdphp|campbell|smucker|ameritas|olin\b|ahold|amazon|aws\b|etc\.',re.I)
pool=[]
for j in J:
    p=j["properties"]; t=p["title"]; co=p["company"]; s=p.get("hireTime") or ""
    if not OFF.search(s+" "+t) or BORING.search(t) or not ENG.search(t) or FLUFF.search((p.get("qualifications") or "")+" "+t): continue
    if JUNK.search(co) and co not in CO2T: continue
    if not passes(p["location"],p.get("workModel"),False,p.get("salary") or "")[0]: continue
    pool.append(dict(co=co,title=t,loc=p["location"],season=s,pay=p.get("salary") or "",ts=j["postedAt"]/1000,inmap=co in CO2T))
need=sorted({r["co"] for r in pool if r["co"] not in boards and r["co"] not in FB})
def slugs(co):
    b=re.sub(r'\b(inc|llc|corp|corporation|company|co|technologies|technology|labs|group|us|usa)\b\.?','',co.lower())
    return list(dict.fromkeys([re.sub(r'[^a-z0-9]','',b),re.sub(r'[^a-z0-9]','',co.lower())]))
def disc(co):
    for sl in slugs(co):
        if not sl: continue
        for k in ("greenhouse","lever","ashby"):
            b=board(k,sl)
            if b and len(b)>=2: return co,b
    return co,None
with ThreadPoolExecutor(max_workers=12) as ex:
    found=0
    for co,b in ex.map(disc,need):
        if b: boards[co]=b; found+=1
json.dump(boards,open("boards.json","w"))
rows=[]; seen=set(); cap=collections.Counter(); nweb=0
for r in sorted(pool,key=lambda z:-z["ts"]):
    k=(r["co"],re.sub(r'\W','',r["title"].lower())[:32])
    if k in seen or cap[r["co"]]>=6: continue
    seen.add(k)
    u=resolve(boards,r["co"],r["title"],r["loc"]); src="ats"
    if not u and r["co"] in FB: u,src=FB[r["co"]].replace("{q}",urllib.parse.quote(r["title"][:45])),"search"
    if not u and r["co"] in boards:
        first=boards[r["co"]][0][1]; u,src=(first.rsplit("/jobs",1)[0] if "/jobs" in first else first.rsplit("/",1)[0]),"search"
    if not u: u,src="https://www.google.com/search?q="+urllib.parse.quote(f'{r["co"]} {r["title"]} internship'),"web"; nweb+=1
    cap[r["co"]]+=1
    r.update(url=u,src=src,name=NAME.get(r["co"],r["co"]),days=int((time.time()-r["ts"])/86400),paytxt="—" if not r["pay"] or r["pay"]=="N/A" else r["pay"].replace("-","–"))
    rows.append(r)
json.dump(rows,open("offcycle.json","w"))
print(f"off-cycle: pool {len(pool)} ({len(pool)-sum(r['inmap'] for r in pool)} off-map) | auto-discovered {found}/{len(need)} boards | rows {len(rows)} | ats {sum(r['src']=='ats' for r in rows)} | careers {sum(r['src']=='search' for r in rows)} | web {nweb}")
