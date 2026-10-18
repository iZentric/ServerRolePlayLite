export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
python3 - <<'PY'
import re
def patch(path, edits):
    # edits: list of (section, {key: val})  section None = top level
    try: t=open(path).read()
    except: print("lipsa",path); return
    lines=t.split('\n'); out=[]; i=0; done=set()
    for si,(sec,vals) in enumerate(edits): done.add(si)
    i=0
    while i < len(lines):
        l=lines[i]; out.append(l); i+=1
        for si,(sec,vals) in enumerate(edits):
            if sec is None: continue
            if re.match(r'^\s*'+re.escape(sec)+r':\s*$',l):
                ind=len(l)-len(l.lstrip())
                # consume children
                kids=[]
                while i<len(lines) and (lines[i].strip()=='' or (len(lines[i])-len(lines[i].lstrip()))>ind):
                    kids.append(lines[i]); i+=1
                newk=[]; used=set()
                for kl in kids:
                    m=re.match(r'^(\s+)([A-Za-z0-9_-]+):(.*)$',kl)
                    if m and m.group(2) in vals:
                        newk.append(f"{m.group(1)}{m.group(2)}: {vals[m.group(2)]}"); used.add(m.group(2))
                    else: newk.append(kl)
                for k,v in vals.items():
                    if k not in used: newk.append(' '*(ind+2)+f"{k}: {v}")
                out+=newk
                edits[si]=(sec,{k:v for k,v in vals.items() if k not in used})
    for si,(sec,vals) in enumerate(edits):
        if vals and sec is None:
            for k,v in vals.items(): out.append(f"{k}: {v}")
    open(path,'w').write('\n'.join(out))
    print("patchat",path)
patch('config/spigot.yml', [
 ('entity-activation-range',{'animals':16,'monsters':24,'raiders':32,'misc':8,'water':16,'villagers':16,'tick-inactive-villagers':'false','ignore-spectators':'true'}),
 ('merge-radius',{'exp':4.0,'item':4.0}),
 ('entity-tracking-range',{'players':48,'animals':24,'monsters':32,'misc':8,'other':32,'water':16}),
])
t=open('config/spigot.yml').read()
t=re.sub(r'^(\s*)mob-spawn-range:.*$',r'\g<1>mob-spawn-range: 4',t,flags=re.M)
open('config/spigot.yml','w').write(t)
patch('config/bukkit.yml', [
 ('spawn-limits',{'monsters':40,'animals':4,'water-animals':2,'ambient':1}),
 ('ticks-per',{'animal-spawns':400,'monster-spawns':6,'water-spawns':400,'ambient-spawns':400}),
 ('chunk-gc',{'period-in-ticks':400}),
])
PY
cat > start.sh <<'EOF'
#!/bin/bash
cd $HOME/cuantic-live
[ -p /tmp/mcctl ] || { rm -f /tmp/mcctl; mkfifo -m 600 /tmp/mcctl; }
tail -f /tmp/mcctl | $HOME/j11/bin/java -Xms1G -Xmx5G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=25 -XX:G1MaxNewSizePercent=40 -XX:InitiatingHeapOccupancyPercent=40 -XX:G1HeapRegionSize=8M -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -XX:+DisableExplicitGC -jar FunCity-1.16.5-b1.0827.jar nogui >> boot.log 2>&1
EOF
chmod +x start.sh
pkill -f "java.*FunCity"; sleep 4
setsid nohup ./start.sh </dev/null >/dev/null 2>&1 &
for i in $(seq 1 60); do sleep 3; grep -aqE "Done \(|Error:" <(tail -3 boot.log) && break; done
grep -aE "Done \(" boot.log | tail -1
ss -lnt | grep -q ':25565 ' && echo PORT-OK || echo PORT-NOK
sleep 3
echo "chunky continue" > /tmp/mcctl; sleep 20
echo "chunky status" > /tmp/mcctl; sleep 6
grep -aE "\[Chunky\]" boot.log | tail -3
