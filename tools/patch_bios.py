import re, sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\20_게임\_에뮬데이터\melonDS-1.1-windows-x86_64\melonDS.toml"
base = r"D:\20_게임\_에뮬데이터\melonDS-1.1-windows-x86_64"
txt = open(p, encoding="utf-8").read()
i = txt.find("[Emu]")
j = txt.find("\n[", i+1)
body = txt[i:j]
body = re.sub(r'ExternalBIOSEnable = .*', 'ExternalBIOSEnable = true', body)
body = re.sub(r'\nBIOS7Path = .*|$', '', body)
body += f'\nBIOS7Path = "{base}/biosnds7.rom"\nBIOS9Path = "{base}/biosnds9.rom"\nFirmwarePath = "{base}/firmware.bin"\nLimiterEnable = true'
txt = txt[:i] + body + txt[j:]
open(p,"w",encoding="utf-8").write(txt)
k = txt.find("[Emu]")
print(txt[k:k+300])
