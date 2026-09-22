import json,re,sys,os,time,urllib.parse,collections
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..'))
sys.path[:0]=[os.path.dirname(os.path.abspath(__file__)),ROOT]
os.makedirs(os.path.join(ROOT,'data'),exist_ok=True); os.chdir(os.path.join(ROOT,'data'))
from lib import resolve
from companies import CO2T,NAME,FB
from filters import passes
boards=json.load(open("boards.json")) if os.path.exists("boards.json") else {}
BORING=re.compile(r'\bIT\b|help desk|technical support|marketing|sales|recruit|business analyst|accounting|audit|legal|communications|social media|content writer|ux research|data entry|field service|technician|data collection|data label|operator|survey|program manager|product manager|deployment strategist|privacy & civil|teacher|nurse|clinical|driver|test \d|ZZZ',re.I)
DEEP=re.compile(r'compiler|kernel|gpu|cuda|distributed|systems|runtime|inference|training|infra|reinforcement|world model|autonomy|perception|robot|embedded|flight|silicon|verification|cryptograph|database|storage|scheduler|network|graphics|render|quantum|firmware|performance|latency|research|foundation model|llm|multimodal|eval|security|platform|backend|full.?stack|machine learning|software|developer|engineer|quant|scientist',re.I)
FLUFF=re.compile(r'data annotation|transcription|survey participant|crowdsourc|labeling task|no experience (is )?(required|necessary)|native speaker|residents -',re.I)
THEMES=[("frontier AI","Frontier AI / ML systems"),("robotics / autonomy","Robotics & autonomy"),("space / hard tech","Space & hard tech"),("silicon / systems","Silicon & systems"),("elite quant","Elite quant"),("product infra","Product & infrastructure"),("research lab","Research labs")]
def link(co,title,loc):
    u=resolve(boards,co,title,loc)
    if u: return u,"ats"
    f=FB.get(co)
    return (f.replace("{q}",urllib.parse.quote(title[:45])),"search") if f else (None,None)
def build(src,cap=4):
    rows=[]
    if src=="simplify":
        NONUS=re.compile(r'UK|United Kingdom|London|Ireland|Dublin|Canada|Toronto|Vancouver|Montreal|India|Germany|Munich|Netherlands|Amsterdam|Singapore|Japan|Australia|Manchester|Hong Kong',re.I)
        for j in json.load(open("listings_dev.json")):
            if not(j.get("active") and j.get("is_visible")) or j.get("date_posted",0)<time.time()-90*86400: continue
            if not re.search(r'Software|Quant|AI/ML',j.get("category","")): continue
            co=j["company_name"]; t=j["title"]; loc=" / ".join(j.get("locations") or [])
            if co not in CO2T or BORING.search(t) or not DEEP.search(t): continue
            if NONUS.search(loc) and not re.search(r'\b(CA|NY|WA|TX|IL|MA|CO|FL|GA|PA|VA|DC|NC|AZ|UT|OH|MD|NJ|MN|OR|TN)\b|United States|Remote in USA',loc): continue
            if not passes(loc,None,"remote" in loc.lower(),"")[0]: continue
            rows.append(dict(co=co,title=t,loc=loc,ts=j["date_posted"],pay="",url=j["url"],src="ats"))
    else:
        for j in json.load(open(f"{src}_raw.json")):
            p=j["properties"]; co=p["company"]; t=p["title"]; q=p.get("qualifications") or ""
            if co not in CO2T or BORING.search(t) or not DEEP.search(t) or FLUFF.search(q+" "+t): continue
            if not passes(p["location"],p.get("workModel"),False,p.get("salary") or "")[0]: continue
            rows.append(dict(co=co,title=t,loc=p["location"],ts=j["postedAt"]/1000,pay=(p.get("salary") or ""),season=p.get("hireTime") or "",url=None,src=None))
    seen=set(); cnt=collections.Counter(); keep=[]
    for r in sorted(rows,key=lambda z:-z["ts"]):
        k=(r["co"],re.sub(r'\W','',r["title"].lower())[:32])
        if k in seen: continue
        seen.add(k); tier=CO2T[r["co"]]
        if cnt[(r["co"],tier)]>=cap: continue
        if not r["url"]:
            u,s=link(r["co"],r["title"],r["loc"])
            if not u: u,s="https://www.google.com/search?q="+urllib.parse.quote(f'{r["co"]} {r["title"]}'),"web"
            r["url"],r["src"]=u,s
        cnt[(r["co"],tier)]+=1
        r.update(tier=tier,name=NAME.get(r["co"],r["co"]),days=int((time.time()-r["ts"])/86400))
        p=r["pay"].strip(); r["paytxt"]="—" if (not p or p=="N/A") else p.replace("-","–")
        keep.append(r)
    return keep
def table(l,pay=True,season=False):
    h="| Company | Role | Location |"+(" Season |" if season else "")+(" Pay (if listed) |" if pay else "")+" Age | Link |"
    o=[h,"|"+"---|"*(h.count("|")-1)]
    for r in sorted(l,key=lambda z:z["days"]):
        t=r["title"].replace("|","/")[:62]; phd=" *(PhD)*" if re.search(r'ph\.?\s?d',r["title"],re.I) else ""
        row=f"| {r['name']}{' 🆕' if r.get('new') else ''} | {t}{phd} | {r['loc'].replace('|','/')[:28]} |"
        if season:
            se=r.get("season") or "—"
            if re.search(r'fall|winter|spring|january',(r.get('season','')+r['title']),re.I): se="**"+(se if se!="—" else "off-cycle")+"**"
            row+=f" {se} |"
        if pay: row+=f" {r['paytxt'][:22]} |"
        row+=f" {r['days']}d | [apply{'' if r['src']=='ats' else (' ⌕' if r['src']=='search' else ' 🔍')}]({r['url']}) |"
        o.append(row)
    return "\n".join(o)
def section(rows,pay=True,season=False):
    return "".join(f"\n### {lab}\n\n{table([r for r in rows if r['tier']==k],pay,season)}\n" for k,lab in THEMES if any(r["tier"]==k for r in rows))
if __name__=="__main__":
    out={lab:build(src) for src,lab in [("simplify","p1"),("newgrad","p2"),("intern","p3")]}
    for k,v in out.items(): print(f"{k}: {len(v)} rows | ats {sum(1 for r in v if r['src']=='ats')}")
    json.dump(out,open("built.json","w"))
