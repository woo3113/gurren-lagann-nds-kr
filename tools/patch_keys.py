import re, sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\20_게임\_에뮬데이터\melonDS-1.1-windows-x86_64\melonDS.toml"
txt = open(p, encoding="utf-8").read()

# Qt key codes
KB = {"A":88,"B":90,"X":83,"Y":65,"L":81,"R":87,
      "Up":16777235,"Down":16777237,"Left":16777234,"Right":16777236,
      "Start":16777220,"Select":16777219,"HK_Pause":16777252,
      "HK_Reset":16777221,"HK_FastForwardToggle":16777274,"HK_FullscreenToggle":16777275}
JB = {"A":0,"B":1,"X":2,"Y":3,"L":4,"R":5,"Up":11,"Down":12,"Left":13,"Right":14,"Start":9,"Select":8}

def fix(section, mapping):
    global txt
    i = txt.find(section)
    if i < 0: return
    j = txt.find("[", i+1)
    body = txt[i:j if j>0 else len(txt)]
    for k,v in mapping.items():
        body = re.sub(rf'^{re.escape(k)} = -1$', f'{k} = {v}', body, flags=re.M)
    txt = txt[:i] + body + (txt[j:] if j>0 else "")

fix("[Instance0.Keyboard]", KB)
fix("[Instance0.Joystick]", JB)
open(p,"w",encoding="utf-8").write(txt)
print("updated")
print(txt[txt.find("[Instance0.Keyboard]"): txt.find("[Instance0.Audio]")])
