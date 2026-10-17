export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
rm -f mods/obfuscate-0.6.2-1.16.3.jar
python3 - <<'PY'
import json,urllib.request,urllib.parse
M='/home/mndvasi9/cuantic-live/mods/'
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'claie'}),timeout=40))
for name in ['obfuscate','selene']:
    done=False
    try:
        s=get('https://api.modrinth.com/v2/search?query='+name+'&limit=8&facets='+urllib.parse.quote('[["versions:1.16.5"]]'))
    except Exception as e:
        print('search fail',name,e); continue
    for hit in s.get('hits',[]):
        if name not in hit['title'].lower(): continue
        try: rels=get('https://api.modrinth.com/v2/project/%s/version'%hit['slug'])
        except Exception: continue
        for r in rels:
            if '1.16.5' not in r.get('game_versions',[]): continue
            for f in r.get('files',[]):
                if f['filename'].lower().endswith('.jar'):
                    try:
                        data=urllib.request.urlopen(urllib.request.Request(f['url'],headers={'User-Agent':'claie'}),timeout=120).read()
                        open(M+f['filename'],'wb').write(data)
                        print('OK %s: %s (%d B)'%(name,f['filename'],len(data))); done=True; break
                    except Exception as e: print('dl fail',f['url'],e)
            if done: break
        if done: break
    if not done: print('NUGASIT',name)
PY
pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 4
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 60); do sleep 5; grep -q "Done (" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -oE "Done \([0-9.]*s\)!" | tail -1
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || { echo "CRASH:"; sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -B2 -A8 "requires\|Failed to load\|Caused by" | head -14 | cut -c1-150; }
