export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "=== RAPORT FINAL FunCity ==="
cd ~/cuantic-live
echo "server: $(pgrep -f unix_args >/dev/null && echo VIU || echo JOS)"
[ -f boot.log ] && grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1 | sed 's/^/pornire: /'
echo "moduri perf: $(ls mods/ 2>/dev/null | grep -ciE 'starlight|ferrite|datafix|chunkload|performant|lithium|modernfix') din 7"
ls mods/ 2>/dev/null | grep -iE "starlight|ferrite|datafix|chunkload" | tr '\n' ' '; echo
RAM=$(ps -o rss= -p $(pgrep -f unix_args|head -1) 2>/dev/null | awk '{printf "%.0fM",$1/1024}')
echo "RAM server: ${RAM:-?}"
echo "tunel: $(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf.log 2>/dev/null | head -1 || echo NICIUNUL)"
free -m | head -2 | tail -1 | awk '{print "mem: "$3" fol / "$7" liberi din "$2"M"}'
