export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
python3 - <<'PY'
import json, zipfile
z = zipfile.ZipFile("/tmp/fc.mrpack")
d = json.load(z.open("modrinth.index.json"))
def name(e):
    return e.get("filename") or e.get("env",{}).get("client","") and e["env"]["client"].split("/")[-1] or e.get("downloads",["?"])[0].split("/")[-1]
files = [name(e) for e in d.get("files", [])]
print("TOTAL MODURI FIȘIERE:", len(files))
susp = [f for f in files if any(k in str(f).lower() for k in ["dynamic","surround","ambient","music","sound","optifine","citre","ctm","lightfall","accountswitch","animation","transliteration","cosmetic","hair","physics","particle","shader"])]
print("SUSPECTE:", "; ".join(map(str,susp)) if susp else "NICIUNA")
print("---LISTA---")
for f in sorted(map(str,files)): print(" -", f)
PY
