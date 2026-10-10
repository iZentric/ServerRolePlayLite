#!/usr/bin/env bash
# ACCEPTANCE — testele de la "hibridul trebuie sa fie INVIZIBIL pentru jucator" (T1-T10).
#
# Fiecare test are DOVADA (linie din log sau cifra), nu parere.
# Toate scrierile in in.fifo au `timeout 4` ca sa nu blocheze niciodata jobul daca fifo-ul nu are cititor.
trap 'bash "$(dirname "$0")/ensure-up.sh" >/dev/null 2>&1 || true' EXIT INT TERM
D=$HOME/cuantic-live
L=$D/live.log
STRIP="s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g; s/\r/\n/g"
BR=arena/a29b4ef4-serverroleplaylite
: > /tmp/acc.txt
out() { echo "$1" >> /tmp/acc.txt; }

# Extrage DOAR logul ultimei porniri (de la ultimul 'ModLauncher running:' sau '==== pornire')
last_boot_log() {
  sed -e "$STRIP" "$L" 2>/dev/null | awk '
    /ModLauncher running:|==== pornire/ { buf = "" }
    { buf = buf $0 "\n" }
    END { printf "%s", buf }
  '
}

# Asigura ca serverul + tunelul frpc sunt pornite si a terminat faza de boot pe pornirea CURENTA (max ~120s)
bash "$(dirname "$0")/ensure-up.sh" >/dev/null 2>&1 || true
for _w in $(seq 1 24); do
  if pgrep -f 'java @unix_args' >/dev/null 2>&1 && ss -lnt 2>/dev/null | grep -q ':25565' && \
     last_boot_log | grep -qaE 'Done \([0-9.]+s\)'; then
    break
  fi
  sleep 5
done

PID=$(pgrep -f 'java @unix_args' | head -1)
FRP_PID=$(pgrep -f 'frpc -c' | head -1)
send_cmd() {
  local c="$1"
  [ -p "$D/in.fifo" ] && timeout 4 sh -c "printf '%s\n' \"$c\" > '$D/in.fifo'" 2>/dev/null || true
  [ -w "$D/cmd.in" ] && printf '%s\n' "$c" >> "$D/cmd.in" 2>/dev/null || true
}

last_boot_log > /tmp/acc.log
TOTL=$(wc -l < /tmp/acc.log 2>/dev/null || echo 0)
out "# ACCEPTANCE CUANTIC — $(date -u '+%F %T UTC') (boot curent: $TOTL linii)"

# ---- T1 proces + port + tunel frpc ----
P25565=$(ss -lnt 2>/dev/null | grep -c ':25565')
if [ -n "$PID" ] && [ "${P25565:-0}" -ge 1 ]; then T="TRECE"; else T="CADE"; fi
out "[$T] T1 proces java + port: java=${PID:-nil} port25565=$P25565 frpc=${FRP_PID:-nil} ($(tail -1 "$HOME/frpc.log" 2>/dev/null | sed -e "$STRIP" | tr -d '\n' | tail -c 60))"

# ---- T2 boot complet ("Done (") + timp ----
DONE=$(grep -ao 'Done ([0-9.]*s)' /tmp/acc.log | tail -1)
FML=$(grep -ao 'Dedicated server took [0-9.]* seconds' /tmp/acc.log | tail -1)
[ -n "$DONE" ] && T="TRECE" || T="CADE"
out "[$T] T2 boot: ${DONE:-NU ESTE DONE} | ${FML:-fara timp FML}"

# ---- T3 erori reale dupa pornire (filtrate cele cunoscute, nevinovate) ----
tail -n 4000 /tmp/acc.log > /tmp/acc.tail
BAD=$(grep -aiE 'ERROR|SEVERE|Exception|Caused by' /tmp/acc.tail 2>/dev/null \
  | grep -aivE 'SLF4J|log4j|StaticLoggerBinder|deprecat|netty.*epoll|Unable to probe|Unable to determine|nag|Permission listener|Permissions lag|pizzamod\.mixin\.json|mushroom_colony_growable_on|does not properly support Bukkit plugins' | wc -l)
[ "${BAD:-0}" -eq 0 ] && T="TRECE" || T="VERIFICA"
out "[$T] T3 erori in log (ultimele 4000 linii, filtering pe cunoscute-nevinovate): $BAD"
grep -aiE 'ERROR|SEVERE|Exception' /tmp/acc.tail 2>/dev/null | grep -aivE 'SLF4J|log4j|StaticLoggerBinder|pizzamod\.mixin\.json|mushroom_colony_growable_on|does not properly support Bukkit plugins' | tail -3 | sed 's/^/      /' >> /tmp/acc.txt

# ---- T4 lista de moduri bat-o-la-login ----
KICK=$(grep -acaiE 'missing .*mods|mod list.*mismatch|Incompatible mods|rejected connecting|Missing or unmatched' /tmp/acc.log)
MODS=$(ls "$D"/mods/*.jar 2>/dev/null | wc -l)
[ "${KICK:-0}" -eq 0 ] && T="TRECE" || T="CADE"
out "[$T] T4 handshake cu clientul: semne de kick pe lista de moduri = $KICK | moduri pe server: $MODS"

# ---- T5 pluginii incarcati ----
PLUG_DISK=$(ls "$D"/plugins/*.jar 2>/dev/null | wc -l)
PLUG_EN=$(grep -acE 'Enabling [A-Za-z0-9_-]+ v' /tmp/acc.log 2>/dev/null || echo 0)
FAILED=$(grep -acaiE "Could not load 'plugins/|Error occurred while enabling " /tmp/acc.log)
[ "${FAILED:-0}" -eq 0 ] && [ "${PLUG_EN:-0}" -gt 0 ] && T="TRECE" || T="VERIFICA"
out "[$T] T5 plugini: pe disk: $PLUG_DISK jar; activati (Enabling): $PLUG_EN | esuati: $FAILED"

# ---- T6 puntea de comenzi e vie (raspuns in log) ----
: > /tmp/acc-proba
L0=$(wc -l < "$L" 2>/dev/null || echo 0)
send_cmd "list"
for i in 1 2 3 4 5 6; do
  sleep 3
  tail -n +$((L0+1)) "$L" 2>/dev/null | sed -e "$STRIP" | grep -ao 'There are [0-9]* out of maximum [0-9]* players' | tail -1 > /tmp/acc-proba
  [ -s /tmp/acc-proba ] && break
done
[ -s /tmp/acc-proba ] && { T="TRECE"; out "[$T] T6 punte console: $(cat /tmp/acc-proba)"; } || out "[CADE] T6 punte console: niciun raspuns la 'list' in 18 s"

# ---- T7 integritatea lumii dupa salvare (region files + level.dat) ----
R0=$(find "$D/world/region" -name '*.mca' 2>/dev/null | wc -l)
M0=$(stat -c %Y "$D/world/level.dat" 2>/dev/null || echo 0)
L1=$(wc -l < "$L" 2>/dev/null || echo 0)
send_cmd "save-all flush"
SAVED="NU"
for i in 1 2 3 4 5 6 7; do
  sleep 3
  tail -n +$((L1+1)) "$L" 2>/dev/null | sed -e "$STRIP" | grep -aq 'Saved the game' && { SAVED="DA"; break; }
done
R1=$(find "$D/world/region" -name '*.mca' 2>/dev/null | wc -l)
M1=$(stat -c %Y "$D/world/level.dat" 2>/dev/null || echo 0)
[ "$SAVED" = "DA" ] && [ "$M1" -ge "$M0" ] && T="TRECE" || T="VERIFICA"
out "[$T] T7 salvare lume: 'Saved the game'=$SAVED | level.dat mtime $M0->$M1 | regiuni $R0->$R1"

# ---- T8 resurse (limitarile casei, nu promisiuni) ----
FREE=$(df -BM "$D" 2>/dev/null | awk 'NR==2{gsub("M","",$4); print $4}')
OUTT=$(df -BM "$D" 2>/dev/null | awk 'NR==2{print $5}')
MEM=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
RSS=$(grep -a VmRSS /proc/${PID:-1}/status 2>/dev/null | awk '{print int($2/1024)}')
out "[INFO] T8 resurse: disc liber ${FREE:-?}MB (ocupat ${OUTT:-?}), MemAvailable ${MEM}MB, RSS java ${RSS:-?}MB, swap $(awk '/SwapFree/{print int($2/1024)}' /proc/meminfo)MB liber"

# ---- T9 ce NU se poate testa de pe box (onestitate obligatorie) ----
out "[N-A] T9 testate DOAR din server. Lipsesc cu client real: latența clientului (ping real de pe scaunul"
out "      lui), desync/rubberband vizual, dublagi de itemi, interactiuni cu moduri de client,"
out "      jucatori multi. Acestea se raporteaza de la client, nu de aici - nu le declara trecute."

# ---- T10: brand Cuantic in /version + provenienta upstream ----
L0=$(wc -l < "$L" 2>/dev/null || echo 0)
send_cmd "version"
sleep 4
send_cmd "cuantic"
sleep 4
NEW=$(tail -n +$((L0+1)) "$L" 2>/dev/null | sed -e "$STRIP")
BOOT_BRAND=$(grep -aiE '\[Cuantic(/version)?\]|This server is running CUANTIC version' /tmp/acc.log 2>/dev/null | tail -3 | tr '\n' ' ')
if printf '%s\n%s' "$NEW" "$BOOT_BRAND" | grep -qai "Cuantic" && printf '%s\n%s' "$NEW" "$BOOT_BRAND" | grep -qaiE "based on|adapted from|1\.16\.5-1d8d6313|CatServer"; then
  T="TRECE"; R10="brand + provenienta upstream confirmate (${BOOT_BRAND:0:110})"
elif printf '%s\n%s' "$NEW" "$BOOT_BRAND" | grep -qai "Cuantic"; then
  T="VERIFICA"; R10="brand apare, dar linia de provenienta lipseste"
else
  T="CADE"; R10="niciun raspuns cu Cuantic (Cuantic-Brand plugin neluat sau punta moarta)"
fi
out "[$T] T10 /version: $R10"

TREC=$(grep -c '^\[TRECE\]' /tmp/acc.txt)
VER=$(grep -c '^\[VERIFICA\]' /tmp/acc.txt)
CADE=$(grep -c '^\[CADE\]' /tmp/acc.txt)
INF=$(grep -c '^\[INFO\]' /tmp/acc.txt)
NA=$(grep -c '^\[N-A\]' /tmp/acc.txt)
TOT_T=$((TREC + VER + CADE + INF + NA))
out ""
out "SCOR: TRECE=$TREC VERIFICA=$VER CADE=$CADE INFO=$INF N-A=$NA (total $TOT_T/10 teste, T1-T10)"

mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
cp /tmp/acc.txt analysis/ACCEPTANCE.md
if [ -n "$PID" ] && [ "${P25565:-0}" -ge 1 ]; then
  { echo "# ALIVE CUANTIC — $(date -u '+%Y-%m-%d %H:%M:%S') UTC"; echo; echo '```'; echo "SUS · 92.5.171.150:25565 (java=$PID, frpc=${FRP_PID:-activ}) · verificat $(date -u '+%H:%M:%S') UTC"; echo '```'; } > analysis/ALIVE.md
fi
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/ACCEPTANCE.md analysis/ALIVE.md >/dev/null 2>&1
git commit -q -m "ACCEPTANCE: $TREC TRECE, $VER VERIFICA, $CADE CADE, $INF INFO, $NA N-A ($TOT_T/10 teste, T1-T10)" || true
git pull --rebase -q origin "$BR" 2>/dev/null || true
git push -q origin "HEAD:$BR" 2>/dev/null || echo "push: nimic"
cat /tmp/acc.txt
exit 0
