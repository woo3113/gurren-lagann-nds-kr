import sys,time,os,json; sys.path.insert(0,os.path.expanduser('~/emu'))
from drv import *
import bspc
E5=[i for i,e in enumerate(bspc.F["spc"]) if e["file"]=="EV_005.SPC"]
files=E5
ST=os.path.expanduser("~/mnt/그랜라간/work/bisect_ev5.json")
st=json.load(open(ST)) if os.path.exists(ST) else {"cur":files,"log":[]}
def test(fs):
    S=set(fs); IDX={id(e):i for i,e in enumerate(bspc.F["spc"])}; bspc.build(EMU+"/b.nds","fw",lambda e:IDX[id(e)] in S)
    e=Emu(EMU+"/b.nds"); e.click(100,100); e.keydown('Tab')
    t0=time.time()
    while time.time()-t0<24: time.sleep(1)
    for i in range(3): e.click(128,310,hold=0.3); time.sleep(2)
    e.click(65,290,hold=0.3); time.sleep(3); e.click(130,339,hold=0.3); time.sleep(3)
    ok=False; t1=time.time()
    while time.time()-t1<16:
        e.key('x'); time.sleep(1.2)
        im=e.shot().crop((0,19,256,211)); px=list(im.getdata())
        if sum(1 for p in px if max(p)>60)/len(px)>0.4: ok=True; break
    e.keyup('Tab'); e.close(); return ok
for _ in range(int(sys.argv[1])):
    cur=st["cur"]
    if len(cur)<=1: print("DONE",cur); break
    A=cur[:len(cur)//2]; B=cur[len(cur)//2:]
    ok=test(A); st["log"].append((len(A),"OK" if ok else "HANG"))
    st["cur"]=B if ok else A
    print(len(cur),"->",len(st["cur"]),"A is","OK" if ok else "HANG",flush=True)
    json.dump(st,open(ST,"w"))
print(st["cur"])
