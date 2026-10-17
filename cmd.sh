export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
python3 - <<'PY'
import json, zipfile
z = zipfile.ZipFile("/tmp/fc.mrpack")
d = json.load(z.open("modrinth.index.json"))
print("== files[] din index ==")
for e in d.get("files", []):
    u = (e.get("downloads") or ["?"])[0]
    print(" -", e.get("filename") or u.rsplit("/",1)[-1], "| env:", json.dumps(e.get("env",{})))
names = z.namelist()
mods = [n.split("/")[-1] for n in names if n.startswith("overrides/mods/") or n.startswith("client-overrides/mods/") or n.startswith("server-overrides/mods/")]
print("== jar-uri in overrides:", len(mods), "==")
for m in sorted(mods): print(" +", m)
PY
