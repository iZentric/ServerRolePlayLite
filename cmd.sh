export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
rm -f mods/obfuscate-0.6.2-1.16.3.jar
python3 - <<'PY'
import json,urllib.request,re
def mr(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'c'}),timeout=40))
def key(v):
    return tuple(int(x) for x in re.findall(r'\d+',v.get('version_number','0'))[:4])
for proj,pat in [('obfuscate','obfuscate'),('selene','selene')]:
    try:
        vs=mr('https://api.modrinth.com/v2/project/%s/version?game_versions=%%5B%%221.16.5%%22%%5D'%proj)
        vs=sorted([v for v in vs if v.get('loaders') and 'forge' in v['loaders']],key=key,reverse=True)
        got=None
        for v in vs:
            for f in v.get('files',[]):
                n=f['filename']
                if n.endswith('.jar') and re.search(pat+r'[^/]*\.jar$',n,re.I):
                    got=(n,f['url']); break
            if got: break
        if not got:
            print('NUGASIT',proj); continue
        d=urllib.request.urlopen(urllib.request.Request(got[1],headers={'User-Agent':'c'}),timeout=180).read()
        open('/home/mndvasi9/cuantic-live/mods/'+got[0],'wb').write(d)
        print('OK',proj,':',got[0],len(d),'B')
    except Exception as e:
        print('FAIL',proj,str(e)[:90])
PY
ls mods/ | grep -aiE "obfuscate|selene"
echo "== BOOT =="
pkill -9 -f java 2>/dev/null; sleep 5
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 80); do sleep 5; grep -qaE "Done \(|FATAL" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
DONE=$(grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1)
echo "BOOT: ${DONE:-NU A DAT DONE}"
[ -z "$DONE" ] && grep -aE "requires|FATAL" boot.clean | head -4 | cut -c1-140
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
    print('PING OK |',d.get('version',{}).get('name'),'| online:',d.get('players',{}).get('online'),'/',d.get('players',{}).get('max'))
except Exception as e:
    print('PING esuat:',str(e)[:80])
PY
