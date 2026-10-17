export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
pgrep -f cloudflared >/dev/null && echo "cloudflared: ruleaza" || echo "cloudflared: mort"
URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log 2>/dev/null | tail -1)
[ -z "$URL" ] && URL=$(sudo cat /var/log/cloudflared.log 2>/dev/null | grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" | tail -1)
[ -z "$URL" ] && URL=$(pgrep -af cloudflared | head -1 | cut -c1-100)
echo "URL: ${URL:-negasit}"
HOSTN=$(echo "$URL" | sed 's|https://||;s|\.trycloudflare\.com.*||')
[ -n "$HOSTN" ] && timeout 10 curl -s -o /dev/null -w "edge probe: %{http_code}\n" "https://$HOSTN.trycloudflare.com/" 2>&1
