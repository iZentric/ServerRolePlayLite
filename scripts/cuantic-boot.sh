#!/usr/bin/env bash
REPO=iZentric/ServerRolePlayLite
BR=arena/a29b4ef4-serverroleplaylite
exec > >(tee /tmp/boot.log) 2>&1
raport() {
  # trimite ce am vazut inapoi in repo (analysis/BOOT.md) - asa aflu si eu starea,
  # fara runner si fara sa lipesc tu comenzi.
  local sha
  sha=$(gh api "repos/$REPO/contents/analysis/BOOT.md?ref=$BR" --jq .sha 2>/dev/null || true)
  if gh api -X PUT "repos/$REPO/contents/analysis/BOOT.md" -f message="boot: raport automat $(date -u +%H:%M:%S)" \
        -f content="$(base64 -w0 /tmp/boot.log)" -f branch="$BR" ${sha:+-f sha=$sha} >/dev/null 2>&1; then
    echo "(raportul a fost trimis in repo: analysis/BOOT.md)"
  else
    echo "(nu am putut trimite raportul - gh nu e autentificat aici?)"
  fi
}
trap raport EXIT
# CUANTIC BOOT — trezeste masina dintr-o rasuflare.
# De ce exista: Cloud Shell omoara TOT ce ai pornit in el (java, frpc, runner-ul GitHub) cand
# terminalul se inchide sau cand sesiunea e recyclata. Home-ul ramane, procesele nu.
# Un rand de lipit in Cloud Shell:
#   curl -fsSLo ~/b.sh https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts/cuantic-boot.sh && bash ~/b.sh
RAW=https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts

echo "== 1. runner-ul GitHub (ca sa pot eu sa ating serverul) =="
R=$(ls -d $HOME/actions-runner* $HOME/*/actions-runner* $HOME/runner* $HOME/*/runner* 2>/dev/null | head -1)
if [ -n "$R" ]; then
  if pgrep -f 'runsvc.sh|actions-runner/run.sh|./run.sh' >/dev/null 2>&1; then
    echo "   e deja pornit"
  else
    ( cd "$R" && setsid ./run.sh </dev/null >/dev/null 2>&1 & )
    sleep 4
    pgrep -f './run.sh' >/dev/null 2>&1 && echo "   pornit in $R" || echo "   NU a pornit (ruleaza manual ./run.sh in $R)"
  fi
else
  echo "   NICIUN folder de runner in \$HOME -> joburile GitHub vor sta la coada la infinit."
  echo "   (se instaleaza o data cu config.sh + token de inrolare; apoi ruleaza ./run.sh)"
fi

echo "== 2. serverul + tunelul frp =="
curl -fsSLo "$HOME/c.sh" "$RAW/cuantic-live.sh" && chmod +x "$HOME/c.sh"
if pgrep -f 'java @unix_args' >/dev/null 2>&1; then
  echo "   java e deja SUS — doar ma uit dupa ea"
else
  mkdir -p "$HOME/cuantic-live"
  ( setsid bash "$HOME/c.sh" >> "$HOME/cuantic-live/sup.log" 2>&1 </dev/null & )
  echo "   il pornesc (ruleaza in fond, terminalul tau ramane liber)"
fi

echo "== 3. astept boot-ul =="
for i in $(seq 1 30); do
  sleep 5
  if tail -c 600000 "$HOME/cuantic-live/live.log" 2>/dev/null | grep -a 'Done (' >/dev/null; then
    echo "   $(tail -c 600000 "$HOME/cuantic-live/live.log" | grep -a -o 'Done ([0-9.]*s)' | tail -1) — serverul e gata"; break
  fi
  [ $((i % 6)) -eq 0 ] && echo "   inca se incarca... $((i*5))s"
done

echo "== 4. porturi =="
ss -lnt 2>/dev/null | grep -E ':25565|:25566' || echo "   nimic nu asculta inca"
echo "== 5. din exterior (prin frp pe 92.5.171.150) =="
curl -s --max-time 15 "https://api.mcsrvstat.us/3/92.5.171.150:25565" | head -c 160; echo
echo "== 6. diagnostc daca n-a pornit =="
if ! ss -lnt 2>/dev/null | grep -q ':25565'; then
  echo "   live.log (ultimele 25 linii relevante):"
  sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" "$HOME/cuantic-live/live.log" 2>/dev/null | grep -aiE 'error|exception|Unrecognized|Done \(|Killed|No such|denied|Address already|EULA' | tail -12 | cut -c1-170 | sed 's/^/     /'
  echo "   sup.log:"; tail -8 "$HOME/cuantic-live/sup.log" 2>/dev/null | cut -c1-170 | sed 's/^/     /'
  echo "   java: $(pgrep -fa 'java @unix_args' | head -2 | cut -c1-120)"
  echo "   unix_args: $(head -4 "$HOME/cuantic-live/unix_args.txt" 2>/dev/null | tr '\n' ' ')"
  echo "   fisiere: $(ls "$HOME/cuantic-live" 2>/dev/null | tr '\n' ' ' | cut -c1-200)"
  echo "   marcare pack: $(cat "$HOME/cuantic-live/.pack" 2>/dev/null || echo FARA)"
  echo "   disc: $(df -h "$HOME" 2>/dev/null | tail -1)"
  echo "   memorie: $(free -m | awk 'NR==2{print $2" total, "$7" libera"}')"
  echo "   gh: $(gh auth status 2>&1 | head -2 | tr '\n' ' ' | cut -c1-120)"
  echo "   FRAPORT: $(pgrep -fa frpc | head -1 | cut -c1-100)"
fi
echo "GATA. Daca la pct. 5 vezi \"online\":true, dai Join in Minecraft."
