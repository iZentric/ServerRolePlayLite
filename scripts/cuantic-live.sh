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
RELJSON=$(curl -fsSLo - --max-time 25 "https://api.github.com/repos/$REPO/releases/tags/lite" 2>/dev/null)
printf '%s' "$RELJSON" | python3 -c "
import sys, json
try:
    a = json.load(sys.stdin).get('assets', [])
except Exception:
    a = []
for x in a:
    if 'Server-CatServer' in x.get('name',''):
        print(x['name']); print(x['browser_download_url']); break
" > /tmp/rel.info 2>/dev/null
RNAME=$(sed -n 1p /tmp/rel.info 2>/dev/null)
RURL=$(sed -n 2p /tmp/rel.info 2>/dev/null)
NEW="$RNAME"
CUR=$(cat "$D/.pack" 2>/dev/null)
if [ -n "$NEW" ] && [ "$NEW" != "$CUR" ]; then
  echo "PACK: ${CUR:-niciunul} -> $NEW (world-ul ramane)"
  Z="/tmp/$NEW"; rm -rf /tmp/pk "$Z"; mkdir -p /tmp/pk
  if [ -n "$RURL" ] && curl -fL --max-time 400 -o "$Z" "$RURL" >/dev/null 2>&1 && [ -s "$Z" ]; then
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
# fixargs — self-heal: daca JVM-ul de aici refuza un flag din unix_args.txt (ex. Java 17 vs
# setul Aikar scris pentru Java 11), il taiem si pornim oricum. Fara asta = „serverul nu porneste".
fixargs() {
  local n=0 ERR BAD
  while :; do
    # validam DOAR flagurile: daca am fi pus si "-jar x.jar" inainte de -version, java ar fi
    # interpretat -version ca ARGUMENT al serverului si ar fi PORNIT un al doilea server.
    FLAGS_ONLY=$(sed '/^-jar$/,$d' unix_args.txt | tr '\n' ' ')
    # java -version scrie INTOTDEAUNA pe stderr, deci stderr-ul nu e dovada esecului:
    # judecam codul de iesire (altfel cada-ul ar crede ca toate flagurile-s stricate).
    if "$J" $FLAGS_ONLY -version >/dev/null 2>&1; then return 0; fi
    ERR=$("$J" $FLAGS_ONLY -version 2>&1 | head -6)
    BAD=$(printf '%s' "$ERR" | grep -aoE "Unrecognized VM option '[^']+'" | head -1 | sed "s/.*'\([^']*\)'.*/\1/" | cut -d= -f1)
    [ -z "$BAD" ] && BAD=$(printf '%s' "$ERR" | grep -aoE "VM option '[^']+' is experimental" | head -1 | sed "s/.*'\([^']*\)'.*/\1/" | cut -d= -f1)
    if [ -z "$BAD" ]; then echo "!! unix_args respins, mesaj necunoscut: $(printf '%s' "$ERR" | head -2 | tr '\n' ' ' | cut -c1-160)"; return 1; fi
    { grep -v -- "-XX:[+-]*$BAD" unix_args.txt; } > /tmp/ua.new && mv /tmp/ua.new unix_args.txt
    echo "   tai flag nesuportat: $BAD (java: $("$J" -version 2>&1 | head -1 | cut -d'"' -f2))"
    n=$((n+1)); [ $n -gt 40 ] && return 1
  done
}
RAW=https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts
start_mc() {
  [ -f "$HOME/cuantic-args.sh" ] || curl -fsSLo "$HOME/cuantic-args.sh" "$RAW/cuantic-args.sh" 2>/dev/null
  [ -f "$HOME/cuantic-args.sh" ] && bash "$HOME/cuantic-args.sh" "$D"
  fixargs
  echo "==== pornire $(date -u '+%F %T UTC') (memorie: $(grep -aoE '^-Xmx[^ ]*' unix_args.txt | head -1), java: $J) ====" >> live.log
  setsid "$J" @unix_args.txt <&3 >> live.log 2>&1 &
}
echo "JAVA: $J -> $("$J" -version 2>&1 | head -1)"
[ -s "$(ls CatServer-*.jar 2>/dev/null | head -1)" ] || echo "!! jar absent - ruleaza jobul JAVA inainte"
tmux kill-session -t frpc 2>/dev/null
tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"
# pază de dublu-pornit: daca java e deja SUS (pornit de ex. de un job de diagnostic), il supervisez
# si il folosesc, dar NU mai pornesc al doilea server pe aceeasi lume (ar bloca region lock-ul).
if pgrep -f 'java @unix_args' >/dev/null 2>&1; then
  echo "java e deja SUS -> il supervisez, nu-il repornesc (puntea cmd.in functioneaza pe procesul existent)"
else
  start_mc
fi
echo "MC pornit. Adresa: 92.5.171.150:25565. Ctrl+C = opresti DOAR supervisorul (serverul ramane sus)."
LAST=-1
while :; do
  # puntea: orice linie din cmd.in merge in consola serverului
  if [ -s cmd.in ]; then
    while IFS= read -r L; do
      [ -n "$L" ] || continue
      case "$L" in
        restart) echo "[$(date +%T)] restart cerut"; pkill -f 'java @unix_args'; sleep 8
                 start_mc; echo "[$(date +%T)] MC repornit" ;;
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
    # guardian de memorie: daca java a murit fara sa apuce "Done (" si logul zice OOM/Killed,
    # coboram plafonul cu 18% si il blocam in fisier - altfel am reintra la nesfarsit in groapa.
    if ! grep -aq 'Done (' live.log 2>/dev/null && grep -aqiE 'Killed process|OutOfMemoryError|GC overhead limit' live.log 2>/dev/null; then
      CUR=$(grep -aoE '^[0-9]{3,7}$' "$D/ramceil" 2>/dev/null | head -1)
      [ -n "$CUR" ] || CUR=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo)
      NEW=$(( CUR * 82 / 100 )); [ "$NEW" -lt 1024 ] && NEW=1024
      echo "$NEW" > "$D/ramceil"; echo "$(date +%T) OOM la ${CUR}MB -> plafon ${NEW}MB" >> "$D/ram.log"
      echo " ram OOM: ${CUR}MB -> ${NEW}MB"
    fi
    echo " mc mort -> repornesc"; [ -f unix_args.txt ] && start_mc; LAST=0
  elif [ "$NOW" = "$LAST" ]; then
    echo " log blocat:"; tail -2 live.log; tail -1 "$HOME/frpc.log" 2>/dev/null
  fi
  # paza de disc: home-ul din Cloud Shell are 5 GB si live.log creste la nesfarsit (spark +
  # 32 moduri). La 200 MB taiem si pastram ultimele 20000 de linii; altfel intr-o saptamana
  # discul se umple si java moare cu "No space left on device", simptom greu de banuit.
  if [ -f live.log ] && [ "$(stat -c %s live.log 2>/dev/null || echo 0)" -gt 209715200 ]; then
    tail -20000 live.log > /tmp/live.trim && mv /tmp/live.trim live.log && echo " disc: live.log trimsat la 20000 linii"
  fi
  # runner-ul GitHub: cat timp traieste acest loop, traieste si accesul agentului pe masina.
  if ! pgrep -f 'runsvc.sh|actions-runner/run.sh|./run.sh' >/dev/null 2>&1; then
    R=$(ls -d "$HOME"/actions-runner* "$HOME"/*/actions-runner* 2>/dev/null | head -1)
    if [ -n "$R" ] && [ -x "$R/run.sh" ]; then
      ( cd "$R" && setsid ./run.sh </dev/null >/dev/null 2>&1 & )
      echo " runner jos -> repornit din $R"
    fi
  fi
  tmux ls 2>/dev/null | grep -q '^frpc:' || { echo " frpc jos -> pornit"; tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"; }
  LAST=$NOW
  sleep 15
done
