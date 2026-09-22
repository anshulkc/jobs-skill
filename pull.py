import json,urllib.request,subprocess
subprocess.run(["curl","-s","-o","listings_dev.json","https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json"])
print("simplify:",len(json.load(open("listings_dev.json"))),"listings")
def fetch(cat,pos,cnt=50):
    r=urllib.request.Request(f"https://jobright.ai/swan/mini-sites/list?position={pos}&count={cnt}",data=json.dumps({"category":cat}).encode(),headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r,timeout=30))["result"]
for grp,cats in [("newgrad",["newgrad:us:swe","newgrad:us:ml_ai","newgrad:us:data_engineer"]),("intern",["intern:us:swe","intern:us:ml_ai","intern:us:data_engineer"])]:
    all={}
    for c in cats:
        pos=0;tot=None
        while True:
            try: r=fetch(c,pos)
            except Exception as e: print("ERR",c,pos,e); break
            jl=r.get("jobList") or []
            if not jl: break
            for j in jl: all[j["jobId"]]=j
            pos+=len(jl); tot=r.get("total")
            if pos>=tot or pos>5000: break
        print(f"  {c}: {pos}/{tot}")
    json.dump(list(all.values()),open(f"{grp}_raw.json","w")); print(f"{grp}: {len(all)} unique")
