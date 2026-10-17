export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "=== v18: status ==="
cd ~/cuantic-live
echo "server: $(pgrep -f unix_args >/dev/null && echo VIU || echo JOS)"
[ -f boot.log ] && grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1 | sed 's/^/pornire: /'
echo "tunel: $(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf.log 2>/dev/null | head -1 || echo NICIUNUL)"
echo "runner: $(pgrep -f run.sh >/dev/null && echo VIU || echo JOS)"
