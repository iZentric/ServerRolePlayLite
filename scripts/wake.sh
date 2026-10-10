#!/usr/bin/env bash
# WAKE — ONE-LINER pentru Cloud Shell: aprinde tot ce tine serverul in picioare si pleaca.
# Se lipeste o singura data, in Cloud Shell:
#   bash <(curl -fsSL https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts/wake.sh)
# Ce face: descarca unelte lipsa, porneste supervisorul (c.sh), runner-ul GitHub, frpc, java.
# Totul cu setsid, deci supravietuieste inchiderii ferestrei.
D=$HOME/cuantic-live
REPO=iZentric/ServerRolePlayLite
BR=arena/a29b4ef4-serverroleplaylite
RAW="https://raw.githubusercontent.com/$REPO/$BR"
echo "== CUANTIC wake =="
mkdir -p "$D"; cd "$D" || exit 1
# Java 17 instalat local (fara root)
if [ ! -x "$HOME/.local/jdk17/bin/java" ] && ! ls /usr/lib/jvm/java-17*/bin/java >/dev/null 2>&1; then
  echo "java: lipsa -> descarc Temurin 17"
  U=$(curl -fsSL --max-time 40 "https://api.adoptium.net/v3/assets/latest/17/hotspot?architecture=x64&image_type=jdk&os=linux" |
      python3 -c "import sys,json;d=json.load(sys.stdin);print(d[0]['binary']['package']['link'])" 2>/dev/null)
  [ -n "$U" ] && curl -fsSL --max-time 300 -o /tmp/j17.tar.gz "$U" && mkdir -p "$HOME/.local" &&
    tar -xzf /tmp/j17.tar.gz -C "$HOME/.local" && L=$(ls -d "$HOME"/.local/jdk-17* | head -1) &&
    ln -sfn "$L" "$HOME/.local/jdk17" && echo "java: $("$HOME/.local/jdk17/bin/java" -version 2>&1|head -1)"
fi
# packul + scripturile la zi
for f in cuantic-live.sh ensure-up.sh cuantic-args.sh; do
  curl -fsSLo "$HOME/.$f" --max-time 25 "$RAW/scripts/$f" || true
done
[ -f "$HOME/c.sh" ] || cp "$HOME/.cuantic-live.sh" "$HOME/c.sh" 2>/dev/null || true
curl -fsSLo "$HOME/c.sh" --max-time 25 "$RAW/scripts/cuantic-live.sh" || true
if [ ! -f "$D/unix_args.txt" ]; then
  echo "pack: lipseste -> descarc ultimul release CatServer"
  Z=$(curl -fsSL --max-time 30 "https://api.github.com/repos/$REPO/releases/tags/lite" |
     python3 -c "import sys,json;print(next((a['browser_download_url'] for a in json.load(sys.stdin).get('assets',[]) if 'Server-CatServer' in a['name']),''))" 2>/dev/null)
  [ -n "$Z" ] && curl -fsSL --max-time 900 -o /tmp/p.zip "$Z" && unzip -oq /tmp/p.zip -d "$D" && rm -f /tmp/p.zip
  chmod +x "$D/start.sh" 2>/dev/null || true
fi
[ -f "$D/eula.txt" ] || echo "eula=true" > "$D/eula.txt"
bash "$HOME/.ensure-up.sh" 2>/dev/null || bash "$RAW/scripts/ensure-up.sh"
R=$(ls -d "$HOME"/actions-runner* "$HOME"/*/actions-runner* 2>/dev/null | head -1)
if [ -n "$R" ] && [ -x "$R/run.sh" ] && ! pgrep -f 'runsvc.sh|actions-runner/run.sh' >/dev/null 2>&1; then
  ( cd "$R" && setsid ./run.sh >/dev/null 2>&1 < /dev/null & ); echo "runner: repornit"
fi
tmux ls 2>/dev/null | grep -q '^frpc:' || { [ -x "$HOME/frpc" ] && tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1" && echo "frpc: pornit"; }
echo "== astept sa urce pe port (max ~150 s, atit dureaza FML cu 30 moduri + 15 pluginuri)"
PORNIT=NU
for i in $(seq 1 30); do
  sleep 5
  if ss -lnt 2>/dev/null | grep -q ':25565' && sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" "$D/live.log" 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)'; then
    PORNIT=DA; break
  fi
done
DONE_STR=$(sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" "$D/live.log" 2>/dev/null | grep -aoE 'Done \([0-9.]+s\)' | tail -1)
echo "== $( [ "$PORNIT" = DA ] && echo "SUS: $DONE_STR, jucabil pe 92.5.171.150:25565" || echo "NU S-A APRINS inca - mai ruleaza o data linia asta si uita-te in $D/live.log" )"
echo "   supervisor: $(pgrep -f 'bash .*c\.sh' >/dev/null && echo alive || echo mort) | runner: $(pgrep -f 'runsvc.sh|actions-runner/run.sh' >/dev/null && echo alive || echo mort) | frpc: $(pgrep -x frpc >/dev/null && echo alive || echo mort)"
