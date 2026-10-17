export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== STARE REALA =="
P=$(pgrep -f "j11/bin/java" | head -1)
[ -n "$P" ] && { ps -o etime=,rss= -p $P; echo "cmd: $(tr '\0' ' ' < /proc/$P/cmdline | cut -c1-90)"; } || echo "Java: NU RULEAZA"
sed 's/\x1b\[[0-9;]*m//g' boot.log 2>/dev/null | grep -oE "Done \([0-9.]*s\)!" | tail -1
echo "mods: $(ls mods/*.jar 2>/dev/null | wc -l)"; echo "world fiere: $(ls world/region/*.mca 2>/dev/null | wc -l)"
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log 2>/dev/null | head -1
echo "== PARTI EXPORT =="
cd ~
rm -f srvpart_*; split -b 99m -d srv-live.tar.gz srvpart_
rm -rf ~/srvparts && mkdir ~/srvparts && cp srvpart_* ~/srvparts/
cd ~/srvparts
git init -qb packdiag
git config user.email c@l && git config user.name c
git add -A && git commit -qm "srv parts $(date +%s)"
git push -qf "$(git -C ~/srpl-claie remote get-url origin)" packdiag:packdiag && echo "PARTI IMPINSE: $(ls srvpart_* | wc -l)" || echo "push parti ESUAT"
