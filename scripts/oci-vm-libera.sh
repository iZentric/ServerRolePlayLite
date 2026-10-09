#!/usr/bin/env bash
# ============================================================
#  CUANTIC — ridica singur VM-ul ARM Gratuit in Oracle Cloud
#  Ruleaza in CLOUD SHELL (are oci deja autentificat).
#  Idempotent: il mai rulezi o data = nu dubleaza nimic.
# ============================================================
set -uo pipefail
S=~/cuantic-vm.state; touch "$S"
say(){ printf '\n\033[1;36m== %s\033[0m\n' "$*"; }
fail(){ printf '\033[1;31m!! %s\033[0m\n' "$*"; exit 1; }
get(){ grep -m1 "^$1=" "$S" | cut -d= -f2-; }
put(){ grep -v "^$1=" "$S" > "$S.tmp" 2>/dev/null; echo "$1=$2" >> "$S.tmp"; mv "$S.tmp" "$S"; }
# interogare sigura: scoate doar ocid-uri, gol daca nu exista
ociq(){ local jq="$1"; shift; oci "$@" --output json 2>/dev/null | jq -r "$jq" 2>/dev/null | grep -m1 -E '^oc' || true; }

say "0. verificari"
command -v oci >/dev/null || fail "Prea frumos — abandoneaza Cloud Shell-ul din dreapta sus si redeschide-l"
# pe tenancy nou `os ns get` inca nu are namespace -> incercam 3 surse
TEN="${TEN:-}"
if [ -z "$TEN" ]; then TEN=$(oci os ns get --query 'data.id' --raw-output 2>/dev/null | grep -m1 -E '^oc' || true); fi
if [ -z "$TEN" ]; then TEN=$(oci iam region subscription list --output json 2>/dev/null | jq -r '.data[0].tenancyId' 2>/dev/null | grep -m1 -E '^oc' || true); fi
if [ -z "$TEN" ]; then TEN=$(oci iam region-subscription list --output json 2>/dev/null | jq -r '.data[0].tenancy-id' 2>/dev/null | grep -m1 -E '^oc' || true); fi
[ -n "$TEN" ] || fail "oci n-autentificat in Cloud Shell — inchide si redeschide Cloud Shell, apoi ruleaza din nou"
echo "tenancy: $TEN"

say "1. retea (VCN + gateway + subnet + porturi 22/25565) — se face o singura data"
VCN=$(ociq '.data[0].id // empty' network vcn list --compartment-id "$TEN" --display-name cuantic-vcn)
[ -n "$VCN" ] || VCN=$(oci network vcn create --compartment-id "$TEN" --cidr-block 10.0.0.0/16 --display-name cuantic-vcn --query 'data.id' --raw-output) || fail "vcn create"
IGW=$(ociq '.data[0].id // empty' network internet-gateway list --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-igw)
[ -n "$IGW" ] || IGW=$(oci network internet-gateway create --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-igw --is-enabled true --query 'data.id' --raw-output)
RT=$(ociq '.data[0].id // empty' network route-table list --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-rt)
[ -n "$RT" ] || RT=$(oci network route-table create --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-rt --route-rules "[{\"destination\":\"0.0.0.0/0\",\"destinationType\":\"CIDR_BLOCK\",\"networkEntityId\":\"$IGW\"}]" --query 'data.id' --raw-output)
SL=$(ociq '.data[0].id // empty' network security-list list --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-sl)
[ -n "$SL" ] || SL=$(oci network security-list create --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-sl \
  --ingress-rules '[{"source":"0.0.0.0/0","protocol":"6","description":"ssh","tcpOptions":{"destinationPortRange":{"min":22,"max":22}}},{"source":"0.0.0.0/0","protocol":"6","description":"minecraft","tcpOptions":{"destinationPortRange":{"min":25565,"max":25565}}}]' \
  --egress-rules '[{"destination":"0.0.0.0/0","protocol":"all","description":"out"}]' --query 'data.id' --raw-output)
SUB=$(ociq '.data[0].id // empty' network subnet list --compartment-id "$TEN" --vcn-id "$VCN" --display-name cuantic-sub)
[ -n "$SUB" ] || SUB=$(oci network subnet create --compartment-id "$TEN" --vcn-id "$VCN" --cidr-block 10.0.1.0/24 --display-name cuantic-sub --route-table-id "$RT" --security-list-ids "[\"$SL\"]" --query 'data.id' --raw-output)
echo "subnet: $SUB"

say "2. cheia noastra de acces (generata aici, in Cloud Shell — nu trece prin chat)"
[ -f ~/.ssh/cuantic_oci ] || ssh-keygen -t ed25519 -f ~/.ssh/cuantic_oci -N "" -q -C "cuantic-deploy"
PUB=$(cat ~/.ssh/cuantic_oci.pub)

say "3. imagine Ubuntu 24.04 ARM (cu fallback la 22.04)"
IMG=$(ociq '.data[0].id // empty' compute image list --compartment-id "$TEN" --operating-system "Canonical Ubuntu" --operating-system-version "24.04" --shape "VM.Standard.A1.Flex" --sort-by TIMECREATED --sort-order DESC)
[ -n "$IMG" ] || IMG=$(ociq '.data[0].id // empty' compute image list --compartment-id "$TEN" --operating-system "Canonical Ubuntu" --operating-system-version "22.04" --shape "VM.Standard.A1.Flex" --sort-by TIMECREATED --sort-order DESC)
[ -n "$IMG" ] || fail "nicio imagine Ubuntu ARM gasita"
AD=$(oci iam availability-domain list --compartment-id "$TEN" --query 'data[0].name' --raw-output)

say "4. porneste VM-ul 4 OCPU / 24 GB (Always Free — platesti 0)"
IID=$(ociq '.data[0].id // empty' compute instance list --compartment-id "$TEN" --display-name cuantic)
if [ -n "$IID" ]; then
  echo "exista deja: $IID"
else
  OUT=$(oci compute instance launch --compartment-id "$TEN" --display-name cuantic \
    --availability-domain "$AD" --shape "VM.Standard.A1.Flex" \
    --shape-config '{"ocpus": 4, "memoryInGBs": 24}' \
    --image "$IMG" --subnet-id "$SUB" --assign-public-ip true \
    --boot-volume-size-in-gbs 200 \
    --metadata "{\"ssh_authorized_keys\":\"$PUB\"}" --output json 2>&1)
  IID=$(echo "$OUT" | jq -r '.data.id // empty' 2>/dev/null || true)
  if [ -z "$IID" ]; then
    echo "$OUT" | tail -5
    case "$OUT" in
      *[Cc]apacity*|*LimitExceeded*|*limit*)
        fail "A1 fara locatie/limita — în Console: Limits, Quotas and Usage -> cauta 'a1 standard' -> ceruta crestere (gratuit, adesea instant) si ruleaza din nou scriptul" ;;
      *) fail "launch esuat ( vezi mai sus ) — ruleaza din nou dupa ce repari" ;;
    esac
  fi
  put IID "$IID"
fi

say "5. astept sa dea semne de viata (2-4 minute)"
oci compute instance wait --instance-id "$IID" --wait-attempt-interval 15 --max-wait-seconds 600 >/dev/null 2>&1 || true
VNIC=$(ociq '.data[0].vnic_id // empty' compute vnic-attachment list --compartment-id "$TEN" --instance-id "$IID")
IP=$(ociq '.data.publicIp // empty' network vnic get --vnic-id "$VNIC")
[ -n "$IP" ] || fail "nu prind IP-ul public — il iei din pagina instantei din Console si il pui singur in OCI_HOST"
put IP "$IP"

say "6. test ca intra prin SSH"
for i in 1 2 3 4 5 6; do
  if ssh -i ~/.ssh/cuantic_oci -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "ubuntu@$IP" 'echo VIU' 2>/dev/null | grep -q VIU; then SSHOK=DA; break; fi
  sleep 15
done
[ "${SSHOK:-NU}" = "DA" ] && echo "SSH: DA, ubuntu@$IP" || echo "SSH: inca nu raspunde (normal in primul minut) — mai incearca: ssh -i ~/.ssh/cuantic_oci ubuntu@$IP"

echo
printf '\033[1;33m╔══════════════ GATA — acum 3 secrets pe GitHub ══════════════╗\033[0m\n'
printf '║  Repo iZentric/ServerRolePlayLite -> Settings -> Secrets and\n'
printf '║  variables -> Actions -> New repository secret:\n'
printf '║\n'
printf '║   OCI_HOST  = %s\n' "$IP"
printf '║   OCI_USER  = ubuntu\n'
printf '║   OCI_SSH_KEY = cheia de mai jos, cu TOT antet/subsol:\n'
printf '╚══════════════════════════════════════════════════════════════╝\n'
echo "----- copiez TOT blocul de mai jos in secretul OCI_SSH_KEY (in browser, NU in chat) -----"
cat ~/.ssh/cuantic_oci
echo "----- (asta e cheia privata; tu o pui in GitHub, eu nu o vad)"
echo
echo "Dupa ce salvezi cele 3 secrets: spune-i agentului „gata” si el împinge tot restul (Java, pachet CUANTIC 1.5.8, systemd, masuratori)."
