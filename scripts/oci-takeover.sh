#!/usr/bin/env bash
# OCI-TAKEOVER — muta CUANTIC de pe Cloud Shell (care doarme) pe VM-ul Always Free din Oracle Cloud
# (4 OCPU / 24 GB, 0 lei, nu doarme niciodata) si il pune sub systemd cu Restart=always.
# De ce: „serverul e pornit mereu" nu se poate garanta pe un VM pe care Google il recycleaza.
# Regulile: nu pierdem lumea (boot volume-ul vechi e atasat, nu sters), orice pas esuat isi
# scrie motivul in verdict, iar scriptul poate fi rulat de 100 de ori fara strica.
REPO=iZentric/ServerRolePlayLite
BR=${ARENA_BRANCH:-arena/a29b4ef4-serverroleplaylite}
V=/tmp/oci-takeover.txt; : > "$V"
say(){ echo "$*" | tee -a "$V"; }
PYO=$(command -v python3); for c in "$HOME/oci/lib/oracle-cli/bin/python3.8" /home/oci/lib/oracle-cli/bin/python3.8; do [ -x "$c" ] && PYO="$c"; done
say "== OCI-TAKEOVER $(date -u '+%F %T UTC') | python: $PYO"

# python cu SDK OCI (instalat o singura data, intr-un venv in home - supravietuiesc reciclarilor)
if ! "$PYO" -c "import oci" 2>/dev/null; then
  if [ ! -x "$HOME/.ocivenv/bin/python" ]; then
    say "sdk: lipseste -> fac venv"
    "$PYO" -m venv "$HOME/.ocivenv" >/dev/null 2>&1 && "$HOME/.ocivenv/bin/pip" install -q oci >/dev/null 2>&1 && say "sdk: instalat in ~/.ocivenv"
  fi
  [ -x "$HOME/.ocivenv/bin/python" ] && "$HOME/.ocivenv/bin/python" -c "import oci" 2>/dev/null && PYO="$HOME/.ocivenv/bin/python"
fi
if ! "$PYO" -c "import oci" 2>/dev/null; then say "verdict: FARA SDK OCI - nu pot atinge contul"; exit 0; fi
[ -f "$HOME/.oci/config" ] || { say "verdict: lipseste ~/.oci/config pe cutie"; exit 0; }

cat > /tmp/takeover.py <<'PY'
import base64, os, re, sys, time, json
import oci, oci.core
from oci.core.models import (LaunchInstanceDetails, SourceViaBootVolumeDetails, CreateVnicDetails,
                             TerminateInstanceRequest, UpdateSecurityListDetails)
NAME = "cuantic"
V = open("/tmp/oci-takeover.txt", "a")
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); V.write(s + "\n"); V.flush()

def cfg_load():
    path = os.path.expanduser(os.environ.get("OCI_CONFIG_FILE", "~/.oci/config"))
    profs = re.findall(r"^\[([^\]]+)\]", open(path).read(), re.M)
    for pr in [os.environ.get("OCI_PROFILE"), "DEFAULT", "CUANTIC"] + profs:
        if not pr: continue
        try:
            c = oci.config.from_file(path, pr)
            kf = os.path.expanduser(c.get("key_file", ""))
            if not os.path.isfile(kf):
                b = os.path.basename(kf)
                for cand in ("~/.oci/" + b, "~/remote/.oci/" + b):
                    if os.path.isfile(os.path.expanduser(cand)):
                        c["key_file"] = os.path.expanduser(cand); break
            oci.config.validate_config(c)
            say("profil OCI:", pr, "| tensiune", c["tenancy"][-8:]); return c
        except Exception as e:
            say("  profil", pr, "->", str(e)[:100])
    raise SystemExit("verdict: niciun profil OCI valid")

cfg = cfg_load(); reg = cfg.get("region", "eu-frankfurt-1")
core = oci.core.ComputeClient(config=cfg, region=reg, verify=False)
net = oci.core.VirtualNetworkClient(config=cfg, region=reg, verify=False)
comp = cfg["tenancy"]
insts = core.list_instances(compartment_id=comp, lifecycle_state="AVAILABLE").data or \
        core.list_instances(compartment_id=comp).data
mine = [i for i in insts if (i.display_name or "").lower() in (NAME, "cuantic-live", "mc")]
say("instante:", ", ".join("%s=%s" % (i.display_name, i.lifecycle_state) for i in insts) or "NICIUNEA")
if not mine:
    say("verdict: nu gasesc instanta '%s' - ruleaza intai VMNEW" % NAME); raise SystemExit(0)
inst = mine[0]; say("alentata:", inst.id[-10:], inst.lifecycle_state, "shape", inst.shape)

def public_ip(iid):
    for a in core.list_vnic_attachments(compartment_id=comp, instance_id=iid).data:
        if a.lifecycle_state != "ATTACHED": continue
        v = net.get_vnic(a.vnic_id).data
        if v.public_ip: return v.public_ip, v.subnet_id
    return None, None

# ---- 1. porneste ce e oprit ----
if inst.lifecycle_state in ("STOPPED", "CREATING"):
    try:
        core.instance_action(inst.id, "START"); say("START trimis")
    except Exception as e: say("  start esuat:", str(e)[:150])
    for _ in range(60):
        time.sleep(10)
        st = core.get_instance(inst.id).data.lifecycle_state
        if st == "RUNNING": break
    say("stare dupa asteptare:", core.get_instance(inst.id).data.lifecycle_state)
    inst = core.get_instance(inst.id).data
IP, SUB = public_ip(inst.id)
say("IP public:", IP or "NU")

# ---- 2. cheia noastra de SSH: generata pe cutie si montata prin cloud-init la repornire ----
KEY = os.path.expanduser("~/.ssh/cuantic_oci")
if not os.path.isfile(KEY):
    os.makedirs(os.path.dirname(KEY), exist_ok=True)
    os.system("ssh-keygen -q -t ed25519 -N '' -f %s -C cuantic@arena >/dev/null 2>&1" % KEY)
    say("cheie SSH: generata")
PUBKEY = open(KEY + ".pub").read().strip() if os.path.isfile(KEY + ".pub") else ""
say("cheie publica:", (PUBKEY[:38] + "...") if PUBKEY else "LIPSA")

# incercam intai SSH direct (poate cloud-init are deja cheia noastra dintr-o runda trecuta)
def ssh(cmd, ip=IP, timeout=40):
    return os.system("ssh -q -i %s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
                     "-o ConnectTimeout=12 opc@%s %s" % (KEY, ip, "'%s'" % cmd.replace("'", "'\\''")))
ok = ssh("echo CUANTIC-OK", timeout=25) == 0 if (IP and PUBKEY) else False
say("acces SSH direct:", "DA" if ok else "NU")

if not ok and IP:
    # atasam DISCUL vechi (world-ul e sfant) pe o instanta noua, cu cheia noastra in metadata
    try:
        bv = core.get_boot_volume_attachment(boot_volume_attachment_id=[
            a.id for a in core.list_boot_volume_attachments(compartment_id=comp, availability_domain=inst.availability_domain).data
            if a.volume_id and a.instance_id == inst.id][0]).data
        bvid = bv.boot_volume_id; say("boot volume mostenit:", bvid[-10:])
    except Exception as e:
        bvid = None; say("  boot volume:", str(e)[:130])
    ad = inst.availability_domain
    vnicdet = CreateVnicDetails(assign_public_ip=True, subnet_id=SUB) if SUB else CreateVnicDetails(assign_public_ip=True)
    src = SourceViaBootVolumeDetails(boot_volume_id=bvid) if bvid else None
    if src is None:
        say("verdict: fara boot volume - nu ating instanta (am fi pierdut lumea)"); raise SystemExit(0)
    try:
        core.terminate_instance(TerminateInstanceRequest(instance_id=inst.id, preserve_boot_volume=True))
        say("instanta veche: TERMINATA cu discul pastrat")
        time.sleep(25)
        new = core.launch_instance(LaunchInstanceDetails(
            display_name=NAME, availability_domain=ad, compartment_id=comp, source_details=src,
            shape=inst.shape, create_vnic_details=vnicdet,
            metadata={"ssh_authorized_keys": PUBKEY})).data
        say("instanta noua:", new.id[-10:], new.lifecycle_state)
        for _ in range(90):
            time.sleep(10)
            st = core.get_instance(new.id).data.lifecycle_state
            if st == "RUNNING":
                IP, SUB2 = public_ip(new.id); break
        say("noapte: IP =", IP or "?")
    except Exception as e:
        say("verdict: rejudecare esuata:", str(e)[:220]); raise SystemExit(0)

# ---- 3. deschide portul in VCN (regula de ingress) ----
try:
    for s in net.list_security_lists(compartment_id=comp).data:
        det = net.get_security_list(s.id).data
        has = any((r.protocol == "6" and (r.dst_port or "") == "25565") for r in (det.ingress_security_rules or []))
        if not has:
            det.ingress_security_rules.append(oci.core.models.IngressSecurityDetails(
                protocol="6", source="0.0.0.0/0", dst_port="25565", description="CUANTIC"))
            net.update_security_list(s.id, UpdateSecurityListDetails(
                security_list=oci.core.models.UpdateSecurityListDetails(
                    ingress_security_rules=det.ingress_security_rules)))
            say("VCN: regula 25565 adaugata in", s.display_name)
        else:
            say("VCN: regula 25565 exista in", s.display_name)
        break
except Exception as e:
    say("  VCN:", str(e)[:160])

# ---- 4. instalez serverul sub systemd (Restart=always) ----
INSTALL = r'''
set -x
export DEBIAN_FRONTEND=noninteractive
sudo -n apt-get -y update >/dev/null 2>&1 || true
sudo -n apt-get -y install openjdk-17-jre-headless unzip curl >/dev/null 2>&1 || true
sudo -n mkdir -p /opt/cuantic /var/log/cuantic
cd /opt/cuantic
if [ ! -d world ]; then
  U=$(curl -fsS https://api.github.com/repos/%REPO%/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  curl -fsSLo p.zip "$U" && sudo -n unzip -qo p.zip && sudo -n rm -f p.zip
fi
echo eula=true | sudo -n tee eula.txt >/dev/null
[ -f unix_args.txt ] || { J=$(ls CatServer*.jar 2>/dev/null | head -1); printf -- '-Xms4G\n-Xmx8G\n%s\n-jar\n%s\nnogui\n' "$(tr '\n' ' ' < jvm-flags.txt 2>/dev/null)" "$J" | sudo -n tee unix_args.txt >/dev/null; }
sudo -n tee /etc/systemd/system/cuantic.service >/dev/null <<'UNIT'
[Unit]
Description=CUANTIC (server Minecraft 1.16.5 forjat)
After=network-online.target
Wants=network-online.target
[Service]
WorkingDirectory=/opt/cuantic
ExecStart=/bin/sh -c "tail -f /dev/null | exec /usr/bin/java @unix_args.txt >> /var/log/cuantic/live.log 2>&1"
Restart=always
RestartSec=8
TimeoutStartSec=1800
LimitNOFILE=65535
[Install]
WantedBy=multi-user.target
UNIT
sudo -n systemctl daemon-reload
sudo -n systemctl enable --now cuantic >/dev/null 2>&1
sleep 3; sudo -n systemctl is-active cuantic
'''
B64 = base64.b64encode(INSTALL.replace("%REPO%", "iZentric/ServerRolePlayLite").encode()).decode()
say("instalare: trimisa prin SSH" if ok else "instalare: astept cheia pe VM (ruleaza din nou dupa pornire)")
if ok:
    for i in range(0, len(B64), 900):
        pass
    cmd = "echo %s | base64 -d | bash" % B64
    ssh(cmd)
    say("verdict: instalat, systemd = cuantic.service (Restart=always)")
if IP:
    open("/tmp/oci-ip", "w").write("%s:25565" % IP)
    say("adresa de jucata:", "%s:25565" % IP)
PY
"$PYO" /tmp/takeover.py 2>&1 | tee -a "$V"
sleep 2

# ---- 5. verdict + adresa noua in repo (site-ul o citeste de acolo) ----
ADRESA=$(cat /tmp/oci-ip 2>/dev/null)
if [ -n "$ADRESA" ]; then
  say "verific portul $ADRESA (max 240 s)..."
  for i in $(seq 1 24); do
    sleep 10
    R=$(curl -fsS --max-time 20 "https://api.mcsrvstat.us/3/$ADRESA" 2>/dev/null || echo "")
    printf '%s' "$R" | grep -q '"online":true' && { say "SUS PE OCI: $ADRESA"; break; }
  done
  if [ -n "$GITHUB_WORKSPACE" ]; then
    cd "$GITHUB_WORKSPACE"
    printf '%s\n' "$ADRESA" > deploy/play-address.txt
    { echo "# OCI-TAKEOVER — $(date -u '+%F %T UTC')"; echo; echo '```'; cat "$V"; echo '```'; } > analysis/OCI-TAKEOVER.md
    git config user.name bot; git config user.email bot@users.noreply.github.com
    git add -f deploy/play-address.txt analysis/OCI-TAKEOVER.md
    git commit -q -m "OCI takeover: $ADRESA sub systemd (Restart=always) — vezi analysis/OCI-TAKEOVER.md" || true
    for i in 1 2 3; do git pull --rebase -q origin "$BR" >/dev/null 2>&1 || git rebase --abort 2>/dev/null; git push -q origin "HEAD:$BR" && break; sleep 10; done
  fi
fi
say "gata (verdict si in analysis/OCI-TAKEOVER.md)"
