import sys,time,os; sys.path.insert(0,os.path.expanduser('~/emu'))
from drv import *
rom=sys.argv[1]; tag=sys.argv[2]; iters=int(sys.argv[3])
e=Emu(rom); e.click(100,100); e.keydown('Tab')
t0=time.time()
while time.time()-t0<24: time.sleep(1)
for i in range(3): e.click(128,310,hold=0.3); time.sleep(2)
e.click(65,290,hold=0.3); time.sleep(3); e.click(130,339,hold=0.3); time.sleep(8)
for i in range(8): e.click(245,330,hold=0.6); time.sleep(1.0)
e.click(160,300,hold=0.5); time.sleep(3)
e.click(160,272,hold=0.5); time.sleep(3)
n=0
for i in range(iters):
    e.key('x'); time.sleep(1.4)
    e.shot(EMU+f"/{tag}_{n:02d}.png"); n+=1
e.keyup('Tab'); e.close()
