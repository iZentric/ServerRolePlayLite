#!/usr/bin/env bash
# CUANTIC ARGS — asigura ca unix_args.txt e VIABIL inainte ca cineva sa dea start la java.
# Motivul existentei: un job de tuning a rescris fisierul si a pierdut coada `-jar <server.jar> nogui`.
# Fara ea java nu are main-class: varsa ~98 linii de usage, iese imediat, iar supervisorul o aprinde
# la nesfarsit (simptom vazut: "mc=NU port=nu asculta log=98" la fiecare 15 s).
# Nu strica niciodata fisierul fara backup.
D=${1:-.}
cd "$D" 2>/dev/null || { echo "args: nu pot intra in $D"; exit 1; }
[ -f unix_args.txt ] || { echo "args: NU exista unix_args.txt in $(pwd)"; exit 1; }

JAR=""
for pat in 'CatServer-*.jar' 'arclight-*.jar' 'Mist-*.jar' 'forge-*.jar' 'server.jar'; do
  C=$(ls $pat 2>/dev/null | head -1)
  if [ -n "$C" ]; then JAR="$C"; break; fi
done
[ -n "$JAR" ] || { echo "args: niciun jar de server in $(pwd) - ruleaza intai deploy-ul (c.sh)"; exit 1; }


# ===== POLITICA DE MEMORIE (cerere utilizator: serverul sa aiba TOATA RAM-ul masinii) =====
# Heap-ul se scrie inainte de fiecare pornire, din /proc/meminfo. Daca guardianul din c.sh a
# descoperit ca OOM-killerul o omora, plafonul gazduit in ramceil este cel folosit (nu mai sarim
# inapuce in groapa la fiecare restart). CUANTIC_RAM=2G suprascrie totul (mod manual).
TOT_MB=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo 2>/dev/null)
[ -n "$TOT_MB" ] || TOT_MB=2048
CEIL=$(grep -aoE '^[0-9]{3,7}$' "$D/ramceil" 2>/dev/null | head -1)
# 1.6.4: plafonul implicit = MemTotal minus 2 GB (jumatate din RAM-ul masinii),
# nu tot RAM-ul. Motiv masurat: cu -Xmx11884M pe 11.8 GB, OOM-killerul omora java
# si lua si runner-ul GitHub => serverul ramanea JOS. MemTotal-2G lasa marja pentru
# sistem + supervisor + frpc, iar guardianul de OOM (ramceil) poate cobori mai mult.
SAFE=$(( TOT_MB - 3072 )); [ "$SAFE" -lt 1024 ] && SAFE=1024
[ "$SAFE" -gt 6144 ] && SAFE=6144
# Daca ramceil de pe disc avea o valoare veche mai mare decat SAFE (ex. 11884 scris de ram-all),
# o stergem ca sa nu suprascrie SAFE si sa cheme OOM-killerul!
if [ -n "$CEIL" ] && [ "$CEIL" -gt "$SAFE" ]; then
  rm -f "$D/ramceil" 2>/dev/null || true
  CEIL=""
fi
[ -n "${CUANTIC_RAM:-}" ] && [ "$CUANTIC_RAM" = "all" ] && SAFE=$TOT_MB
HEAP="${SAFE}M"
[ -n "$CEIL" ] && HEAP="${CEIL}M"
[ -n "${CUANTIC_RAM:-}" ] && [ "${CUANTIC_RAM}" != "all" ] && HEAP="$CUANTIC_RAM"
XMS=1024
if ! grep -qxF -- "-Xmx$HEAP" unix_args.txt; then
  cp unix_args.txt "unix_args.txt.bak.$(date +%s)"
  grep -vE '^-(Xms|Xmx)[0-9]+[MGmg]?$' unix_args.txt > /tmp/args.mem
  { printf -- '-Xms%sM\n-Xmx%s\n' "$XMS" "$HEAP"; cat /tmp/args.mem; } > unix_args.txt
  echo "args: MEMORIE -Xmx $HEAP (masina are ${TOT_MB}MB), -Xms ${XMS}M, plafon=$( [ -n "$CEIL" ] && echo ${CEIL}MB || echo 'niciodata' )"
fi

if ! grep -qx -- '-jar' unix_args.txt; then
  cp unix_args.txt "unix_args.txt.bak.$(date +%s)"
  grep -v -x -- '-jar' unix_args.txt | grep -v -x -- 'nogui' | grep -vE '^(CatServer|arclight|Mist|forge)[^ ]*\.jar$' > /tmp/args.head
  { cat /tmp/args.head; printf -- '-jar\n%s\nnogui\n' "$JAR"; } > unix_args.txt
  echo "args: REPARAT — am adaugat coada lipsa (-jar $JAR nogui), backup facut"
  exit 0
fi

JARLINIE=$(grep -A1 -x -- '-jar' unix_args.txt | tail -1)
if [ ! -f "$JARLINIE" ]; then
  cp unix_args.txt "unix_args.txt.bak.$(date +%s)"
  grep -v -x -- "$JARLINIE" unix_args.txt > /tmp/args.head
  { cat /tmp/args.head; printf -- '-jar\n%s\nnogui\n' "$JAR"; } > unix_args.txt
  echo "args: REPARAT — jar-ul din fisier ($JARLINIE) nu exista, inlocuit cu $JAR"
  exit 0
fi
echo "args: OK ($JARLINIE, $(wc -l < unix_args.txt) linii)"
exit 0
