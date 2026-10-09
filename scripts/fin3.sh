#!/usr/bin/env bash
# FIN3 — pe VM-urile REALE (iZen/Evovv): gaseste IP-ul public, deschide 25565 in security list,
# testeaza SSH cu cheia noastra. Nimic distructiv.
LOG=/tmp/fin3.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
TEN=ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa
R=eu-frankfurt-1
say "== FIN3 — $(date -u '+%F %T UTC') =="

say "vnics (cli):"
oci network vnic list --compartment-id "$TEN" --region $R --output json > /tmp/vnics.json 2>/tmp/vnics.err
say "  rc=$? bytes=$(wc -c < /tmp/vnics.json) eroare=$(head -c 200 /tmp/vnics.err | tr '\n' ' ')"
jq -r '.data[]? | "  \(.["display-name"] // "?") | privat \(.["private-ip"]) | public \(.["public-ip"] // "NICIUNUL") | subnet \(.["subnet-id"]|tostring|.[0:28]) | SL-uri \((.["security-list-ids"]//[])|length)"' /tmp/vnics.json 2>/dev/null >> $LOG

for IID in $(oci compute instance list --compartment-id "$TEN" --region $R --output json 2>/dev/null | jq -r '.data[]? | select(.["lifecycle-state"]=="RUNNING") | .id'); do
  NAME=$(oci compute instance get --instance-id "$IID" --region $R --output json 2>/dev/null | jq -r '.data["display-name"]')
  say "instanta $NAME:"
  VNIC=$(oci network vnic list --compartment-id "$TEN" --display-name "$NAME" --region $R --output json 2>/dev/null | jq -r '.data[0].id // empty')
  [ -z "$VNIC" ] && VNIC=$(oci compute vnic-attachment list --compartment-id "$TEN" --instance-id "$IID" --region $R --output json 2>/dev/null | jq -r '.data[0].["vnic-id"] // empty')
  say "  vnic: ${VNIC:-NICIUNUL}"
  [ -z "$VNIC" ] && continue
  PUB=$(oci network vnic get --vnic-id "$VNIC" --region $R --output json 2>/dev/null | jq -r '.data["public-ip"] // empty')
  SUB=$(oci network vnic get --vnic-id "$VNIC" --region $R --output json 2>/dev/null | jq -r '.data["subnet-id"]')
  say "  ip public: ${PUB:-NICIUNUL} | subnet: ${SUB: -14}"
  if [ -z "$PUB" ]; then
    say "  incearc atribui IP rezervat..."
    RID=$(oci network public-ip create --compartment-id "$TEN" --allocated-resource-id "$VNIC" --assigned-type IPADDRESS --display-name cuantic-$NAME --region $R --output json 2>/dev/null | jq -r '.data.id // empty')
    if [ -n "$RID" ]; then
      PUB=$(oci network public-ip get --public-ip-id "$RID" --region $R --output json 2>/dev/null | jq -r '.data["ip-address"]')
      oci network vnic update --vnic-id "$VNIC" --public-ip-id "$RID" --force --region $R > /dev/null 2>&1
      PUB=$(oci network vnic get --vnic-id "$VNIC" --region $R --output json 2>/dev/null | jq -r '.data["public-ip"] // empty')
      say "  dupa atribuire: ${PUB:-TOT NICIUNUL}"
    else
      say "  nu pot crea IP rezervat (cuota 0 pe Public IPs)"
    fi
  fi
  VCN=$(oci network subnet get --subnet-id "$SUB" --region $R --output json 2>/dev/null | jq -r '.data["vcn-id"]')
  for SL in $(oci network security-list list --vcn-id "$VCN" --compartment-id "$TEN" --region $R --output json 2>/dev/null | jq -r '.data[].id'); do
    CUR=$(oci network security-list get --security-list-id "$SL" --region $R --output json 2>/dev/null)
    HAS=$(echo "$CUR" | jq -r '[.data["ingress-security-rules"][]? | select(.protocol=="6" and .["source"]=="0.0.0.0/0" and (.tcp_options.destination_port.min==25565))] | length')
    say "  SL ${SL: -10}: regula 25565 = $HAS"
    if [ "$HAS" = "0" ]; then
      NEW=$(echo "$CUR" | jq -c '.data["ingress-security-rules"] + [{protocol:"6",source:"0.0.0.0/0",description:"CUANTIC Minecraft",tcp_options:{destination_port:{min:25565,max:25565}}}]')
      EGG=$(echo "$CUR" | jq -c '.data["egress-security-rules"]')
      OUT=$(oci network security-list update --security-list-id "$SL" --ingress-security-rules "$NEW" --egress-security-rules "$EGG" --force --region $R 2>&1 | tail -2 | tr '\n' ' ')
      say "    update: ${OUT:-OK (fara iesire = succces)}"
    fi
  done
  if [ -n "$PUB" ]; then
    say "  test SSH $PUB:22 ..."
    timeout 8 bash -c "exec 3<>/dev/tcp/$PUB/22" 2>/dev/null && say "    port 22 DESCHIS" || say "    port 22 inchis/filtrat"
    for U in opc ubuntu root oracle; do
      R2=$(ssh -i ~/.ssh/cuantic_oci -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes $U@$PUB 'echo VIU; nproc; free -m | sed -n 2p; df -h / | sed -n 2p; java -version 2>&1 | head -1; sudo -n true 2>/dev/null && echo SUDO-DA || echo SUDO-NU' 2>&1 | head -6)
      case "$R2" in VIU*) say "    ACCES $U@$PUB: $R2"; break;; esac
    done
    say "    (daca nu zice ACCES, cheia noastra nu e pe instanta — a lor e in panou)"
    [ -n "$PUB" ] && echo "$PUB" >> /tmp/pubs.txt
  fi
done
say "IP-uri publice rezultate: $(cat /tmp/pubs.txt 2>/dev/null | tr '\n' ' ')"
mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
F=analysis/fin3.md
printf '# CUANTIC FIN3 — %s\n```\n' "$(date -u '+%F %T UTC')" > $F
cat $LOG >> $F
printf '```\n' >> $F
git add -f analysis/fin3.md; git commit -q -m "fin3: vnic/IP/security list pe VM-urile reale" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0
