export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
python3 - <<'PY'
import zipfile,re,os,collections
z=zipfile.ZipFile('/tmp/oldcfg.zip')
names=z.namelist()
print("total intrari:",len(names))
print("primele:", " | ".join(names[:6]))
want=re.compile(r'(server\.properties|spigot\.yml|bukkit\.yml|mohist\.yml)$',re.I)
hits=[n for n in names if want.search(n.replace('\\','/'))]
print("hits:",len(hits))
os.makedirs('/tmp/oc',exist_ok=True)
seen=collections.Counter()
for n in hits:
    fn=n.replace('\\','/').lstrip('./')
    parts=fn.split('/')
    tag='_'.join(parts[-3:-1]) if len(parts)>=3 else parts[0]
    leaf=parts[-1]
    base=(tag+'__'+leaf).replace(' ','')
    if seen[base]>3: continue
    seen[base]+=1
    try: v=z.read(n)[:3500]
    except Exception as e: print("sare",n[:50],e); continue
    open('/tmp/oc/'+base,'wb').write(v)
fs=sorted(os.listdir('/tmp/oc'))
print("fisierete extrase:",len(fs))
for f in fs:
    t=open('/tmp/oc/'+f,'rb').read().decode('utf-8','replace')
    if 'server.properties' in f:
        g=[l for l in t.split('\n') if re.match(r'^(view-distance|max-players|entity-broadcast|network-compression|max-tick-time|use-native|player-idle)',l)]
        print("### PROPS "+f.replace('__','/')); print("  "+" | ".join(x.strip() for x in g[:9]))
    elif 'spigot' in f:
        g=[l for l in t.split('\n') if re.search(r'(animals:|monsters:|misc:|other:|players:|tick-inactive|mob-spawn-range|max-entity|item-despawn|netty)',l)]
        print("### SPIGOT "+f.replace('__','/')); print("  "+" | ".join(x.strip() for x in g[:18]))
PY
