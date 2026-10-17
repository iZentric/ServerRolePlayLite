export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
python3 - <<'PY'
import json,urllib.request
M='/home/mndvasi9/cuantic-live/mods/'
def gh(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'claie'}),timeout=30))
cands={'obfuscate':['MrCrayfish/Obfuscate'],'selene':['Mehvahdjukaar/Selene'],'playeranimator':['KosmX/PlayerAnimator','KosmX/playeranimator']}
for lib,repos in cands.items():
    got=None
    for repo in repos+[None]:
        if got: break
        if repo is None:
            try: repos=[i['full_name'] for i in gh('https://api.github.com/search/repositories?q=%s+in:name'%lib).get('items',[])[:4]]
            except Exception: repos=[]
            repo=repos.pop(0) if repos else None
            if not repo: continue
        try: rels=gh('https://api.github.com/repos/%s/releases?per_page=100'%repo)
        except Exception: continue
        for r in rels:
            for a in r.get('assets',[]):
                n=a['name'].lower()
                if n.endswith('.jar') and '1.16' in n and lib[:4] in n:
                    got=a['browser_download_url']; break
            if got: break
    if got:
        data=urllib.request.urlopen(got,timeout=180).read()
        open(M+got.split('/')[-1],'wb').write(data)
        print('OK %s <- %s (%d B)'%(lib,got.split('/')[-1],len(data)))
    else:
        print('NUGASIT %s'%lib)
PY
[ -z "$(ls mods/ 2>/dev/null | grep -i playeranim)" ] && ls mods/ | grep -i emotecraft | sed 's|^|mods/|' | xargs -r rm -v
pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 4
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 60); do sleep 5; grep -q "Done (" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -oE "Done \([0-9.]*s\)!" | tail -1
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || { echo "CRASH:"; sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -A10 "Exception\|Error" | head -12 | cut -c1-150; }
