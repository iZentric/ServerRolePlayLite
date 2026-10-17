export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
M=$HOME/cuantic-live
cd ~/freeroam
echo "== MONTARE mods din manifest =="
python3 - <<'PY'
import json,os,urllib.request
base=os.path.expanduser('~/freeroam/x')
mdir=os.path.expanduser('~/cuantic-live/mods'); os.makedirs(mdir,exist_ok=True)
idx=json.load(open(base+'/modrinth.index.json'))
n=0
for f in idx.get('files',[]):
    dest=os.path.join(mdir,f['path'])
    os.makedirs(os.path.dirname(dest),exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest)>1000: continue
    try:
        d=urllib.request.urlopen(urllib.request.Request(f['downloads'][0],headers={'User-Agent':'claie'}),timeout=120).read()
        open(dest,'wb').write(d); n+=1
    except Exception as e: print('esuat',f['path'],str(e)[:60])
print('descarcate:',n,'total files manifest:',len(idx.get('files',[])))
PY
cp -f x/overrides/mods/*.jar ~/cuantic-live/mods/ 2>/dev/null
cp -rn x/overrides/config/. ~/cuantic-live/config/ 2>/dev/null
ls x/overrides/ 2>/dev/null
echo "mods final: $(ls ~/cuantic-live/mods | wc -l)"
ls ~/cuantic-live/mods | grep -icE "obfuscate|selene|playeranim" | sed 's/^/lib prezenta: /'
pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 4
rm -f ~/cuantic-live/world/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 56); do sleep 5; grep -q "Done (" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -oE "Done \([0-9.]*s\)!" | tail -1
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || { echo EROII:; sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -E "requires|FATAL|Caused by|Error" | head -6 | cut -c1-150; }
