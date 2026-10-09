#!/bin/bash
# CUANTIC live v5 — serverul + puntea de comenzi.
# In aceeasi masina cu serverul: java isi tine stdin deschis printr-un fifo (fara EOF = fara "Stopping server" fantoma)
# si citeste comenzi de consola din ~/cuantic-live/cmd.in (scrise din orice container, inclusiv de agent).
D=$HOME/cuantic-live
REPO=iZentric/ServerRolePlayLite
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
mkdir -p "$D"
# ===== 1.5.9: packul se singureaza de unul singur =====
# Clientul si serverul trebuie sa vina din ACELASI build: altfel id-urile de registru
# difera si FML refuza login-ul ("Missing registry data"). Daca pe release e o versiune
# noua, o punem pe server fara sa stricam world-ul.
NEW=$(gh release view lite --repo "$REPO" --json assets --jq '[.assets[].name|select(test("Server-CatServer"))][0]' 2>/dev/null)
CUR=$(cat "$D/.pack" 2>/dev/null)
if [ -n "$NEW" ] && [ "$NEW" != "$CUR" ]; then
  echo "PACK: ${CUR:-niciunul} -> $NEW (world-ul ramane)"
  Z="/tmp/$NEW"; rm -rf /tmp/pk "$Z"; mkdir -p /tmp/pk
  if gh release download lite --repo "$REPO" -p "$NEW" -D /tmp --clobber >/dev/null 2>&1; then
    unzip -oq "$Z" -d /tmp/pk
    ( cd "$D" && rm -rf mods plugins && mkdir -p mods plugins
      for f in /tmp/pk/*; do b=$(basename "$f"); case "$b" in
        mods|plugins) cp -r "$f" ./ ;;
        *.jar|*.txt|*.json) cp "$f" ./ ;;
      esac; done )
    echo "$NEW" > "$D/.pack"
    echo "PACK: actualizat -> $(ls "$D"/*.jar 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')"
    echo "unix_args md5: $(md5sum "$D/unix_args.txt" 2>/dev/null | cut -c1-8)"
  else
    echo "PACK: descarcarea a esuat - ramble varianta veche ($CUR)"
  fi
  rm -rf /tmp/pk "$Z"
fi
cd "$D" || { echo "nu exista $D"; exit 1; }
echo eula=true > eula.txt
sed -i "s/^online-mode=.*/online-mode=false/" server.properties 2>/dev/null
echo "RULEAZA: pack $(cat "$D/.pack" 2>/dev/null || echo vechi), java $($J -version 2>&1 | head -1)"
: > cmd.in
mkfifo -m 600 in.fifo 2>/dev/null
exec 3<>in.fifo
echo "JAVA: $J -> $("$J" -version 2>&1 | head -1)"
[ -s "$(ls CatServer-*.jar 2>/dev/null | head -1)" ] || echo "!! jar absent - ruleaza jobul JAVA inainte"
tmux kill-session -t frpc 2>/dev/null
tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"
setsid "$J" @unix_args.txt < in.fifo > live.log 2>&1 &
echo "MC pornit. Adresa: 92.5.171.150:25565. Ctrl+C = opresti DOAR supervisorul (serverul ramane sus)."
LAST=-1
while :; do
  # puntea: orice linie din cmd.in merge in consola serverului
  if [ -s cmd.in ]; then
    while IFS= read -r L; do
      [ -n "$L" ] || continue
      case "$L" in
        restart) echo "[$(date +%T)] restart cerut"; pkill -f 'java @unix_args'; sleep 8
                 setsid "$J" @unix_args.txt < in.fifo > live.log 2>&1 & echo "[$(date +%T)] MC repornit" ;;
        stop)    echo "[$(date +%T)] stop cerut"; printf 'stop\n' >&3; sleep 6 ;;
        *)       printf '%s\n' "$L" >&3; echo "[$(date +%T)] trimis: $L" ;;
      esac
    done < cmd.in
    : > cmd.in
  fi
  NOW=$(wc -l < live.log 2>/dev/null)
  if pgrep -f 'java @unix_args' > /dev/null; then ALIVE=DA; else ALIVE=NU; fi
  if ss -lnt | grep -q ':25565'; then S="SUS"; else S="nu asculta"; fi
  echo " $(date +%T) mc=$ALIVE port=$S log=$NOW"
  if [ "$ALIVE" = NU ]; then
    echo " mc mort -> repornesc"; setsid "$J" @unix_args.txt < in.fifo > live.log 2>&1 & LAST=0
  elif [ "$NOW" = "$LAST" ]; then
    echo " log blocat:"; tail -2 live.log; tail -1 "$HOME/frpc.log" 2>/dev/null
  fi
  tmux ls 2>/dev/null | grep -q '^frpc:' || { echo " frpc jos -> pornit"; tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"; }
  LAST=$NOW
  sleep 15
done
