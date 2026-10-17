export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
sleep 5
A=$(cat ~/lr-last.txt 2>/dev/null)
[ -z "$A" ] && A=$(grep -oE "[a-z0-9.-]+\.tcp\.localhost\.run:[0-9]+" /tmp/lr.log | tail -1) && echo "$A" > ~/lr-last.txt
echo "ADRESA: ${A:-tot-nemers}"
grep -aE "Forwarded|ssh://|tcp://" /tmp/lr.log | tail -3
H=${A%:*}; P=${A##*:}
if [ -n "$H" ] && [ -n "$P" ]; then
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
    print("HAIRPIN:", "JUCABIL" if len(d)>=5 else f"doar {len(d)} bytes")
except Exception as e:
    print("HAIRPIN: ESUAT:", e)
PY
fi
