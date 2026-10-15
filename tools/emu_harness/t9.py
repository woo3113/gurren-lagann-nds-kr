import sys,time,os; sys.path.insert(0,os.path.expanduser('~/emu'))
from drv import *
rom=sys.argv[1]; tag=sys.argv[2]; iters=int(sys.argv[3])
e=Emu(rom); e.click(100,100); e.keydown('Tab')
t0=time.time()
while time.time()-t0<24: time.sleep(1)
for i in range(3): e.click(128,310,hold=0.3); time.sleep(2)
e.click(65,290,hold=0.3); time.sleep(3); e.click(130,339,hold=0.3); time.sleep(8)
n=0
for i in range(iters):
    e.click(245,330,hold=0.6); time.sleep(0.8); e.key('x'); time.sleep(0.8)
    if i%2==1: e.shot(EMU+f"/{tag}_{n:02d}.png"); n+=1
e.keyup('Tab'); e.close()
