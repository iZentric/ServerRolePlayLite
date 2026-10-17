#!/bin/bash
export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "### 1. SERVER: repornire sanatoasa ###"
cd ~/cuantic-live 2>/dev/null || { echo "NU AM GASIT ~/cuantic-live"; exit 1; }
pgrep -f unix_args >/dev/null && echo "server deja VIU" || {
  nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 &
  echo "astept pornire..."; for i in $(seq 1 60); do sleep 5; grep -q "Done (" boot.log && break; done
}
grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1
echo "### 2. CLIENT: zip + release ###"
if [ ! -f ~/FunCity-Client-Lite.zip ]; then echo "client pack lipseste - il rulez prin claie dupa"; else
  T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
  RID=$(curl -s https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/client-lite | grep -oE '"id": *[0-9]+' | head -1 | grep -oE '[0-9]+')
  UP=$(curl -s https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/$RID | grep -oE '"upload_url": *"[^"]*"' | cut -d'"' -f4 | sed 's/{?name,label}//')
  C=$(curl -s -o /tmp/up.out -w "%{http_code}" -X POST -H "Authorization: token $T" -H "Content-Type: application/zip" --data-binary @~/FunCity-Client-Lite.zip "$UP?name=FunCity-Client-Lite.zip&label=client+zip")
  echo "upload HTTP $C"; grep -oE '"browser_download_url": *"[^"]*"' /tmp/up.out | head -1
fi
echo "### 3. ADRESA PUBLICA ###"
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log 2>/dev/null | head -1 || {
  cd ~/cuantic-live; nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 &
  for i in $(seq 1 25); do sleep 3; grep -q trycloudflare /tmp/cf.log && break; done
  grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
}
echo "### GATA — pornesc claie (canalul tau direct cu Arena) ###"
[ -f ~/.claie.sh ] || curl -s https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/main/claie.sh -o ~/.claie.sh
exec bash ~/.claie.sh
