export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== MASURA REALA =="
P=$(pgrep -f "j11/bin/java" | head -1)
[ -n "$P" ] && { ps -o etime=,rss=,args= -p $P | cut -c1-120; echo "RAM: $(( $(awk '/VmRSS/{print $2}' /proc/$P/status 2>/dev/null || echo 0) / 1024 ))MB"; } || echo "Java: NU E"
echo "mods: $(ls mods/*.jar 2>/dev/null | wc -l)"; ls mods/ 2>/dev/null | head -6
echo "--- boot.log ultime:"; sed 's/\x1b\[[0-9;]*m//g' boot.log 2>/dev/null | grep -aE "Done|FATAL|Loading|Exception|start" | tail -6 | cut -c1-140
echo "--- MC PING local:"
python3 - <<'PY'
import socket,struct,json
def vi(n):
    b=bytearray();
    while n>0x7f or n<-0x80: b.append((n&0x7f)|0x80); n>>=7
    b.append(n); return bytes(b)
try:
    s=socket.create_connection(("127.0.0.1",25565),4)
    p=vi(0)+vi(0)+vi(2)+b'\xff\xff\xff\xff'+b'\x02'+b'\x01'+b'\x02'+vi(0)+vi(0)
    s.sendall(vi(len(p))+p)
    d=s.recv(4); n=int.from_bytes(b'','x') if 0 else None
    import itertools
    ln=0; sh=0; buf=b''
    while True:
        c=s.recv(1); ln|=c[0]
        if not c[0]&0x80: break
        sh+=7
    data=s.recv(ln)
    json.loads(data)
    print("PING: server raspunde, JSON ok")
    j=json.loads(data)
    print("desc:",j.get('description','')[:60])
    print("players:",j.get('players',{}).get('online'),"/",j.get('players',{}).get('max'))
    print("version:",j.get('version',{}).get('name'))
except Exception as e:
    print("PING esuat:",str(e)[:80])
PY
