#!/usr/bin/env bash
# CHAT-BRIDGE — duce chat-ul Minecraft la agent si inapoi, prin GitHub.
#
# De ce asa: agentul nu poate trai incontinuu pe masina (joburile GitHub mor, Cloud Shell la fel),
# deci puntea lucreaza in runduri: fiecare runda = 1 job care (a) citeste ce s-a scris in joc de la
# ultima pozitie, (b) citeste raspunsul agentului din repo si il varsa in chat prin `say`.
# Directia box->agent are nevoie de un job (fara token pe masina nu se poate impinge din c.sh),
# de-aiia Agentul este cel care "da tonul" (trigger = push pe deploy/chat.txt).
D=$HOME/cuantic-live
L=$D/live.log
BR=arena/a29b4ef4-serverroleplaylite
V="CHAT:"
cd "$D" 2>/dev/null || { echo "CHAT: lipsa $D"; exit 0; }
STRIP="s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g; s/\r/\n/g"

# ---- 1. raspunsul agentului -> in joc (doar o data per mesaj) ----
REPLY_FILE="$GITHUB_WORKSPACE/deploy/CHAT-REPLY.txt"
if [ -s "$REPLY_FILE" ]; then
  TXT=$(head -c 900 "$REPLY_FILE" | tr '\n' ' ')
  HASH=$(printf '%s' "$TXT" | md5sum | cut -c1-12)
  if [ "$HASH" != "$(cat "$D/.replyhash" 2>/dev/null)" ]; then
    # Scriem pe FIFO (stdin-ul JVM-ului), nu pe cmd.in: cmd.in are nevoie de supervisorul c.sh,
    # care moare odata cu sesiunea Cloud Shell. Scrierea pe fifo blocheaza daca nimeni nu citeste,
    # deci timeout 6s ca sa nu atarnam jobul.
    LINIE=$(printf 'say CUANTIC agent: %s' "$TXT")
    if timeout 6 sh -c "printf '%s\n' \"$1\" > \"$D/in.fifo\"" _ "$LINIE" 2>/dev/null; then
      V="$V spus-prin-fifo=$HASH"
    else
      printf 'say CUANTIC agent: %s\n' "$TXT" >> "$D/cmd.in"
      V="$V fifo-plin->cmd.in"
    fi
    echo "$HASH" > "$D/.replyhash"
    sleep 4
  else
    V="$V mesaj-vechi-ignorat"
  fi
else
  V="$V fara-raspuns-in-repo"
fi

# ---- 2. ce s-a scris in joc de la ultima pozitie ----
POS=$(cat "$D/.chatpos" 2>/dev/null || echo 0)
TOT=$(wc -l < "$L" 2>/dev/null || echo 0)
sed -e "$STRIP" "$L" 2>/dev/null | tail -n +$(( POS + 1 )) > /tmp/chat-window.txt
grep -aoE '<[A-Za-z0-9_]{2,16}> [^|]{1,140}' /tmp/chat-window.txt 2>/dev/null | tail -40 > /tmp/chat-new.txt
grep -aoE '\]: [A-Za-z0-9_]{2,16} (joined the game|lost connection[^|]{0,60}|left the game)' /tmp/chat-window.txt 2>/dev/null | tail -10 >> /tmp/chat-new.txt
grep -aoE 'CUANTIC agent: .*' /tmp/chat-window.txt 2>/dev/null | tail -3 >> /tmp/chat-new.txt
N=$(wc -l < /tmp/chat-new.txt 2>/dev/null || echo 0)
[ "$TOT" -gt 0 ] && echo "$TOT" > "$D/.chatpos"
V="$V linii-nou=$N poz=$TOT supervisor=$(pgrep -f 'bash .*c\.sh' >/dev/null && echo DA || echo NU)"
cat /tmp/chat-new.txt >> "$D/chat.log" 2>/dev/null
tail -1 /tmp/chat-new.txt >/dev/null 2>&1 && grep -ac . "$D/chat.log" >/dev/null 2>&1

mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
{ echo "# CHAT CUANTIC — $(date -u '+%F %T UTC')"; echo
  echo "$V"; echo
  echo "### noile linii din acest tur:"; echo '```'
  cat /tmp/chat-new.txt 2>/dev/null || true; echo '```'
  echo "### istoric (ultimele 25):"; echo '```'
  tail -25 "$D/chat.log" 2>/dev/null || echo "(nimic)"; echo '```'
  echo
  echo "pozitie in live.log: $TOT | cmd.in marime: $(wc -c < "$D/cmd.in" 2>/dev/null || echo 0) bytes | java: $(pgrep -f 'java @unix_args' >/dev/null && echo SUS || echo JOS)"
  echo "port: $(ss -lnt 2>/dev/null | grep -c ':25565') | login-pluginuri in .fara-login: $(ls "$D/plugins/.fara-login" 2>/dev/null | grep -c jar)"
} > analysis/CHAT.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/CHAT.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 170)" || true
git pull --rebase -q origin "$BR" 2>/dev/null || true
git push -q origin "HEAD:$BR" 2>/dev/null || echo "push: nimic"
echo "$V"
exit 0
