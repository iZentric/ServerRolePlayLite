export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
[ -f ~/.ssh/lr ] || ssh-keygen -t rsa -b 2048 -N "" -f ~/.ssh/lr -C functity@server -q
sed -i 's|ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=25 -o ExitOnForwardFailure=yes -R 22 localhost.run|ssh -n -i $HOME/.ssh/lr -o StrictHostKeyChecking=no -o ServerAliveInterval=25 -o ExitOnForwardFailure=yes -R 22 localhost.run|' ~/lr-loop.sh
grep -c "ssh/lr" ~/lr-loop.sh
pkill -f "lr-loop"; pkill -f "ssh.*localhost.run"; rm -f ~/lr-last.txt; sleep 2
(setsid nohup ~/lr-loop.sh >/dev/null 2>&1 </dev/null &)
for i in $(seq 1 25); do sleep 4; [ -s ~/lr-last.txt ] && break; done
A=$(cat ~/lr-last.txt 2>/dev/null); echo "ADRESA: ${A:-NEMERS}"
if [ -n "$A" ]; then
  H=${A%:*}; P=${A##*:}
  timeout 25 python3 - "$H" "$P" <<'PY'
import socket,sys,time
h,p=sys.argv[1],int(sys.argv[2])
try:
    s=socket.create_connection((h,p),timeout=12); s.settimeout(15)
    def vs(n):
        o=b""
        while True:
            b=n&0x7f; n>>=7
            if n: b|=0x80
            o+=bytes([b])
            if not n: return o
    hs=vs(0)+vs(-1)+vs(0)
    s.sendall(vs(len(hs))+hs)
    time.sleep(3)
    d=b""
    while len(d)<4:
        c=s.recv(4096)
        if not c: break
        d+=c
    print("TEST EXTERN:", "JUCABIL" if len(d)>=5 else f"RASPUNS PARTIAL {len(d)}B")
except Exception as e:
    print("TEST EXTERN: ESUAT:", e)
PY
fi
