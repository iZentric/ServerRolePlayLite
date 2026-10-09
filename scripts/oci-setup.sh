#!/usr/bin/env bash
# CUANTIC · instalare/remontare pe VM Oracle Cloud (ARM Always Free)
# Ruleaza CA UTILIZATORUL normal (ex. opc), cu sudo-passwordless. Idempotent.
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive
REPO="iZentric/ServerRolePlayLite"

echo "== 1. baze (java 17, unelte) =="
sudo -n apt-get update -qq
sudo -n apt-get install -y -qq openjdk-17-jre-headless unzip curl jq >/dev/null

echo "== 2. pack CUANTIC (cea mai noua release lite) =="
mkdir -p ~/cuantic && cd ~/cuantic
URL=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/tags/lite" | jq -r '.assets[].browser_download_url' | grep -m1 'Server-CatServer')
test -n "$URL"
if [ ! -f CUANTIC-VERSION ] || [ "$(cat CUANTIC-VERSION)" != "$URL" ]; then
  curl -fsSL -o pack.zip "$URL"
  unzip -qo pack.zip
  echo "$URL" > CUANTIC-VERSION
  touch .deploy-nou
fi

echo "== 3. lumea (doar la prima pornire — progresul copiilor nu se schimba niciodata automat) =="
if [ ! -d world ]; then
  WURL=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/tags/world" 2>/dev/null | jq -r '.assets[].browser_download_url' | head -1 || true)
  if [ -n "${WURL:-}" ]; then curl -fsSL -o world.zip "$WURL" && unzip -qo world.zip && rm -f world.zip; fi
fi

echo "== 4. RAM pe masura ARM-ului (UNIX_ARGS = linii 1-2) =="
if [ -f unix_args.txt ]; then
  MEM=$(awk '/MemTotal/{print int($2/1048576)}' /proc/meminfo)
  if [ "${MEM:-0}" -ge 14 ]; then HEAP=10G; else HEAP=6G; fi
  sed -i "1s/.*/-Xms${HEAP}/;2s/.*/-Xmx${HEAP}/" unix_args.txt
  head -2 unix_args.txt
fi

echo "== 5. portul 25565 prin iptables OCI (imaginea Oracle blocheaza totul ce nu-i SSH) =="
if sudo -n iptables -L INPUT --line-numbers 2>/dev/null | grep -q 25565; then echo "regula existenta"; else
  sudo -n iptables -I INPUT 6 -m state --state NEW -p tcp --dport 25565 -j ACCEPT 2>/dev/null || \
  sudo -n iptables -I INPUT -p tcp --dport 25565 -j ACCEPT
  sudo -n netfilter-persistent save 2>/dev/null || true
fi

echo "== 6. systemd (porneste singur, revine dupa crash) =="
ME=$(id -un); MYHOME="$HOME"
sudo -n tee /etc/systemd/system/cuantic.service >/dev/null <<EOF
[Unit]
Description=CUANTIC 1.16.5 CatServer EvoKode
After=network-online.target
[Service]
User=$ME
WorkingDirectory=$MYHOME/cuantic
ExecStart=/usr/bin/java -XX:+UseNUMA @$MYHOME/cuantic/unix_args.txt
Restart=always
RestartSec=10
LimitNOFILE=65536
EOF
sudo -n systemctl daemon-reload
sudo -n systemctl enable --now cuantic

echo "== 7. prima pornire masurata =="
for i in $(seq 1 60); do
  if sudo -n journalctl -u cuantic --no-pager 2>/dev/null | grep -qE "Done \("; then break; fi
  sleep 5
done
sudo -n journalctl -u cuantic --no-pager | grep -m1 -E "Done \(" || echo "INCĂ-PORNESTE"
sudo -n journalctl -u cuantic --no-pager | grep -m1 -iE "spark" || echo "(spark: de verificat in mods)"
sudo -n systemctl is-active cuantic
echo "CEA-MAI-NOUA-PORNIRE:$URL"
rm -f ~/cuantic/.deploy-nou
