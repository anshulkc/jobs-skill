import json,sys,os; ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..'))
import os
sys.path[:0]=[os.path.dirname(os.path.abspath(__file__)),ROOT]
os.makedirs(os.path.join(ROOT,'data'),exist_ok=True); os.chdir(os.path.join(ROOT,'data'))
from lib import board
from concurrent.futures import ThreadPoolExecutor
T=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"board_tokens.json")))
out={}
def w(it):
    co,l=it
    for k,t in l:
        b=board(k,t)
        if b: return co,b
    return co,None
with ThreadPoolExecutor(max_workers=14) as ex:
    miss=[]
    for co,b in ex.map(w,T.items()):
        if b: out[co]=b
        else: miss.append(co)
json.dump(out,open("boards.json","w")); print(f"boards: {len(out)}/{len(T)} | missing: {', '.join(miss)}")
