export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd /tmp
curl -sfLo f121.mrpack "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FunCity-1.2.1.mrpack" && echo "desc: $(stat -c%s f121.mrpack)B"
python3 - <<'PY'
import json, zipfile
z = zipfile.ZipFile("/tmp/f121.mrpack")
d = json.load(z.open("modrinth.index.json"))
names = []
for e in d.get("files", []):
    n = e.get("filename") or (e.get("downloads") or ["?"])[0].rsplit("/", 1)[-1]
    names.append(n.split("?")[0])
names += [n.split("/")[-1] for n in z.namelist() if n.endswith(".jar")]
print("TOTAL CLIENT 1.2.1:", len(names))
for k in ["radon", "entityculling", "out_of_sight", "collision"]:
    hit = [n for n in names if k in n.lower()]
    print(("OK  " if hit else "LIPSA ") + k, hit[:1])
gunoi = [n for n in names if any(k in n.lower() for k in ["dynamic", "surround", "ctm-mc", "notenough", "transliter", "lightfall", "accountswitch"])]
print("GUNOI:", gunoi if gunoi else "NICIUN ✔")
PY
