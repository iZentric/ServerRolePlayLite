export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
python3 - <<'PY'
import re,os
def patch(path, sections):
    lines=open(path).read().split('\n') if os.path.exists(path) else []
    for sec,vals in sections:
        i=0; hit=False
        while i<len(lines) and vals:
            l=lines[i]
            if re.match(r'^\s*'+re.escape(sec)+r':\s*$',l):
                ind=len(l)-len(l.lstrip()); i+=1
                while i<len(lines) and vals:
                    if lines[i].strip()=='' or (lines[i].rstrip()!=lines[i] and False): i+=1; continue
                    ind2=len(lines[i])-len(lines[i].lstrip())
                    if ind2<=ind: break
                    m=re.match(r'^(\s+)([A-Za-z0-9_.-]+):(.*)$',lines[i])
                    if m and m.group(2) in vals:
                        lines[i]=f"{m.group(1)}{m.group(2)}: {vals[m.group(2)]}"; del vals[m.group(2)]
                    i+=1
                j=i if i<len(lines) else len(lines)
                for k,v in list(vals.items()):
                    lines.insert(j, ' '*(ind+2)+f"{k}: {v}"); j+=1; del vals[k]
                hit=True
            i+=1 if not hit else 0
            if hit: break
        if vals and not hit:
            for k,v in vals.items():
                lines.append(f"{sec}:") if False else None
            lines.append(sec+':')
            for k,v in vals.items(): lines.append('  '+f"{k}: {v}")
    open(path,'w').write('\n'.join(lines)); print("patchat",path)
def setglobal(path,pairs):
    t=open(path).read()
    for k,v in pairs:
        if re.search(r'^\s*'+re.escape(k)+r':',t,re.M): t=re.sub(r'^(\s*)'+re.escape(k)+r':.*$',r'\g<1>'+k+': '+str(v),t,flags=re.M,count=1)
        else: t=t.rstrip('\n')+'\n'+k+': '+str(v)+'\n'
    open(path,'w').write(t)
# ---- spigot.yml: valorile CUANTIC ale lui user ----
patch('config/spigot.yml',[('settings',{'save-user-cache-on-stop-only':True,'log-villager-deaths':False,'moved-wrongly-threshold':0.35,'moved-too-quickly-multiplier':25.0})])
patch('config/spigot.yml',[('entity-activation-range',{'animals':12,'monsters':16,'raiders':16,'misc':6,'water':12,'villagers':12,'tick-inactive-villagers':False})])
patch('config/spigot.yml',[('entity-tracking-range',{'players':48,'animals':24,'monsters':24,'misc':12,'other':32,'water':16})])
patch('config/spigot.yml',[('merge-radius',{'item':4.0,'exp':6.0})])
patch('config/spigot.yml',[('ticks-per',{'hopper-transfer':24,'hopper-check':24,'monster-spawns':10})])
setglobal('config/spigot.yml',[('mob-spawn-range',3),('max-tnt-per-tick',10),('item-despawn-rate',2400),('max-entity-collisions',2),('arrow-despawn-rate',200),('trident-despawn-rate',200),('nerf-spawner-mobs',True),('zombie-aggressive-towards-villager',False),('hopper-amount',3)])
# ---- bukkit.yml ----
patch('config/bukkit.yml',[('settings',{'allow-end':False,'chunk-gc-period':30})])
patch('config/bukkit.yml',[('spawn-limits',{'monsters':20,'animals':6,'water-animals':2,'water-ambient':2,'ambient':0})])
patch('config/bukkit.yml',[('chunk-gc',{'period-in-ticks':400,'load-threshold':300})])
patch('config/bukkit.yml',[('ticks-per',{'animal-spawns':400,'monster-spawns':10,'water-spawns':40,'ambient-spawns':400,'autosave':6000})])
# ---- server.properties (stil cuantic) ----
t=open('server.properties').read()
for k,v in [('view-distance',4),('player-idle-timeout',0),('use-native-transport','true'),('network-compression-threshold',512),('spawn-protection',0),('allow-flight','true'),('max-tick-time',-1),('entity-broadcast-range-percentage',60),('online-mode','false'),('max-players',40)]:
    if re.search(r'^%s='%k,re.M,t): t=re.sub(r'^%s=.*$'%k,'%s=%s'%(k,v),t,flags=re.M)
    else: t=t.rstrip('\n')+f'\n{k}={v}\n'
open('server.properties','w').write(t); print("server.properties: stil cuantic (vd4 ebr60 comp512 fly-ok tickoff)")
# ---- connectivity + modernfix + scut anti-crash (din raportul cuantic) ----
os.makedirs('config',exist_ok=True); os.makedirs('defaultconfigs',exist_ok=True)
open('config/connectivity-common.toml','w').write('''["Connectivity settings"]
\tdisableLoginLimits = true
\tdisablePacketLimits = true
\tdebugPrintMessages = false
\tlogintimeout = 2400
\tdisconnectTimeout = 60
\tpacketHistoryMinutes = 5
\tshowFullResourceLocationException = false
''')
open('config/modernfix-mixins.properties','w').write('''# FunCity SERVER - aliniat cu reteta CUANTIC
mixin.perf.dynamic_resources=true
mixin.perf.dedup_location=true
mixin.perf.compact_bit_storage=true
mixin.perf.thread_priorities=true
mixin.bugfix.chunk_deadlock=true
''')
open('defaultconfigs/forge-server.toml','w').write('''# Scutul anti-crash (Forge 1.16: [server] traieste in defaultconfigs)
[server]
    removeErroringEntities = true
    removeErroringTileEntities = true
''')
print("config extra: connectivity + modernfix + anti-crash scrise")
PY
pkill -f "java.*FunCity"; sleep 4
setsid nohup ./start.sh </dev/null >/dev/null 2>&1 &
for i in $(seq 1 60); do sleep 3; grep -aqE "Done \(|Error:" <(tail -2 boot.log) && break; done
grep -aE "Done \(" boot.log | tail -1
ss -lnt | grep -q ':25565 ' && echo PORT-OK || echo PORT-NOK
sleep 3; echo "chunky status" > /tmp/mcctl; sleep 8
grep -aE "\[Chunky\]|Unknown setting" boot.log | tail -3
free -m | awk '/^Mem:/{print "libera: "$7"M"}'
