#!/usr/bin/env bash
# IZEN — pe VM-ul real din cont: IP public, regula 25565, server pornit PRIN SSH (traieshte dupa job), proba dinafara.
LOG=/tmp/izen.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
TEN=ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa
KEY=$HOME/.ssh/cuantic_oci
say "== IZEN — $(date -u '+%F %T UTC') =="

IID=$(oci compute instance list --compartment-id "$TEN" --output json 2>/dev/null | jq -r '.data[]?|select(.["lifecycle-state"]=="RUNNING")|select(.["display-name"]=="iZen")|.id' | head -1)
[ -z "$IID" ] && IID=$(oci compute instance list --compartment-id "$TEN" --output json 2>/dev/null | jq -r '.data[]?|select(.["lifecycle-state"]=="RUNNING")|.id' | head -1)
say "instanta: ${IID:-NICIUNUL}"
[ -z "$IID" ] && { say "nu gasesc instanta"; exit 0; }

VNIC=$(oci compute instance list-vnics --instance-id "$IID" --output json 2>/dev/null | jq -r '.data[0].id // empty')
say "vnic: ${VNIC:-NICIUNUL}"
if [ -n "$VNIC" ]; then
  VJ=$(oci network vnic get --vnic-id "$VNIC" --output json 2>/dev/null)
  PUB=$(echo "$VJ" | jq -r '.data["public-ip"] // empty')
  SUB=$(echo "$VJ" | jq -r '.data["subnet-id"]')
  say "privat $(echo "$VJ"|jq -r '.data["private-ip"]') | public ${PUB:-NICIUNUL}"
  if [ -z "$PUB" ]; then
    OUT=$(oci network public-ip create --compartment-id "$TEN" --allocated-resource-id "$VNIC" --assigned-type VNIC --display-name cuantic-ip 2>&1)
    PUB=$(echo "$OUT" | jq -r '.data["ip-address"] // empty' 2>/dev/null)
    [ -z "$PUB" ] && say "  create IP: $(echo "$OUT" | head -c 220 | tr '\n' ' ')"
    sleep 5
    [ -n "$PUB" ] || PUB=$(oci network vnic get --vnic-id "$VNIC" --output json 2>/dev/null | jq -r '.data["public-ip"] // empty')
    say "  IP public acum: ${PUB:-NICIUNUL}"
  fi
  if [ -n "$PUB" ]; then
    VCN=$(oci network subnet get --subnet-id "$SUB" --output json 2>/dev/null | jq -r '.data["vcn-id"]')
    for SL in $(oci network security-list list --vcn-id "$VCN" --compartment-id "$TEN" --output json 2>/dev/null | jq -r '.data[].id'); do
      CUR=$(oci network security-list get --security-list-id "$SL" --output json 2>/dev/null)
      HAS=$(echo "$CUR" | jq -r '[.data["ingress-security-rules"][]?|select(.protocol=="6" and .["source"]=="0.0.0.0/0" and ((.tcp_options.destination_port.min // .tcp_options.destination_port)==25565))]|length')
      if [ "$HAS" = "0" ]; then
        NEW=$(echo "$CUR" | jq -c '.data["ingress-security-rules"] + [{protocol:"6",source:"0.0.0.0/0",description:"CUANTIC MC",tcp_options:{destination_port:{min:25565,max:25565}}}]')
        EGG=$(echo "$CUR" | jq -c '.data["egress-security-rules"]')
        oci network security-list update --security-list-id "$SL" --ingress-security-rules "$NEW" --egress-security-rules "$EGG" --force >/dev/null 2>/tmp/sl.err
        say "  regula 25565 pe SL ${SL: -10}: $( [ -s /tmp/sl.err ] && head -c 160 /tmp/sl.err | tr '\n' ' ' || echo ADAUGATA)"
      else say "  regula 25565 exista pe SL ${SL: -10}"; fi
    done
    echo "$PUB" > /tmp/izen-ip.txt
  fi
fi

PUB=$(cat /tmp/izen-ip.txt 2>/dev/null)
if [ -z "$PUB" ]; then say "fara IP public, ma opresc"; exit 0; fi
U_OK=""
for U in opc ubuntu root oracle; do
  O=$(ssh -i $KEY -o StrictHostKeyChecking=no -o ConnectTimeout=12 -o BatchMode=yes $U@$PUB 'echo OK; nproc; free -m|sed -n 2p; df -h /|sed -n 2p; ls /usr/lib/jvm 2>/dev/null|head -4' 2>&1 | head -8)
  case "$O" in OK*) U_OK=$U; say "SSH OK ca $U:"$'\n'"$O"; break;; *) say "  $U@$PUB: $(echo "$O"|head -c 120)";; esac
done
if [ -z "$U_OK" ]; then say "cheia noastra nu intra pe iZen"; exit 0; fi

cat > /tmp/deploy.sh <<'EOS'
mkdir -p ~/mc && cd ~/mc
URL=$(curl -fsS --max-time 30 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
[ -f CatServer-1.16.5-1d8d6313-server.jar ] || { curl -fsSL --retry 2 -o p.zip "$URL" && unzip -qo p.zip && rm -f p.zip; }
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/; s/^view-distance=.*/view-distance=4/' server.properties
echo 'eula=true' > eula.txt
MEM=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo)
HEAP=$(( MEM>2600 ? 1024 : 512 ))
if [ -f unix_args.txt ]; then sed -i "1s/.*/-Xms128M/;2s/.*/-Xmx${HEAP}M/" unix_args.txt; ARGS=@unix_args.txt; else ARGS="-Xmx${HEAP}M -jar $(ls CatServer-*.jar|head -1) nogui"; fi
J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null|head -1); [ -z "$J" ] && J=$(ls /usr/lib/jvm/java-8*/bin/java /usr/lib/jvm/java-11*/bin/java 2>/dev/null|head -1); [ -z "$J" ] && J=java
pkill -f 'unix_args' 2>/dev/null; pkill -f 'CatServer' 2>/dev/null; sleep 2
setsid bash -c "cd $HOME/mc && exec tail -f /dev/null | $J $ARGS >> run.log 2>&1" &
sleep 8; echo "mem $(free -m|sed -n 2p) java=$(pgrep -c java)"
sudo -n iptables -I INPUT -p tcp --dport 25565 -j ACCEPT 2>/dev/null && echo iptables-ok || echo iptales-skip
EOS
ssh -i $KEY -o StrictHostKeyChecking=no $U_OK@$PUB 'bash -s' < /tmp/deploy.sh 2>&1 | tail -12 | sed 's/^/  /' >> $LOG

for i in $(seq 1 12); do
  sleep 15
  R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/$PUB:25565" 2>/dev/null)
  say "  proba $i: $(echo "$R" | grep -oE '\"online\":(true|false)') $(echo "$R" | grep -oE '\"players\":\{[^}]*\}')"
  case "$R" in *'"online":true'*) break;; esac
done
say "==> ADRESA: $PUB:25565"

mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
{ printf '# IZEN — %s\n\n- adresa: `%s:25565`\n\n' "$(date -u '+%F %T UTC')" "$PUB"; echo '```'; cat $LOG; echo '```'; } > analysis/izen.md
git add -f analysis/izen.md; git commit -q -m "izen: $PUB:25565" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0
