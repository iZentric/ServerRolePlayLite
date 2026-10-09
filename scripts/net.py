#!/usr/bin/env python3
# NET v2 — public IP atasat + porturi 7000/25565 deschise in Security List SI in NSG-urile VNIC-ului.
import oci, oci.core
L = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); L.append(s)

cfg = oci.config.from_file(); cfg.setdefault("region", "eu-frankfurt-1")
ten = cfg["tenancy"]
def cli(name):
    err = None
    for mod in ("oci.core", "oci.network"):
        try:
            m = __import__(mod, fromlist=[name])
            return getattr(m, name)(config=cfg, region="eu-frankfurt-1", verify=False)
        except Exception as e:
            err = e
    say("client", name, "indisponibil:", str(err)[:150]); return None

core = cli("ComputeClient"); net = cli("VirtualNetworkClient")
if not (core and net):
    open("/tmp/net.txt", "w").write("\n".join(L)); raise SystemExit(0)

insts = [i for i in core.list_instances(compartment_id=ten).data if i.lifecycle_state == "RUNNING"]
tgt = [i for i in insts if (i.display_name or "").lower() == "izen"] or insts
if not tgt:
    say("NICI O INSTANTA RUNNING"); open("/tmp/net.txt", "w").write("\n".join(L)); raise SystemExit(0)
t = tgt[0]; say("instanta:", t.display_name, t.shape)

vnic = None; nsgs = []
for a in core.list_vnic_attachments(compartment_id=t.compartment_id, instance_id=t.id).data:
    if a.lifecycle_state == "ATTACHED":
        vnic = net.get_vnic(a.vnic_id).data; nsgs = list(a.network_security_group_ids or []); break
if vnic is None:
    say("NU AM GASIT VNIC-UL"); open("/tmp/net.txt", "w").write("\n".join(L)); raise SystemExit(0)
say("vnic privat:", vnic.private_ip, "public:", vnic.public_ip or "NICIUNUL", "| NSG-uri:", len(nsgs))

if not vnic.public_ip:
    for det in ("CreatePublicIpCompartmentDetails", "CreatePublicIpDetails"):
        try:
            M = getattr(oci.core.models, det)
            d = M(compartment_id=t.compartment_id, allocated_resource_id=vnic.id, assigned_type="VNIC", display_name="cuantic-ip")
            p = net.create_public_ip(d).data; say("IP PUBLIC CREAT:", p.public_ip); break
        except Exception as e:
            say("   ", det, "->", str(e)[:170])

sub = net.get_subnet(vnic.subnet_id).data
sls = net.list_security_lists(compartment_id=t.compartment_id, vcn_id=sub.vcn_id).data

def has(ing, port):
    for r in ing:
        if str(r.protocol) != "6":
            continue
        if (r.source or "") != "0.0.0.0/0":
            continue
        to = getattr(r, "tcp_options", None)
        dp = getattr(to, "destination_port", None) if to else None
        mn = getattr(dp, "min", dp)
        try:
            if int(mn) == port:
                return True
        except Exception:
            pass
    return False

def port_range(p):
    try:
        return oci.core.models.PortRange(min=p, max=p)
    except Exception:
        return p

for sl in sls:
    cur = net.get_security_list(sl.id).data
    ing = list(cur.ingress_security_rules or [])
    add = [p for p in (7000, 25565) if not has(ing, p)]
    if not add:
        say("SL", sl.display_name, ": 7000+25565 DEJA DESCHISE"); continue
    for p in add:
        ing.append(oci.core.models.IngressSecurityRule(protocol="6", source="0.0.0.0/0",
                 description="CUANTIC %d" % p, tcp_options=oci.core.models.TcpOptions(destination_port=port_range(p))))
    try:
        net.update_security_list(sl.id, oci.core.models.UpdateSecurityListDetails(
            ingress_security_rules=ing, egress_security_rules=list(cur.egress_security_rules or [])))
        chk = net.get_security_list(sl.id).data
        say("SL", sl.display_name, ":", {p: has(list(chk.ingress_security_rules or []), p) for p in (7000, 25565)})
    except Exception as e:
        say("SL", sl.display_name, ": ESUEAZA ->", str(e)[:200])

for nsg_id in nsgs:
    cur = net.get_network_security_group(nsg_id).data
    ing = list(cur.ingress_security_rules or [])
    add = [p for p in (7000, 25565) if not has(ing, p)]
    if not add:
        say("NSG", cur.display_name, ": DEJA DESCHISE"); continue
    rules = []
    for p in add:
        try:
            rules.append(oci.core.models.IngressSecurityRuleForNetworkSecurity(protocol="6", source="0.0.0.0/0",
                        description="CUANTIC %d" % p, tcp_options=oci.core.models.TcpOptions(destination_port=port_range(p))))
        except Exception as e:
            say("   model NSG esueaza:", str(e)[:150])
    try:
        net.add_network_security_group_ingress_security_rules(nsg_id,
            oci.core.models.AddNetworkSecurityGroupIngressSecurityRulesDetails(ingress_security_rules=rules))
        say("NSG", cur.display_name, ": REGULI ADAUGATE", add)
    except Exception as e:
        say("NSG", cur.display_name, ": ESUEAZA ->", str(e)[:200])

say("VERDICT IP_PUBLIC=", net.get_vnic(vnic.id).data.public_ip or "NICIUNUL")
open("/tmp/net.txt", "w").write("\n".join(L) + "\n")
