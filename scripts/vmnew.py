#!/usr/bin/env python3
"""Create or verify the CUANTIC Oracle A1 VM using the runner's OCI profile.

The OCI SDK is available on the self-hosted runner, not necessarily on a local
checkout. All exits write a machine-readable verdict to /tmp/vmverdict and a
human-readable log to /tmp/vm.txt for the workflow to archive.
"""
import base64
import json
import os
import re
import time

NAME = "cuantic"
SHAPE = "VM.Standard.A1.Flex"
OCPUS = 4
MEMORY_GB = 24
UBUNTU_IMAGES = (
    ("Canonical Ubuntu", "24.04"),
    ("Ubuntu", "24.04"),
    ("Canonical Ubuntu", "22.04"),
    ("Ubuntu", "22.04"),
)

LOG = []


def say(*items):
    line = " ".join(str(item) for item in items)
    print(line, flush=True)
    LOG.append(line)


def finish(verdict):
    """Persist both the detailed run log and a short workflow/commit verdict."""
    os.makedirs("/tmp", exist_ok=True)
    with open("/tmp/vm.txt", "w", encoding="utf-8") as report:
        report.write("\n".join(LOG) + "\n")
        report.write(verdict + "\n")
    with open("/tmp/vmverdict", "w", encoding="utf-8") as report:
        report.write(verdict + "\n")
    say(verdict)


def load_cfg(oci):
    """Find the first usable OCI profile, including keys copied from remote/.oci."""
    path = os.path.expanduser(os.environ.get("OCI_CONFIG_FILE", "~/.oci/config"))
    try:
        with open(path, encoding="utf-8") as config_file:
            profiles = re.findall(r"^\[([^\]]+)\]", config_file.read(), re.M)
    except Exception as exc:
        raise RuntimeError("nu pot citi config OCI: " + str(exc)[:120]) from exc

    requested = [os.environ.get("OCI_PROFILE"), "DEFAULT", "CUANTIC"] + profiles
    tried = set()
    for profile in requested:
        if not profile or profile in tried:
            continue
        tried.add(profile)
        try:
            config = oci.config.from_file(path, profile)
            key_file = os.path.expanduser(config.get("key_file", ""))
            if not os.path.isfile(key_file):
                key_name = os.path.basename(key_file)
                for candidate in ("~/.oci/" + key_name, "~/remote/.oci/" + key_name):
                    candidate = os.path.expanduser(candidate)
                    if os.path.isfile(candidate):
                        config["key_file"] = candidate
                        break
            oci.config.validate_config(config)
            say("profil OCI:", profile, "| cheie:", os.path.basename(config.get("key_file", "?")))
            return config
        except Exception as exc:
            say("profil", profile, "->", str(exc)[:100])
    raise RuntimeError("niciun profil OCI valid in " + path)


def find_ubuntu_image(compute, compartment_id):
    """Find an available Ubuntu ARM image compatible with the A1 Flex shape."""
    for operating_system, version in UBUNTU_IMAGES:
        try:
            images = compute.list_images(
                compartment_id=compartment_id,
                operating_system=operating_system,
                operating_system_version=version,
                shape=SHAPE,
            ).data or []
        except Exception as exc:
            say("imagini", operating_system, version, "->", str(exc)[:130])
            continue
        available = [image for image in images
                     if getattr(image, "lifecycle_state", "AVAILABLE") == "AVAILABLE"]
        if available:
            return available[0]
    return None


def public_subnet(subnet):
    return (getattr(subnet, "lifecycle_state", "AVAILABLE") == "AVAILABLE"
            and not getattr(subnet, "prohibit_public_ip_on_vnic", False))


def choose_subnet(compute, network, tenancy_id, instances):
    """Prefer a public subnet used by an existing running VM; otherwise use one in tenancy."""
    for instance in instances:
        if instance.lifecycle_state != "RUNNING":
            continue
        try:
            attachments = compute.list_vnic_attachments(
                compartment_id=instance.compartment_id,
                instance_id=instance.id,
            ).data or []
            for attachment in attachments:
                if attachment.lifecycle_state != "ATTACHED":
                    continue
                vnic = network.get_vnic(attachment.vnic_id).data
                subnet = network.get_subnet(vnic.subnet_id).data
                if public_subnet(subnet):
                    say("subnet mostenit de la", instance.display_name,
                        "->", subnet.id[-10:], "vcn", subnet.vcn_id[-10:])
                    return instance.compartment_id, subnet
                say("subnet de la", instance.display_name, "nu permite IP public")
        except Exception as exc:
            say("inspectare subnet", getattr(instance, "display_name", "?"), "->", str(exc)[:130])

    try:
        subnets = network.list_subnets(compartment_id=tenancy_id).data or []
    except Exception as exc:
        raise RuntimeError("nu pot lista subneturile: " + str(exc)[:140]) from exc
    available = [subnet for subnet in subnets if public_subnet(subnet)]
    if not available:
        raise RuntimeError("nu exista subnet disponibil care sa permita IP public")
    subnet = available[0]
    say("subnet tenancy ->", subnet.id[-10:], "vcn", subnet.vcn_id[-10:])
    return tenancy_id, subnet


def public_ip_for(compute, network, instance):
    """Return the first attached public IP, if one has been assigned."""
    try:
        attachments = compute.list_vnic_attachments(
            compartment_id=instance.compartment_id,
            instance_id=instance.id,
        ).data or []
        for attachment in attachments:
            if attachment.lifecycle_state != "ATTACHED":
                continue
            vnic = network.get_vnic(attachment.vnic_id).data
            if vnic.public_ip:
                return vnic.public_ip
    except Exception as exc:
        say("citire IP public ->", str(exc)[:130])
    return None


def make_user_data(branch):
    """Build cloud-init data that fetches the matching committed installer."""
    branch = branch or "arena/a29b4ef4-serverroleplaylite"
    script_url = ("https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/"
                  + branch + "/scripts/cuantic-vm.sh")
    command = "curl -fsSLo /tmp/i.sh " + script_url + " && bash /tmp/i.sh"
    cloud_config = "#cloud-config\nruncmd:\n - [bash, -c, " + json.dumps(command) + "]\n"
    return base64.b64encode(cloud_config.encode("utf-8")).decode("ascii"), script_url


def make_launch_details(models, compartment_id, availability_domain, subnet, image, user_data):
    """Build a current OCI SDK launch request (image, shape, and public VNIC)."""
    return models.LaunchInstanceDetails(
        display_name=NAME,
        availability_domain=availability_domain,
        compartment_id=compartment_id,
        shape=SHAPE,
        shape_config=models.LaunchInstanceShapeConfigDetails(
            ocpus=OCPUS,
            memory_in_gbs=MEMORY_GB,
        ),
        create_vnic_details=models.CreateVnicDetails(
            subnet_id=subnet.id,
            assign_public_ip=True,
        ),
        source_details=models.InstanceSourceViaImageDetails(
            source_type="image",
            image_id=image.id,
        ),
        metadata={"user_data": user_data},
    )


def run(oci=None):
    global LOG
    LOG = []
    try:
        if oci is None:
            import oci as oci_sdk
            oci = oci_sdk
        config = load_cfg(oci)
        region = config.get("region") or "eu-frankfurt-1"
        tenancy_id = config["tenancy"]
        say("regiune OCI:", region)

        # Keep normal TLS certificate verification enabled for signed OCI requests.
        compute = oci.core.ComputeClient(config=config, region=region)
        network = oci.core.VirtualNetworkClient(config=config, region=region)
        identity = oci.identity.IdentityClient(config=config, region=region)
        instances = compute.list_instances(compartment_id=tenancy_id).data or []
        say("instante:", ", ".join(
            "%s(%s,%s)" % (instance.display_name, instance.lifecycle_state, instance.shape)
            for instance in instances
        ) or "NICIUNEA")

        existing = [instance for instance in instances
                    if (instance.display_name or "").lower() in (NAME, "cuantic-live", "mc")]
        if existing:
            instance = sorted(existing, key=lambda item: (item.display_name.lower() != NAME,
                                                           item.lifecycle_state != "RUNNING"))[0]
            ip = public_ip_for(compute, network, instance) or "fara IP public"
            say("EXISTA:", instance.id[-12:], "stare:", instance.lifecycle_state,
                "shape:", instance.shape, "IP:", ip)
            finish("VM: EXISTĂ id=%s stare=%s shape=%s ip=%s" %
                   (instance.id[-12:], instance.lifecycle_state, instance.shape, ip))
            return 0

        compartment_id, subnet = choose_subnet(compute, network, tenancy_id, instances)
        availability_domains = identity.list_availability_domains(
            compartment_id=compartment_id
        ).data or []
        if not availability_domains:
            raise RuntimeError("compartimentul nu are availability domain disponibil")

        # The VM installer uses apt-get; do not silently fall back to an incompatible OS.
        image = find_ubuntu_image(compute, compartment_id)
        if image is None:
            raise RuntimeError("nu am gasit imagine Ubuntu ARM disponibila pentru " + SHAPE)
        say("imagine:", image.display_name, "| OCID:", image.id[-12:])

        branch = (os.environ.get("GITHUB_REF_NAME") or os.environ.get("ARENA_BRANCH")
                  or "arena/a29b4ef4-serverroleplaylite")
        user_data, script_url = make_user_data(branch)
        say("cloud-init:", script_url)
        launch = make_launch_details(
            oci.core.models,
            compartment_id,
            availability_domains[0].name,
            subnet,
            image,
            user_data,
        )
        created = compute.launch_instance(launch).data
        say("CREATA:", created.id[-12:], created.lifecycle_state, "shape:", created.shape)

        # Report the actual state and assigned IP, rather than treating an accepted
        # launch request as proof that a VM is already usable.
        instance = created
        for attempt in range(40):  # at most ten minutes; the workflow has a 20-minute limit
            if instance.lifecycle_state not in ("PROVISIONING", "STARTING"):
                break
            time.sleep(15)
            instance = compute.get_instance(created.id).data
            say("stare VM:", instance.lifecycle_state)
        ip = public_ip_for(compute, network, instance) or "fara IP public"
        verdict = "VM: CREATĂ id=%s stare=%s shape=%s ip=%s" % (
            instance.id[-12:], instance.lifecycle_state, instance.shape, ip
        )
        finish(verdict)
        return 0
    except Exception as exc:
        message = (str(exc).replace("\n", " ") or exc.__class__.__name__)[:180]
        say("eroare:", message)
        finish("VM: EȘUAT - " + message)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
