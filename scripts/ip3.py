#!/usr/bin/env python3
# IP3 — pe VM-ul real: IP public atasat, regula 25565 in security list, probe SSH, deploy CUANTIC.
# Totul cu erori la vedere (fara 2>/dev/null), ca sa stii exact ce blocheaza.
import oci, oci.core, subprocess, time, json, traceback
L = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); L.append(s)

cfg = oci.config.from_file(); cfg.setdefault("region", "eu-frankfurt-1")
ten = cfg["tenancy"]; REG = "eu-frankfurt-1"
sign = oci.signer.Signer(ten, cfg)
core = oci.core.ComputeClient(config=cfg, signer=sign, region=REG, verify=False)
net = None
for cls_path in ("oci.core.VirtualNetworkClient", "oci.network.VirtualNetworkClient"):
    try:
        mod, cl = cls_path.rsplit(".", 1)
        if mod == "oci.network":
            import oci.network
        net = getattr(__import__(mod, fromlist=[cl]), cl)(config=cfg, signer=sign, region=REG, verify=False)
        say("client retea:", cls_path); break
    except Exception as e:
        say("  %s -> %s" % (cls_path, str(e)[:150]))
if net is None:
    say("FARA client de retea — nu pot atribui IP/modifica security list"); open("/tmp/ip3.txt","w").write("\n".join(L)); raise SystemExit(0)

insts = core.list_instances(compartment_id=ten, lifecycle_state="RUNNING").data
say("instante RUNNING:", ", ".join("%s(%s)" % (i.display_name, i.shape) for i in insts) or "NICIUNEA")
tgt = None
for i in insts:
    if (i.display_name or "").lower() == "izen": tgt = i
tgt = tgt or (insts[0] if insts else None)
if tgt is None:
    say("nimica de facut"); open("/tmp/ip3.txt","w").write("\n".join(L)); raise SystemExit(0)
say("tinta:", tgt.display_name, tgt.shape, tgt.id[-14:])

vnic = None
try:
    atts = core.list_vnic_attachments(compartment_id=tgt.compartment_id, instance_id=tgt.id).data
    for a in atts:
        if a.lifecycle_state == "ATTACHED":
            vnic = net.get_vnic(a.vnic_id).data; break
except Exception:
    say("vnic-attachment esuat:\n" + traceback.format_exc().splitlines()[-1])
if vnic is None:
    try:
        for v in net.list_vnics(compartment_id=ten).data:
            if v.display_name and tgt.display_name and tgt.display_name.lower() in (v.display_name or "").lower():
                vnic = v; break
        if vnic is None and net.list_vnics(compartment_id=ten).data:
            vnic = net.list_vnics(compartment_id=ten).data[0]
    except Exception:
        say("list_vnics esuat:\n" + traceback.format_exc().splitlines()[-1])
if vnic is None:
    say("NU GASesc VNIC"); open("/tmp/ip3.txt","w").write("\n".join(L)); raise SystemExit(0)
say("vnic:", vnic.id[-12:], "privat:", vnic.private_ip, "public:", vnic.public_ip, "subnet:", (vnic.subnet_id or "")[-12:])

PUB = vnic.public_ip
if not PUB:
    ok = False
    for det in ("CreatePublicIpCompartmentDetails", "CreatePublicIpDetails"):
        try:
            M = getattr(oci.core.models, det)
            try:
                d = M(compartment_id=tgt.compartment_id, allocated_resource_id=vnic.id, assigned_type="VNIC", display_name="cuantic-ip")
            except TypeError:
                d = M(compartment_id=tgt.compartment_id, allocated_resource_id=vnic.id, assigned_type="IP", display_name="cuantic-ip")
            p = net.create_public_ip(d).data
            say("IP creat prin", det, "->", p.public_ip)
            try:
                net.update_vnic(vnic.id, oci.core.models.UpdateVnicDetails(public_ip_id=p.id))
            except Exception as e:
                say("  update_vnic:", str(e)[:200])
            PUB = net.get_vnic(vnic.id).data.public_ip or p.public_ip
            ok = True
            break
        except Exception as e:
            say("  %s -> %s" % (det, str(e)[:260]))
    if not ok:
        say("NU POT creea IP public (vezi eroarea de mai sus)")
say("IP PUBLIC FINAL:", PUB or "NICIUNUL")

# ---------- security list ----------
if PUB:
    try:
        sub = net.get_subnet(vnic.subnet_id).data
        vcn = sub.vcn_id
        rules = net.list_security_lists(compartment_id=tgt.compartment_id, vcn_id=vcn).data
        for sl in rules:
            cur = net.get_security_list(sl.id).data
            ing = list(cur.ingress_security_rules or [])
            have = any((r.protocol == "6" and r.source == "0.0.0.0/0" and r.tcp_options and
                        (getattr(r.tcp_options.destination_port, "min", None) == 25565 or r.tcp_options.destination_port == 25565)) for r in ing)
            if have:
                say("SL", sl.display_name, ": regula 25565 exista"); continue
            pr = None
            try: pr = oci.core.models.PortRange(min=25565, max=25565)
            except Exception: pass
            ing.append(oci.core.models.IngressSecurityRule(protocol="6", source="0.0.0.0/0",
                     description="CUANTIC MC", tcp_options=oci.core.models.TcpOptions(destination_port=pr or 25565)))
            try:
                net.update_security_list(sl.id, oci.core.models.UpdateSecurityListDetails(
                    ingress_security_rules=ing, egress_security_rules=list(cur.egress_security_rules or [])))
                say("SL", sl.display_name, ": regula 25565 ADAUGATA")
            except Exception as e:
                say("SL", sl.display_name, "update esuat:", str(e)[:300])
    except Exception:
        say("security list:\n" + traceback.format_exc().splitlines()[-1])

# ---------- SSH ----------
KEY = "/home/" + subprocess.run(["id","-un"],capture_output=True,text=True).stdout.strip() + "/.ssh/cuantic_oci"
USER_OK = None
for U in ("opc", "ubuntu", "root", "oracle"):
    try:
        p = subprocess.run(["ssh","-i",KEY,"-o","StrictHostKeyChecking=no","-o","ConnectTimeout=12","-o","BatchMode=yes",
                            f"{U}@{PUB}", "echo OK; nproc; free -m | sed -n 2p; java -version 2>&1 | head -1; sudo -n true 2>/dev/null && echo SUDO-DA || echo SUDO-NU"],
                           capture_output=True, text=True, timeout=40)
        if p.returncode == 0 and p.stdout.startswith("OK"):
            USER_OK = U; say("ACCES SSH:", U, "\n" + p.stdout.strip()); break
        else:
            say("  %s@%s: %s" % (U, PUB, (p.stderr.strip() or p.stdout.strip() or "refuzat")[:160]))
    except Exception as e:
        say("  %s@%s: %r" % (U, PUB, e))

DEPLOY = r'''
set -x
mkdir -p ~/mc && cd ~/mc
URL=$(curl -fsS --max-time 30 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
[ -f CatServer-1.16.5-1d8d6313-server.jar ] || { curl -fsSL --retry 2 -o p.zip "$URL" && unzip -qo p.zip && rm -f p.zip; }
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties
echo 'eula=true' > eula.txt
MEM=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo); HEAP=$(( MEM>2600 ? 1024 : 640 ))
sed -i "1s/.*/-Xms256M/;2s/.*/-Xmx${HEAP}M/" unix_args.txt
J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1); [ -z "$J" ] && J=$(command -v java)
pkill -f 'unix_args' 2>/dev/null; sleep 2
setsid bash -c "cd $HOME/mc && exec tail -f /dev/null | $J @unix_args.txt >> run.log 2>&1" &
sleep 6; echo "sus: $(pgrep -c java) java, mem $(free -m | sed -n 2p)"
sudo -n iptables -I INPUT -p tcp --dport 25565 -j ACCEPT 2>/dev/null && echo iptables-ok || echo iptales-skip
'''
if USER_OK:
    open("/tmp/deploy.sh","w").write(DEPLOY)
    p = subprocess.run(["ssh","-i",KEY,"-o","StrictHostKeyChecking=no",f"{USER_OK}@{PUB}","bash -s"],
                       stdin=open("/tmp/deploy.sh"), capture_output=True, text=True, timeout=420)
    say("deploy:", (p.stdout or "")[-900:], "\n", (p.stderr or "")[-400:])
    for i in range(12):
        time.sleep(15)
        try:
            r = subprocess.run(["curl","-fsS","--max-time","25","https://api.mcsrvstat.us/3/%s:25565" % PUB],
                              capture_output=True, text=True, timeout=30).stdout
        except Exception as e:
            r = str(e)
        st = "online" in r and '"online":true' in r
        say("proba %d: %s" % (i+1, "ONLINE" if st else (r[:120] or "fara raspuns")))
        if st: break
    say("==> ADRESA:", "%s:25565" % PUB)
else:
    say("cheia noastra nu intra — IPul e gata dar serverul trebuie urcat cu cheia din panou")

open("/tmp/ip3.txt","w").write("\n".join(L) + "\n")
print("GATA")
