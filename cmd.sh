export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
J=$(pgrep -f "j11/bin/java" | head -1)
if [ -n "$J" ]; then
  echo "Java traieste deja (eloadare in curs) - NU il omor. il las 12 min:"
  for i in $(seq 1 144); do sleep 5; grep -qaE "Done \(|FATAL" boot.log && break; done
else
  echo "Java mort - capat RAM la 8G si pornire curata:"
  grep -oE "\-Xmx[0-9]+M" unix_args.txt user_jvm_args.txt 2>/dev/null | head -2
  sed -i -E 's/-Xmx[0-9]+M/-Xmx8192M/' unix_args.txt user_jvm_args.txt 2>/dev/null
  rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
  setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
  for i in $(seq 1 144); do sleep 5; grep -qaE "Done \(|FATAL" boot.log && break; done
fi
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
DONE=$(grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1)
echo "BOOT: ${DONE:-FARA DONE dupa 12 min}"
tail -3 boot.clean | cut -c1-130
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: INCHIS"
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
    print('PING OK |',d.get('version',{}).get('name'),'| online:',d.get('players',{}).get('online'),'/',d.get('players',{}).get('max'),'| desc:',str(d.get('description'))[:45])
except Exception as e:
    print('PING esuat:',str(e)[:80])
PY
