export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== MONTAJ VALIDAT =="
if [ -z "$(ls mods/*.jar 2>/dev/null)" ] && [ -d mods-pre-fr ]; then mv -f mods-pre-fr mods && echo "mods restaurat din pre-fr: $(ls mods/*.jar | wc -l)"; fi
pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 4
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 60); do sleep 5; grep -qE "Done \(|LoadingFailed|FATAL" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
if grep -q "Done (" boot.clean; then grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1; echo "server: VIU";
else
  BAD=$(grep -oE "Mod .§e[a-zA-Z0-9_-]+§r requires" boot.clean | sed 's/.*§e//;s/§r.*//' | sort -u)
  for m in $BAD; do rm -fv mods/*"${m}"* 2>/dev/null; done
  [ -n "$BAD" ] && { pkill -9 -f "j11/bin/java"; sleep 4; setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null & for i in $(seq 1 60); do sleep 5; grep -qE "Done \(|FATAL" boot.log && break; done; sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean; }
  grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1 || { echo "CRASHEAZA:"; grep -aE "requires|FATAL" boot.clean | head -4 | cut -c1-140; }
fi
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: INCHIS"
echo "== TUNEL =="
pgrep -f "cloudflared tunnel" >/dev/null || setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null &
for i in $(seq 1 15); do sleep 3; grep -q trycloudflare /tmp/cf.log 2>/dev/null && break; done
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
echo "== PARTI (branch dedicat) =="
cd ~; rm -f srvpart_* srv-live.tar.gz
tar czf srv-live.tar.gz -C ~/cuantic-live . 2>/dev/null
split -b 99m -d srv-live.tar.gz srvpart_
rm -rf ~/srvparts && mkdir ~/srvparts && cp srvpart_* ~/srvparts/
cd ~/srvparts && git init -qb srvparts && git config user.email c@l && git config user.name c
git add -A && git commit -qm "parts $(date +%s)"
git push -qf "$(git -C ~/srpl-claie remote get-url origin)" srvparts:srvparts && echo "PARTI: IMPINSE ($(ls ~/srvpart_* | wc -l) bucati)" || echo "PARTI: ESUAT"
