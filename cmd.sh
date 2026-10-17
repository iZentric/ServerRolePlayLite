export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd /tmp
curl -sfLo fc.mrpack "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FunCity-1.0.0.mrpack" && echo "mrpack: $(stat -c%s fc.mrpack) B"
python3 - <<'PY'
import json, zipfile
z = zipfile.ZipFile("/tmp/fc.mrpack")
d = json.load(z.open("modrinth.index.json"))
files = [e["filename"] for e in d.get("files", [])]
print("TOTAL MODURI FIȘIERE:", len(files))
susp = [f for f in files if any(k in f.lower() for k in ["dynamic", "surround", "ambient", "music", "sound", "optifine", "citre", "ctm", "lightfall", "accountswitch", "animation", "transliteration", "cosmetic", "hair", "physics", "particle"]) ]
print("SUSPECTE (cosmetic/sunete/meniu):", susp if susp else "NICIUNA")
print("PRIMELE 25:")
for f in sorted(files)[:25]: print(" -", f)
PY
