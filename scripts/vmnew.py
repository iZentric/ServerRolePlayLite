#!/usr/bin/env python3
# VMNEW — creeaza VM.Standard.A1.Flex (4 ocpu / 24 GB, Always Free) cu serverul CUANTIC prin cloud-init.
import oci, oci.core, base64, os, re
L = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); L.append(s)
def fin(verdict):
    open("/tmp/vm.txt", "w").write("\n".join(L) + "\n")
    open("/tmp/vmverdict", "w").write(verdict + "\n")

def load_cfg():
    """Profilul nu e mereu DEFAULT: cautam orice profil functionala (DEFAULT, CUANTIC, altii)."""
    path = os.path.expanduser(os.environ.get("OCI_CONFIG_FILE", "~/.oci/config"))
    try:
        profs = re.findall(r"^\[([^\]]+)\]", open(path).read(), re.M)
    except Exception as e:
        say("verdict: citire config esuata:", str(e)[:120]); raise SystemExit(0)
    for pr in [os.environ.get("OCI_PROFILE"), "DEFAULT", "CUANTIC"] + profs:
        if not pr:
            continue
        try:
            c = oci.config.from_file(path, pr)
            kf = os.path.expanduser(c.get("key_file", ""))
            if not os.path.isfile(kf):
                base = os.path.basename(kf)
                for cand in ("~/.oci/" + base, "~/remote/.oci/" + base):
                    if os.path.isfile(os.path.expanduser(cand)):
                        c["key_file"] = os.path.expanduser(cand); break
            oci.config.validate_config(c)
            say("profil OCI:", pr, "| cheie:", os.path.basename(c.get("key_file", "?")))
            return c
        except Exception as e:
            say("  profil", pr, "->", str(e)[:90])
    say("verdict: NICIUN profil OCI valid in", path); raise SystemExit(0)

cfg = load_cfg(); region = cfg.get("region", "eu-frankfurt-1"); ten = cfg["tenancy"]
core = oci.core.ComputeClient(config=cfg, region=region, verify=False)
net = oci.core.VirtualNetworkClient(config=cfg, region=region, verify=False)
M = oci.core.models
NAME = "cuantic"

insts = core.list_instances(compartment_id=ten).data
say("instante:", ", ".join("%s(%s)" % (i.display_name, i.lifecycle_state) for i in insts) or "NICIUNEA")
ex = [i for i in insts if (i.display_name or "").lower() == NAME]
if ex:
    say("EXISTA:", ex[0].id[-10:], ex[0].lifecycle_state)
    fin("VM: exista %s (%s)" % (ex[0].id[-10:], ex[0].lifecycle_state)); raise SystemExit(0)

comp = ten; sub = None
for i in [x for x in insts if x.lifecycle_state == "RUNNING"]:
    try:
        for a in core.list_vnic_attachments(compartment_id=i.compartment_id, instance_id=i.id).data:
            if a.lifecycle_state == "ATTACHED":
                v = net.get_vnic(a.vnic_id).data
                sub = net.get_subnet(v.subnet_id).data
                comp = i.compartment_id
                say("subnet mostenit de la", i.display_name, "->", sub.id[-10:], "vcn", sub.vcn_id[-10:])
                break
    except Exception as e:
        say("  vnic", str(e)[:120])
    if sub: break
if sub is None:
    try:
        r = net.list_subnets(compartment_id=ten).data
        sub = r[0] if r else None
        say("fallback subnet:", sub.id[-10:] if sub else "NICIUNUL")
    except Exception as e:
        say("subnets esueaza:", str(e)[:150])
if sub is None:
    fin("VM: ESUAT - fara subnet"); raise SystemExit(0)

PUB = None
for det in ("CreatePublicIpCompartmentDetails", "CreatePublicIpDetails"):
    try:
        PUB = net.create_public_ip(getattr(M, det)(compartment_id=comp, reserved=True, display_name="cuantic-ip")).data.public_ip
        say("IP REZERVAT:", PUB); break
    except Exception as e:
        say("  ip", det, str(e)[:140])

img = None
for osn, ver in (("Ubuntu", "24.04"), ("Ubuntu", "22.04"), ("Oracle Linux", "9"), ("Oracle Linux", "8")):
    try:
        r = net.list_images(compartment_id=comp, operating_system=osn, operating_system_version=ver).data
        c = [x for x in r if "aarch64" in (x.display_name or "")] or list(r)
        if c:
            img = c[0]; break
    except Exception as e:
        say("  images", ver, str(e)[:110])
say("imagine:", (img.display_name if img else "NICIUNEA") or "NICIUNEA")
if img is None:
    fin("VM: ESUAT - fara imagine ARM"); raise SystemExit(0)

SCRIPT = "https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts/cuantic-vm.sh"
cloud = ("#cloud-config\nruncmd:\n - [bash, -c, 'curl -fsSLo /tmp/i.sh %s; bash /tmp/i.sh']\n" % SCRIPT).encode()
ad = core.list_availability_domains(compartment_id=comp).data[0].name

vnic = None
for kw in (({"subnet_id": sub.id, "public_ip": PUB} if PUB else {"subnet_id": sub.id, "assign_public_ip": True}),
           {"subnet_id": sub.id, "assign_public_ip": True}):
    try:
        vnic = M.CreateVnicDetails(**kw); break
    except Exception as e:
        say("  vnic details", list(kw), str(e)[:120])

launch = None
for sc in ("LaunchInstanceShapeConfigDetails", "LaunchFlexInstanceShapeDetails"):
    try:
        launch = M.LaunchInstanceDetails(display_name=NAME, availability_domain=ad, compartment_id=comp,
                                         create_vnic_details=vnic, shape="VM.Standard.A1.Flex",
                                         shape_config=getattr(M, sc)(ocpus=4, memory_in_gbs=24),
                                         source_details=M.SourceViaDetails(source_type="image", source_id=img.id),
                                         metadata={"user_data": base64.b64encode(cloud).decode()})
        say("shape_config prin", sc); break
    except Exception as e:
        say("  ", sc, str(e)[:160])

try:
    data = core.launch_instance(launch).data
    say("CREATA:", data.id, data.lifecycle_state)
    fin("VM: CREATA %s ip=%s stare=%s" % (data.id[-12:], PUB or "ephemerala", data.lifecycle_state))
except Exception as e:
    m = str(e)[:300]
    say("ESUAT launch:", m)
    fin("VM: ESUAT - " + ("OUT_OF_CAPACITY" if "capacity" in m.lower() else m[:120]))
