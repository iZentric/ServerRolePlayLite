export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== OBfuscate latest 1.16.5 =="
python3 - <<'PY'
import json,urllib.request,os
def gh(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'c'}),timeout=30))
best=None
for r in gh('https://api.github.com/repos/MrCrayfish/Obfuscate/releases?per_page=100'):
    for a in r.get('assets',[]):
        n=a['name']
        if n.endswith('.jar') and ('1.16' in n) and 'deobfuscation' not in n:
            if best is None or r['tag_name']>best[0]: best=(r['tag_name'],a['browser_download_url'],n)
if not best:
    print('nu gasit pe github, incerc modrinth')
    vs=gh('https://api.modrinth.com/v2/project/obfuscate/version?game_versions=%5B%221.16.5%22%5D')
    for v in vs:
        for f in v.get('files',[]):
            if f['filename'].endswith('.jar'): best=('mr',f['url'],f['filename']); break
        if best: break
if best:
    d=urllib.request.urlopen(urllib.request.Request(best[1],headers={'User-Agent':'c'}),timeout=120).read()
    open('/home/mndvasi9/cuantic-live/mods/'+best[2],'wb').write(d)
    print('instalat:',best[2],len(d),'B tag',best[0])
else: print('NUGASIT')
PY
ls mods/ | grep -i obfuscate
echo "== BOOT =="
pkill -9 -f java 2>/dev/null; sleep 5
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 80); do sleep 5; grep -qaE "Done \(|FATAL|LoadingFailed" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
DONE=$(grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1)
echo "BOOT: ${DONE:-NU A DAT DONE}"
[ -z "$DONE" ] && grep -aE "requires|FATAL" boot.clean | head -4 | cut -c1-140
echo "== PING =="
python3 - <<'PY'
import socket,json
try:
    s=socket.create_connection(('127.0.0.1',25565),8)
    s.sendall(b'\x0b\x00\x00\x09127.0.0.1\x63\xed\x01')
    s.sendall(b'\x01\x00')
    ln=s.recv(1)[0]
    buf=s.recv(ln+4)
    i=0
    while buf[i]&0x80: i+=1
    i+=1
    n=0;sh=0;i+=0
    j=buf[i]
    # sar peste al doilea varint (packet id=0) si citesc len JSON
    while buf[i]&0x80: n|=(buf[i]&0x7f)<<sh; sh+=7; i+=1
    n|=(buf[i]&0x7f)<<sh; i+=1
    d=json.loads(buf[i:i+n])
    print('PING OK |',d.get('version',{}).get('name'),'| online:',d.get('players',{}).get('online'),'/',d.get('players',{}).get('max'))
except Exception as e:
    print('PING esuat:',str(e)[:80])
PY
echo "== TUNEL =="
pgrep -f "cloudflared tunnel" >/dev/null || setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null &
for i in $(seq 1 20); do sleep 3; grep -q trycloudflare /tmp/cf.log 2>/dev/null && break; done
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
