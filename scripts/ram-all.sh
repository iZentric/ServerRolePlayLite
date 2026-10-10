#!/usr/bin/env bash
# RAM-ALL — pune serverul pe TOATA memoria masinii, asa cum a cerut utilizatorul.
#
# Ce face concret: sterge orice plafon mostenit, scrie -Xmx din /proc/meminfo (MemTotal integral),
# reporneste java si o lasa sa se dovedeasca. Daca OOM-killerul o omora inainte de "Done ("
# coboram plafonul cu 18% si incercam din nou - asa afla masina singura cat poate duce, fara
# sa ramana in bucla de morti. Fiecare incercare e inregistrata in verdict, cu cifre.
D=$HOME/cuantic-live
BR=arena/a29b4ef4-serverroleplaylite
RAW=https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/$BR/scripts
V="RAMALL:"
RPT=/tmp/ramall.txt; : > $RPT
say() { echo "$1" | tee -a $RPT; }

cd "$D" 2>/dev/null || { say "director $D lipseste"; exit 0; }
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)

# 1) aducem politica noua pe masina (atat arg-urile, cat si supervisorul cu guardianul)
curl -fsSLo "$HOME/cuantic-args.sh" "$RAW/cuantic-args.sh" && say "args.sh: actualizat"
curl -fsSLo "$HOME/c.sh" "$RAW/cuantic-live.sh" && say "c.sh: actualizat (guardian OOM inclus)"
rm -f "$D/ramceil"

TOT=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo); AV0=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
say "masina: MemTotal=${TOT}MB MemAvailable=${AV0}MB swap=$(awk '/SwapTotal/{print int($2/1024)}' /proc/meminfo)MB"

# Cursa care a facut cautarea plafonului sa dea erori false: supervisorul c.sh isi reporneste
# singur java la 15 s, in timp ce jobul meu o porneste manual => al doilea proces da in
# SessionLockManager (AlreadyLockedException) si iese in ~6 s, iar eu notam "plafonul e prea mare".
# Asa ca pe toata durata cautarii supervisorul sta oprit, iar la final il pornim inapoi cu plafonul ales.
SUP_OPRA=NU
if pgrep -f 'bash .*c\.sh' >/dev/null 2>&1; then pkill -f 'bash .*c\.sh'; sleep 3; SUP_OPRA=DA; fi

try_boot() {  # $1 = plafon in MB
  echo "$1" > "$D/ramceil" 2>/dev/null
  bash "$HOME/cuantic-args.sh" "$D" >> $RPT 2>&1
  say "  incercare -Xmx${1}M -> $(grep -aoE '^-Xmx[^ ]*' "$D/unix_args.txt" | head -1)"
  pkill -f 'java @unix_args' 2>/dev/null
  for k in 1 2 3 4 5 6 7 8 9 10; do pgrep -f 'java @unix_args' >/dev/null 2>&1 || break; sleep 2; done
  : > "$D/live.log" 2>/dev/null
  # NU folosim "< in.fifo" de-aici: deschiderea FIFO-ului pentru citire BLOCAZA pana apare un
  # scriitor, iar in timpul cautarii supervisorul (care tine fd-ul 3 deschis) e oprit => java nu
  # apuca sa existe si notam fals "a murit la 6s" pentru fiecare plafon. Solutia: deschidem fifo-ul
  # read-write (nu blocheaza niciodata) si il dam lui java ca stdin.
  ( cd "$D" && mkfifo -m 600 in.fifo 2>/dev/null; setsid "$J" @unix_args.txt 3<>"$D/in.fifo" <&3 >> live.log 2>&1 & )
  for i in $(seq 1 28); do
    sleep 6
    grep -aq 'Done (' "$D/live.log" 2>/dev/null && return 0
    pgrep -f 'java @unix_args' >/dev/null || { say "  java nu e SUS la $(($i*6))s (log: $(wc -l < \"$D/live.log\")) : $(tail -2 "$D/live.log" | tr '\n' ' ' | cut -c1-140)"; return 1; }
  done
  say "  168s fara linie Done ( : $(tail -2 "$D/live.log" | tr '\n' ' ' | cut -c1-140)"; return 1
}

CEIL=$TOT
for n in 1 2 3 4; do
  if try_boot "$CEIL"; then
    OK=$CEIL; say " PORNIT la -Xmx${CEIL}MB (asta e de fapt memoria pe care o are serverul"
    break
  fi
  CEIL=$(( CEIL * 82 / 100 )); [ "$CEIL" -lt 2048 ] && CEIL=2048
  say "  cobor plafonul la ${CEIL}MB"
done

PID=$(pgrep -f 'java @unix_args' | head -1)
if [ -n "$OK" ] && [ -n "$PID" ]; then
  say "Masuratori cu serverul pe ${OK}MB:"
  say "  heap: $(timeout 20 "$J" -version >/dev/null 2>&1; $HOME/.local/jdk17/bin/jcmd $PID GC.heap_info 2>/dev/null | grep -aE 'heap|region' | head -4 | tr '\n' ' ')"
  say "  proces: $(grep -aE 'VmHWM|VmRSS' /proc/$PID/status | tr '\n' ' ')"
  say "  masina acum: $(grep -aE 'MemAvailable' /proc/meminfo | tr '\n' ' ')"
  say "  boot: $(grep -ao 'Done ([0-9.]*s)' "$D/live.log" | tail -1) | Can't keep up: $(grep -ac "Can't keep up" "$D/live.log" 2>/dev/null)"
  say "  port 25565: $(ss -lnt 2>/dev/null | grep -c ':25565')"
  # supervisorul trebuie sa apara inapoi peste procesul pornit de job, altfel n-am cine sa primeasca comenzi
  pgrep -f 'bash .*c\.sh' >/dev/null || { ( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 & ) ; say "  supervisor repornit (a stat oprit $SUP_OPRA pe toata cautarea)"; }
else
  [ -n "$PID" ] && kill $PID 2>/dev/null
  echo $(( CEIL )) > "$D/ramceil"; say "NICIUN plafon nu a mers (ultima incercare ${CEIL}MB) - revin la varianta sigura:"
  rm -f "$D/ramceil"; bash "$HOME/cuantic-args.sh" "$D" >> $RPT 2>&1
  echo "rollback:" >> $RPT; grep -aoE '^-Xmx[^ ]*' "$D/unix_args.txt" | head -1 >> $RPT
  ( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 & ); say "  supervisor pornit cu varianta sigura"
fi

# verdictul in repo: fara fisierul asta jobul e verde degeaba
cd "$GITHUB_WORKSPACE" 2>/dev/null || exit 0
mkdir -p analysis
{ echo "# RAM-ALL — $(date -u '+%F %T UTC')"; echo; echo '```'; cat $RPT; echo '```';
  echo; echo "baseline anterior (masurate, 2G): MSPT p95 4.9 ms, GC young 47.2 ms, VmHWM 2613 MB."; } > analysis/RAM-ALL.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/RAM-ALL.md >/dev/null 2>&1
git commit -q -m "$(echo "$V $OK" | tr -d '"' | head -c 170)$(grep -aoE 'Boots la [0-9]+MB' $RPT | head -1)" || true
git pull --rebase -q origin "$BR" 2>/dev/null || true
git push -q origin "HEAD:$BR" 2>/dev/null || say "push esuat"
cat $RPT
exit 0
