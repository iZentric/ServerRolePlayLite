export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "== SERVER mods =="; ls ~/cuantic-live/mods/ | head -40; echo "TOTAL: $(ls ~/cuantic-live/mods/*.jar 2>/dev/null | wc -l)"
echo "== plugins =="; ls ~/cuantic-live/plugins/ 2>/dev/null | head -12
echo "== CLIENT suspecti din index =="
python3 - <<'PY'
import json, zipfile
z = zipfile.ZipFile("/tmp/fc.mrpack")
d = json.load(z.open("modrinth.index.json"))
all_names = [e.get("filename") or (e.get("downloads") or ["?"])[0].rsplit("/",1)[-1] for e in d.get("files", [])]
all_names += [n.split("/")[-1] for n in z.namelist() if n.startswith("overrides/mods/")]
print("client total:", len(all_names))
for n in all_names: print(" *", n)
PY
