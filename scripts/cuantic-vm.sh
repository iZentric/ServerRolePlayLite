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
sed -i 's/^online-mode=.*/online-mode=false/; s/^server-ip=.*/server-ip=/' server.properties
# 6G de swap: free tier, nu strica nimic si evita OOM in varf
if [ ! -f /swapfile ]; then fallocate -l 6G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile; fi
# stdin-ul nu trebuie sa dea EOF (pe 1.16.5 EOF = "Stopping server"), deci il tinem ocupat cu tail
printf '[Unit]\nDescription=CUANTIC MC\nAfter=network-online.target\nWants=network-online.target\n[Service]\nWorkingDirectory=/opt/cuantic\nExecStart=/bin/sh -c "tail -f /dev/null | /usr/bin/java @unix_args.txt"\nExecStopPre=/bin/sh -c "echo save-all > /proc/1/fd/0 || true"\nRestart=always\nRestartSec=10\nTimeoutStartSec=1800\nLimitNOFILE=65535\n[Install]\nWantedBy=multi-user.target\n' > /etc/systemd/system/mc.service
systemctl daemon-reload
systemctl enable --now mc
ufw allow 25565/tcp
iptables -C INPUT -p tcp --dport 25565 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 25565 -j ACCEPT
# unealta de control (o folosesc si din agent, prin Run Command)
printf '#!/bin/sh\n# mcctl stop|start|restart|log|save\nC="$1"; [ -z "$C" ] && C=log\ncase "$C" in\n  save) journalctl -u mc -n 5 --no-pager; systemctl restart mc;;\n  log) journalctl -u mc -n 60 --no-pager;;\n  *) systemctl "$C" mc;;\nesac\nsleep 1\njournalctl -u mc -n 6 --no-pager\n' > /usr/local/bin/mcctl
chmod +x /usr/local/bin/mcctl
sleep 25
systemctl is-active mc
ss -lnt | grep 25565
echo "BOOT-DONE $(date -u +%FT%TZ)"
