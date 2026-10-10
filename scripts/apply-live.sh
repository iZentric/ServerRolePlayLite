#!/usr/bin/env bash
# APPLY-LIVE — aduce serverul live la ULTIMA versiune de pe release `lite` si il porneste curat:
# opreste supervisorul vechit, isi ia singur noul pack (world-ul ramane), pune flagurile de build,
# reporneste frpc + java, si lasa verdictul in mesajul commitului.
# Asta e UNEALTA de implantare/rollback: VETE_ASTEPTAT=1.6.0 -> aseaza fix versiunea aceea.
# keepalive: orice iesire (si eroare, si Ctrl-C) reporneste ce am oprit noi
trap 'bash "$(dirname "$0")/ensure-up.sh" >/dev/null 2>&1 || true' EXIT INT TERM
D=$HOME/cuantic-live
REPO=iZentric/ServerRolePlayLite
AS=${VETA_ASTEPTAT:-}
[ -n "$AS" ] || AS=$(python3 -c "import json;print(json.load(open('$GITHUB_WORKSPACE/pack-rules.json'))['pack_version'])" 2>/dev/null)
V="APPLY: incepe"

# ---- 1. aşteaptă release-ul aşteptat (build-ul trebuie sa termine inainte) ----
if [ -n "$AS" ]; then
  for i in $(seq 1 40); do
    CUR=$(curl -fsSLo - --max-time 20 "https://api.github.com/repos/$REPO/releases/tags/lite" 2>/dev/null | python3 -c "import sys,json;print(next((a['name'] for a in json.load(sys.stdin).get('assets',[]) if 'Server-CatServer' in a['name']),''))" 2>/dev/null)
    case "$CUR" in *"$AS"*) V="$V release=$CUR"; break ;; esac
    sleep 15
    [ $i -eq 40 ] && V="$V release=asteptam-$AS-am-gasit-$CUR"
  done
fi

# ---- 2. supervisorul vechi jos (altfel isi tine propriul java in memorie veche) ----
# ---- snapshot inainte de orice atingere (ruleaza pe discul de 5 GB, pastram doar ultimul) ----
rm -f "$D"/snapshot-*.tar.gz 2>/dev/null || true
SNAP="$D/snapshot-$(date +%s).tar.gz"
tar -czf "$SNAP" -C "$D" mods plugins unix_args.txt server.properties 2>/dev/null
echo "SNAP: $SNAP ($(du -h "$SNAP" 2>/dev/null | cut -f1))" >> /tmp/apply.txt
echo "$NEW" > "$D/.pack.target"
pkill -f 'bash .*c\.sh' 2>/dev/null && V="$V sup=oprit" || V="$V sup=nimic"
sleep 3
pkill -TERM -f 'java @unix_args' 2>/dev/null
sleep 20
pgrep -f 'java @unix_args' >/dev/null 2>&1 && { pkill -KILL -f 'java @unix_args'; sleep 6; }

# ---- 3. scriptul de run la zi + packul cel nou ----
curl -fsSLo "$HOME/c.sh" "https://raw.githubusercontent.com/$REPO/arena/a29b4ef4-serverroleplaylite/scripts/cuantic-live.sh" || V="$V c.sh=ESUAT"
( cd "$D" 2>/dev/null && rm -f .pack ) 2>/dev/null
ZP="/tmp/apply-pack.zip"
RURL=$(curl -fsSLo - --max-time 25 "https://api.github.com/repos/$REPO/releases/tags/lite" 2>/dev/null | python3 -c "import sys,json;print(next((a['browser_download_url'] for a in json.load(sys.stdin).get('assets',[]) if 'Server-CatServer' in a['name']),''))" 2>/dev/null)
if [ -n "$RURL" ] && curl -fL --max-time 400 -o "$ZP" "$RURL" >/dev/null 2>&1 && [ -s "$ZP" ]; then
  rm -rf /tmp/pk; mkdir -p /tmp/pk; unzip -oq "$ZP" -d /tmp/pk
  ( cd "$D" && rm -rf mods plugins && mkdir -p mods plugins
    for f in /tmp/pk/*; do b=$(basename "$f"); case "$b" in
      mods|plugins) cp -r "$f" ./ ;;
      *.jar|*.txt|*.json|*.yml) cp "$f" ./ ;;
    esac; done
    if [ -d "$D/plugins/plugins" ]; then mv -f "$D"/plugins/plugins/*.jar "$D/plugins/" 2>/dev/null || true; rmdir "$D/plugins/plugins" 2>/dev/null || true; fi )
  echo "CUANTIC" > /dev/null
  echo "$AS" > "$D/.pack.new"
  V="$V moduri=$(ls "$D"/mods/*.jar 2>/dev/null | wc -l) plugini=$(ls "$D"/plugins/*.jar 2>/dev/null | wc -l)"
  STRAT=0; for y in spigot.yml bukkit.yml catserver.yml commands.yml; do [ -f "$D/$y" ] && STRAT=$((STRAT+1)); done
  V="$V straturi-tuning=$STRAT/4"
  echo "$V" > /tmp/apply-v.txt
else
  V="$V descarcare-esuata"
fi
( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & )
V="$V sup=pornit"

# ---- 4. asteapta boot-ul ----
PORNIT=NU
for i in $(seq 1 60); do
  sleep 10
  sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" "$D/live.log" 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)' && { PORNIT=DA; break; }
done
V="$V boot=$PORNIT"
sleep 8
R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/92.5.171.150:25565" 2>/dev/null)
echo "$R" | grep -q '"online":true' && V="$V online=DA" || V="$V online=NU"
JARS=$(ls "$D"/*.jar 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')
V="$V jar=${JARS:-NICIUNUL} pack=$(cat "$D/.pack" 2>/dev/null || echo -)"
FL=$(head -6 "$D/unix_args.txt" 2>/dev/null | tr '\n' ' ' | cut -c1-90)

mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
{ echo "# APPLY-LIVE — $(date -u '+%F %T UTC')"; echo; echo "$V"; echo; echo "flaguri active: \`$FL\`"
  echo; echo '```'; tail -6 "$D/live.log" 2>/dev/null | sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g"; echo "sup.log:"; tail -6 "$D/sup.log" 2>/dev/null; echo '```'; } > analysis/APPLY-LIVE.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/APPLY-LIVE.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
echo "$V"
exit 0
