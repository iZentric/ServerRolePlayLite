export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== CAUT LIBURILE LIPSA PE DISC =="
for n in obfuscate selene playeranimator player-animator playerAnimator; do find ~ -iname "*${n}*.jar" 2>/dev/null | grep -v "/mods/" | head -3; done
echo "== RESTAURARE DIN backup (daca exista)"
for d in ~/functity-out ~/funcity-backup ~/funcity-live ~/pack ~/final; do
  [ -d "$d" ] && ls "$d"/mods/*.jar 2>/dev/null | grep -iE "obfuscate|selene|playeranim" | while read -r f; do cp -n "$f" mods/ && echo "restaurat: $(basename $f)"; done
done
echo "== PORNIRE =="
pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 4
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 50); do sleep 5; grep -q "Done (" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -oE "Done \([0-9.]*s\)!" | tail -1
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || { echo "TOT CRASHEAZA:"; sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -A14 "LoadingFailedException" | head -16 | cut -c1-150; }
