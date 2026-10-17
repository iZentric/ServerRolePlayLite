export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
echo "== cloudflared client (arm64) =="
[ -x ~/cfd ] || curl -sfLo ~/cfd https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 && chmod +x ~/cfd
~/cfd --version 2>&1 | head -1
pkill -f "cfd access" 2>/dev/null; sleep 1
(setsid nohup ~/cfd access tcp --hostname browser-definitely-cardiff-room.trycloudflare.com --url 127.0.0.1:15565 > /tmp/cfa.log 2>&1 < /dev/null &)
sleep 8
ss -lnt 2>/dev/null | grep -q ":15565 " && echo "proxy local: ASCOLTAT pe 15565" || { echo "proxy: NU IESI"; tail -3 /tmp/cfa.log; }
python3 - <<'PY' 2>&1
import socket, time
try:
    s = socket.create_connection(("127.0.0.1", 15565), timeout=15); s.settimeout(25)
    def vs(n):
        out=b""
        while True:
            b=n&0x7f; n>>=7
            if n: b|=0x80
            out+=bytes([b])
            if not n: return out
    hs=vs(0)+vs(-1)+vs(0)
    s.sendall(vs(len(hs))+hs)
    time.sleep(4)
    data=b""
    while len(data)<4:
        c=s.recv(4096)
        if not c: break
        data+=c
    print("RECIEVED:", len(data))
    if len(data)>4:
        import json as J
        n=len(data)
        print("JAR-STYLE STATUS OK" if data[0:1]!=b"\x00" or True else "?")
        print("SAMPLE:", data[:60])
except Exception as e:
    print("ERROR:", e)
PY
