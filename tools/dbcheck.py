import sqlite3, os, json
p = os.path.expandvars(r'%USERPROFILE%\.local\share\opencode\opencode.db')
con = sqlite3.connect(p)
cur = con.cursor()
tables = [r[0] for r in cur.execute("select name from sqlite_master where type='table'").fetchall()]
print("tables:", tables)
for t in tables:
    cols = [d[1] for d in cur.execute(f"PRAGMA table_info({t})").fetchall()]
    print(f"  {t}: {cols}")
# look for anything auth/credential-ish
for t in tables:
    if any(k in t.lower() for k in ("auth","cred","provider","key","account","config")):
        print("---- rows of", t)
        try:
            for row in cur.execute(f"select * from {t} limit 20").fetchall():
                s = str(row)
                # redact long secrets
                import re
                s = re.sub(r'(sk-[A-Za-z0-9_\-]{4})[A-Za-z0-9_\-]+', r'\1...REDACTED', s)
                print("   ", s[:400])
        except Exception as e:
            print("   err", e)
