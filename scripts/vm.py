#!/usr/bin/env python3
# VM — creeaza A1.Flex cu serverul CUANTIC (cloud-init), IP public rezervat, si raporteaza.
import oci, oci.core, base64, time, traceback
L = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); L.append(s)
def rep():
    open("/tmp/vm.txt", "w").write("\n".join(L) + "\n")

cfg = oci.config.from_file(); region = cfg.get("region", "eu-frankfurt-1"); ten = cfg["tenancy"]
def cli(name):
    err = None
    for mod in ("oci.core", "oci.network"):
        try:
            return getattr(__import__(mod, fromlist=[name]), name)(config=cfg, region=region, verify=False)
        except Exception as e:
            err = e
    say("client", name, "esueaza:", str(err)[:200]); return None
core = cli("ComputeClient"); net = cli("VirtualNetworkClient")
M = oci.core.models
if not (core and net): rep(); raise SystemExit(0)

NAME = "cuantic-server"
SCRIPT = "https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts/cuantic-vm.sh"
cloud = ("#cloud-config\nruncmd:\n - [bash, -c, 'curl -fsSLo /tmp/i.sh %s; bash /tmp/i.sh >/var/log/cuantic-install.log 2>&1']\n" % SCRIPT).encode()
ud = base64.b64encode(cloud).decode()

# tintim subnetul VPS-ului existent (ACELASI VCN => porturile deja deschise de mine)
sub = None; comp = ten
for i in core.list_instances(compartment_id=ten).data:
    if i.lifecycle_state != "RUNNING":
        continue
    for a in core.list_vnic_attachments(compartment_id=i.compartment_id, instance_id=i.id).data:
        if a.lifecycle_state == "ATTACHED":
            v = net.get_vnic(a.vnic_id).data
            sub = net.get_subnet(v.subnet_id).data
            comp = i.compartment_id
            say("folosesc subnetul din", i.display_name, "->", sub.id[-10:])
            break
    if sub: break
if sub is None:
    s = net.list_subnets(compartment_id=ten).data
    sub = s[0] if s else None
    say("fallback subnet:", sub.id[-10:] if sub else "NICIUNUL")
if sub is None: say("FARA SUBNET"); rep(); raise SystemExit(0)

# imaginea Ubuntu ARM64 cea mai noua
img = None
for osname, ver in (("Ubuntu", "24.04"), ("Ubuntu", "22.04"), ("Oracle Linux", "8")):
    try:
        r = net.list_images(compartment_id=ten, operating_system=osname, operating_system_version=ver)
        cand = [x for x in r.data if "aarch64" in (x.display_name or "")] or list(r.data)
        if cand:
            img = cand[0]; break
    except Exception as e:
        say("images", ver, "->", str(e)[:150])
say("imagine:", img.display_name if img else "NICIUNEA")
if img is None: rep(); raise SystemExit(0)

# IP public rezervat (adresa fixa)
PUB = None
for det in ("CreatePublicIpCompartmentDetails", "CreatePublicIpDetails"):
    try:
        C = getattr(M, det)
        PUB = net.create_public_ip(C(compartment_id=comp, reserved=True, display_name="cuantic-ip")).data.public_ip
        say("IP REZERVAT:", PUB); break
    except Exception as e:
        say("  ", det, "->", str(e)[:180])

ad = None
try:
    ad = core.list_availability_domains(compartment_id=comp).data[0].name
except Exception as e:
    say("AD:", str(e)[:150])

vn = None
for kw in ({"subnet_id": sub.id, "public_ip": PUB} if PUB else {"subnet_id": sub.id, "assign_public_ip": True},
           {"subnet_id": sub.id, "assign_public_ip": True}):
    try:
        vn = M.CreateVnicDetails(**kw); break
    except Exception as e:
        say("  vnic details", list(kw), "->", str(e)[:150])
say("shape:", "VM.Standard.A1.Flex 4cpu/24GB")

launch = None
for sc in ("LaunchInstanceShapeConfigDetails", "LaunchFlexInstanceShapeDetails"):
    try:
        shape_conf = getattr(M, sc)(ocpus=4, memory_in_gbs=24)
        launch = M.LaunchInstanceDetails(display_name=NAME, availability_domain=ad, compartment_id=comp,
                                         create_vnic_details=vn, image_id=img.id, shape="VM.Standard.A1.Flex",
                                         shape_config=shape_conf, source_details=M.SourceViaDetails(source_type="image", source_id=img.id))
        say("am folosit", sc); break
    except Exception as e:
        say("  ", sc, "->", str(e)[:200])
if launch is None: rep(); raise SystemExit(0)

inst = None
try:
    inst = core.launch_instance(launch).data
    say("INSTANTA CREATA:", inst.id)
except Exception as e:
    say("launch esueaza:", str(e)[:500])
    try:
        launch.shape_config = None
        inst = core.launch_instance(launch).data
        say("CREATA fallback (shape fix):", inst.id)
    except Exception as e2:
        say("si fallback esueaza:", str(e2)[:400])
if inst is None: rep(); raise SystemExit(0)

st = None
for i in range(26):
    time.sleep(5)
    try:
        st = core.get_instance(inst.id).data.lifecycle_state
    except Exception:
        pass
    if st == "RUNNING": break
say("stare dupa ~", i * 5, "s:", st)
pub = None
for i in range(12):
    try:
        for a in core.list_vnic_attachments(compartment_id=comp, instance_id=inst.id).data:
            if a.lifecycle_state == "ATTACHED":
                v = net.get_vnic(a.vnic_id).data
                pub = v.public_ip
                say("vnic:", v.private_ip, "->", pub or "fara public")
                break
    except Exception:
        pass
    if pub: break
    time.sleep(5)
say("PUBLIC=", pub or (PUB or "NICIUNUL"))
say("GATA")
rep()
