#!/usr/bin/env bash
# FIN2 — trei lucruri deodata:
#  A) listener TCP brut pe 25565 ca sa stim DACA mai intra cineva din internet in gazda;
#  B) regula de ingress 25565 in security list (OCI CLI + jq, ca SDK-ul vechi n-are oci.network);
#  C) de ce zice MC "Done" dar nu leaga portul (eroarea reala de bind).
LOG=/tmp/fin2.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
TEN=ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa
IPV=132.145.236.16
say "== FIN2 — $(date -u '+%F %T UTC') =="

# ---------- A) listener brut ----------
python3 - <<'PY' > /tmp/listen.log 2>&1 &
import socket, threading
srv=socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    srv.bind(("0.0.0.0",25565)); srv.listen(16); print("BIND-OK")
except Exception as e:
    print("BIND-ESUAT", e); raise SystemExit(0)
def h(c):
    try:
        c.sendall(b"CUANTIC-LISTEN-TEST\n"); c.close()
    except Exception: pass
while True:
    try:
        c,_=srv.accept(); h(c)
    except Exception: break
PY
LPID=$!
sleep 3
LP=$(cat /tmp/listen.log 2>/dev/null)
say "listener brut: ${LP:-NU}"

# ---------- B) regula in VCN ----------
VNIC=$(oci network vnic list --compartment-id "$TEN" --output json 2>/dev/null | jq -r '.data[] | select(.["private-ip"]=="10.215.108.231") | .id' | head -1)
[ -z "$VNIC" ] && VNIC=$(oci network vnic list --compartment-id "$TEN" --output json 2>/dev/null | jq -r '.data[0].id' | head -1)
say "vnic tinta: ${VNIC:-NICIUNUL}"
if [ -n "$VNIC" ]; then
  oci network vnic get --vnic-id "$VNIC" --output json 2>/dev/null | jq -r '"  ip public: \(.data["public-ip"] // "NICIUNUL (NAT doar de iesire)")\n  subnet: \(.data["subnet-id"])\n  security lists: \(.data["security-list-ids"]|join(","))"' | tee -a $LOG
  for SL in $(oci network vnic get --vnic-id "$VNIC" --output json 2>/dev/null | jq -r '.data["security-list-ids"][]'); do
    CUR=$(oci network security-list get --security-list-id "$SL" --output json 2>/dev/null)
    HAS=$(echo "$CUR" | jq -r '[.data["ingress-security-rules"][]? | select(.protocol=="6" and .["source"]=="0.0.0.0/0" and .tcp_options.destination_port.min==25565)] | length')
    say "  SL ${SL: -12}: regula 25565 prezenta=$HAS"
    if [ "$HAS" = "0" ]; then
      NEW=$(echo "$CUR" | jq -c '.data["ingress-security-rules"] + [{protocol:"6",source:"0.0.0.0/0",description:"CUANTIC MC",tcp_options:{destination_port:{min:25565,max:25565}}}]')
      EGG=$(echo "$CUR" | jq -c '.data["egress-security-rules"]')
      oci network security-list update --security-list-id "$SL" --ingress-security-rules "$NEW" --egress-security-rules "$EGG" 2>&1 | tail -2 | sed 's/^/    /' >> $LOG
      say "    regula ADAUGATA pe ${SL: -12}"
    fi
  done
fi

# ---------- proba externa pe listener ----------
say "probe external pe listener (2 incercari):"
for i in 1 2; do
  R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/$IPV:25565" 2>/dev/null)
  say "  $i: $(echo "$R" | grep -oE '\"message\":\"[^\"]+\"' | head -1) online=$(echo "$R" | grep -oE '\"online\":(true|false)')"
  sleep 6
done
say "  (timeout = paclit de retea/firewall; refused ori 'read from socket' = a ajuns la listener, deci intrarea e OK)"
kill $LPID 2>/dev/null; sleep 2
say "listener oprit: $(pgrep -fc python3) python3 ramasi"

# ---------- C) de ce nu leaga MC ----------
pkill -f 'java @unix_args' 2>/dev/null; sleep 2
cd $DIR
[ -e cin ] && [ ! -p cin ] && rm -f cin; [ -p cin ] || mkfifo cin
setsid nohup tail -f /dev/null > $DIR/cin &
setsid nohup "$J17" @unix_args.txt < $DIR/cin > $DIR/live.log 2>&1 &
for i in $(seq 1 70); do grep -qE 'Done \(|Failed to bind' $DIR/live.log 2>/dev/null && break; sleep 3; done
say "boot: $(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log) | bind: $(grep -m1 -iE 'Starting Minecraft server on|Failed to bind' $DIR/live.log)"
say "dupa Done (12 linii):"; grep -A12 -m1 'Done (' $DIR/live.log 2>/dev/null | sed 's/^/  /' | cut -c1-150 >> $LOG
say "ss:"; ss -lnt 2>/dev/null | sed -n '1,8p' | sed 's/^/  /' >> $LOG
python3 -c "
import socket
try:
    s=socket.create_connection(('127.0.0.1',25565),timeout=6); print('  MC asculta local: DA'); s.close()
except Exception as e:
    print('  MC asculta local: NU', e)
" 2>&1 | tee -a $LOG

mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
F=analysis/fin2.md
printf '# CUANTIC FIN2 — %s\n```\n' "$(date -u '+%F %T UTC')" > $F
cat $LOG >> $F
printf '```\n' >> $F
git add -f analysis/fin2.md; git commit -q -m "fin2: listener test + regula VCN + eroare bind MC" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0
