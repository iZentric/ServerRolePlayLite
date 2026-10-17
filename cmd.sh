export PATH=$PATH:/usr/bin:/bin:/usr/local/bin:$HOME/oci-cli/bin
echo "== fisiere oci =="; ls -la ~/.oci/ 2>/dev/null | head -5; cat ~/.oci/config 2>/dev/null | grep -vE "^\s*#|^\s*$" | sed 's/key_file.*/key_file: OK/' | head -8
echo "== test auth cu cheia de pe disc =="
K=$(grep -oE "key_file=.*" ~/.oci/config 2>/dev/null | cut -d= -f2 | tr -d ' ')
[ -f "$K" ] || K=$(ls ~/.oci/*.pem 2>/dev/null | head -1)
CFG=$(grep -E "tenancy|user|fingerprint|region" ~/.oci/config 2>/dev/null)
TEN=$(echo "$CFG" | grep tenancy | cut -d= -f2 | tr -d ' ')
USR=$(echo "$CFG" | grep "^user" | cut -d= -f2 | tr -d ' ')
FPR=$(echo "$CFG" | grep fingerprint | cut -d= -f2 | tr -d ' ')
REG=$(echo "$CFG" | grep region | cut -d= -f2 | tr -d ' ')
if [ -f "$K" ] && [ -n "$TEN" ]; then
  echo "key gasit: $K | fp: $FPR"
  D=$(date -u +"%a, %d %b %Y %H:%M:%S UTC")
  P="/20160918/availabilityDomains?compartmentId=$TEN"
  SIG=$(printf 'GET %s\ndate: %s' "$P" "$D" | openssl dgst -sha256 -sign "$K" | openssl base64 -A)
  RESP=$(curl -s "https://iaas.$REG.oraclecloud.com$P" -H "date: $D" -H "Authorization: Signature headers=\"date (request-target)\",keyId=\"$TEN/$USR/$FPR\",algorithm=\"rsa-sha256\",signature=\"$SIG\"")
  echo "RESP: $(echo $RESP | head -c 150)"
  echo "$RESP" | grep -q '"name"' && echo "AUTENTIFICARE OCI: FUNCTIONEALA" || echo "AUTENTIFICARE: MOARTA (cheia nu mai e in cont)"
else
  echo "fara key/config"
fi
