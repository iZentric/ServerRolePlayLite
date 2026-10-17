export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== BRAND + LIB + BOOT (v45) =="
python3 - <<'PY'
import json,os,urllib.request,shutil
z=json.load(open(os.path.expanduser('~/freeroam/x/modrinth.index.json')))
need=('obfuscate','selene','playeranimator')
m=os.path.expanduser('~/cuantic-live/mods')
for f in z.get('files',[]):
    p=f['path'].lower()
    if any(n in p for n in need):
        fn=os.path.basename(f['path'])
        if not os.path.exists(os.path.join(m,fn)) and f.get('downloads'):
            try:
                d=urllib.request.urlopen(urllib.request.Request(f['downloads'][0],headers={'User-Agent':'c'}),timeout=120).read()
                open(os.path.join(m,fn),'wb').write(d); print('LIB OK',fn,len(d))
            except Exception as e: print('LIB ES',fn,str(e)[:60])
ov=os.path.expanduser('~/freeroam/x/overrides/mods')
if os.path.isdir(ov):
    for fn in os.listdir(ov):
        if any(n in fn.lower() for n in need):
            dst=os.path.join(m,fn)
            if not os.path.exists(dst):
                shutil.copy(os.path.join(ov,fn),dst); print('OVR',fn)
PY
ls mods/ | grep -aiE "obfuscate|selene|playeranim" | head -5
# motd brand funcity
sed -i 's/^motd=.*/motd=\\u00A7b\\u00A7lFunCity\\u00A7r \\u00A77RolePlay 1.16.5/' server.properties
grep -a motd server.properties
pkill -9 -f java 2>/dev/null; sleep 5
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 80); do sleep 5; grep -qaE "Done \(|FATAL" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
DONE=$(grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1)
echo "BOOT: ${DONE:-NU A DAT DONE}"
if [ -z "$DONE" ]; then
  grep -aE "requires" boot.clean | head -6
  for m in $(grep -oE "Mod .[a-zA-Z0-9_-]+. requires" boot.clean | sed -E 's/Mod .([a-zA-Z0-9_-]+).*/\1/' | sort -u); do
    LIB=$(grep -oE "Mod .$m. requires .[a-zA-Z0-9_-]+" boot.clean | sed -E "s/.*requires .([a-zA-Z0-9_-]+)/\1/" | head -1)
    ls ~/cuantic-live/mods/ | grep -qi "$LIB" && continue
    rm -fv ~/cuantic-live/mods/*"$m"*.jar
  done
  pkill -9 -f java 2>/dev/null; sleep 5
  setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
  for i in $(seq 1 80); do sleep 5; grep -qaE "Done \(|FATAL" boot.log && break; done
  sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
  echo "RETRY: $(grep -oE 'Done \([0-9.]*s\)!' boot.clean | tail -1)"
fi
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: INCHIS"
echo "== TUNEL =="
pgrep -f "cloudflared tunnel" >/dev/null || setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null &
for i in $(seq 1 20); do sleep 3; grep -q trycloudflare /tmp/cf.log 2>/dev/null && break; done
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
