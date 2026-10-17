export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
chmod -R u+rwX ~/freeroam 2>/dev/null
cd ~/cuantic-live
echo "== LIBS DIN MANIFEST (perm fixate) =="
python3 - <<'PY'
import json,os,urllib.request,shutil
z=json.load(open(os.path.expanduser('~/freeroam/x/modrinth.index.json')))
m=os.path.expanduser('~/cuantic-live/mods')
need=('obfuscate','selene','playeranimator')
res={}
for f in z.get('files',[]):
    p=f['path'].lower()
    if any(n in p for n in need) and '.jar' in p:
        fn=os.path.basename(f['path'])
        if 'lib_compatible' in p: continue
        res.setdefault(p.split('/')[-1] if '/' in p else fn, f)
# preferam versiuni 1.16.x
for name,f in res.items():
    fn=os.path.basename(f['path'])
    dst=os.path.join(m,fn)
    if os.path.exists(dst): print('EXISTA',fn); continue
    try:
        d=urllib.request.urlopen(urllib.request.Request(f['downloads'][0],headers={'User-Agent':'c'}),timeout=180).read()
        open(dst,'wb').write(d); print('LIB OK',fn,len(d))
    except Exception as e: print('LIB ES',fn,str(e)[:70])
ov=os.path.expanduser('~/freeroam/x/overrides/mods')
if os.path.isdir(ov):
    for fn in os.listdir(ov):
        if any(n in fn.lower() for n in need) and 'lib_compatible' not in fn and not os.path.exists(os.path.join(m,fn)):
            shutil.copy(os.path.join(ov,fn),os.path.join(m,fn)); print('OVR',fn)
print('MODS LIB FINAL:', [x for x in os.listdir(m) if any(n in x.lower() for n in need)])
PY
echo "== BOOT =="
pkill -9 -f java 2>/dev/null; sleep 5
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 80); do sleep 5; grep -qaE "Done \(|FATAL" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
DONE=$(grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1)
echo "BOOT: ${DONE:-INCĂ FĂRĂ DONE}"
if [ -z "$DONE" ]; then
  grep -aE "requires" boot.clean | head -5
  for LINE in $(grep -oE "Mod .[a-zA-Z0-9_-]+§r requires .§6[a-zA-Z0-9_-]+" boot.clean | sort -u); do :; done
  grep -oE "Mod §e[a-zA-Z0-9_-]+§r requires §6[a-zA-Z0-9_-]+" boot.clean | sed -E 's/Mod §e([a-z0-9_-]+)§r requires §6([a-z0-9_-]+)/\1:\2/' | sort -u | while IFS=: read MOD LIB; do
    if ls ~/cuantic-live/mods/ | grep -qiE "^${LIB}[^_].*\.jar$"; then continue; fi
    rm -fv ~/cuantic-live/mods/*"${MOD}"*.jar
  done
  pkill -9 -f java 2>/dev/null; sleep 5
  setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
  for i in $(seq 1 80); do sleep 5; grep -qaE "Done \(|FATAL" boot.log && break; done
  sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
  echo "RETRY: $(grep -oE 'Done \([0-9.]*s\)!' boot.clean | tail -1)"
fi
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: INCHIS"
echo "== PING =="
python3 - <<'PY'
import socket,json
try:
    s=socket.create_connection(('127.0.0.1',25565),8)
    s.sendall(b'\x0b\x00\x00\x09127.0.0.1\x63\xed\x01'); s.sendall(b'\x01\x00')
    ln=s.recv(1)[0]; buf=s.recv(ln+2500)
    i=0
    while buf[i]&0x80: i+=1
    i+=1
    n=0;sh=0
    while buf[i]&0x80: n|=(buf[i]&0x7f)<<sh;sh+=7;i+=1
    n|=(buf[i]&0x7f)<<sh;i+=1
    d=json.loads(buf[i:i+n])
    print('PING OK |',d.get('version',{}).get('name'),'| online:',d.get('players',{}).get('online'),'/',d.get('players',{}).get('max'),'| desc:',str(d.get('description'))[:40])
except Exception as e:
    print('PING esuat:',str(e)[:80])
PY
echo "== TUNEL =="
pgrep -f "cloudflared tunnel" >/dev/null || setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null &
for i in $(seq 1 20); do sleep 3; grep -q trycloudflare /tmp/cf.log 2>/dev/null && break; done
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
