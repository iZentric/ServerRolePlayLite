export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
python3 - <<'PY'
import re
t=open('server.properties').read()
def set(k,v):
    global t
    if re.search('^%s='%re.escape(k),t,re.M): t=re.sub('^%s=.*$'%re.escape(k),'%s=%s'%(k,v),t,flags=re.M)
    else: t=t.rstrip('\n')+'\n%s=%s\n'%(k,v)
for k,v in [('view-distance','4'),('player-idle-timeout','0'),('use-native-transport','true'),('network-compression-threshold','512'),('spawn-protection','0'),('allow-flight','true'),('max-tick-time','-1'),('entity-broadcast-range-percentage','60'),('online-mode','false'),('max-players','40')]: set(k,v)
open('server.properties','w').write(t)
print("props OK")
import os
os.makedirs('config',exist_ok=True); os.makedirs('defaultconfigs',exist_ok=True)
open('config/connectivity-common.toml','w').write('["Connectivity settings"]\n\tdisableLoginLimits = true\n\tdisablePacketLimits = true\n\tdebugPrintMessages = false\n\tlogintimeout = 2400\n\tdisconnectTimeout = 60\n\tpacketHistoryMinutes = 5\n\tshowFullResourceLocationException = false\n')
open('config/modernfix-mixins.properties','w').write('# FunCity SERVER - reteta CUANTIC\nmixin.perf.dynamic_resources=true\nmixin.perf.dedup_location=true\nmixin.perf.compact_bit_storage=true\nmixin.perf.thread_priorities=true\nmixin.bugfix.chunk_deadlock=true\n')
open('defaultconfigs/forge-server.toml','w').write('# Scutul anti-crash\n[server]\n    removeErroringEntities = true\n    removeErroringTileEntities = true\n')
print("3 fisiere config scrise")
PY
pkill -f "java.*FunCity"; sleep 4
setsid nohup ./start.sh </dev/null >/dev/null 2>&1 &
for i in $(seq 1 60); do sleep 3; grep -aqE "Done \(" <(tail -3 boot.log) && break; done
grep -aE "Done \(" boot.log | tail -1
ss -lnt | grep -q ':25565 ' && echo PORT-OK || echo PORT-NOK
echo "=== VERIFICARE valori ==="
grep -aE "view-distance|max-players|entity-broadcast|network-compression|max-tick-time" server.properties | tr '\n' ' '; echo
grep -aA9 "entity-activation-range:" config/spigot.yml | head -10 | tr -d ' ' | tr '\n' ' '; echo
grep -aE "mob-spawn-range|max-entity-collisions|item-despawn-rate" config/spigot.yml | tr -d ' ' | tr '\n' ' '; echo
grep -aA7 "spawn-limits:" config/bukkit.yml | tr -d ' ' | tr '\n' ' '; echo
sleep 3; echo "chunky status" > /tmp/mcctl; sleep 8
grep -aE "\[Chunky\]" boot.log | tail -2
free -m | awk '/^Mem:/{print "libera: "$7"M"}'
