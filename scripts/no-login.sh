#!/usr/bin/env bash
# NO-LOGIN — scoate temporar logarea cu parola (AuthMe + FastLogin), la cererea proprietarului.
# Nu stergeti nimic: pluginurile sunt REDENUMITE in *.disabled-<ts>. Revenirea = cativa `mv`.
# Repornirea se face prin punte (cmd.in), nu prin pkill, ca sa testam si puntea.
D=$HOME/cuantic-live
L=$D/live.log
REPO=iZentric/ServerRolePlayLite
BR=arena/a29b4ef4-serverroleplaylite
TS=$(date +%s)
V="NOLOGIN:"
cd "$D" || { echo "NOLOGIN: lipsa $D" > /tmp/nl.txt; exit 0; }

# ---- 1. cine e de oprit ----
GASITE=$(ls plugins/ 2>/dev/null | grep -aiE '^(AuthMe|FastLogin)' | grep -avi '\.disabled')
if [ -z "$GASITE" ]; then
  V="$V deja-scoase"
else
  for f in $GASITE; do
    mv "plugins/$f" "plugins/$f.disabled-$TS" && V="$V -$f"
  done
fi
# parolă obligatorie nici prin AltMode: stingem forțat din config (ramâne dacă pluginul revine)
[ -f plugins/AuthMe/config.yml ] && sed -i 's/^ForceLogin:.*/ForceLogin: false/' plugins/AuthMe/config.yml 2>/dev/null
[ -f plugins/FastLogin/config.yml ] && sed -i -e 's/^autoLogin:.*/autoLogin: false/' -e 's/^autoRegister:.*/autoRegister: false/' plugins/FastLogin/config.yml 2>/dev/null

# ---- 2. repornire prin punte ----
: > "$D/cmd.in" 2>/dev/null
printf 'restart\n' >> "$D/cmd.in"
A=NU
for i in $(seq 1 30); do
  sleep 6
  if ! pgrep -f 'java @unix_args' >/dev/null 2>&1; then A=AMURIT; break; fi
done
[ "$A" = NU ] && { pkill -TERM -f 'java @unix_args'; sleep 20; A=printr-un-pkill; }
# supervisorul (c.sh) il reaprinde singur; daca el lipseste, il pornim noi
for i in $(seq 1 30); do
  sleep 6
  sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" "$L" 2>/dev/null | grep -qa 'Done (' && break
done
pgrep -f 'java @unix_args' >/dev/null 2>&1 || { [ -f "$HOME/c.sh" ] && ( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 </dev/null & ); }

# ---- 3. verificare: pluginuri_active + port ----
sleep 8
: > "$D/cmd.in" 2>/dev/null
printf 'plugins\n' >> "$D/cmd.in"
PL=NA
for i in $(seq 1 12); do
  sleep 4
  PL=$(sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" "$L" 2>/dev/null | grep -a 'This server is running' | tail -1 | grep -oE '[0-9]+ plugins' )
  [ -n "$PL" ] && break
done
V="$V $PL"
sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" "$L" 2>/dev/null | grep -aiE 'AuthMe|FastLogin' | tail -4 > /tmp/nl-plugins.txt
grep -qi 'AuthMe enabled\|FastLogin.*Enabling' /tmp/nl-plugins.txt && V="$V ATENTIE-incarca-actorii" || V="$V actorii-nu-si-au-aparut"
ss -lnt 2>/dev/null | grep -q ':25565' && V="$V port=SUS" || V="$V port=NU"
R=$(curl -fsS --max-time 20 "https://api.mcsrvstat.us/3/92.5.171.150:25565" 2>/dev/null)
echo "$R" | grep -q '"online":true' && V="$V online=DA" || V="$V online=NU"
ls "$D/plugins" 2>/dev/null | grep -a disabled > /tmp/nl-redenumite.txt
echo "$V" > /tmp/nl.txt

mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
{ echo "# NO-LOGIN — $(date -u '+%F %T UTC')"; echo; echo "$V"; echo
  echo '```'; cat /tmp/nl-plugins.txt 2>/dev/null; echo "redenumite:"; cat /tmp/nl-redenumite.txt 2>/dev/null; echo '```'; echo
  echo "## cum bagi logarea inapoi (aceeasi masina, un singur rand)"; echo '```'
  echo "cd \$HOME/cuantic-live && for f in plugins/*.disabled-*; do mv \"\$f\" \"\${f%.disabled-*}\"; done; echo restart >> cuantic-live/cmd.in"
  echo '```'; } > analysis/NO-LOGIN.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/NO-LOGIN.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "$BR" || true
git push -q origin "HEAD:$BR" || echo "push: nimic"
cat /tmp/nl.txt
exit 0
