export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
mkdir -p ~/freeroam && cd ~/freeroam
echo "== DESCARC =="
curl -sL -o F.zip https://github.com/iZentric/ServerRolePlayLite/releases/download/freeroam/Freeroam.1.0.0.zip
echo "marime: $(stat -c %s F.zip) din 147809645"
rm -rf x && unzip -q F.zip -d x 2>/dev/null || python3 -c "import zipfile;zipfile.ZipFile('F.zip').extractall('x')"
echo "== STRUCTURA =="
find x -maxdepth 2 | grep -vE "/(data|assets|logs)/" | head -18
SRC=""; for c in x x/* x/overrides x/*/overrides; do [ -d "$c/mods" ] && SRC="$c/mods" && break; done
echo "source mods: ${SRC:-N-AFLAT}"
if [ -n "$SRC" ]; then
  cd ~/cuantic-live
  mv -f mods mods-pre-fr 2>/dev/null
  cp -r "$SRC" mods
  # configuri ale packului, fara a suprascrie ce exista
  CFG=$(dirname "$SRC")/config; [ -d "$CFG" ] && cp -rn "$CFG"/. config/ 2>/dev/null
  echo "mods din pack: $(ls mods | wc -l) (backup: $(ls ~/cuantic-live/mods-pre-fr 2>/dev/null | wc -l))"
  ls mods | grep -iE "obfuscate|selene|playeranim" || echo "ATTENTIE: packul tot nu aduce lib"
  pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 4
  rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
  setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
  for i in $(seq 1 56); do sleep 5; grep -q "Done (" boot.log && break; done
  sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -oE "Done \([0-9.]*s\)!" | tail -1
  ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || { echo "EROII:"; sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -E "requires|not installed|FATAL|Caused by" | head -8 | cut -c1-150; }
fi
