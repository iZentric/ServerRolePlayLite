#!/usr/bin/env python3
# CURATARE — sterge tot ce apucasem sa creez pentru varianta cu VM nou (nu mai folosim).
import oci, oci.core
L = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); L.append(s)
cfg = oci.config.from_file(); region = cfg.get("region", "eu-frankfurt-1"); ten = cfg["tenancy"]
core = oci.core.ComputeClient(config=cfg, region=region, verify=False)
net = oci.core.VirtualNetworkClient(config=cfg, region=region, verify=False)
n = 0
for i in core.list_instances(compartment_id=ten).data:
    if "cuantic" in (i.display_name or "").lower():
        say("TERMINET:", i.display_name, i.lifecycle_state)
        try:
            core.terminate_instance(i.id); n += 1
        except Exception as e:
            say("  esueaza:", str(e)[:200])
try:
    for p in net.list_public_ips(compartment_id=ten, reserved=True).data:
        if "cuantic" in (p.display_name or "").lower():
            say("ELIBEREZ IP:", p.public_ip)
            try:
                net.release_public_ip(p.id)
            except Exception as e:
                say("  ip esueaza:", str(e)[:150])
except Exception as e:
    say("list_public_ips:", str(e)[:150])
say("STERSE:", n)
open("/tmp/net.txt", "w").write("\n".join(L) + "\n")
