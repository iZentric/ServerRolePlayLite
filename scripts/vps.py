#!/usr/bin/env python3
# VPS-LIVE: gaseste orice instanta din tenancy (toate regiunile/compartmentele),
# porneste ce e STOPPED, ataseaza IP public instantelor RUNNING, testeaza SSH.
# Nimic distructiv: doar START + asignare IP + citire.
import traceback, subprocess, os

out = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)

def dump():
    open("/tmp/vps.txt", "w").write("\n".join(out) + "\n")

try:
    import oci
except Exception:
    log("FARA SDK OCI:", traceback.format_exc()); dump(); raise SystemExit(0)

try:
    config = oci.config.from_file()
except Exception:
    log("CONFIG OCI FAIL:", traceback.format_exc()); dump(); raise SystemExit(0)

ten = config.get("tenancy")
HOME_REGION = config.get("region") or "eu-frankfurt-1"
config.setdefault("region", HOME_REGION)
log("tenancy:", ten[:60], "| home region:", HOME_REGION)

def sign(cls, region):
    try:
        return cls(config=config, signer=oci.signer.Signer(ten, config), region=region, verify=False)
    except Exception:
        return cls(config=config, region=region, verify=False)

# --- regiuni abonate ---
regions = []
try:
    idc = sign(oci.identity.IdentityClient, HOME_REGION)
    r = idc.list_regions(compartment_id=ten)
    regions = [x.region_name for x in r.data]
except Exception:
    log("list_regions esuat:", traceback.format_exc().splitlines()[-1])
if not regions:
    regions = [HOME_REGION]
regions = [rr for rr in dict.fromkeys(regions)]
log("regiuni luate la verificat:", ", ".join(regions))

# --- compartimente ---
comps = [ten]
try:
    idc = sign(oci.identity.IdentityClient, HOME_REGION)
    cc = idc.list_compartments(compartment_id=ten, access_level="ACCESSED", compartment_id_in_subtree=True)
    comps += [c.id for c in cc.data if c.lifecycle_state == "ACTIVE"]
except Exception:
    log("list_compartments:", traceback.format_exc().splitlines()[-1])
log("compartimente:", len(comps))

insts = []
for rr in regions:
    for cid in comps:
        try:
            cc = sign(oci.core.ComputeClient, rr)
            for it in cc.list_instances(compartment_id=cid).data:
                insts.append((rr, it))
        except Exception as e:
            log(f"  list_instances {rr}/{cid[:25]}..: {str(e)[:120]}")

log(f"\n=== INSTANTE GASITE: {len(insts)} ===")
for rr, it in insts:
    log(f"- {it.display_name} | {it.lifecycle_state} | {it.shape} | region {rr} | ad {it.availability_domain} | {it.id}")

stopped = [(rr, it) for rr, it in insts if it.lifecycle_state == "STOPPED"]
if stopped:
    log(f"\n=== PORNESC {len(stopped)} INSTANTE OPRITE ===")
    for rr, it in stopped:
        try:
            cc = sign(oci.core.ComputeClient, rr)
            cc.instance_action(instance_id=it.id, action="START")
            log(f"  START trimis pentru {it.display_name} ({it.id[:40]}..)")
        except Exception as e:
            log(f"  START ESUAT {it.display_name}: {str(e)[:400]}")
else:
    log("\n(nici o instanta oprita — nu am ce porni)")

# --- IP-uri publice ---
results = []
for rr, it in insts:
    if it.lifecycle_state not in ("RUNNING", "STARTING", "STOPPED"):
        continue
    try:
        vnc = sign(oci.network.VirtualNetworkClient, rr)
        cc = sign(oci.core.ComputeClient, rr)
        atts = cc.list_vnic_attachments(compartment_id=it.compartment_id, instance_id=it.id).data
        att = [a for a in atts if a.lifecycle_state == "ATTACHED"]
        if not att:
            log(f"\n{it.display_name}: niciun VNIC atasat"); continue
        vnic = vnc.get_vnic(att[0].vnic_id).data
        pub = vnic.public_ip
        log(f"\n{it.display_name} [{it.lifecycle_state}] privat={vnic.private_ip} public={'DA: ' + pub if pub else 'NIMIC'}")
        if not pub and it.lifecycle_state == "RUNNING":
            # incearca IP rezervat (gratuit pe free tier, 1 per VNIC)
            try:
                pip = vnc.create_public_ip(
                    oci.core.models.CreatePublicIpCompartmentDetails(
                        compartment_id=it.compartment_id,
                        assigned_type="IP",
                        display_name="cuantic-ip"))
                pid = pip.data.id
                log(f"  IP rezervat creat: {pip.data.public_ip}")
                vnc.update_vnic(vnic_id=vnic.id, update_vnic_details=oci.core.models.UpdateVnicDetails(public_ip_id=pid))
                vnic2 = vnc.get_vnic(vnic.id).data
                pub = vnic2.public_ip
                log(f"  atasat pe VNIC -> IP PUBLIC: {pub}")
            except Exception as e:
                pub = None
                log(f"  IP public nu se poate atasa: {str(e)[:400]}")
        results.append((it.display_name, it.id, rr, pub, vnic.private_ip, it.shape))
    except Exception:
        log(f"\n{it.display_name}: probe esuata\n{traceback.format_exc()}")

# --- SSH probe ---
log("\n=== SSH ===")
KEY = os.path.expanduser("~/.ssh/cuantic_oci")
CMD = ("hostname; nproc; free -m | sed -n 2p; df -h / | sed -n 2p; uptime; "
       "java -version 2>&1 | head -1; "
       "echo --- java-proc:; pgrep -af java | head -5; "
       "echo --- porturi:; ss -lntp 2>/dev/null | head -14; "
       "echo --- dir:; ls -d ~/*/ 2>/dev/null | head -10; "
       "echo --- jaruri:; find /home /root /opt /srv -maxdepth 3 -name *.jar 2>/dev/null | head -12; "
       "echo --- sudo:; sudo -n true 2>/dev/null && echo SUDO-DA || echo SUDO-NU")

for name, iid, rr, pub, priv, shape in results:
    if not pub:
        log(f"{name}: fara IP public, nu testez SSH"); continue
    got = False
    for u in ("opc", "ubuntu", "oracle", "cloud-user", "admin", "root"):
        try:
            p = subprocess.run(["ssh", "-i", KEY, "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
                                "-o", "BatchMode=yes", "-p", "22", f"{u}@{pub}", CMD],
                              capture_output=True, text=True, timeout=40)
            if p.returncode == 0 and p.stdout.strip():
                got = True
                log(f"--- ACCES DA: {u}@{pub} ({name} / {shape})\n{p.stdout.strip()}")
                if p.stderr.strip():
                    log("  (stderr: %s)" % p.stderr.strip()[:200])
                break
        except Exception as e:
            log(f"  {u}@{pub}: {type(e).__name__} {str(e)[:120]}")
    if not got:
        log(f"--- {name} ({pub}): cheia noastra NU intra (instanta creata cu alta cheie)")

log("\n=== PE SCURT ===")
for name, iid, rr, pub, priv, shape in results:
    log(f"{name} | {shape} | {rr} | public: {pub or 'NIMIC'} | privat: {priv}")
log("DONE")
dump()
print("GATA")
