export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
python3 - <<'PY'
import zipfile,re,hashlib
z=zipfile.ZipFile('/tmp/oldcfg.zip')
want=re.compile(r'(server\.properties|spigot\.yml|bukkit\.yml|mohist\.yml|catserver\.yml|commands\.yml|paper-world\.yml|paper-global\.yml|forge-server\.toml)$',re.I)
seen={}
recs=[]
for info in z.infolist():
    n=info.filename.replace('\\','/')
    base=n.split('/')[-1]
    if not want.search(base): continue
    if info.file_size==0 or info.file_size>60000: continue
    try: d=z.open(info).read()
    except Exception: continue
    h=hashlib.md5(d).hexdigest()
    if h in seen: continue
    t=d.decode('utf-8','replace')
    mm=re.search(r'motd=(.*)',t); lm=re.search(r'level-name=(.*)',t); ver=re.search(r'(1\.7\.7|1\.12\.2|1\.16\.5|1\.7\.10|1\.20|1\.18)',t)
    tag=(mm.group(1)[:38] if mm else (lm.group(1)[:30] if lm else '?'))
    key=base+"|"+tag
    if key in seen: continue
    seen[key]=1
    recs.append((base,t,len(d)))
print("unice:",len(recs))
def g(t,pat):
    out=[]
    for l in t.split('\n'):
        s=l.strip()
        if re.match(pat,s): out.append(s)
    return out
for base,t,sz in sorted(recs):
    print("=== %s (%dB) ==="%(base,sz))
    if base=='server.properties':
        gl=g(t,r'^(motd|max-players|view-distance|entity-broadcast|network-compression|max-tick-time|use-native|player-idle|spawn-protection|allow-flight)')
    elif 'spigot' in base:
        gl=g(t,r'^(animals:|monsters:|misc:|other:|players:|water:|raiders:|villagers:|tick-inactive-villagers:|mob-spawn-range:|item-despawn-rate:|max-entity-collisions:|netty-threads:|merge-radius:|save-user-cache)')
    elif 'bukkit' in base:
        gl=g(t,r'^(monsters:|animals:|ambient:|water-animals:|period-in-ticks:|animal-spawns:|monster-spawns:|autosave:|allow-end:)')
    elif 'mohist' in base:
        gl=g(t,r'^(chunk_unload_delay:|optimize_explosions:|prevent_from_entering|max-bees|ignore_empty_time|.*activation.*|.*tracking.*)')
    elif 'catserver' in base:
        gl=g(t,r'^(keepSpawnInMemory|forceSaveOnWatchdog|eventPass|disableAsyncCatchWarn)')
    elif 'paper' in base:
        gl=g(t,r'^(max-|keep-spawn|delay-|unload|entity-activation|mob-spawn|tick-)')
    else:
        gl=g(t,r'^(name:|filter:)')[:3]
    print("  "+"\n  ".join(gl[:14]))
PY
