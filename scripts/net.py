#!/usr/bin/env python3
# NET — pe instanta din cont (iZen): IP public atasat + reguli 7000/25565 in security list.
import oci, oci.core, traceback
L = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); L.append(s)

cfg = oci.config.from_file(); cfg.setdefault("region", "eu-frankfurt-1")
ten = cfg["tenancy"]
def client(cls_name):
    last = None
    for mod in ("oci.core", "oci.network"):
        try:
            m = __import__(mod, fromlist=[cls_name])
            return getattr(m, cls_name)(config=cfg, region="eu-frankfurt-1", verify=False)
        except Exception as e:
            last = e
    say("client %s indisponibil: %s" % (cls_name, last)); return None

core = client("ComputeClient")
net = client("VirtualNetworkClient")
say("core:", bool(core), "net:", bool(net))
if not (core and net):
    open("/tmp/net.txt", "w").write("\n".join(L)); raise SystemExit(0)

PORTS = (7000, 25565)
insts = [i for i in core.list_instances(compartment_id=ten).data if i.lifecycle_state == "RUNNING"]
say("instante RUNNING:", ", ".join("%s/%s" % (i.display_name, i.shape) for i in insts) or "NICIUNEA")
tgt = None
for i in insts:
    if (i.display_name or "").lower() == "izen": tgt = i
tgt = tgt or (insts[0] if insts else None)
if tgt is None:
    open("/tmp/net.txt", "w").write("\n".join(L)); raise SystemExit(0)
say("tinta:", tgt.display_name, tgt.shape, tgt.id[-10:])

vnic = None
try:
    for a in core.list_vnic_attachments(compartment_id=tgt.compartment_id, instance_id=tgt.id).data:
        if a.lifecycle_state == "ATTACHED":
            vnic = net.get_vnic(a.vnic_id).data; break
except Exception:
    say("vnic attachments:", traceback.format_exc().splitlines()[-1])
if vnic is None:
    try:
        lv = net.list_vnics(compartment_id=tgt.compartment_id)
        for v in lv.data:
            say("  vnic gasit:", v.display_name, v.private_ip, v.public_ip)
            vnic = vnic or v
    except Exception as e:
        say("list_vnics esueaza:", str(e)[:300])
if vnic is None:
    say("NU AM VNIC"); open("/tmp/net.txt", "w").write("\n".join(L)); raise SystemExit(0)
say("vnic:", vnic.id[-10:], "privat:", vnic.private_ip, "public:", vnic.public_ip)

PUB = vnic.public_ip
if not PUB:
    made = False
    for det in ("CreatePublicIpCompartmentDetails", "CreatePublicIpDetails"):
        try:
            M = getattr(oci.core.models, det)
            d = M(compartment_id=tgt.compartment_id, allocated_resource_id=vnic.id, assigned_type="VNIC", display_name="cuantic-ip")
            p = net.create_public_ip(d).data
            say("IP creat:", p.public_ip)
            made = True
            break
        except Exception as e:
            say("  %s: %s" % (det, str(e)[:260]))
    try:
        PUB = net.get_vnic(vnic.id).data.public_ip
    except Exception:
        pass
    say("dupa creare, vnic.public_ip =", PUB or "inca NICIUNUL")
say("IP_PUBLIC=", PUB or "NICIUNUL")

try:
    sub = net.get_subnet(vnic.subnet_id).data
    vcn = sub.vcn_id
    sls = net.list_security_lists(compartment_id=tgt.compartment_id, vcn_id=vcn).data
    say("security lists in", vcn[-10:], ":", ", ".join(s.display_name for s in sls))
    for sl in sls:
        cur = net.get_security_list(sl.id).data
        ing = list(cur.ingress_security_rules or [])
        for port in PORTS:
            have = any((r.protocol == "6" and r.source == "0.0.0.0/0" and r.tcp_options and
                        (getattr(r.tcp_options.destination_port, "min", None) == port or r.tcp_options.destination_port == port)) for r in ing)
            if have:
                say("  %s: %d existent" % (sl.display_name, port)); continue
            try: pr = oci.core.models.PortRange(min=port, max=port)
            except Exception: pr = port
            ing.append(oci.core.models.IngressSecurityRule(protocol="6", source="0.0.0.0/0",
                     description="CUANTIC frp %d" % port, tcp_options=oci.core.models.TcpOptions(destination_port=pr)))
            try:
                net.update_security_list(sl.id, oci.core.models.UpdateSecurityListDetails(
                    ingress_security_rules=ing, egress_security_rules=list(cur.egress_security_rules or [])))
                cur = net.get_security_list(sl.id).data
                say("  %s: regula %d ADAUGATA" % (sl.display_name, port))
            except Exception as e:
                say("  %s: update esuat: %s" % (sl.display_name, str(e)[:260]))
except Exception:
    say("security list:", traceback.format_exc().splitlines()[-1])

say("GATA")
open("/tmp/net.txt", "w").write("\n".join(L) + "\n")
