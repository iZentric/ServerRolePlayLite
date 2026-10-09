#!/usr/bin/env bash
# IP — pe VM-ul real (iZen): IP public + regula 25565 in security list + server CUANTIC prin SSH.
LOG=/tmp/ip.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
TEN=ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa
say "== IP — $(date -u '+%F %T UTC') =="
J=/usr/bin/jq; command -v jq >/dev/null && J=$(command -v jq)

IID=$(oci compute instance list --compartment-id "$TEN" --output json 2>/dev/null | $J -r '.data[]? | select(.["lifecycle-state"]=="RUNNING") | select(.["display-name"]=="iZen") | .id' | head -1)
[ -z "$IID" ] && IID=$(oci compute instance list --compartment-id "$TEN" --output json 2>/dev/null | $J -r '.data[]? | select(.["lifecycle-state"]=="RUNNING") | .id' | head -1)
say "instanta tinta: ${IID:-NICIUNUL}"
if [ -z "$IID" ]; then say "nu gasesc instanta running"; exit 0; fi

VNIC=$(oci compute instance list-vnics --instance-id "$IID" --output json 2>/dev/null | $J -r '.data[0].id // empty')
[ -z "$VNIC" ] && VNIC=$(oci network vnic list --compartment-id "$TEN" --output json 2>/dev/null | $J -r --arg i "$IID" '.data[]? | select(.["attachments"][0]?["vnic-id"] // "" | . != null) | .id' | head -1)
say "vnic: ${VNIC:-NICIUNUL}"
if [ -z "$VNIC" ]; then say "nu gasesc vnic"; exit 0; fi
VJ=$(oci network vnic get --vnic-id "$VNIC" --output json 2>/dev/null)
PUB=$(echo "$VJ" | $J -r '.data["public-ip"] // empty')
PRIV=$(echo "$VJ" | $J -r '.data["private-ip"]')
SUB=$(echo "$VJ" | $J -r '.data["subnet-id"]')
say "privat: $PRIV | public: ${PUB:-NICIUNUL} | subnet: ${SUB: -12}"

# ---------- IP public, daca nu are ----------
if [ -z "$PUB" ]; then
  say "creez Reserved Public IP atasat pe VNIC..."
  OUT=$(oci network public-ip create --compartment-id "$TEN" --allocated-resource-id "$VNIC" --assigned-type VNIC --display-name cuantic-ip 2>&1)
  PID=$(echo "$OUT" | $J -r '.data.id // empty' 2>/dev/null)
  PUB=$(echo "$OUT" | $J -r '.data["ip-address"] // empty' 2>/dev/null)
  [ -z "$PUB" ] && { say "create a esuat: $(echo "$OUT" | head -c 300 | tr '\n' ' ')"; }
  [ -n "$PID" ] && [ -z "$PUB" ] && PUB=$(oci network public-ip get --public-ip-id "$PID" --output json 2>/dev/null | $J -r '.data["ip-address"] // empty')
  say "rezultat: ${PUB:-TOT NICIUNUL}"
  sleep 6
  PUB=$(oci network vnic get --vnic-id "$VNIC" --output json 2>/dev/null | $J -r '.data["public-ip"] // empty')
fi
say "IP public final: ${PUB:-NICIUNUL}"
[ -z "$PUB" ] && { say "far IP public nu are rost mai departe"; exit 0; }

# ---------- regula in security list ----------
VCN=$(oci network subnet get --subnet-id "$SUB" --output json 2>/dev/null | $J -r '.data["vcn-id"]')
for SL in $(oci network security-list list --vcn-id "$VCN" --compartment-id "$TEN" --output json 2>/dev/null | $J -r '.data[].id'); do
  CUR=$(oci network security-list get --security-list-id "$SL" --output json 2>/dev/null)
  HAS=$(echo "$CUR" | $J -r '[.data["ingress-security-rules"][]? | select(.protocol=="6" and .["source"]=="0.0.0.0/0" and (.tcp_options.destination_port.min==25565 // .tcp_options.destination_port==25565))] | length')
  if [ "$HAS" = "0" ]; then
    NEW=$(echo "$CUR" | $J -c '.data["ingress-security-rules"] + [{protocol:"6",source:"0.0.0.0/0",description:"CUANTIC MC",tcp_options:{destination_port:{min:25565,max:25565}}}]')
    EGG=$(echo "$CUR" | $J -c '.data["egress-security-rules"]')
    oci network security-list update --security-list-id "$SL" --ingress-security-rules "$NEW" --egress-security-rules "$EGG" --force > /dev/null 2>/tmp/sl.err
    say "  SL ${SL: -10}: $( [ -s /tmp/sl.err ] && head -c 200 /tmp/sl.err | tr '\n' ' ' || echo 'regula 25565 ADAUGATA')"
  else
    say "  SL ${SL: -10}: regula 25565 exista deja"
  fi
done

# ---------- SSH: intra cheia noastra? ----------
say "test port 22 pe $PUB: $(timeout 8 bash -c "exec 3<>/dev/tcp/$PUB/22" 2>/dev/null && echo DESCHIS || echo FILTRAT)"
USEROK=""; for U in opc ubuntu root oracle; do
  O=$(ssh -i ~/.ssh/cuantic_oci -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes $U@$PUB 'echo OK; nproc; free -m|sed -n 2p; java -version 2>&1|head -1' 2>/dev/null)
  case "$O" in OK*) USEROK=$U; say "ACCES prin $U: $(echo "$O"|tr '\n' ' ')"; break;; esac
done
if [ -z "$USEROK" ]; then
  say "cheia noastra NU intra pe instanta (a lui e in panou) — IPul e gata, dar trebuie urcat serverul de tine"
  echo "$PUB:25565" > /tmp/ip-out.txt
else
  say "rulez deploy CUANTIC prin SSH ca $USEROK..."
  cat > /tmp/deploy.sh <<'EOS'
set -x
mkdir -p ~/mc && cd ~/mc
URL=$(curl -fsS --max-time 30 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
[ -f CatServer-1.16.5-1d8d6313-server.jar ] || { curl -fsSL --retry 2 -o p.zip "$URL" && unzip -qo p.zip && rm -f p.zip; }
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties
echo 'eula=true' > eula.txt
MEM=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo)
HEAP=$(( MEM>2600 ? 1024 : 640 ))
sed -i "1s/.*/-Xms256M/;2s/.*/-Xmx${HEAP}M/" unix_args.txt
J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1); [ -z "$J" ] && J=$(command -v java)
pkill -f 'unix_args' 2>/dev/null; sleep 2
setsid bash -c "cd $HOME/mc && exec tail -f /dev/null | $J @unix_args.txt >> run.log 2>&1" &
sleep 5; echo "mem: $(free -m | sed -n 2p)"; echo "java: $(pgrep -fc java)"
sudo -n iptables -I INPUT -p tcp --dport 25565 -j ACCEPT 2>/dev/null && echo "iptables: regula adaugata" || echo "iptables: n-am voie (OK daca e dezactivat)"
EOS
  ssh -i ~/.ssh/cuantic_oci -o StrictHostKeyChecking=no $USEROK@$PUB 'bash -s' < /tmp/deploy.sh 2>&1 | tail -25 | sed 's/^/  /' >> $LOG
  say "astept boot + prob din internet:"
  OK=NU
  for i in $(seq 1 14); do
    sleep 20
    R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/$PUB:25565" 2>/dev/null)
    say "  proba $i: $(echo "$R" | grep -oE '\"online\":(true|false)') $(echo "$R" | grep -oE '\"players\":\{[^}]*\}')"
    case "$R" in *'"online":true'*) OK=DA; break;; esac
  done
  say "==> JUCABIL PE $PUB:25565 : $OK"
  echo "$PUB:25565 $OK" > /tmp/ip-out.txt
fi

mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
F=analysis/ip.md
printf '# IP pe iZen — %s\n```\n' "$(date -u '+%F %T UTC')" > $F
cat $LOG >> $F; printf '```\n' >> $F
git add -f analysis/ip.md; git commit -q -m "ip: $(cat /tmp/ip-out.txt 2>/dev/null)" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0
