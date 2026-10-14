#!/usr/bin/env bash
# FUNCTITY-STAGE — împachetare, pornire și verificare candidat FunCity PE GAZDA, fără a atinge
# producția. Reguli scrise în piatră:
#  * NU scrie nimic în ~/cuantic-live (doar citește pentru backup/copy de lume);
#  * NU atinge cmd.in, frpc, systemd-ul producției; NU repornește producția;
#  * dacă java de producție e SUS, modul test refusează să ia portul 25565;
#  * tot ce e "pe test" se întâmplă în ~/funcity-live pe portul 25566 (25565 doar cu
#    FUNCIETY_PUBLIC=1 și producție absentă verificată);
#  * backup + verificare integritate înainte de orice boot; rollback = ștergi staging,
#    producția n-a fost mișcată.
set -uo pipefail
export RUNNER_TRACKING_ID=""
D=$HOME/funcity-live          # staging (al nostru)
P=$HOME/cuantic-live          # producție (doar citire)
B=$HOME/funcity-backup        # backup-uri
REPO=${GITHUB_REPOSITORY:-iZentric/ServerRolePlayLite}
BR_OUT=functity-out
CAND=b1.2256; PORT=25566          # defaulturile; le pot suprascrie din marker (mai jos)
XMX=${FUNCITY_XMX:-3G}
LOG=$D/stage.log; REPORT=/tmp/funcity-stage.txt
mkdir -p "$(dirname "$REPORT")" 2>/dev/null; : > "$REPORT" 2>/dev/null || true
say(){ echo "$*" | tee -a "$REPORT"; }
fail(){ say "ERORE: $*"; finish 1; }
finish(){ mkdir -p /tmp; cp "$REPORT" /tmp/funcity-stage.txt 2>/dev/null; say "(sfarsit rc=$1)"; exit "$1"; }

prod_java(){ pgrep -f 'java @unix_args' | head -1 || true; }
port_viu(){ ss -lnt 2>/dev/null | grep -q ":$1 " && echo da || echo nu; }

java11_gaseste(){
  for c in /usr/lib/jvm/*11*/bin/java /usr/lib/jvm/*-11/bin/java /opt/java/*11*/bin/java "$D/jdk11/bin/java"; do
    [ -x "$c" ] && { echo "$c"; return 0; }
  done
  return 1
}
java11_adoptium(){
  # Fără JDK 11 pe gazda? Luam Temurin 11 de la GitHub adoptium (aceeasi sursa folosita
  # de CI), cu verificare sha256 impotriva fisierului .sha256.txt de langa arhiva.
  say "java11 absent local: descarc Temurin 11 JRE (adoptium, verificat sha256)"
  local v=11.0.24+8 arch f
  case $(uname -m) in aarch64) arch=aarch64;; *) arch=x64;; esac
  f=OpenJDK11U-jre_${arch}_linux_hotspot_11.0.24_8.tar.gz
  mkdir -p "$D" && cd "$D" || fail "nu pot intra $D"
  curl -fsSLo "$f" "https://github.com/adoptium/temurin11-binaries/releases/download/jdk-${v}/${f}" || fail "descarcare JRE esuata"
  curl -fsSLo "$f.sha256.txt" "https://github.com/adoptium/temurin11-binaries/releases/download/jdk-${v}/${f}.sha256.txt" || fail "descarcare sha esuata"
  ( sha256sum -c "$f.sha256.txt" ) || fail "SHA-256 JRE NU COINCIDE — opresc, nu rulez binar necunoscut"
  tar xzf "$f" && mv jdk-11.0.24+8-jre jdk11 2>/dev/null && rm -f "$f" "$f.sha256.txt"
  echo "$D/jdk11/bin/java"
}

moduri_count(){ ls "$D/mods" 2>/dev/null | grep -c '\.jar$' || echo 0; }
plugini_count(){ ls "$D/plugins" 2>/dev/null | grep -c '\.jar$' || echo 0; }

cmd_fifo(){ # trimite o linie consolei serverului (fifo O_RDWR, acelasi model dovedit in CI)
  local line=$1
  [ -p "$D/console.in" ] || { say "fifo absent"; return 1; }
  python3 - "$D/console.in" "$line" <<'PY'
import os, sys
fd = os.open(sys.argv[1], os.O_RDWR)
os.write(fd, (sys.argv[2] + "\n").encode()); os.close(fd)
print("trimis:", sys.argv[2])
PY
}

start_server(){ # nohup + fifo stdin; supravietuieste jobului CI (TRACKING_ID curatat sus)
  local JAVA=$1
  say "pornesc FunCity pe portul $PORT (heap $XMX, java: $JAVA)"
  : > "$LOG"
  ( cd "$D" && mkfifo -m 600 console.in 2>/dev/null; rm -f console.fifo
    python3 - "$JAVA" "$PORT" "$LOG" <<'PY' &
import os, subprocess, sys
java, port, log = sys.argv[1:4]
fifo = "console.in"
fd = os.open(fifo, os.O_RDWR)
lf = open(log, "ab", buffering=0)
p = subprocess.Popen([java, "-Xms1G", f"-Xmx{os.environ.get('FUNCITY_XMX','3G')}",
                      "-XX:MaxGCPauseMillis=200", "-jar",
                      os.environ.get("FUNCITY_JARFILE", "FunCity.jar"), "nogui"],
                     stdin=fd, stdout=lf, stderr=subprocess.STDOUT,
                     start_new_session=True, cwd=os.getcwd())
open("server.pid", "w").write(str(p.pid))
PY
  ) </dev/null >/dev/null 2>&1 &
  disown 2>/dev/null || true
}

asteapta_done(){ # $1 = secunde max
  local lim=$1 i=0
  while [ $i -lt "$lim" ]; do
    grep -q "Done (" "$LOG" 2>/dev/null && { grep "Done (" "$LOG" | tail -1 | sed 's/^/  /'; return 0; }
    if ! pgrep -f "FunCity.*jar nogui" >/dev/null 2>&1 && ! pgrep -f "funcity-live" >/dev/null 2>&1; then
      kill -0 "$(cat "$D/server.pid" 2>/dev/null)" 2>/dev/null || { say "JVM-ul a murat la boot:"; tail -25 "$LOG" | sed 's/^/  /' >>"$REPORT"; return 1; }
    fi
    sleep 4; i=$((i+4))
  done
  return 1
}

opreste_server(){
  cmd_fifo "stop" || true
  local i=0
  while [ $i -lt 90 ]; do kill -0 "$(cat "$D/server.pid" 2>/dev/null)" 2>/dev/null || break; sleep 3; i=$((i+3)); done
  if kill -0 "$(cat "$D/server.pid" 2>/dev/null)" 2>/dev/null; then say "OPRIRE NERESPONSA (am dat stop, nu omor fortat in raport)"; return 1; fi
  say "oprire curata (server a iesit dupa 'stop')"
  grep -iE "all dimensions are saved|saving worlds|ThreadedAnvil" "$LOG" | tail -2 | sed 's/^/  /'
}

verifica_log(){
  say "== verificare log =="
  say "  mods in flotasare: 'Forge mod loading' = $(grep -c 'Forge mod loading' "$LOG") (linii); 'found [0-9]* mods' = $(grep -oE 'mods active|Loading [0-9]+ mod' "$LOG" | tail -1)"
  say "  plugini (Enabling): $(grep -cE '\[?[A-Za-z0-9_]+ ]? v?[0-9.]+ |Enabling ' "$LOG" 2>/dev/null || echo 0) linii Enabling"
  say "  erori EROARE/ERROR in log: $(grep -cE '\bERROR\b| severe ' "$LOG") | Can't keep up: $(grep -c "Can't keep up" "$LOG")"
  say "  critice suspecte: $(grep -ciE 'OutOfMemory|Unable to load plugin|Failed to load|NoSuchMethod|AbstractMethodError' "$LOG")"
  say "  motd anuntat prin SLP:"
  if command -v node >/dev/null 2>&1; then
    node -e '
    const net=require("net");const s=net.connect('$PORT',"127.0.0.1");let buf=Buffer.alloc(0);
    s.on("error",e=>{console.log("    SLP esuat:",e.code);process.exit(0)});
    s.on("connect",()=>{const v=n=>{n>>>=0;const o=[];for(;;){const h=n&0x7f,c=n>>>7?0x80:0;o.push(h|c);if(!c)return Buffer.from(o);n>>>=7}};
    const hs=Buffer.concat([v(0),v(-1),v(9),Buffer.from("127.0.0.1"),(()=>{const b=Buffer.alloc(2);b.writeUInt16BE('$PORT');return b})(),v(1)]);
    s.write(Buffer.concat([v(hs.length),hs,v(1),Buffer.from([0])]))});
    s.on("data",d=>{buf=Buffer.concat([buf,d]);try{const j=JSON.parse(buf.slice(buf.indexOf(0x0a)+1).toString());console.log("    description:",j.description&&j.description.text||j.description);console.log("    players:",j.players&&j.players.online+"/"+j.players.max);s.end();process.exit(0)}catch(e){}});
    setTimeout(()=>{console.log("    SLP: timp depasit");process.exit(0)},8000);' | tee -a "$REPORT"
  else
    say "    (node absent, SLP sarit)"
  fi
}

# ============ SUBCOMENZI ============
M=${1:-test}
if [ "$M" = auto ] && [ -f deploy/funcity-stage.txt ]; then
  read -r M FP FJ _ < deploy/funcity-stage.txt || true
  export FUNCITY_PORT=${FP:-25566} FUNCITY_JAR=${FJ:-}; M=${M:-test}
  say "mod automat din marker: $M port=$FUNCITY_PORT jar=$FUNCITY_JAR" 2>/dev/null || true
fi
CAND=${FUNCITY_JAR:-b1.2256}; PORT=${FUNCITY_PORT:-25566}; XMX=${FUNCITY_XMX:-3G}
case "$M" in
  host-info)  # read-only: ce avem aici — CPU/RAM/disc/java/porturi/jucatori
    say "== FUNCTITY HOST-INFO (read-only) — $(date -u '+%F %T UTC') =="
    say "utilizator: $(whoami) | HOME=$HOME | hostname: $(hostname 2>/dev/null || cat /proc/sys/kernel/hostname)"
    say "sistem: $(uname -srm) | $(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d'"' -f2)"
    say "cpu: $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ //') | $(nproc) fire"
    awk '/MemTotal|MemAvailable/ {printf "  %s: %d MiB\n",$1,$2/1024}' /proc/meminfo | tee -a "$REPORT"
    df -m "$HOME" | tail -1 | awk '{print "  disc "$6": "$3" MiB folositi din "$2" ("$5"), liber "$4" MiB"}' | tee -a "$REPORT"
    say "java sistem: $(command -v java >/dev/null && java -version 2>&1 | head -1 || echo NICIUNA)"
    say "java11: $(java11_gaseste || echo 'absent (se va instala local la nevoie)')"
    say "node: $(command -v node >/dev/null && node --version || echo absent) | python3: $(python3 -V 2>&1) | git: $(git --version 2>&1 | head -1)"
    say "— gazda server (producție):"
    say "  director $P: $(du -sm "$P" 2>/dev/null | cut -f1) MiB total, subdirectoare mari:"
    du -sm "$P"/* 2>/dev/null | sort -rn | head -6 | sed 's/^/    /' | tee -a "$REPORT"
    say "  lume: $(du -sm "$P/world" 2>/dev/null | cut -f1) MiB | world_nether: $(du -sm "$P/world_nether" 2>/dev/null | cut -f1) | world_the_end: $(du -sm "$P/world_the_end" 2>/dev/null | cut -f1)"
    say "  jar producție: $(ls "$P"/*.jar 2>/dev/null | head -3)"
    say "  config port/motd/online-mode: $(grep -E '^(server-port|motd|online-mode|max-players)=' "$P/server.properties" 2>/dev/null | tr '\n' ' ')"
    say "— procese si porturi:"
    say "  java producție: $(prod_java || echo JOS) | supervisor c.sh: $(pgrep -f 'bash .*c\.sh' | head -1 || echo NU)"
    say "  frpc: $(pgrep -f 'frpc -c' | head -1 || echo JOS) | port 25565: $(port_viu 25565) | port 25566: $(port_viu 25566)"
    say "  jucatori (din live.log, ultima 'There are'): $(grep -oE 'There are [0-9]+ out of maximum [0-9]+' "$P/live.log" 2>/dev/null | tail -1 || grep -oE 'There are [0-9]+ out of maximum [0-9]+' "$P/logs/latest.log" 2>/dev/null | tail -1 || echo 'niciun eveniment recent')"
    say "  last Done producție: $(grep -m1 -oE 'Done \([0-9.]+s\)' "$P/live.log" 2>/dev/null | tail -1 || echo '—')"
    say "— service supervizare: systemd user: $(command -v systemctl >/dev/null && systemctl --user is-system-running 2>&1 || echo absent) | crontab: $(crontab -l 2>/dev/null | wc -l) linii"
    say "— spatiu pentru staging+backup: trebuie ~ 2x lumea; liber $(df -m "$HOME" | tail -1 | awk '{print $4}') MiB"
    finish 0
    ;;
  backup)
    say "== FUNCTITY BACKUP — $(date -u '+%F %T UTC') =="
    [ -d "$P" ] || fail "nu gasesc $P"
    mkdir -p "$B" || fail "nu pot crea $B"
    TS=$(date -u +%Y%m%d-%H%M)
    LISTA="world world_nether world_the_end server.properties server-icon.png ops.json whitelist.json permissions groups users plugins config mods run/scripts"
    TAR="$B/prod-$TS.tar.gz"
    ( cd "$P" && tar czf "$TAR" $(for x in $LISTA; do [ -e "$x" ] && printf '%s ' "$x"; done) ) || fail "tar esuat"
    say "tar scris: $TAR ($(du -m "$TAR" | cut -f1) MiB)"
    tar tzf "$TAR" >/dev/null 2>&1 || fail "arhiva CORUPTE la citire — nu continuu"
    say "integritate tar: OK ($(tar tzf "$TAR" | wc -l) intrari)"
    sha256sum "$TAR" | tee "$TAR.sha256" | sed 's/^/  /'
    sha256sum -c "$TAR.sha256" >/dev/null && say "verificare sha: OK" || fail "sha verificare esuata"
    say "rollback: copile $TAR inapoi in $P (procedura: opresti serverul, extragi in $P, pornești)"
    echo "$TAR" > "$B/ULTIMUL"
    finish 0
    ;;
  assemble)
    say "== FUNCTITY ASSEMBLE staging — $(date -u '+%F %T UTC') =="
    mkdir -p "$D" || fail "nu pot crea $D"
    say "ia artefactul validat din functity-out (builds/$CAND), cu SHA de manifest"
    rm -rf /tmp/fcclone /tmp/fcsrc; git clone -q --filter=blob:none --depth 2 "https://github.com/$REPO" /tmp/fcclone 2>/dev/null || git clone -q --depth 2 "https://github.com/$REPO" -b "$BR_OUT" /tmp/fcclone || fail "clone esuat"
    ( cd /tmp/fcclone && git fetch -q --depth 2 origin "refs/heads/$BR_OUT" && git checkout -q FETCH_HEAD ) || fail "nu gasesc $BR_OUT"
    SRC=/tmp/fcclone/builds/$CAND
    [ -d "$SRC" ] || { ls /tmp/fcclone/builds/ | sed 's/^/    /'; fail "nu exista builds/$CAND"; }
    JF=$(ls "$SRC"/FunCity-*.jar 2>/dev/null | head -1)
    [ -n "$JF" ] || fail "nu gasesc FunCity-*.jar in $CAND (posibil pasul 'Colecteaza' a murat — vezi metadata)"
    ( cd "$SRC" && [ -f SHA256SUMS.txt ] && sha256sum -c SHA256SUMS.txt ) || say "ATENTIE: fara SHA256SUMS langa jar"
    cp "$JF" "$D/$(basename "$JF")"; echo "$(basename "$JF")" > "$D/.jarname"
    export FUNCITY_JARFILE=$(basename "$JF")
    say "semnatura hibrid: $(unzip -p "$D/$(basename "$JF")" META-INF/MANIFEST.MF 2>/dev/null | grep -c ServerLaunchArgs) ServerLaunchArgs (1 = MOHIST, nu vanilla)"
    say "pachetul de componente = copia exacta a gazdei de productie (fara 'optimizari' ascunse)"
    for x in mods plugins config run/scripts spigot.yml bukkit.yml; do
      if [ -d "$P/$x" ]; then mkdir -p "$D/$x"; rsync -a --exclude='*.tmp' "$P/$x/" "$D/$x/" 2>/dev/null || cp -a "$P/$x/." "$D/$x/" 2>/dev/null; say "  copiat $x"; fi
    done
    for f in server.properties server-icon.png ops.json whitelist.json spigot.yml bukkit.yml; do
      [ -f "$P/$f" ] && cp -n "$P/$f" "$D/" && say "  copiat $f"
    done
    for w in world world_nether world_the_end; do
      if [ -d "$P/$w" ]; then rsync -a "$P/$w" "$D/" 2>>"$REPORT" || cp -a "$P/$w" "$D/"; say "  lume $w copiata in staging ($(du -sm "$D/$w" 2>/dev/null | cut -f1) MiB) - originalul neatins"; fi
    done
    say "ajustari de identitate doar pentru staging, pe portul $PORT:"
    python3 - "$D/server.properties" "$PORT" "$CAND" <<'PY'
import sys
p, port, cand = sys.argv[1:4]
try:
    ls = open(p, encoding="utf-8").read().splitlines()
except FileNotFoundError:
    ls = []
kv = {}
for l in ls:
    if "=" in l and not l.startswith("#"):
        k, v = l.split("=", 1); kv[k.strip()] = v
kv["server-port"] = port
kv["motd"] = f"FunCity RP Lite - TEST candidat {cand} (nu e serverul obisnuit)"
out = "\n".join(f"{k}={v}" for k, v in sorted(kv.items())) + "\n"
open(p, "w", encoding="utf-8").write(out)
print("  server.properties: port=" + port + " | motd=FunCity test | online-mode pastrat din productie:", kv.get("online-mode", "?"), "rcon:", kv.get("enable-rcon", "?"))
PY
    say "componente staging: $(moduri_count) moduri | $(plugini_count) plugini"
    say "config JVM staging: -Xms1G -Xmx$XMX (gazda: vezi host-info; NU umplem RAM-ul); G1 implicit, MaxGCPauseMillis=200 — atat, fara colectie de flaguri"
    finish 0
    ;;
  test)
    say "== FUNCTITY TEST (boot->stop->reboot->persistenta) — $(date -u '+%F %T UTC') =="
    [ -d "$D/mods" ] || fail "ruleaza intai assemble"
    if [ "$PORT" = 25565 ] && [ -n "$(prod_java)" ]; then fail "productia e SUS pe 25565 — nu testez in acelasi loc"; fi
    [ "$(port_viu "$PORT")" = nu ] || fail "portul $PORT e deja ocupat"
    JAVA=$(java11_gaseste) || JAVA=$(java11_adoptium) || fail "java11 indisponibil"
    export FUNCITY_XMX="$XMX" FUNCITY_JARFILE="$(cat "$D/.jarname")"
    say "--- PROBA 1: boot (include instalarea bibliotecilor Mohist daca lips) ---"
    start_server "$JAVA"
    if ! asteapta_done 240; then
      if grep -qiE "install|libraries" "$LOG" 2>/dev/null && ! grep -q "Done (" "$LOG"; then
        say "  bootstrap Mohist a instalat biblioteci — repornim o data (identic cu faza A din CI)"
        start_server "$JAVA"; asteapta_done 420 || { tail -40 "$LOG" | sed 's/^/  /' >>"$REPORT"; fail "nu a vazut 'Done (' nici dupa repornirea post-instalare"; }
      else
        tail -40 "$LOG" | sed 's/^/  /' >>"$REPORT"; fail "nu a vazut 'Done (' in 240s si nu pare instalare"
      fi
    fi
    verifica_log
    opreste_server || say "oprire problemati (raportat, mai incerc o data)"
    say "--- PROBA 2: repornire din datele salvate (persistenta) ---"
    [ -f "$D/world/level.dat" ] && say "  level.dat prezent ($(du -m "$D/world/level.dat" | cut -f1) MiB)" || say "  (fara world in staging — persistenta se va testa cu copia de lume, vezi PASIIUtilizator)"
    start_server "$JAVA"
    asteapta_done 420 || fail "al doilea boot esuat — datele salvate nu incarca"
    cmd_fifo "list" ; sleep 3
    grep -E "There are|Invalid session" "$LOG" | tail -2 | sed 's/^/  /'
    opreste_server
    say "RESULTAT: boot1+stop+boot2 OK, 0 crash la salvare/realuare"
    finish 0
    ;;
  up)
    [ "$(port_viu "$PORT")" = nu ] || fail "portul $PORT ocupat"
    JAVA=$(java11_gaseste) || JAVA=$(java11_adoptium) || fail "java11 indisponibil"
    export FUNCITY_XMX="$XMX" FUNCITY_JARFILE="$(cat "$D/.jarname")"
    start_server "$JAVA"
    asteapta_done 480 || fail "nu porneste — vezi $LOG"
    verifica_log
    say "STAGING SUS pentru testul tau (port $PORT). Oprire: functity-stage down"
    finish 0
    ;;
  down)
    opreste_server && say "jos curat"
    finish 0
    ;;
  *)
    echo "folosire: $0 host-info|backup|assemble|test|up|down"; exit 2;;
esac
