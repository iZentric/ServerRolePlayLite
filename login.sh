#!/bin/bash
# logare GitHub in Cloud Shell FARA gh: device flow (v3: Accept JSON fix)
J=$(curl -s -H "Accept: application/json" https://github.com/login/device/code -d client_id=178c6fc778ccc68e1d6a -d "scope=repo")
UC=$(echo "$J" | grep -o '"user_code":"[^"]*"' | cut -d'"' -f4)
DC=$(echo "$J" | grep -o '"device_code":"[^"]*"' | cut -d'"' -f4)
IV=$(echo "$J" | grep -o '"interval":[0-9]*' | cut -d: -f2)
if [ -z "$UC" ]; then echo "esuat device flow: $J" | head -c 300; exit 1; fi
echo ""
echo "        >>>  CODUL TAU:  $UC  <<<"
echo "        Tasteaza-l pe: https://github.com/login/device"
echo "        Astept..."
( xdg-open https://github.com/login/device ) 2>/dev/null &
while :; do
  sleep ${IV:-5}
  R=$(curl -s -H "Accept: application/json" https://github.com/login/oauth/access_token -d client_id=178c6fc778ccc68e1d6a -d device_code="$DC" -d grant_type=urn:ietf:params:oauth:grant-type:device_code)
  T=$(echo "$R" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
  [ -n "$T" ] && break
  echo -n "."
done
echo "$T" > ~/.claie_token && chmod 600 ~/.claie_token
echo "TOKEN SALVAT. Pornesc claie..."
curl -s https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/main/claie.sh -o ~/.claie.sh
bash ~/.claie.sh
