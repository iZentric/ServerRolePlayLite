export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
N=35; : > /tmp/oc.b64
for i in $(seq 0 $((N-1))); do cat "$(ls -d ~/*ServerRolePlayLite* ~/*lite* 2>/dev/null | head -1)/diag/oc_part$i.txt" >> /tmp/oc.b64 2>/dev/null || { D=$(dirname "$(find /home -maxdepth 3 -name 'oldcfg-meta.txt' 2>/dev/null | head -1)"); cat "$D/oc_part$i.txt" >> /tmp/oc.b64; }; done
tr -d '\n\r ' < /tmp/oc.b64 | base64 -d > /tmp/oldcfg.zip 2>/dev/null
echo "zip: $(stat -c%s /tmp/oldcfg.zip 2>/dev/null) B (asteptat 9032359)"
rm -rf /tmp/oc && mkdir -p /tmp/oc
python3 - <<'PY'
import zipfile,os,re
try: z=zipfile.ZipFile('/tmp/oldcfg.zip')
except Exception as e: print("ZIP CORPUT:",e); raise SystemExit
pat=re.compile(r'(server\.properties|spigot\.yml|bukkit\.yml|commands\.yml|mohist[^/]*\.yml|paper[^/]*\.yml|purpur\.yml)$',re.I)
keep=[]
for n in z.namelist():
    fn=n.replace('\\','/')
    if fn.startswith(('servere referinta','FunCity server','motor','builduri','_ex')) and pat.search(fn) and '/world' not in fn and 'plugins/' not in fn:
        keep.append(n)
print("extrag:",len(keep))
for n in keep:
    try:
        d=z.read(n); p=os.path.join('/tmp/oc',n.replace('\\','_'))
        open(p,'wb').write(d)
    except Exception as e: print("sare",n[:60],e)
print("gata")
PY
ls /tmp/oc | head -5; ls /tmp/oc | wc -l
for f in /tmp/oc/*server.properties; do echo "########## $(basename "$f" | cut -d. -f1) ##########"; grep -aE "view-distance|max-players|broadcast|compression|tick-time|spawn-prot|netty|idle|motd" "$f" 2>/dev/null | head -10; done
for f in /tmp/oc/*spigot.yml; do echo "########## SPIGOT $(basename "$f") ##########"; grep -aE "animals:|monsters:|misc:|players:|other:|villagers|tick-inactive|mob-spawn-range|merge|item-despawn|collisions|hopper|netty" "$f" | head -16; done
