sleep 8
A=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1)
echo "ADRESA: ${A:-incă în legătură}"
[ -z "$A" ] && tail -20 /tmp/cf.log
grep -c "connSet" /tmp/cf.log 2>/dev/null | head -1
