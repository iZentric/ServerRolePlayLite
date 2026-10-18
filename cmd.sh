export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
FR=$(free -m | awk '/^Mem:/{print $7}')
if [ "$FR" -ge 14000 ]; then XM=8G; else XM=6G; fi
echo "ram libera: $FR MB -> heap $XM"
cat > start.sh <<EOF
#!/bin/bash
cd \$HOME/cuantic-live
exec \$HOME/j11/bin/java -Xms$XM -Xmx$XM -XX:+UseG1GC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M -XX:MaxGCPauseMillis=25 -XX:+ParallelRefProcEnabled -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -jar FunCity-1.16.5-b1.0827.jar nogui > boot.log 2>&1
EOF
chmod +x start.sh
python3 - <<'PY'
import re, secrets
t=open('server.properties').read()
def set(k,v):
    global t
    if re.search('^%s='%re.escape(k),t,re.M): t=re.sub('^%s=.*$'%re.escape(k),'%s=%s'%(k,v),t,flags=re.M)
    else: t=t.rstrip('\n')+'\n%s=%s\n'%(k,v)
set('view-distance','6'); set('max-players','40'); set('animals','4'); set('monsters','55')
pw=secrets.token_hex(8); open('rcon.pass','w').write(pw); os_chmod='';
set('enable-rcon','true'); set('rcon.port','25575'); set('rcon.password',pw)
open('server.properties','w').write(t)
print('props: view-distance=6 max-players=40 animals=4 rcon=on')
PY
pkill -f "java.*FunCity" 2>/dev/null; sleep 5
setsid nohup ./start.sh </dev/null >/dev/null 2>&1 &
for i in $(seq 1 50); do sleep 3; grep -aqE "Done \(" boot.log && break; done
grep -aE "Done \(" boot.log | tail -1
cat > /tmp/rcon.py <<'PY'
import socket,struct,sys
pw=open(sys.argv[1]).read().strip()
def recvn(s,n):
    b=b''
    while len(b)<n:
        c=s.recv(n-len(b))
        if not c: raise OSError('closed')
        b+=c
    return b
s=socket.create_connection(('127.0.0.1',25575),15); s.settimeout(60)
def pkt(i,t,p):
    e=p.encode()+b'\x00\x00'
    s.sendall(struct.pack('<iii',12+len(p),i,t,e))
def rd():
    l=struct.unpack('<i',recvn(s,4))[0]; d=recvn(s,l+4)
    return d[8:-2].decode('utf-8','replace')
pkt(1,3,pw); rd()
pkt(2,2,' '.join(sys.argv[2:])); print(rd().strip()[:300])
PY
R="python3 /tmp/rcon.py $HOME/cuantic-live/rcon.pass"
$R "list"; $R "chunky radius 1000"; $R "chunky start"; sleep 20; $R "chunky status"
ss -lnt | grep -q ':25565 ' && echo PORT-OK || echo PORT-NOK
