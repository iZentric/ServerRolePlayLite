export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
echo "== gardieni =="; pgrep -af "daemon|claie|watchdog" 2>/dev/null | grep -v pgrep | cut -c1-70 | head -4 || echo "NICIUNA DAEMON VIU"
echo "== test round-trip cloudflare (direct, fara daemon dependence) =="
[ -x ~/cfd ] || { curl -sfLo ~/cfd https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 && chmod +x ~/cfd; }
~/cfd --version 2>&1 | head -1
pkill -f "cfd access" 2>/dev/null; sleep 1
(setsid nohup ~/cfd access tcp --hostname browser-definitely-cardiff-room.trycloudflare.com --url 127.0.0.1:15565 > /tmp/cfa.log 2>&1 < /dev/null &)
sleep 8
ss -lnt 2>/dev/null | grep -q ":15565" && echo "proxy: ASCULTA" || { echo "proxy: NU"; tail -4 /tmp/cfa.log; }
timeout 30 python3 /tmp/probe65.py 2>&1 || { cat > /tmp/probe65.py <<'PP'
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
    print("RECIEVED:", len(data), "JUCABIL-CF" if len(data)>=5 else "FARA-RASPUNS")
except Exception as e:
    print("ERROR:", e)
PP
timeout 30 python3 /tmp/probe65.py; }
