#!/bin/bash
# CUANTIC — ruleaza prin cloud-init pe VM-ul proaspat creat (root).
exec >> /var/log/cuantic-boot.log 2>&1
set -x
export DEBIAN_FRONTEND=noninteractive
for i in $(seq 1 30); do fuser /var/lib/dpkg/lock-frontend 2>/dev/null || break; sleep 10; done
apt-get -y update
apt-get install -y openjdk-17-jre-headless unzip curl ca-certificates
mkdir -p /opt/cuantic
cd /opt/cuantic
URL=$(curl -fsS https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
echo "PACK_URL=$URL"
curl -fsSLo p.zip "$URL"
S=$(sha256sum p.zip | cut -d' ' -f1)
echo "SHA256=$S"
if [ "$S" != "b97230e1073a8d1568205ab6fec92981b3903d947a101026deb5f9e75de0b278" ]; then echo "!! SHA diferit - continui dar se raporteaza"; fi
unzip -qo p.zip
rm -f p.zip
echo eula=true > eula.txt
sed -i 's/^online-mode=.*/online-mode=false/; s/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25566/' server.properties
grep -q '^server-port=' server.properties || echo 'server-port=25566' >> server.properties
# 6G de swap: free tier, nu strica nimic si evita OOM in varf
if [ ! -f /swapfile ]; then fallocate -l 6G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile; fi
# stdin-ul nu trebuie sa dea EOF (pe 1.16.5 EOF = "Stopping server"), deci il tinem ocupat cu tail
# ---- mc.service: NU e pornit la boot; e trezit de proxy-ul CUANTIC WAKE la primul contact ----
printf '[Unit]\nDescription=CUANTIC MC (trezit la nevoie)\nAfter=network-online.target\nWants=network-online.target\n[Service]\nType=simple\nWorkingDirectory=/opt/cuantic\nExecStart=/bin/sh -c "tail -f /dev/null | /usr/bin/java @unix_args.txt"\nRestart=no\nTimeoutStartSec=1800\nTimeoutStopSec=120\nSendSIGKILL=no\nLimitNOFILE=65535\n' > /etc/systemd/system/mc.service
# ---- cuantic-wake.py: asculta 25565 non-stop (citeva zeci de MB), ridica MC cand da cineva Join,
#      il opreste dupa 15 minute fara nici un jucator => cost 0 cand e gol, ~15s cand intri
printf '[Unit]\nDescription=CUANTIC WAKE (port 25565 mereu deschis, server trezit la contact)\nAfter=network-online.target\nWants=network-online.target\n[Service]\nWorkingDirectory=/opt/cuantic\nExecStart=/usr/bin/python3 /opt/cuantic/cuantic-wake.py\nEnvironment=MC_IDLE_SEC=900\nEnvironment=MC_BOOT_WAIT=180\nRestart=always\nRestartSec=5\n[Install]\nWantedBy=multi-user.target\n' > /etc/systemd/system/cuantic-wake.service
curl -fsSLo /opt/cuantic/cuantic-wake.py https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts/cuantic-wake.py || echo "!! cuantic-wake.py nu s-a descarcat (serverul va ramane mereu pornit)"
systemctl daemon-reload
systemctl disable mc 2>/dev/null || true
systemctl enable --now cuantic-wake
ufw allow 25565/tcp
iptables -I INPUT -p tcp --dport 25565 -j ACCEPT 2>/dev/null || true
printf '#!/bin/sh\n# mcctl wake|log|save|on|off|restart|stare\nC="$1"; [ -z "$C" ] && C=stare\ncase "$C" in\n  wake|on) systemctl start cuantic-wake; systemctl start mc;;\n  off) systemctl stop mc;;\n  restart) systemctl restart mc;;\n  save) systemctl kill -s SIGTERM mc;;\n  log) journalctl -u mc -n 80 --no-pager;;\n  stare) systemctl is-active cuantic-wake mc; ss -lnt | grep -E "25565|25566";;\nesac\nsleep 1\njournalctl -u cuantic-wake -n 6 --no-pager\n' > /usr/local/bin/mcctl
chmod +x /usr/local/bin/mcctl
echo "== stare =="; systemctl is-active cuantic-wake || true; ( exec 3<>/dev/tcp/127.0.0.1/25565 ) 2>/dev/null && echo "port 25565: DESCHIS (asteapta primul join)" || echo "port 25565: INCHIS"
systemctl is-active mc
ss -lnt | grep 25565
echo "BOOT-DONE $(date -u +%FT%TZ)"
