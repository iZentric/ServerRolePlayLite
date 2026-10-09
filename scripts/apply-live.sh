#!/usr/bin/env bash
# APPLY-LIVE — aduce serverul live la ULTIMA versiune de pe release `lite` si il porneste curat:
# opreste supervisorul vechit, isi ia singur noul pack (world-ul ramane), pune flagurile de build,
# reporneste frpc + java, si lasa verdictul in mesajul commitului.
# Asta e UNEALTA de implantare/rollback: VETE_ASTEPTAT=1.6.0 -> aseaza fix versiunea aceea.
D=$HOME/cuantic-live
REPO=iZentric/ServerRolePlayLite
AS=${VETA_ASTEPTAT:-}
V="APPLY: incepe"

# ---- 1. aşteaptă release-ul aşteptat (build-ul trebuie sa termine inainte) ----
if [ -n "$AS" ]; then
  for i in $(seq 1 40); do
    CUR=$(gh release view lite --repo "$REPO" --json assets --jq '[.assets[].name|select(test("Server-CatServer"))][0]' 2>/dev/null)
    case "$CUR" in *"$AS"*) V="$V release=$CUR"; break ;; esac
    sleep 15
    [ $i -eq 40 ] && V="$V release=asteptam-$AS-am-gasit-$CUR"
  done
fi

# ---- 2. supervisorul vechi jos (altfel isi tine propriul java in memorie veche) ----
pkill -f 'bash .*c\.sh' 2>/dev/null && V="$V sup=oprit" || V="$V sup=nimic"
sleep 3
pkill -TERM -f 'java @unix_args' 2>/dev/null
sleep 20
pgrep -f 'java @unix_args' >/dev/null 2>&1 && { pkill -KILL -f 'java @unix_args'; sleep 6; }

# ---- 3. scriptul de run la zi + packul cel nou ----
curl -fsSLo "$HOME/c.sh" "https://raw.githubusercontent.com/$REPO/arena/a29b4ef4-serverroleplaylite/scripts/cuantic-live.sh" || V="$V c.sh=ESUAT"
( cd "$D" 2>/dev/null && rm -f .pack ) 2>/dev/null
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
