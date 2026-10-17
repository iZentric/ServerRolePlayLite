export PATH=$PATH:/usr/bin:/bin
python3 - <<'PY'
import socket, struct, json
s=socket.create_connection(("127.0.0.1",25565),10)
def vi(n):
    o=b""
    while True:
        b=n&0x7f; n>>=7
        if n: b|=0x80
        o+=bytes([b])
        if not n: return o
def send(pid,data):
    p=vi(pid)+data; s.sendall(vi(len(p))+p)
send(0x00, vi(len("1.16.5"))+b"1.16.5"+vi(7)+vi(12345)+vi(1)+vi(0))
hdr=s.recv(8); ln=0
for i,b in enumerate(hdr[:5]):
    ln|=(b&0x7f)<<(7*i)
    if not b&0x80: break
body=s.recv(4096)
import re
m=re.search(rb'\{.*\}',body)
d=json.loads(m.group(0))
print("MOTD:", d.get("description","?") if isinstance(d.get("description"),str) else d.get("description",{}).get("text","?"))
print("JUCATORI:", d.get("players"))
print("VERSIUNE:", d.get("version",{}).get("name"), "| online-mode:", d.get("enforceSecureProfile","?"))
PY
tail -3 ~/cuantic-live/boot.log | sed "s/\x1b\[[0-9;]*m//g"
