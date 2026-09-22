import json,re,difflib,urllib.request,urllib.parse,time,collections
ST=r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|DC)\b'
SEASON=re.compile(r'\b(summer|fall|winter|spring)\b',re.I); YEAR=re.compile(r'\b(202[5-9])\b')
def norm(s): return re.sub(r'[^a-z0-9 ]',' ',s.lower())
def compatible(st,sl,at,al):
    s,a=st.lower(),at.lower()
    si=any(k in s for k in("intern","co-op","coop")); ai=any(k in a for k in("intern","co-op","coop"))
    if si!=ai: return False,"level"
    ss,as_={x.lower() for x in SEASON.findall(s)},{x.lower() for x in SEASON.findall(a)}
    if ss and as_ and not ss&as_: return False,"season"
    sy,ay=set(YEAR.findall(s)),set(YEAR.findall(a))
    if sy and ay and not sy&ay: return False,"year"
    s1,s2=set(re.findall(ST,sl or "")),set(re.findall(ST,al or ""))
    if s1 and s2 and not s1&s2: return False,"location"
    return True,None
def resolve(boards,co,title,loc,floor=0.72):
    b=boards.get(co)
    if not b: return None
    c=[]
    for bt,u,bl in b:
        r=difflib.SequenceMatcher(None,norm(title),norm(bt)).ratio()
        if r<floor: continue
        ok,_=compatible(title,loc,bt,bl)
        if ok: c.append((r,u))
    return max(c)[1] if c else None
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=25))
def board(kind,tok):
    try:
        if kind=="greenhouse":
            d=get(f"https://boards-api.greenhouse.io/v1/boards/{tok}/jobs")
            return [(j["title"],j["absolute_url"],(j.get("location") or {}).get("name","")) for j in d.get("jobs",[])]
        if kind=="lever":
            d=get(f"https://api.lever.co/v0/postings/{tok}?mode=json")
            return [(j["text"],j["hostedUrl"],j.get("categories",{}).get("location","")) for j in d]
        if kind=="ashby":
            d=get(f"https://api.ashbyhq.com/posting-api/job-board/{tok}")
            return [(j["title"],j.get("jobUrl") or j.get("applyUrl",""),j.get("location","")) for j in d.get("jobs",[])]
    except Exception: return None
