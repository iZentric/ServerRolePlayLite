export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== PING FIXAT =="
python3 - <<'PY'
import socket,json
def rv(f):
    n=0;sh=0
    for _ in range(5):
        c=f.recv(1)
        if not c: raise Exception('eof')
        b=c[0]; n|=(b&0x7f)<<sh; sh+=7
        if not b&0x80: return n
    raise Exception('varint')
try:
    s=socket.create_connection(('127.0.0.1',25565),8); s.settimeout(8)
    f=s.makefile('rb')
    s.sendall(b'\x0b\x00\x00\x09127.0.0.1\x63\xed\x01'); s.sendall(b'\x01\x00')
    ln=rv(f); data=b''
    while len(data)<ln: data+=f.read(ln-len(data))
    i=0
    while data[i]&0x80: i+=1
    i+=1
    n=0;sh=0
    while data[i]&0x80: n|=(data[i]&0x7f)<<sh; sh+=7; i+=1
    n|=(data[i]&0x7f)<<sh; i+=1
    d=json.loads(data[i:i+n].decode('utf8'))
    print('PING OK |',d.get('version',{}).get('name'),'| online:',d.get('players',{}).get('online'),'/',d.get('players',{}).get('max'))
    print('DESC:',str(d.get('description'))[:60])
except Exception as e:
    print('PING esuat:',str(e)[:90])
PY
echo "== TUNEL =="
pgrep -f "cloudflared tunnel" >/dev/null && echo "tunnel: proces viu" || { setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null & sleep 30; }
AD=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | tail -1)
echo "ADRESA: $AD"
echo "== RESURSE =="
P=$(pgrep -f "j11/bin/java" | head -1)
[ -n "$P" ] && awk '/VmRSS/{printf "Java RAM: %.1f GB\n",$2/1048576}' /proc/$P/status
free -m | awk '/Mem/{printf "RAM libera: %dMB din %dMB\n",$4,$2}'
uptime
