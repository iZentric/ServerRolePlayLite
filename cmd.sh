export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== CURATARE TOTALA =="
pkill -9 -f java 2>/dev/null; pkill -9 -f cloudflared 2>/dev/null; sleep 6
fuser -k 25565/tcp 2>/dev/null; sleep 2
if [ -d mods/mods-pre-fr ]; then mv -f mods/mods-pre-fr/* mods/ 2>/dev/null; rmdir mods/mods-pre-fr; fi
echo "mods: $(ls mods/*.jar 2>/dev/null | wc -l)"
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 80); do sleep 5; grep -qaE "Done \(|FATAL|LoadingFailed" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
DONE=$(grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1)
echo "BOOT: ${DONE:-NU A DAT DONE}"
[ -z "$DONE" ] && grep -aE "requires|FATAL|Exception" boot.clean | head -5 | cut -c1-140
echo "== MC PING real =="
python3 - <<'PY'
import socket,struct,json
def wv(n):
    o=b''
    while True:
        if (n&~0x7F)==0: return o+bytes([n])
        o+=bytes([(n&0x7F)|0x80]); n>>=7
def rv(f):
    n=0;s=0
    while True:
        c=f.read(1)
        if not c: raise Exception('eof')
        b=c[0]; n|=(b&0x7f)<<s; s+=7
        if not b&0x80: return n
try:
    s=socket.create_connection(('127.0.0.1',25565),8)
    body=wv(0)+wv(-1&0xFFFFFFFFFFFFFFFF)
    host=b'127.0.0.1'
    body=wv(0)+wv(len(host))+host+struct.pack('>H',25565)+wv(1)+wv(0)
    s.sendall(wv(len(body))+body)
    body=wv(0)+wv(0)
    s.sendall(wv(len(body))+body)
    ln=rv(s.makefile('rb'))
    data=s.recv(ln+8)
    # sari peste varint len + packet id
    i=0;n=0;sh=0
    while data[i]&0x80: n|=data[i]&0x7f;sh+=7;i+=1
    n|=data[i]&0x7f;i+=1
    d2=n;s2=0
    while data[i]&0x80: d2|=(data[i]&0x7f)<<s2;s2+=7;i+=1
    d2|=data[i]&0x7f;i+=1
    j=json.loads(data[i:i+d2])
    print('PING OK |', j.get('version',{}).get('name'), '| jucatori:', j.get('players',{}).get('online'),'/',j.get('players',{}).get('max'), '|', str(j.get('description'))[:50])
except Exception as e:
    print('PING esuat:',str(e)[:100])
PY
echo "== TUNEL =="
cd ~/cuantic-live && setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null &
for i in $(seq 1 20); do sleep 3; grep -q trycloudflare /tmp/cf.log 2>/dev/null && break; done
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
