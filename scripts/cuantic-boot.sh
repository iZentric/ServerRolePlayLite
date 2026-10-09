#!/usr/bin/env bash
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
echo "GATA. Daca la pct. 5 vezi \"online\":true, dai Join in Minecraft."
