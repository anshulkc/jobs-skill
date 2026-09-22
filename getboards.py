import json,sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import board
from concurrent.futures import ThreadPoolExecutor
T=json.load(open("board_tokens.json"))
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
