#!/usr/bin/env bash
# ============================================================
#  CUANTIC v2 — ridica singur VM-ul ARM Gratuit in Oracle Cloud
#  Ruleaza in CLOUD SHELL (are oci deja autentificat).
#  Idempotent: il mai rulezi o data = nu dubleaza nimic.
#  v2: foloseste VCN/subnet EXISTENTE (limita free 2 VCN e de regula ocupata)
#      si doar adauga portul 25565 pe security list.
# ============================================================
set -uo pipefail
S=~/cuantic-vm.state; touch "$S"
say(){ printf '\n\033[1;36m== %s\033[0m\n' "$*"; }
fail(){ printf '\033[1;31m!! %s\033[0m\n' "$*"; exit 1; }
get(){ grep -m1 "^$1=" "$S" | cut -d= -f2-; }
ociq(){ local jq="$1"; shift; oci "$@" --output json 2>/dev/null | jq -r "$jq" 2>/dev/null | grep -m1 -E '^oc' || true; }

say "0. verificari"
command -v oci >/dev/null || fail "Cloud Shell-ul e altundeva — redeschide-l din dreapta sus"
TEN="${TEN:-}"
if [ -z "$TEN" ]; then TEN=$(oci os ns get --query 'data.id' --raw-output 2>/dev/null | grep -m1 -E '^oc' || true); fi
if [ -z "$TEN" ]; then TEN=$(oci iam region-subscription list --output json 2>/dev/null | jq -r '.data[0].tenancy-id' 2>/dev/null | grep -m1 -E '^oc' || true); fi
[ -n "$TEN" ] || fail "oci n-autentificat in Cloud Shell — inchide si redeschide Cloud Shell, apoi ruleaza din nou"
echo "tenancy: $TEN"

say "1. retea: folosim ce exista, cream doar ce lipseste"
VCN=$(ociq '.data[0].id // empty' network vcn list --compartment-id "$TEN" --display-name cuantic-vcn)
if [ -z "$VCN" ]; then
  VCN=$(ociq '.data[0].id // empty' network vcn list --compartment-id "$TEN" --lifecycle-state AVAILABLE)
  [ -n "$VCN" ] && echo "VCN existent reutilizat: $VCN"
fi
if [ -z "$VCN" ]; then
  VCN=$(oci network vcn create --compartment-id "$TEN" --cidr-block 10.99.0.0/16 --display-name cuantic-vcn --query 'data.id' --raw-output 2>/dev/null) \
    || fail "niciun VCN de folosit si limita de creat e plina — in Console: Limits, Quotas and Usage -> 'vcn count' (cresterea e gratuita)"
fi
SUB=$(ociq '.data[0].id // empty' network subnet list --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-sub)
if [ -z "$SUB" ]; then
  SUB=$(ociq '.data[0].id // empty' network subnet list --compartment-id "$TEN" --vcn-id "$VCN" --lifecycle-state AVAILABLE)
  [ -n "$SUB" ] && echo "subnet existent reutilizat: $SUB"
fi
if [ -z "$SUB" ]; then
  CID=$(oci network vcn get --vcn-id "$VCN" --output json 2>/dev/null | jq -r '.data["cidr-blocks"][0] // "10.0.0.0/16"')
  BASE="${CID%/*}"; O1=${BASE%%.*}
  IGW=$(ociq '.data[0].id // empty' network internet-gateway list --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-igw)
  [ -n "$IGW" ] || IGW=$(oci network internet-gateway create --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-igw --is-enabled true --query 'data.id' --raw-output)
  RT=$(ociq '.data[0].id // empty' network route-table list --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-rt)
  [ -n "$RT" ] || RT=$(oci network route-table create --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-rt --route-rules "[{\"destination\":\"0.0.0.0/0\",\"destinationType\":\"CIDR_BLOCK\",\"networkEntityId\":\"$IGW\"}]" --query 'data.id' --raw-output)
  SL=$(ociq '.data[0].id // empty' network security-list list --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-sl)
  [ -n "$SL" ] || SL=$(oci network security-list create --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-sl \
    --ingress-rules '[{"source":"0.0.0.0/0","protocol":"6","description":"ssh+mc","tcpOptions":{"destinationPortRange":{"min":22,"max":25565}}}]' \
    --egress-rules '[{"destination":"0.0.0.0/0","protocol":"all"}]' --query 'data.id' --raw-output)
  SUB=$(oci network subnet create --compartment-id "$TEN" --vcn-id "$VCN" --cidr-block "$O1.254.0/24" --display-name cuantic-sub --route-table-id "$RT" --security-list-ids "[\"$SL\"]" --query 'data.id' --raw-output) \
    || fail "subnet create esuat ( vezi mai sus )"
fi

say "2. portul 25565 liber pe reteaua existenta (inca o data, ca siguranta)"
SLIDS=$(oci network subnet get --subnet-id "$SUB" --output json 2>/dev/null | jq -r '.data["security-list-ids"][]? // empty')
for SLID in $SLIDS; do
  HAVE=$(oci network security-list get --security-list-id "$SLID" --output json 2>/dev/null | jq -r '.data["ingress-security-rules"] // [] | .[] | (.["tcp-options"] // {}) | (.["destination-port-range"] // {}) | .min // empty' | grep -c "^25565$" || true)
  ALL=$(oci network security-list get --security-list-id "$SLID" --output json 2>/dev/null | jq -r '.data["ingress-security-rules"] // [] | .[] | (.source // "") ' | grep -c "0.0.0.0/0" || true)
  if [ "${HAVE:-0}" -gt 0 ]; then echo "regula 25565 existenta pe $SLID"
  elif [ "${ALL:-0}" -gt 0 ]; then echo "lista $SLID permite deja tot traficul — nu adaug nimic"
  else
    NEWJSON=$(oci network security-list get --security-list-id "$SLID" --output json | jq -c '(.data["ingress-security-rules"] // []) + [{"source":"0.0.0.0/0","protocol":"6","description":"minecraft-cuantic","tcpOptions":{"destinationPortRange":{"min":25565,"max":25565}}}]')
    oci network security-list update --security-list-id "$SLID" --ingress-rules "$NEWJSON" >/dev/null && echo "25565 adaugat pe $SLID"
  fi
done

say "3. cheia noastra de acces (ramane aici, in Cloud Shell)"
if [ ! -f ~/.ssh/cuantic_oci ]; then
  ssh-keygen -t ed25519 -f ~/.ssh/cuantic_oci -N "" -q -C "cuantic-deploy" 2>/dev/null || \
  ssh-keygen -t rsa -b 3072 -f ~/.ssh/cuantic_oci -N "" -q -C "cuantic-deploy"   # FIPS nu lasa ed25519 -> RSA
fi
PUB=$(cat ~/.ssh/cuantic_oci.pub 2>/dev/null) || true
[ -n "$PUB" ] || fail "cheia n-a putut fi generata — ruleaza din nou"

say "4. imagine Ubuntu ARM"
IMG=$(ociq '.data[0].id // empty' compute image list --compartment-id "$TEN" --operating-system "Canonical Ubuntu" --operating-system-version "24.04" --shape "VM.Standard.A1.Flex" --sort-by TIMECREATED --sort-order DESC)
[ -n "$IMG" ] || IMG=$(ociq '.data[0].id // empty' compute image list --compartment-id "$TEN" --operating-system "Canonical Ubuntu" --operating-system-version "22.04" --shape "VM.Standard.A1.Flex" --sort-by TIMECREATED --sort-order DESC)
[ -n "$IMG" ] || fail "nicio imagine Ubuntu ARM gasita"
AD=$(oci iam availability-domain list --compartment-id "$TEN" --query 'data[0].name' --raw-output)

say "5. pornim VM-ul 4 OCPU / 24 GB (Always Free = 0 lei)"
IID=$(ociq '.data[0].id // empty' compute instance list --compartment-id "$TEN" --display-name cuantic)
if [ -n "$IID" ]; then
  echo "VM existent, il folosim: $IID"
else
  OUT=$(oci compute instance launch --compartment-id "$TEN" --display-name cuantic \
    --availability-domain "$AD" --shape "VM.Standard.A1.Flex" \
    --shape-config '{"ocpus": 4, "memoryInGBs": 24}' \
    --image-id "$IMG" --subnet-id "$SUB" --assign-public-ip true \
    --boot-volume-size-in-gbs 200 \
    --metadata "{\"ssh_authorized_keys\":\"$PUB\"}" --output json 2>&1)
  IID=$(echo "$OUT" | jq -r '.data.id // empty' 2>/dev/null || true)
  if [ -z "$IID" ]; then
    echo "$OUT" | tail -6
    case "$OUT" in
      *[Cc]apacity*) fail "A1 fara capacitate acum in Frankfurt — lasa-l sa reincerce mai tarziu (rulezi ACELASI comanda) sau cere crestere de limita 'a1 standard' din Limits, Quotas and Usage" ;;
      *LimitExceeded*) fail "limita atinsa (a1-count/a1-ocpu/a1-memory sau vcn-count) — cere cresterea gratuita in Console, apoi aceeasi comanda" ;;
      *) fail "launch esuat — copiaza aici textul de mai sus ca sa-l citesc" ;;
    esac
  fi
  echo "IID=$IID" >> "$S"
fi

say "6. astept sa dea semne de viata (2-5 minute)"
oci compute instance wait --instance-id "$IID" --wait-attempt-interval 15 --max-wait-seconds 900 >/dev/null 2>&1 || true
VNIC=$(ociq '.data[0].vnic_id // empty' compute vnic-attachment list --compartment-id "$TEN" --instance-id "$IID")
IP=$(ociq '.data.publicIp // empty' network vnic get --vnic-id "$VNIC")
if [ -z "$IP" ]; then
  IP=$(oci network public-ip list --compartment-id "$TEN" --scope REGION --output json 2>/dev/null | jq -r --arg v "$IID" '.data[]? | select(.["assigned-instance-id"]==$v) | .ip_address' | grep -m1 -E '^[0-9]' || true)
fi
[ -n "$IP" ] || fail "nu prind IP-ul — ia-l din pagina instantei din Console si pune-l in secretul OCI_HOST tu"
echo "IP=$IP" >> "$S"

say "7. test SSH"
SSHOK=NU
for i in 1 2 3 4 5 6; do
  if ssh -i ~/.ssh/cuantic_oci -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "ubuntu@$IP" 'echo VIU' 2>/dev/null | grep -q VIU; then SSHOK=DA; break; fi
  sleep 15
done
[ "$SSHOK" = "DA" ] && echo "SSH: DA, ubuntu@$IP" || echo "SSH: inca nu raspunde (normal in primele minute) — reincearca mai tarziu acelasi test: ssh -i ~/.ssh/cuantic_oci ubuntu@$IP"

echo
printf '\033[1;33m╔══════════ GATA — acum 3 secrets pe GitHub ══════════╗\033[0m\n'
printf '║  Repo iZentric/ServerRolePlayLite -> Settings -> Secrets and\n'
printf '║  variables -> Actions -> New repository secret:\n'
printf '║\n'
printf '║   OCI_HOST  = %s\n' "$IP"
printf '║   OCI_USER  = ubuntu\n'
printf '║   OCI_SSH_KEY = cheia de mai jos, intreg (antet+subsols)\n'
printf '╚═════════════════════════════════════════════════════╝\n'
echo "----- copieaza TOT blocul urmator in secretul OCI_SSH_KEY (in browser, NU in chat) -----"
cat ~/.ssh/cuantic_oci
echo "----- gata. apoi spune-i agentului: gata"
