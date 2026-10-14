"""Guard OCI image selection and launch payload construction without cloud credentials."""
import base64
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import vmnew  # noqa: E402


class FakeCompute:
    def __init__(self):
        self.calls = []

    def list_images(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs["operating_system"] == "Canonical Ubuntu" and kwargs["operating_system_version"] == "24.04":
            return SimpleNamespace(data=[])
        return SimpleNamespace(data=[SimpleNamespace(
            id="image-arm-id", display_name="Ubuntu 22.04 ARM", lifecycle_state="AVAILABLE"
        )])


class Model:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeModels:
    LaunchInstanceDetails = Model
    LaunchInstanceShapeConfigDetails = Model
    CreateVnicDetails = Model
    InstanceSourceViaImageDetails = Model


class VMNewTests(unittest.TestCase):
    def test_image_lookup_uses_compute_api_and_filters_for_a1_shape(self):
        compute = FakeCompute()
        image = vmnew.find_ubuntu_image(compute, "tenancy-id")
        self.assertEqual(image.id, "image-arm-id")
        self.assertEqual(len(compute.calls), 2)
        self.assertEqual(compute.calls[0]["shape"], "VM.Standard.A1.Flex")
        self.assertEqual(compute.calls[1]["operating_system"], "Ubuntu")
        self.assertEqual(compute.calls[1]["operating_system_version"], "24.04")

    def test_launch_uses_supported_oci_model_names_and_public_vnic(self):
        subnet = SimpleNamespace(id="subnet-id")
        image = SimpleNamespace(id="image-id")
        details = vmnew.make_launch_details(
            FakeModels, "compartment-id", "AD-1", subnet, image, "base64-user-data"
        )
        self.assertEqual(details.kwargs["shape"], "VM.Standard.A1.Flex")
        self.assertEqual(details.kwargs["source_details"].kwargs,
                         {"source_type": "image", "image_id": "image-id"})
        self.assertEqual(details.kwargs["create_vnic_details"].kwargs,
                         {"subnet_id": "subnet-id", "assign_public_ip": True})
        self.assertEqual(details.kwargs["shape_config"].kwargs,
                         {"ocpus": 4, "memory_in_gbs": 24})

    def test_cloud_init_references_the_pushed_branch_and_is_base64_encoded(self):
        encoded, url = vmnew.make_user_data("arena/test-branch")
        content = base64.b64decode(encoded).decode("utf-8")
        self.assertIn("arena/test-branch/scripts/cuantic-vm.sh", url)
        self.assertIn(url, content)
        self.assertIn("#cloud-config", content)

    def test_subnet_that_disallows_public_addresses_is_rejected(self):
        self.assertFalse(vmnew.public_subnet(SimpleNamespace(
            lifecycle_state="AVAILABLE", prohibit_public_ip_on_vnic=True
        )))
        self.assertTrue(vmnew.public_subnet(SimpleNamespace(
            lifecycle_state="AVAILABLE", prohibit_public_ip_on_vnic=False
        )))


if __name__ == "__main__":
    unittest.main()
