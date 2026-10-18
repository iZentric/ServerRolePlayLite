export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
REPO=$(pwd)
[ -d "$REPO/diag" ] || REPO=$(dirname "$(dirname "$(find /home /root /tmp -maxdepth 4 -name oldcfg-meta.txt 2>/dev/null | head -1)")")
echo "repo=$REPO parts=$(ls $REPO/diag/oc_part*.txt 2>/dev/null | wc -l)"
: > /tmp/oc.b64
for i in $(seq 0 34); do cat "$REPO/diag/oc_part$i.txt" >> /tmp/oc.b64 2>/dev/null; done
tr -d '\n\r ' < /tmp/oc.b64 | base64 -d > /tmp/oldcfg.zip 2>/dev/null
echo "zip: $(stat -c%s /tmp/oldcfg.zip) B (asteptat 9032359)"
python3 - <<'PY'
import zipfile,os,re
z=zipfile.ZipFile('/tmp/oldcfg.zip')
pat=re.compile(r'(server\.properties|spigot\.yml|bukkit\.yml|mohist\.yml|mohist-config)$',re.I)
out={}
for n in z.namelist():
    fn=n.replace('\\','/')
    top=fn.split('/')[0]
    if top in ('servere referinta','FunCity server','motor','builduri','_ex') and pat.search(fn) and '/world' not in fn and '\\world' not in n and 'plugins' not in fn:
        try: out[fn]=z.read(n)[:4000]
        except: pass
os.makedirs('/tmp/oc',exist_ok=True)
print("extrase:",len(out))
for k,v in out.items():
    p='/tmp/oc/'+k.replace('/','__')
    open(p,'wb').write(v)
for k,v in sorted(out.items()):
    short='/'.join(k.split('/')[1:])
    t=v.decode('utf-8','replace')
    if 'server.properties' in k:
        print("### PROPS "+short)
        for l in t.split('\n'):
            if re.match(r'^(view-distance|max-players|entity-broadcast|network-compression|max-tick-time|spawn-protection|use-native|player-idle)',l): print("  "+l.strip())
    elif 'spigot' in k:
        print("### SPIGOT "+short)
        keep=[l for l in t.split('\n') if re.search(r'(activation-range|tracking-range|animals:|monsters:|misc:|other:|water:|players:|tick-inactive|mob-spawn-range|max-entity|item-despawn|merge-radius|netty|tick-spa)',l)]
        print("  "+"\n  ".join(keep[:22]))
    elif 'bukkit' in k:
        print("### BUKKIT "+short)
        keep=[l for l in t.split('\n') if re.search(r'(spawn-limits|monsters:|animals:|ambient|chunk-gc|period-in-ticks|animal-spawns|monster-spawns|autosave)',l)]
        print("  "+"\n  ".join(keep[:14]))
    elif 'mohist' in k:
        print("### MOHIST "+short)
        keep=[l for l in t.split('\n') if re.search(r'(spawn|track|activat|unload|explos|range|tick)',l,re.I)]
        print("  "+"\n  ".join(keep[:16]))
PY
