#!/usr/bin/env bash
# NETPROBE — diagnostic DOAR DE CITIRE al portului public al serverului CUANTIC.
# Nu atinge java, nu schimbă fișiere, nu repornește nimic: raportează de ce
# 92.5.171.150:25565 răspunde diferit dinăuntru față de dinafară.
# Regula proiectului: orice atingere a live-ului trece întâi prin staging.
unset RUNNER_TRACKING_ID
D=$HOME/cuantic-live
say(){ echo "$*"; }

say "== NETPROBE — $(date -u '+%F %T UTC') (read-only) =="
say "java=$(pgrep -f 'java @unix_args' | head -1) sup=$(pgrep -f 'bash .*c\.sh' | head -1) frpc=$(pgrep -f 'frpc -c' | head -1) frps=$(pgrep -f 'frps' | head -1)"
say "--- ascultatori pe 25565 / 24454 ---"
ss -ltnp 2>/dev/null | grep -E ':(25565|24454|7000)' | sed 's/^/  /' || echo "  (ss indisponibil)"
say "--- firewall ---"
if command -v sudo >/dev/null 2>&1; then
  sudo -n iptables -S 2>/dev/null | head -12 | sed 's/^/  iptables: /' || echo "  iptables: fără sudo"
  sudo -n nft list ruleset 2>/dev/null | head -20 | sed 's/^/  nft: /' || echo "  nft: fără sudo"
  sudo -n ufw status numbered 2>/dev/null | head -12 | sed 's/^/  ufw: /' || true
fi
command -v firewall-cmd >/dev/null 2>&1 && firewall-cmd --state 2>/dev/null | sed 's/^/  firewalld: /'
say "--- tunel ---"
if [ -f "$HOME/frpc.toml" ]; then
  say "  frpc.toml prezent ($(wc -l < "$HOME/frpc.toml") linii)"; tail -3 "$HOME/frpc.log" 2>/dev/null | sed 's/^/  log: /'
else
  say "  frpc.toml LIPSEȘTE -> nu există tunel de verificat"
fi
say "--- handshake local, pe aceeasi porta, din interior ---"
python3 - "$D" <<'PYP'
import re, socket, sys, time
port = 25565
targets = [("127.0.0.1", port), ("92.5.171.150", port)]
payload = b"\x00\x0a\x09\x00\x00\x00\x00\x00\x00"
for host, p in targets:
    try:
        s = socket.create_connection((host, p), timeout=8)
        s.sendall(payload)
        time.sleep(2.5)
        data = s.recv(512)
        s.close()
        clean = re.sub(rb"\x00", b"", data).decode("utf-8", "replace")[:150]
        print(f"  {host}:{p} -> conexiune acceptata, {len(data)} octeti: {clean!r}")
    except Exception as exc:  # noqa: BLE001 - diagnostic, nu actiune
        print(f"  {host}:{p} -> {type(exc).__name__}: {exc}")
PYP
say "--- interpretare ---"
cat <<'TXT'
  Daca 127.0.0.1 raspunde cu JSON iar IP-ul public da RST/0 octeti, serverul e SUS
  dar expunerea publica (tunelul frps sau regulile de retea ale gazdei) e cea care pica.
  Asta NU se repara de pe o rulare de CI: cere o actiune pe contul gazdei, aproband-o.
TXT
exit 0
