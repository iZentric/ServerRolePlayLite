#!/usr/bin/env bash
# FIN — un singu r lucru: serverul CUANTIC sus pe gazda noastra + portul 25565 DESCHIS
# in reteaua Oracle (security list, prin API) + mentinere prin cron (cronul nu moare la final de job).
LOG=/tmp/fin.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
IPV=132.145.236.16
say "== FIN — $(date -u '+%F %T UTC') =="

cd $DIR 2>/dev/null || { say "fara $DIR"; exit 1; }
echo "eula=true" > eula.txt
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties

# ---------- 1. server ----------
pkill -f 'java @unix_args' 2>/dev/null; sleep 2
[ -e cin ] && [ ! -p cin ] && rm -f cin
[ -p cin ] || mkfifo cin
setsid nohup tail -f /dev/null > $DIR/cin &
setsid nohup "$J17" @unix_args.txt < $DIR/cin > $DIR/live.log 2>&1 &
DONE=""
for i in $(seq 1 80); do DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null); [ -n "$DONE" ] && break; sleep 3; done
say "boot: ${DONE:-NU}"
python3 -c "
import socket
try:
    s=socket.create_connection(('127.0.0.1',25565),timeout=6); print('  port local: DESCHIS'); s.close()
except Exception as e:
    print('  port local: REFUZAT', e)
" 2>&1 | tee -a $LOG

# ---------- 2. cron keepalive (supravietuieste jobului) ----------
CRON=NU
pgrep -x crond >/dev/null 2>&1 && CRON=DA
pgrep -x cron >/dev/null 2>&1 && CRON=DA
cat > $DIR/keep.sh <<EOS
#!/usr/bin/env bash
[ -f $DIR/STOP ] && exit 0
cd $DIR || exit 0
pgrep -f 'java @unix_args' >/dev/null && exit 0
[ -p cin ] || mkfifo cin 2>/dev/null
setsid nohup tail -f /dev/null > $DIR/cin &
setsid nohup $J17 @unix_args.txt < $DIR/cin >> $DIR/live.log 2>&1 &
EOS
if [ "$CRON" = "DA" ]; then
  ( crontab -l 2>/dev/null | grep -v 'cuantic-live/keep.sh' ; echo "* * * * * /bin/bash $DIR/keep.sh" ) | crontab - 2>/dev/null \
    && say "cron inarmat (serverul e repornit in max 1 min daca pica)" || say "crontab refuza"
else
  say "crond NU ruleaza pe gazda — serverul traieste cat jobul"
fi

# ---------- 3. port 25565 deschis in VCN (API) ----------
PYPY=$(head -1 "$(which oci)" 2>/dev/null | sed 's/^#!//' | tr -d '\r')
[ -x "$PYPY" ] || PYPY=python3
say "python OCI: $PYPY"
"$PYPY" - <<'PY' 2>&1 | tee -a $LOG
import sys
try:
    import oci, oci.core, oci.network
except Exception as e:
    print("SDK indisponibil:", e); sys.exit(0)
cfg = oci.config.from_file(); cfg.setdefault("region","eu-frankfurt-1")
core = oci.core.ComputeClient(config=cfg, signer=oci.signer.Signer(cfg["tenancy"], cfg), region="eu-frankfurt-1", verify=False)
net  = oci.network.VirtualNetworkClient(config=cfg, signer=oci.signer.Signer(cfg["tenancy"], cfg), region="eu-frankfurt-1", verify=False)
ten = cfg["tenancy"]
target=None; first=None
for it in core.list_instances(compartment_id=ten).data:
    if it.lifecycle_state != "RUNNING": continue
    for a in core.list_vnic_attachments(compartment_id=it.compartment_id, instance_id=it.id).data:
        if a.lifecycle_state != "ATTACHED": continue
        v = net.get_vnic(a.vnic_id).data
        first=v
        print("VNIC:", it.display_name, v.private_ip, "public:", v.public_ip, "NSG:", v.nsg_ids, "SL:", v.security_list_ids)
        if v.private_ip and v.private_ip.startswith("10.215"): target=v
if target is None:
    target = first
    print("niciun VNIC cu 10.215.x — folosesc:", target.private_ip if target else "NICIUNUL")
rule = oci.core.models.IngressSecurityRule(protocol="6",
        source="0.0.0.0/0", description="CUANTIC Minecraft",
        tcp_options=oci.core.models.TcpOptions(destination_port=oci.core.models.PortRange(min=25565, max=25565)))
for sl_id in target.security_list_ids:
    sl = net.get_security_list(security_list_id=sl_id).data
    ing = list(sl.ingress_security_rules or [])
    have = any((r.protocol=="6" and r.source=="0.0.0.0/0" and r.tcp_options and getattr(r.tcp_options.destination_port,'min',None)==25565) for r in ing)
    print(("  regula existenta pe " if have else "  ADAUG pe ")+sl_id[-14:])
    if not have:
        ing.append(rule)
        net.update_security_list(security_list_id=sl_id,
            update_security_list_details=oci.core.models.UpdateSecurityListDetails(
                ingress_security_rules=ing, egress_security_rules=list(sl.egress_security_rules or [])))
        print("  security list actualizata")
PY

# ---------- 4. proba din internet ----------
sleep 20
A=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/$IPV:25565" 2>/dev/null)
B=$(curl -fsS --max-time 25 "https://api.mcstatus.io/v2/status/java/$IPV:25565" 2>/dev/null)
say "mcsrvstat: $(echo "$A" | grep -oE '\"online\":(true|false)')"
say "mcstatus:  $(echo "$B" | grep -oE '\"online\":(true|false)')"
ON=NU; case "$A$B" in *'"online":true'*) ON=DA;; esac
say "==> JUCABIL PE $IPV:25565: $ON"
{ echo "Adresa de joc: $IPV:25565"; echo "Online: $ON"; echo "Boot: ${DONE:-NU}"; } > $DIR/ADRESA

mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
F=analysis/fin.md
printf '# CUANTIC FIN — %s\n```\n' "$(date -u '+%F %T UTC')" > $F
cat $LOG >> $F
printf '```\n' >> $F
git add -f analysis/fin.md; git commit -q -m "fin: $IPV:25565 online=$ON" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0
