#!/bin/bash
# ===================================================================
# ORACLE CLOUD (ARM, gratis pe viata) -> serverul nostru, 1 comanda:
#   curl -sL https://github.com/iZentric/ServerRolePlayLite/raw/arena/a29b4ef4-serverroleplaylite/deploy/oracle-setup.sh | sudo bash
# Ubuntu 22.04/24.04 aarch64 (Ampere A1). Face TOT: java, server,
# firewall, swap, systemd (porneste singur la boot), backup local.
# ===================================================================
set -eo pipefail
echo ">>> [1/6] Java 11 (ARM) + unelte"
apt-get update -qq && apt-get install -y -qq openjdk-11-jre-headless unzip curl jq

echo ">>> [2/6] Swap 4G (plasa de siguranta RAM)"
if [ ! -f /swapfile ]; then
  fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo ">>> [3/6] Firewall: 25565 deschis (+ regula Oracle din panou!)"
iptables -I INPUT -p tcp --dport 25565 -j ACCEPT || true
command -v netfilter-persistent >/dev/null && netfilter-persistent save || true

echo ">>> [4/6] Descarc ultimul server Mist din Releases"
mkdir -p /opt/minecraft && cd /opt/minecraft
URL=$(curl -s https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | jq -r '.assets[] | select(.name | test("Server-Mist")) | .browser_download_url')
curl -sL -o server.zip "$URL" && unzip -oq server.zip && rm server.zip
echo "eula=true" > eula.txt

echo ">>> [5/6] Serviciu systemd (porneste singur, repornire la crash)"
JAR=$(ls mist-*.jar | head -1)
FLAGS=$(grep -o '\-XX[^ "]*' start.sh | tr '\n' ' ' || echo "-XX:+UseG1GC")
cat > /etc/systemd/system/minecraft.service << EOF
[Unit]
Description=Server RolePlay Lite
After=network.target
[Service]
WorkingDirectory=/opt/minecraft
ExecStart=/usr/bin/java -Xms2G -Xmx10G $FLAGS -jar $JAR nogui
Restart=on-failure
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload && systemctl enable minecraft

echo ">>> [6/6] Backup local zilnic la 04:00"
echo '0 4 * * * root tar -czf /opt/backup-world-$(date +\%u).tgz -C /opt/minecraft world' > /etc/cron.d/mc-backup

echo ""
echo "=========================================="
echo " GATA. Porneste cu:  sudo systemctl start minecraft"
echo " Loguri:             journalctl -u minecraft -f"
echo " NU UITA: in panoul Oracle -> VCN -> Security List -> Ingress 25565/TCP"
echo "=========================================="
