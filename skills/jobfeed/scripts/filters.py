"""Row filters shared by every feed. Configure in companies.py -> FILTERS. Empty list / None = no constraint."""
import re,sys,os
import os
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..'))
sys.path[:0]=[os.path.dirname(os.path.abspath(__file__)),ROOT]
os.makedirs(os.path.join(ROOT,'data'),exist_ok=True); os.chdir(os.path.join(ROOT,'data'))
from companies import FILTERS
_WM={"onsite":"onsite","on site":"onsite","on-site":"onsite","in person":"onsite","in-person":"onsite","hybrid":"hybrid","remote":"remote"}
def norm_wm(s,is_remote=False):
    if is_remote: return "remote"
    return _WM.get((s or "").strip().lower(),None)
def annual(s):
    """'$120,000-$150,000/yr' | '$55/hr' | '$9,000/mo' -> (lo,hi) annual USD, or None."""
    if not s or s=="N/A": return None
    m=re.search(r'/(hr|yr|mon|mo|wk)\b',s); n=[float(x.replace(",","")) for x in re.findall(r'\$\s*([\d,]+(?:\.\d+)?)',s)]
    if not m or not n: return None
    k={"hr":2080,"yr":1,"mon":12,"mo":12,"wk":52}[m.group(1)]; lo,hi=min(n)*k,max(n)*k
    return None if hi>2_000_000 or hi<15_000 else (lo,hi)
def passes(loc="",work_model=None,is_remote=False,salary=""):
    """Return (ok, reason). Applies FILTERS['locations'], ['work_model'], ['salary_min'] (+ 'salary_min_strict')."""
    L=[x.lower() for x in FILTERS.get("locations") or []]
    wm=norm_wm(work_model,is_remote)
    if L:
        want_remote="remote" in L
        hit=any(x!="remote" and x in (loc or "").lower() for x in L) or (want_remote and (wm=="remote" or "remote" in (loc or "").lower()))
        if not hit: return False,"location"
    W=[x.lower() for x in FILTERS.get("work_model") or []]
    if W:
        if wm is None:
            if not FILTERS.get("work_model_keep_unknown",True): return False,"work_model_unknown"
        elif wm not in W: return False,"work_model"
    smin=FILTERS.get("salary_min")
    if smin:
        a=annual(salary)
        if a is None:
            if FILTERS.get("salary_min_strict",False): return False,"salary_unknown"
        elif a[1]<smin: return False,"salary"
    return True,None
