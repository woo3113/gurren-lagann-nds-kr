import os, sys, time, subprocess, signal
from Xlib import X, display, XK
from Xlib.ext import xtest
from PIL import Image
EMU=os.path.expanduser("~/emu")
env=dict(os.environ)
for l in open(EMU+"/env.sh"):
    l=l.strip()
    if l.startswith("export "):
        for kv in l[7:].split():
            k,v=kv.split("=",1); env[k]=v.replace("$HOME",os.path.expanduser("~")).replace("$EMU",EMU).replace("$LD_LIBRARY_PATH",env.get("LD_LIBRARY_PATH",""))
env["EMU"]=EMU
env["DISPLAY"]=":99"
class Emu:
    def __init__(self, rom, w=1024,h=768):
        subprocess.call("pkill Xvfb; pkill melonDS; sleep 1; rm -f /tmp/.X99-lock /tmp/.X11-unix/X99",shell=True); time.sleep(1)
        self.xv=subprocess.Popen(["Xvfb",":99","-screen","0",f"{w}x{h}x24"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        time.sleep(2)
        self.p=subprocess.Popen([EMU+"/squashfs-root/usr/bin/melonDS",rom],env=env,cwd=EMU,stdout=open(EMU+"/emu.log","w"),stderr=subprocess.STDOUT)
        time.sleep(3)
        for _ in range(20):
            try: self.d=display.Display(":99"); break
            except Exception: time.sleep(1)
        self.root=self.d.screen().root
    def shot(self,path=None):
        out=subprocess.run(["import","-window","root","png:-"],env=env,capture_output=True).stdout
        import io
        im=Image.open(io.BytesIO(out)).convert("RGB")
        if path: im.save(path)
        return im
    def key(self,name,hold=0.12):
        ks=XK.string_to_keysym(name); kc=self.d.keysym_to_keycode(ks)
        xtest.fake_input(self.d,X.KeyPress,kc); self.d.sync(); time.sleep(hold)
        xtest.fake_input(self.d,X.KeyRelease,kc); self.d.sync(); time.sleep(0.05)
    def keydown(self,name):
        kc=self.d.keysym_to_keycode(XK.string_to_keysym(name)); xtest.fake_input(self.d,X.KeyPress,kc); self.d.sync()
    def keyup(self,name):
        kc=self.d.keysym_to_keycode(XK.string_to_keysym(name)); xtest.fake_input(self.d,X.KeyRelease,kc); self.d.sync()
    def click(self,x,y,hold=0.15):
        xtest.fake_input(self.d,X.MotionNotify,x=x,y=y); self.d.sync(); time.sleep(0.05)
        xtest.fake_input(self.d,X.ButtonPress,1); self.d.sync(); time.sleep(hold)
        xtest.fake_input(self.d,X.ButtonRelease,1); self.d.sync(); time.sleep(0.05)
    def focus(self):
        # click into window to focus
        xtest.fake_input(self.d,X.MotionNotify,x=500,y=500); self.d.sync()
    def close(self):
        self.p.kill(); self.xv.kill()
