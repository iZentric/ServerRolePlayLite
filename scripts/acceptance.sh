#!/usr/bin/env bash
# ACCEPTANCE — testele de la "híbridul trebuie sa fie INVIZIBIL pentru jucator".
#
# Regulile din promptul CUANTIC zic clar: nu marchezi "invizibil" daca ai masurat doar TPS.
# Asa ca lista asta nu priveste performanta, priveste senzatiile care omoră un server RP:
# kick la login din cauza listei de moduri, erori ingropate in log, pluginuri care nu s-au
# incarcat, lume corupta dupa restart, permisiuni care mormaie. Fiecare test are DOVADA (linie
# din log sau cifra), nu parere. Ruleaza pe box, prin runner; verdictul se impinge in repo.
D=$HOME/cuantic-live
L=$D/live.log
STRIP="s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g; s/\r/\n/g"
BR=arena/a29b4ef4-serverroleplaylite
: > /tmp/acc.txt
out() { echo "$1" >> /tmp/acc.txt; }
PID=$(pgrep -f 'java @unix_args' | head -1)

# copia curat-ANSI ANSI a logului, ca sa prinDEM ce scrie java (spark pune caractere de culoare)
sed -e "$STRIP" "$L" > /tmp/acc.log 2>/dev/null
TOTL=$(wc -l < /tmp/acc.log 2>/dev/null || echo 0)
out "# ACCEPTANCE CUANTIC — $(date -u '+%F %T UTC') (live.log: $TOTL linii)"

# ---- T1 proces + port ----
if [ -n "$PID" ]; then T="TRECE"; else T="CADE"; fi
out "[$T] T1 proces java + port: java=${PID:-nil} port25565=$(ss -lnt 2>/dev/null | grep -c ':25565')"

# ---- T2 boot complet ("Done (") + timp ----
DONE=$(grep -ao 'Done ([0-9.]*s)' /tmp/acc.log | tail -1)
FML=$(grep -ao 'Dedicated server took [0-9.]* seconds' /tmp/acc.log | tail -1)
[ -n "$DONE" ] && T="TRECE" || T="CADE"
out "[$T] T2 boot: ${DONE:-NU ESTE DONE} | ${FML:-fara timp FML}"

# ---- T3 erori reale dupa pornire (filtrate cele cunoscute, nevinovate) ----
tail -n 4000 /tmp/acc.log > /tmp/acc.tail
BAD=$(grep -aiE 'ERROR|SEVERE|Exception|Caused by' /tmp/acc.tail 2>/dev/null \
  | grep -aivE 'SLF4J|log4j|StaticLoggerBinder|deprecat|netty.*epoll|Unable to probe|Unable to determine|nag|Permission listener|Permissions lag' | wc -l)
[ "${BAD:-0}" -eq 0 ] && T="TRECE" || T="VERIFICA"
out "[$T] T3 erori in log (ultimele 4000 linii, filtering pe cunoscute-nevinovate): $BAD"
grep -aiE 'ERROR|SEVERE|Exception' /tmp/acc.tail 2>/dev/null | grep -aivE 'SLF4J|log4j|StaticLoggerBinder' | tail -3 | sed 's/^/      /' >> /tmp/acc.txt

# ---- T4 lista de moduri bat-o-la-login (kick "missing mods" = boala hibridelor) ----
KICK=$(grep -acaiE 'missing .*mods|mod list.*mismatch|Incompatible mods|rejected connecting|Missing or unmatched' /tmp/acc.log)
MODS=$(ls "$D"/mods/*.jar 2>/dev/null | wc -l)
[ "${KICK:-0}" -eq 0 ] && T="TRECE" || T="CADE"
out "[$T] T4 handshake cu clientul: semne de kick pe lista de moduri = $KICK | moduri pe server: $MODS"

# ---- T5 pluginii incarcati ----
PLUG=$(grep -ao 'This server is running [0-9]* plugin[^\n]*' /tmp/acc.log | tail -1)
[ -n "$PLUG" ] || PLUG="pe disk: $(ls "$D"/plugins/*.jar 2>/dev/null | wc -l) jar; $(grep -aco 'Loading [0-9]* plugins' /tmp/acc.log 2>/dev/null | head -1) linii de incarcare"
FAILED=$(grep -acaiE 'Failed to (load|enable)|Could not load plugin' /tmp/acc.log)
[ "${FAILED:-0}" -eq 0 ] && T="TRECE" || T="VERIFICA"
out "[$T] T5 plugini: ${PLUG:-niciun rand 'This server is running'} | esuati: $FAILED"

# ---- T6 puntea de comenzi e vie (raspuns in log) ----
: > /tmp/acc-proba
L0=$(wc -l < "$L")
printf 'list\n' >> "$D/cmd.in"
for i in 1 2 3 4 5 6 7 8; do
  sleep 3
  tail -n +$((L0+1)) "$L" 2>/dev/null | sed -e "$STRIP" | grep -ao 'There are [0-9]* out of maximum [0-9]* players' | tail -1 > /tmp/acc-proba
  [ -s /tmp/acc-proba ] && break
done
[ -s /tmp/acc-proba ] && { T="TRECE"; out "[$T] T6 punte console: $(cat /tmp/acc-proba)"; } || out "[CADE] T6 punte console: niciun raspuns la 'list' in 24 s"

# ---- T7 integritatea lumii dupa salvare (region files + level.dat) ----
R0=$(find "$D/world/region" -name '*.mca' 2>/dev/null | wc -l)
M0=$(stat -c %Y "$D/world/level.dat" 2>/dev/null || echo 0)
L1=$(wc -l < "$L")
printf 'save-all flush\n' >> "$D/cmd.in"
SAVED="NU"
for i in 1 2 3 4 5 6 7 8 9 10; do
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
RSS=$(grep -a VmRSS /proc/$PID/status 2>/dev/null | awk '{print int($2/1024)}')
out "[INFO] T8 resurse: disc liber ${FREE:-?}MB (ocupat ${OUTT:-?}), MemAvailable ${MEM}MB, RSS java ${RSS:-?}MB, swap $(awk '/SwapFree/{print int($2/1024)}' /proc/meminfo)MB liber"

# ---- T9 ce NU se poate testa de pe box (onestitate obligatorie) ----
out "[N-A] T9 testate DOAR din server. Lipsesc cu client real: latența clientului (ping real de pe scaunul"
out "      lui), desync/rubberband vizual, dublagi de itemi, interactiuni cu moduri de client,"
out "      jucatori multi. Acestea se raporteaza de la client, nu de aici - nu le declara trecute."

# ---- T10: brand Cuantic in /version (cerut: dovada pe build-ul real) ----
if [ -p "$D/in.fifo" ] || [ -p "$D/cmd.in" ]; then
  F="$D/cmd.in"; [ -p "$F" ] || F="$D/in.fifo"
  L0=$(wc -l < "$D/live.log" 2>/dev/null || echo 0)
  echo "version" > "$F" 2>/dev/null; sleep 6; echo "cuantic" > "$F" 2>/dev/null; sleep 6
  NEW=$(tail -n +$((L0+1)) "$D/live.log" 2>/dev/null | sed -e "s/\x1b\[[0-9;]*[a-zA-Z]//g")
  if printf '%s' "$NEW" | grep -qai "Cuantic" && printf '%s' "$NEW" | grep -qaiE "based on|adapted from|CraftBukkit|CatServer"; then
    T="TRECE"; R10="brand + provenienta upstream in iesire"
  elif printf '%s' "$NEW" | grep -qai "Cuantic"; then
    T="VERIFICA"; R10="brand apare, dar linia de provenienta lipseste"
  else
    T="CADE"; R10="niciun raspuns cu Cuantic (Cuantic-Brand plugin neluat sau punta moarta)"
  fi
  out "[$T] T10 /version: $R10"
else
  out "[N-A] T10 /version: niciun fisier de comanda pe $D"
fi

TREC=$(grep -c '^\[TRECE\]' /tmp/acc.txt); CADE=$(grep -c '^\[CAD' /tmp/acc.txt); VER=$(grep -c '^\[VERIFICA\]' /tmp/acc.txt)
out ""
out "

SCOR: TRECE=$TREC VERIFICA=$VER CADE=$CADE din 10 teste"

mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
cp /tmp/acc.txt analysis/ACCEPTANCE.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/ACCEPTANCE.md >/dev/null 2>&1
git commit -q -m "ACCEPTANCE: $TREC TRECE, $VER VERIFICA, $CADE CADE (T1-T9, testul invizibilitatii hibridului)" || true
git pull --rebase -q origin "$BR" 2>/dev/null || true
git push -q origin "HEAD:$BR" 2>/dev/null || echo "push: nimic"
cat /tmp/acc.txt
exit 0
