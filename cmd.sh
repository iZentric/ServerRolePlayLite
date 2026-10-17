export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
python3 - <<'PY'
import json,os,urllib.request
z=json.load(open(os.path.expanduser('~/freeroam/x/modrinth.index.json')))
need=('obfuscate','selene','playeranimator','lightfall')
print('manifest fisiere:',len(z.get('files',[])),'| overrides:',sum(1 for f in os.listdir(os.path.expanduser('~/freeroam/x/overrides/mods')) if f.endswith('.jar')) if os.path.isdir(os.path.expanduser('~/freeroam/x/overrides/mods')) else 0)
got=[]
for f in z.get('files',[]):
    p=f['path'].lower()
    if any(n in p for n in need):
        got.append((f['path'],f.get('downloads',[])))
print('lib in manifest:',got or 'NICIUNA')
m=os.path.expanduser('~/cuantic-live/mods')
import shutil
for path,dl in got:
    fn=os.path.basename(path)
    if os.path.exists(os.path.join(m,fn)): continue
    if dl:
        try:
            d=urllib.request.urlopen(urllib.request.Request(dl[0],headers={'User-Agent':'c'}),timeout=120).read()
            open(os.path.join(m,fn),'wb').write(d); print('OK',fn,len(d))
        except Exception as e: print('ES',fn,str(e)[:60])
# si din overrides (arhiva locala a userului)
ov=os.path.expanduser('~/freeroam/x/overrides/mods')
if os.path.isdir(ov):
    for fn in os.listdir(ov):
        if any(n in fn.lower() for n in need) and not os.path.exists(os.path.join(m,fn)):
            shutil.copy(os.path.join(ov,fn),os.path.join(m,fn)); print('OVR',fn)
PY
ls mods/ | grep -aiE "obfuscate|selene|playeranim|lightfall"
echo "== BOOT =="
pkill -9 -f java 2>/dev/null; sleep 5
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 80); do sleep 5; grep -qaE "Done \(|FATAL" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
DONE=$(grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1)
echo "BOOT: ${DONE:-NU A DAT DONE}"
if [ -z "$DONE" ]; then
  grep -aE "requires" boot.clean | head -6
  echo "== PLAN B: eliminam exact modurile care cer lib absent si repornim =="
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
  grep -c "Done" boot.clean >/dev/null
fi
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: INCHIS"
