export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
python3 - <<'PY'
import re,os
t=open('server.properties').read()
t=re.sub(r'^network-compression-threshold=.*$','network-compression-threshold=-1',t,flags=re.M)
open('server.properties','w').write(t)
b=open('config/bukkit.yml').read()
if re.search(r'^  keep-spawn-loaded:',b,re.M): b=re.sub(r'^  keep-spawn-loaded:.*$','  keep-spawn-loaded: false',b,flags=re.M)
else: b=re.sub(r'^settings:\s*$','settings:\n  keep-spawn-loaded: false',b,count=1,flags=re.M)
open('config/bukkit.yml','w').write(b)
open('config/commands.yml','w').write("name: FunCity\nfilter: \u00a7\ncommands: {}\nalias:\n  fctps:\n  - tps\n  fcv:\n  - version\n")
print("comp=-1, keep-spawn-loaded=false, commands.yml FunCity")
PY
pkill -f "java.*FunCity"; sleep 4
setsid nohup ./start.sh </dev/null >/dev/null 2>&1 &
for i in $(seq 1 60); do sleep 3; grep -aqE "Done \(" <(tail -3 boot.log) && break; done
grep -aE "Done \(|Killed" boot.log | tail -1
ss -lnt | grep -q ':25565 ' && echo PORT-OK || echo PORT-NOK
grep -a "network-compression" server.properties
grep -a "keep-spawn" config/bukkit.yml
sleep 3; echo "chunky status" > /tmp/mcctl; sleep 6; grep -aE "\[Chunky\]" boot.log | tail -1
