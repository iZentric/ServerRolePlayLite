echo "== CINE SUNT =="
pgrep -fa "cloudflared tunnel" | head -2 || echo "cf: NICIUNUL"
pgrep -f "unix_args" >/dev/null && echo "server MC: VIU" || echo "server MC: MORT"
echo "== FISIER CF =="
ls -l ~/cuantic-live/cloudflared 2>/dev/null | awk '{print $5" bytes"}'
echo "== LOG CF =="
tail -12 /tmp/cf.log 2>/dev/null || echo "log absent"
grep -oE "[a-z0-9-]+\.trycloudflare\.com:[0-9]+" /tmp/cf.log 2>/dev/null | head -1
echo "== PORT =="
ss -lnt 2>/dev/null | grep 25565 || netstat -lnt 2>/dev/null | grep 25565 || echo "ss/netstat muti"
