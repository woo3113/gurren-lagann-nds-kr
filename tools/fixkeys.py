import bspc,collections
S=bspc.F["spc"]
first={}
for e in S:
    if e["file"] not in first or e["off"]<first[e["file"]]["off"]: first[e["file"]]=e
H={e["text"] for e in first.values() if e["off"]==22}
man={'アダイ村入り口':'아다이 입구','アダイ村食事処':'아다이 식당','ジーハ村採掘場':'지하 채굴장'}
for ch in 'ＡＢＣＤＥＦ': man['ジーハ村通路'+ch]='지하통로'+ch
def apply():
    n=0
    for e in S:
        if e["text"] in man: e["ko"]=man[e["text"]]; n+=1
    # consistency + uniqueness of key translations
    m=collections.defaultdict(set)
    for e in S:
        if e["text"] in H: m[e["text"]].add(e["ko"])
    incons={t:v for t,v in m.items() if len(v)>1}
    inv=collections.defaultdict(set)
    for t,v in m.items():
        for k in v: inv[k].add(t)
    coll={k:v for k,v in inv.items() if len(v)>1}
    return n,incons,coll
if __name__=="__main__":
    n,i,c=apply(); print(n,"overridden; inconsistent:",len(i),"collisions:",len(c))
    for t,v in list(i.items())[:15]: print(' inc',t,v)
    for k,v in list(c.items())[:15]: print(' col',k,v)
