export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd /tmp
curl -sfLo fc11.mrpack "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FunCity-1.1.0.mrpack" && echo "desc: $(stat -c%s fc11.mrpack)B"
python3 - <<'PY'
import json, zipfile
z = zipfile.ZipFile("/tmp/fc11.mrpack")
d = json.load(z.open("modrinth.index.json"))
names = [e.get("filename") or (e.get("downloads") or ["?"])[0].rsplit("/",1)[-1] for e in d.get("files", [])]
names += [n.split("/")[-1] for n in z.namelist() if n.endswith(".jar")]
print("TOTAL CLIENT 1.1.0:", len(names))
bad = [n for n in names if any(k in n.lower() for k in ["dynamic","surround","ctm-mc","notenough","transliter","lightfall","accountswitch"])]
print("GUNOI RAMAS:", bad if bad else "NICIUN ✔")
content = [n for n in names if any(k in n.lower() for k in ["gun","vehicle","cfm","pamhc","pizzaland","modernlife","supp","mapperbase","obfuscate","voicechat"])]
print("CONTENT PREZENT:", len(content), "bucate:", "; ".join(sorted(content)))
PY
