"""Senior/experienced feed: careerin.ai's search endpoint (a Jobright front-end with seniority labels).
Filters live in companies.py -> SENIOR.  Codes: seniority 1 intern/new grad, 2 entry, 3 mid, 4 senior,
5 lead/staff, 6 director.  workModel 1 onsite, 2 remote, 3 hybrid.  type: ai_company_jobs | ai_jobs.
domain (ai_company_jobs): software_engineer, data_analyst, product_management, design, ...
domain (ai_jobs): all_roles, ai_infrastructure, ai_researcher, robotics, computer_vision, llm, nlp, ..."""
import json,sys,os,time,urllib.request
import os
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..'))
sys.path[:0]=[os.path.dirname(os.path.abspath(__file__)),ROOT]
os.makedirs(os.path.join(ROOT,'data'),exist_ok=True); os.chdir(os.path.join(ROOT,'data'))
from companies import SENIOR,FILTERS
WMCODE={'onsite':1,'remote':2,'hybrid':3}
def page(pos,cnt,body):
    r=urllib.request.Request(f"https://www.careerin.ai/swan/ai-site/search/jobs?position={pos}&count={cnt}",data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json","Referer":"https://www.careerin.ai/","User-Agent":"Mozilla/5.0"})
    for a in range(3):
        try: return json.load(urllib.request.urlopen(r,timeout=40))["result"].get("jobList") or []
        except Exception as e:
            if a==2: print("  page",pos,"failed:",e); return []
            time.sleep(2*(a+1))
seen={}
for q in SENIOR["queries"]:
    wm=q.get("workModel") or [WMCODE[w] for w in (FILTERS.get("work_model") or []) if w in WMCODE]
    body={"workModel":wm,"city":q.get("city",""),"seniority":q["seniority"],"radiusRange":50,"type":q["type"],"domain":q["domain"]}
    pos=0; got=0
    while pos<SENIOR.get("max_per_query",4000):
        jl=page(pos,100,body)
        if not jl: break
        new=0
        for x in jl:
            jid=x["jobResult"]["jobId"]
            if jid not in seen: seen[jid]=x; new+=1
        got+=new; pos+=100
        if new==0: break
    print(f"  {q['type']}/{q['domain']} seniority={q['seniority']}: {got} unique")
json.dump(list(seen.values()),open("careerin_raw.json","w")); print(f"careerin: {len(seen)} unique jobs")
