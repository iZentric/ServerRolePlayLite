#!/usr/bin/env bash
# TUNE-LIVE — pune STRATURILE DE TUNING CUANTIC pe box-ul live si dovedeste ca au intrat.
# De ce exista: build_lite.py scrie spigot.yml / bukkit.yml / catserver.yml in zip, dar
# apply-live copiau doar jar/txt/json => serverul live a ramas cu configurile IMPLICITE CatServer.
# Adica, corect: semana cu „CatServer oficial + Java 17". Scriptul asta inchide diferenta.
# Idempotent, cu backup la fiecare fisier atins, si raporteaza per cheie: veche -> noua.
D=$HOME/cuantic-live
REPO=iZentric/ServerRolePlayLite
BR=$ARENA_BRANCH
[ -n "$BR" ] || BR=arena/a29b4ef4-serverroleplaylite
cd "$D" 2>/dev/null || { echo "TUNE: lipsa $D" > /tmp/tune.txt; exit 0; }

tmp=$(mktemp -d)
for y in spigot.yml bukkit.yml catserver.yml commands.yml server.properties; do
  curl -fsSLo "$tmp/$y" --max-time 25 \
    "https://raw.githubusercontent.com/$REPO/$BR/site/tuning/$y" 2>/dev/null || true
done
R="TUNE:"
APLIC=0
for y in spigot.yml bukkit.yml catserver.yml commands.yml; do
  [ -s "$tmp/$y" ] || { R="$R $y=absent"; continue; }
  if [ -f "$y" ]; then
    if cmp -s "$tmp/$y" "$y"; then R="$R $y=la-zi"; continue; fi
    cp "$y" "$y.bak.$(date +%s)"
  fi
  cp "$tmp/$y" "$y"; APLIC=$((APLIC+1)); R="$R $y=apus"
done
# server.properties: doar cheile de consum, fara sa stricam world-ul existent
for k in "view-distance=4" "max-players=25" "entity-broadcast-range-percentage=60" \
         "use-native-transport=true" "network-compression-threshold=512" "max-tick-time=-1" \
         "allow-flight=true" "enable-command-block=true" "online-mode=false" "spawn-protection=0"; do
  K=${k%%=*}
  if grep -q "^$K=" server.properties 2>/dev/null; then
    grep -q "^$K=${k#*=}$" server.properties || { sed -i "s|^$K=.*|$k|" server.properties; R="$R $K=reparat"; }
  else printf '%s\n' "$k" >> server.properties; R="$R $K=adaugat"; fi
done
V=$(grep -c "u00A7" server.properties 2>/dev/null)
R="$R aplicate=$APLIC motd-ascii=$V"
rm -rf "$tmp"

# ---- repornire curata ca sa fie citite yml-urile ----
[ -p in.fifo ] || mkfifo -m 600 in.fifo
pkill -TERM -f 'java @unix_args' 2>/dev/null; sleep 22
pgrep -f 'java @unix_args' >/dev/null 2>&1 && { pkill -KILL -f 'java @unix_args'; sleep 6; }
( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & )
PORNIT=NU; T=0
for i in $(seq 1 40); do
  sleep 5; T=$((T+5))
  sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" live.log 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)' && { PORNIT=DA; break; }
done
BT=$(sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" live.log 2>/dev/null | grep -aoE 'Done \([0-9.]+s\)' | tail -1)
KT=$(sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" live.log 2>/dev/null | grep -cai "can't keep up")
R="$R pornit=$PORNIT boot='$BT' cannot-keep-up=$KT dupa=${T}s"
echo "$R" > /tmp/tune.txt
echo "$R"
