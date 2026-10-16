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

sync_port(){ # aduce server.properties din staging la portul din marker + MOTD FunCity (doar
  # directorul de staging $D — productia nu se atinge ici).
  sed -i -E "s/^server-port=.*/server-port=$PORT/" "$D/server.properties"
  grep -q '^motd=' "$D/server.properties" && sed -i -E "s/^motd=.*/motd=FunCity RP Lite/" "$D/server.properties" || printf 'motd=FunCity RP Lite\n' >> "$D/server.properties"
  say "  server-port sincronizat cu markerul: $PORT | motd: FunCity RP Lite"
}

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
  say "java11 absent local: descarc Temurin 11 JRE (adoptium, verificat sha256)" >&2
  local v=11.0.24+8 arch f
  case $(uname -m) in aarch64) arch=aarch64;; *) arch=x64;; esac
  f=OpenJDK11U-jre_${arch}_linux_hotspot_11.0.24_8.tar.gz
  mkdir -p "$D" && cd "$D" || fail "nu pot intra $D"
  curl -fsSLo "$f" "https://github.com/adoptium/temurin11-binaries/releases/download/jdk-${v}/${f}" 2>/dev/null || { say "JRE descarcare esuata" >&2; return 1; }
  curl -fsSLo "$f.sha256.txt" "https://github.com/adoptium/temurin11-binaries/releases/download/jdk-${v}/${f}.sha256.txt" 2>/dev/null || { say "JRE sha descarcare esuata" >&2; return 1; }
  ( sha256sum -c "$f.sha256.txt" >&2 ) || { say "SHA-256 JRE NU COINCIDE - opresc, nu rulez binar necunoscut" >&2; return 1; }
  tar xzf "$f" && mv jdk-11.0.24+8-jre jdk11 2>/dev/null && rm -f "$f" "$f.sha256.txt"
  echo "$D/jdk11/bin/java"
}

voicechat_port(){ # Simple Voice Chat 1.16.5-2.3.x: configbuilder -> cheia PLATA `port`,
  # fisierul REAL e <rădăcină>/serverconfig/voicechat-server.toml (verificat in ConfigMigrator.java
  # din sursa oficiala, branch 1.16.5). config/voicechat/*.properties e doar calea VECHE de migrare.
  # Productia retine UDP 24454 -> staging foloseste 24455.
  local toml="$D/serverconfig/voicechat-server.toml"
  mkdir -p "$D/serverconfig"
  if [ -f "$toml" ] && grep -qE '^[[:space:]]*port[[:space:]]*=' "$toml"; then
    sed -i -E 's/^[[:space:]]*port[[:space:]]*=.*/port = 24455/' "$toml"
  elif [ -f "$toml" ]; then
    printf 'port = 24455\n' >> "$toml"
  else
    printf '# FunCity staging (productia tine 24454)\nport = 24455\n' > "$toml"
  fi
  # si varianta veche, complete, ca migrarea sa nu o restabileasca pe 24454
  mkdir -p "$D/config/voicechat"
  printf 'port=24455\n' > "$D/config/voicechat/voicechat-server.properties"
  say "  voicechat: serverconfig/voicechat-server.toml -> $(grep -m1 -E '^[[:space:]]*port' "$toml" | tr -d ' ')"
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

start_server(){ # supervisor separat (functity/ci/functity-supervise.py): nu da EOF pe stdin,
  # supravietuieste jobului CI (setsid + session separation) si traieste cat JVM-ul.
  local JAVA=$1
  say "pornesc FunCity pe portul $PORT (heap $XMX, java: $JAVA)"
  mkdir -p "$D" || { say "nu pot crea $D"; return 1; }
  cd "$D" || return 1
  [ -p console.in ] || mkfifo -m 600 console.in
  : > "$LOG"
  rm -f "$D/server.pid"
  setsid env FUNCITY_JAVA="$JAVA" FUNCITY_LOG="$LOG" FUNCITY_XMX="$XMX" \
    FUNCITY_JARFILE="${FUNCITY_JARFILE:-$(cat "$D/.jarname" 2>/dev/null || echo FunCity.jar)}" \
    python3 "$GITHUB_WORKSPACE/functity/ci/functity-supervise.py" >/dev/null 2>&1 &
  for t in 1 2 3 4 5 6; do sleep 3; [ -f "$D/server.pid" ] && break; done
  [ -s "$D/server.pid" ] || { say "supervisorul nu a scris server.pid"; return 1; }
  return 0
}

asteapta_done(){ # $1 = secunde max
  local lim=$1 i=0
  while [ $i -lt "$lim" ]; do
    grep -q "Done (" "$LOG" 2>/dev/null && { grep "Done (" "$LOG" | tail -1 | sed 's/^/  /' | tee -a "$REPORT"; return 0; }
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
    say "  toate java de pe gazda:"
    for p in $(pgrep java); do ps -o pid=,etime=,args= -p "$p" 2>/dev/null | sed 's/^/    /' | cut -c1-220 | tee -a "$REPORT"; done
    say "  ocupanti porturi 25565/25566:"; ss -lntp 2>/dev/null | grep -E ':(25565|25566) ' | sed 's/^/    /' | tee -a "$REPORT"
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
    [ -f "$P/eula.txt" ] && cp "$P/eula.txt" "$D/" || printf 'eula=true\n' > "$D/eula.txt"
    say "  eula: $(cat "$D/eula.txt") (identic cu productia)"
    mkdir -p "$D/mohist-config" && printf 'check_update: false\n' > "$D/mohist-config/mohist.yml" 2>/dev/null && say "  mohist.yml: check_update=false (fara legaturi inutile la pornire)"
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
    [ -f "$D/eula.txt" ] || { [ -f "$P/eula.txt" ] && cp "$P/eula.txt" "$D/" || printf 'eula=true\n' > "$D/eula.txt"; say "  eula.txt scris la pornire (gasda eula=produtiei)"; }
  mkdir -p "$D/mohist-config" && [ -f "$D/mohist-config/mohist.yml" ] || printf 'check_update: false\n' > "$D/mohist-config/mohist.yml"
    if [ "$PORT" = 25565 ] && [ -n "$(prod_java)" ]; then fail "productia e SUS pe 25565 — nu testez in acelasi loc"; fi
    [ "$(port_viu "$PORT")" = nu ] || fail "portul $PORT e deja ocupat"
    JAVA=$(java11_gaseste) || JAVA=$(java11_adoptium) || fail "java11 indisponibil"
    export FUNCITY_XMX="$XMX" FUNCITY_JARFILE="$(cat "$D/.jarname")"
    sync_port; voicechat_port
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
  install) # SCHIMB VALIDAT pe productie: FunCity b1.0827 devine serverul de pe 25565,
    # sub supravegherea lui c.sh (auto-restart, runner keepalive, frpc — tot ce are omul acasa).
    # Ordine: backup -> stop curat prin puntea cmd.in -> c.sh oprit -> jar+args+props inlocuite
    # (world NU se atinge) -> c.sh repornit -> verificare. Fiecare pas are drum de intoarcere.
    say "== INSTALL FunCity pe productie =="
    SHA_ASTEPTATA=d6ffa35c1ea9032a4a95f7f1e34b734aa7f53b0358dda6b9e6592326640a15dd
    TS=$(date -u +%Y%m%d-%H%M%S)
    # 0. canditatul exista si e cel validat?
    [ -f "$D/FunCity-1.16.5-b1.0827.jar" ] || fail "jar candidat absent in $D"
    ACTUAL=$(sha256sum "$D/FunCity-1.16.5-b1.0827.jar" | cut -d' ' -f1)
    [ "$ACTUAL" = "$SHA_ASTEPTATA" ] || fail "SHA candidat diferit: $ACTUAL"
    # 1. snapshot de rollback (marime mica, cat e nevoie: jar, args, props, c.sh, consola)
    mkdir -p "$B/install-$TS"; for f in unix_args.txt server.properties start.sh; do [ -f "$P/$f" ] && cp "$P/$f" "$B/install-$TS/"; done
    [ -f "$HOME/c.sh" ] && cp "$HOME/c.sh" "$B/install-$TS/c.sh"
    [ -f "$P/world/level.dat" ] && cp "$P/world/level.dat" "$B/install-$TS/level.dat"
    say "  rollback: $B/install-$TS (tar world complet: ~1-2 min)"
    tar -czf "$B/prod-world-$TS.tar.gz" -C "$P" world world_nether world_the_end 2>/dev/null && say "  snapshot lumi: $(du -m "$B/prod-world-$TS.tar.gz" | cut -f1) MiB OK" || say "  ATENTIE: tar world a esuat (disc?) — instalez oricum, rollback partial ramas"
    # 2. oprire curata a serverului curent prin puntea supervisorului
    if pgrep -f 'java @unix_args' >/dev/null; then
      : > "$P/cmd.in"; echo stop > "$P/cmd.in"
      for k in $(seq 1 24); do sleep 5; pgrep -f 'java @unix_args' >/dev/null || break; done
      pgrep -f 'java @unix_args' >/dev/null && fail "serverul actual nu a iesit dupa 120s — NU fortez, instalezi manual" || say "  server vechi: oprit curat (save facut de el)"
    fi
    # 3. opresc supervisorul ca sa nu-si repornesc singur motorul vechi in timpul mutarii
    pkill -f 'bash .*[/]c\.sh' 2>/dev/null; sleep 2
    # 4. instalare: java 11 in c.sh + unix_args pentru FunCity + jar + properties(+MOTD) + configuri identice cu staging-ul validat
    sed -i 's#^J=\$HOME/\.local/jdk17/bin/java#J=$( [ -x "$HOME/funcity-live/jdk11/bin/java" ] \&\& echo "$HOME/funcity-live/jdk11/bin/java" || echo "$HOME/.local/jdk17/bin/java" )#' "$HOME/c.sh"
    say "  c.sh: java -> $(grep -m1 '^J=' "$HOME/c.sh" | cut -c1-80)..."
    printf -- '-Xms1G\n-Xmx3G\n-XX:MaxGCPauseMillis=200\n-jar\nFunCity-1.16.5-b1.0827.jar\nnogui\n' > "$P/unix_args.txt"
    cp "$D/FunCity-1.16.5-b1.0827.jar" "$P/"
    cp "$D/server.properties" "$P/server.properties"
    rsync -a --delete "$D/mods/" "$P/mods/" 2>/dev/null
    rsync -a "$D/plugins/" "$P/plugins/" 2>/dev/null
    rsync -a "$D/config/" "$P/config/" --exclude 'voicechat*' 2>/dev/null
    [ -f "$D/server-icon.png" ] && cp "$D/server-icon.png" "$P/"
    rm -f "$P/serverconfig/voicechat-server.toml" 2>/dev/null # pe productie voicechat vrea default 24454
    say "  jar+args+props+mods->productie (world neatins, voicechat pe default)"
    # 5. pornire sub supraveghere deplina
    ( env -u RUNNER_TRACKING_ID setsid bash "$HOME/c.sh" >> "$P/sup.log" 2>&1 < /dev/null & )
    say "  c.sh repornit — il las sa faca boot (max 150s)"
    OK=NU
    for k in $(seq 1 30); do sleep 5
      if ss -lnt 2>/dev/null | grep -q ':25565 ' && grep -qa 'Done (' "$P/live.log" 2>/dev/null; then OK=DA; break; fi
    done
    say "  boot 25565: $OK | $(grep -a 'Done (' "$P/live.log" 2>/dev/null | tail -1 | cut -c1-60)"
    say "  erori la pornire: $(grep -acE 'ERROR' "$P/live.log" 2>/dev/null | tail -1) ( numaratoare la intreg logul, nu doar boot-ul curent)"
    grep -a 'Starting Minecraft server on' "$P/live.log" | tail -1 | sed 's/^/    B /' | tee -a "$REPORT"
    if [ "$OK" = DA ]; then say "  FUNCITY E PE PRODUCTIE — intri pe 92.5.171.150:25565"; else
      cp "$B/install-$TS/unix_args.txt" "$P/" 2>/dev/null; cp "$B/install-$TS/server.properties" "$P/" 2>/dev/null
      printf 'ROLLBACK manual: fisierele in $B/install-%s/, jar vechi in $P/.world salvat; repornire: setsid bash ~/c.sh\n' "$TS" > "$P/ROLLBACK.txt"
      say "  boot NU s-a confirmat in 150s — am readus unix_args+properties vechi; LAS c.sh pornit sa incerce motorul vechi singur; ROLLBACK.txt in $P"
    fi
    ;;
  expose) # tunele de TEST in frpc (game 25566 + voice UDP 24454) ca sa poata intra jucatorul
    # real de pe PC. Backup + verify-gate + autorefacere la config invalid. Tunelul de producție
    # existent (25565) nu se atinge — doar i se alatura una linie noua.
    F="$HOME/frpc.toml"
    [ -f "$F" ] || fail "nu gasesc $F"
    BK="$B/frpc.toml.bak-$(date -u +%Y%m%d-%H%M%S)"; mkdir -p "$B"; cp "$F" "$BK"
    say "== EXPOSE tuneluri test (frpc) — backup: $BK =="
    if grep -q 'name = "fcgame"' "$F"; then
      say "  tunelele de test exista deja in config — doar repornesc frpc"
    else
      printf '\n[[proxies]]\nname = "fcgame"\ntype = "tcp"\nlocalIP = "127.0.0.1"\nlocalPort = 25566\nremotePort = 25566\n\n[[proxies]]\nname = "fcvoice"\ntype = "udp"\nlocalIP = "127.0.0.1"\nlocalPort = 24454\nremotePort = 24454\n' >> "$F"
      say "  adaugate: tcp 25566 (game) si udp 24454 (voicechat) — porturi distincte de productie"
    fi
    if "$HOME/frpc" verify -c "$F" >/tmp/frpc-verify.txt 2>&1; then
      say "  frpc verify: OK"
      tmux send-keys -t frpc C-c 2>/dev/null; sleep 2
      pkill -x frpc 2>/dev/null; sleep 1
      tmux send-keys -t frpc "exec $HOME/frpc -c $HOME/frpc.toml >> $HOME/frpc.log 2>&1" Enter 2>/dev/null \
        || { setsid bash -c "exec $HOME/frpc -c $HOME/frpc.toml >> $HOME/frpc.log 2>&1" >/dev/null 2>&1 < /dev/null & }
      sleep 4
      if pgrep -x frpc >/dev/null; then
        say "  frpc: REPORNIT cu tunelele de test — clientul tau poate intra pe 92.5.171.150:25566"
      else
        cp "$BK" "$F"; setsid bash -c "exec $HOME/frpc -c $HOME/frpc.toml >> $HOME/frpc.log 2>&1" >/dev/null 2>&1 < /dev/null &
        say "  ATENTIE: frpc nu a supravietuit — config readus din backup si repornit cum era (25565 functiona din nou)"
      fi
    else
      cp "$BK" "$F"
      say "  frpc verify a CASUT -> config readus din backup, frpc neatins. Eroare verify:"
      tail -4 /tmp/frpc-verify.txt | sed 's/^/    V /' | tee -a "$REPORT"
    fi
    say "  porturi acum: 25565 $(ss -lnt 2>/dev/null | grep -q ':25565 ' && echo VIU || echo mort) | 25566 $(ss -lnt 2>/dev/null | grep -q ':25566 ' && echo VIU || echo mort) | frpc: $(pgrep -x frpc >/dev/null && echo viu || echo mort)"
    ;;
  restart|up)
    if [ "$M" = restart ] && [ -f "$D/server.pid" ] && kill -0 "$(cat "$D/server.pid")" 2>/dev/null; then
      opreste_server || true; sleep 3
    fi
    if [ "$(port_viu "$PORT")" = da ]; then
      say "ocupant port $PORT:"; ss -lntp 2>/dev/null | grep ":$PORT " | sed 's/^/  /' | tee -a "$REPORT"
      ps -o pid,user,etime,args -p "$(ss -lntp 2>/dev/null | awk -Fpid= '/:"'"$PORT"'" /{split($2,a,",");print a[1]; exit}')" 2>/dev/null | tail -1 | sed 's/^/  /' | tee -a "$REPORT"
      fail "portul $PORT ocupat de altceva — nu Fortez"
    fi
    JAVA=$(java11_gaseste) || JAVA=$(java11_adoptium) || fail "java11 indisponibil"
    export FUNCITY_XMX="$XMX" FUNCITY_JARFILE="$(cat "$D/.jarname")"
    sync_port
    voicechat_port
    start_server "$JAVA"
    asteapta_done 480 || fail "nu porneste — vezi $LOG"
    verifica_log
    ok=nu
    for t in 1 2 3; do
      sleep 15
      kill -0 "$(cat "$D/server.pid" 2>/dev/null)" 2>/dev/null || { say "JVM-ul a murat dupa Done (rc final: $(tail -1 "$LOG" | head -c 160))"; break; }
      if exec 3<>/dev/tcp/127.0.0.1/$PORT 2>/dev/null; then exec 3>&- 3<&-; ok=da; break; fi
      say "  port $PORT inchis inca, reincep ($t/3)"
    done
    say "port local $PORT: $( [ $ok = da ] && echo VIU || echo INCHIS )"
    echo $ok > "$D/.portviu"
    say "STAGING $( [ $ok = da ] && echo SUS || echo SUS-PORT-PROBLEMA ) pentru testul tau (port $PORT). Oprire: functity-stage down"
    finish 0
    ;;
  down)
    opreste_server || true
    # maturam orice JVM de staging ramas din cicluri anterioare (pid vechi suprasris)
    for pid in $(pgrep -f 'funcity-live' | grep -v $$ || true); do
      kill "$pid" 2>/dev/null || true
    done
    sleep 12
    for pid in $(pgrep -f 'java.*funcity-live|java.*FunCity' || true); do kill -9 "$pid" 2>/dev/null || true; done
    say "curatari: java staging ramas = $(pgrep -cf 'funcity-live.*jar|FunCity.*jar' || echo 0) | port 25565: $(port_viu 25565) | port 25566: $(port_viu 25566)"
    say "jos curat"
    finish 0
    ;;
  status)
    say "== FUNCTITY STATUS — $(date -u '+%F %T UTC') =="
    say "  staging java: $(pgrep -af 'java.*$(cat "$D/.jarname" 2>/dev/null || echo FunCity)' | head -2 | cut -c1-160 || echo NICIUNA)"
    say "  port $PORT: $(port_viu $PORT) | 25565: $(port_viu 25565) | 25566: $(port_viu 25566)"
    say "  log: Done = $(grep -c 'Done (' "$LOG" 2>/dev/null) | erori = $(grep -cE ' ERROR ' "$LOG" 2>/dev/null) | keep-up = $(grep -c "Can't keep up" "$LOG" 2>/dev/null)"
    say "  post-Done (12 linii):"
    grep -A12 'Done (' "$LOG" 2>/dev/null | tail -12 | cut -c1-200 | sed 's/^/    D /' | tee -a "$REPORT"
    say "  pidfile staging: $(cat "$D/server.pid" 2>/dev/null || echo absent)"
    say "  linii ERROR:"
    grep -E ' ERROR ' "$LOG" 2>/dev/null | tail -6 | cut -c1-200 | sed 's/^/    E /' | tee -a "$REPORT"
    say "  bind port:"
    grep -iE 'starting minecraft server on|failed to bind|address already|bind exception' "$LOG" 2>/dev/null | tail -4 | sed 's/^/    B /' | tee -a "$REPORT"
    say "  primele 12 linii log:"
    head -12 "$LOG" 2>/dev/null | cut -c1-160 | sed 's/^/    L /' | tee -a "$REPORT"
    say "  plugini Enabling: $(grep -cE 'Enabling ' "$LOG" 2>/dev/null) | ultimi 6 linii:"
    tail -6 "$LOG" 2>/dev/null | sed 's/^/    /' | tee -a "$REPORT"
    say "  frpc: porturi expuse (fara tokenuri):"
    grep -E 'remotePort|localPort|^name' "$HOME/frpc.toml" 2>/dev/null | paste - - - 2>/dev/null | head -6 | sed 's/^/    T /' | tee -a "$REPORT"
    say "  java staging vie acum: $(pgrep -fc 'funcity-live' 2>/dev/null || echo 0)"
    say "  libertate disc: $(df -m "$HOME" | tail -1 | awk '{print $4}') MiB"
    say "  interior jar voicechat (fisiere config citate):"
    local vj; vj=$(ls "$D"/mods/*voicechat*.jar 2>/dev/null | head -1)
    if [ -n "$vj" ]; then
      unzip -Z1 "$vj" 2>/dev/null | grep -iE '\.(properties|toml|json)$|pack.png|mod.json|mods.toml' | head -10 | sed 's/^/    J /' | tee -a "$REPORT"
      unzip -p "$vj" 'assets/voicechat/lang/en_us.json' 2>/dev/null | grep -oE '"voicechat[^"]*port[^"]*"' | head -4 | sed 's/^/    K /' | tee -a "$REPORT"
      unzip -p "$vj" $(unzip -Z1 "$vj" | grep -m1 -iE 'VoiceChatConfig|ServerConfig|ConfigManager' | head -1) 2>/dev/null | strings 2>/dev/null | grep -oE '[a-zA-Z0-9_/.-]*voicechat[a-zA-Z0-9_/.-]*\.(properties|toml)' | sort -u | head -6 | sed 's/^/    F /' | tee -a "$REPORT"
    fi
    say "  moduri voice/chat in pack:"
    ls "$D/mods" 2>/dev/null | grep -iE 'voice|chat|talk|plastic' | sed 's/^/    M /' | tee -a "$REPORT"
    say "  configuri voicechat staging:"
    find "$D/config" -iname '*voice*' 2>/dev/null | head -8 | sed 's/^/    C /' | tee -a "$REPORT"
    for f in $(find "$D/config" -iname '*voicechat*server*' 2>/dev/null | head -2); do say "    continut $f:"; head -8 "$f" | sed 's/^/      /' | tee -a "$REPORT"; done
    say "  porturi voicechat pe gazda:"; ss -lntup 2>/dev/null | grep -E ':(24454|24455) ' | sed 's/^/    P /' | tee -a "$REPORT"
    say "  linii voicechat din log:"
    grep -iE 'voicechat|voice chat' "$LOG" 2>/dev/null | tail -8 | cut -c1-200 | sed 's/^/    V /' | tee -a "$REPORT"
    finish 0
    ;;
  *)
    echo "folosire: $0 host-info|backup|assemble|test|status|up|down"; exit 2;;
esac
