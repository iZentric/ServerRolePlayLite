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
unzip -qo p.zip
rm -f p.zip
echo eula=true > eula.txt
sed -i 's/^online-mode=.*/online-mode=false/; s/^server-ip=.*/server-ip=/' server.properties
ls -1 | head -20
printf '[Unit]\nDescription=CUANTIC MC\nAfter=network-online.target\nWants=network-online.target\n[Service]\nWorkingDirectory=/opt/cuantic\nExecStart=/usr/bin/java @unix_args.txt\nRestart=always\nRestartSec=10\nTimeoutStartSec=1800\nLimitNOFILE=65535\n[Install]\nWantedBy=multi-user.target\n' > /etc/systemd/system/mc.service
systemctl daemon-reload
systemctl enable --now mc
ufw allow 25565/tcp
iptables -C INPUT -p tcp --dport 25565 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 25565 -j ACCEPT
sleep 25
systemctl is-active mc
ss -lnt | grep 25565
echo "BOOT-DONE $(date -u +%FT%TZ)"
