#!/bin/bash
# CUANTIC — se ruleaza ca root:  sudo bash frps-install.sh
set -x
cd /tmp
ARCH=$(uname -m); case $ARCH in aarch64) A=arm64;; *) A=amd64;; esac
VER=$(curl -fsS https://api.github.com/repos/fatedier/frp/releases/latest | grep -oE '"tag_name": *"v[0-9.]+"' | head -1 | grep -oE '[0-9.]+')
VER=${VER:-0.61.1}
if [ ! -x /opt/frp/frps ]; then
  curl -fsSLo frp.tgz "https://github.com/fatedier/frp/releases/download/v${VER}/frp_${VER}_linux_${A}.tar.gz"
  tar xzf frp.tgz
  mkdir -p /opt/frp
  cp frp_${VER}_linux_${A}/frps /opt/frp/frps
  chmod 755 /opt/frp/frps
fi
/opt/frp/frps --version
iptables -C INPUT -p tcp -m multiport --dports 443,25565 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp -m multiport --dports 443,25565 -j ACCEPT
nft list ruleset 2>/dev/null | grep -m1 -E 'dport (443|25565)'
printf 'bindAddr = "0.0.0.0"\nbindPort = 443\nauth.method = "token"\nauth.token = "pateu-de-codru-7"\n' > /etc/frps.toml
printf '[Unit]\nDescription=CUANTIC frp server\nAfter=network.target\n[Service]\nExecStartPre=/bin/sh -c "iptables -C INPUT -p tcp -m multiport --dports 443,25565 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp -m multiport --dports 443,25565 -j ACCEPT"\nExecStart=/opt/frp/frps -c /etc/frps.toml\nRestart=always\nRestartSec=5\n[Install]\nWantedBy=multi-user.target\n' > /etc/systemd/system/frps.service
systemctl daemon-reload
systemctl enable --now frps
sleep 3
systemctl is-active frps
ss -lnt | grep 443
echo "REZULTAT: active=$(systemctl is-active frps 2>&1) listen=$(ss -lnt | grep -c ':443') iptables_first=$(iptables -S INPUT | head -1)"
if iptables -S INPUT | head -1 | grep -q 'REJECT'; then
  echo "REGULA NU E PE PRIMUL LOC - incerc din nou"
  iptables -D INPUT -p tcp -m multiport --dports 443,25565 -j ACCEPT 2>/dev/null
  iptables -I INPUT 1 -p tcp -m multiport --dports 443,25565 -j ACCEPT
  echo "DUPA: $(iptables -S INPUT | head -1)"
fi
