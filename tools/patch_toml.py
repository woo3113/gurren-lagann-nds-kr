import io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\20_게임\_에뮬데이터\melonDS-1.1-windows-x86_64\melonDS.toml"
base = r"D:\20_게임\_에뮬데이터\melonDS-1.1-windows-x86_64"
txt = open(p, encoding="utf-8").read()
lines = txt.splitlines()
# insert BIOS keys at root level (before first section header)
out = []
inserted = False
for ln in lines:
    if not inserted and ln.strip().startswith("[") and ln.strip().endswith("]"):
        out.append(f'BIOS7Path = "{base}\\biosnds7.rom"')
        out.append(f'BIOS9Path = "{base}\\biosnds9.rom"')
        out.append(f'FirmwarePath = "{base}\\firmware.bin"')
        out.append('ExternalBIOSEnable = true')
        out.append('ConsoleType = 0')
        inserted = True
    if ln.startswith("ConsoleType"):
        continue
    if ln.startswith("BIOS7Path") or ln.startswith("BIOS9Path") or ln.startswith("FirmwarePath") or ln.startswith("ExternalBIOSEnable"):
        continue
    out.append(ln)
if not inserted:
    out += ['BIOS7Path = "%s\\biosnds7.rom"' % base, 'BIOS9Path = "%s\\biosnds9.rom"' % base,
            'FirmwarePath = "%s\\firmware.bin"' % base, 'ExternalBIOSEnable = true']
open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[:20]))
