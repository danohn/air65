"""Protect rotor semantics, zero-angle geometry and the existing static export."""
import copy
import json
from pathlib import Path
import struct
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from export_web_model import (
    check_numeric_pitch, compare_static_glb, component_primitives,
    load_motion_authority, motion_role, read_glb, triangle_fingerprint,
    validate_motion_glb,
)


@pytest.fixture
def authority():
    return load_motion_authority(ROOT / "specs/studio/motion.json")


def test_rotation_membership_follows_part_identity_not_material(authority):
    # These stationary pieces share purple/steel materials with the rotor.
    for part in ("lower_mount_center", "mount_ear_1", "mount_web_2", "exposed_lower_stator_neck", "inner_stator_core", "mount_screw_shank_1", "copper_winding_01", "upper_bushing"):
        assert motion_role("motor", "motor_FL." + part, authority) == "stator"
    for part in authority["parts"]:
        assert motion_role("motor", "motor_FL." + part, authority) == "rotor"


def test_propeller_blur_partition_keeps_socket_and_hub(authority):
    for i in range(1, 4):
        assert motion_role("prop_cw", f"prop_FL.blade_{i}", authority) == "blades"
    for part in ("outer_hub_barrel", "center_shaft_socket", "hub_radial_web_1", "hub_radial_web_2", "hub_radial_web_3"):
        assert motion_role("prop_cw", "prop_FL." + part, authority) == "hub"
    assert motion_role("motor", "motor_FL.silver_bell", None) is None


def test_motion_authority_rejects_duplicate_rotor_members(tmp_path):
    document = json.loads((ROOT / "specs/studio/motion.json").read_text())
    document["motion"]["rotating_motor_parts"][-1] = document["motion"]["rotating_motor_parts"][0]
    path = tmp_path / "motion.json"
    path.write_text(json.dumps(document))
    with pytest.raises(ValueError, match="unique"):
        load_motion_authority(path)


def test_motion_authority_rejects_inverted_adjacent_corners(tmp_path):
    document = json.loads((ROOT / "specs/studio/motion.json").read_text())
    document["motion"]["sign_by_corner"]["FR"] = 1
    path = tmp_path / "motion.json"
    path.write_text(json.dumps(document))
    with pytest.raises(ValueError, match="numeric blade pitch"):
        load_motion_authority(path)


def pitch_fixture(authority):
    specification = {"assembly": {"instances": []}, "components": {}}
    for corner, sign in authority["signs"].items():
        name = "pitch_" + corner
        specification["assembly"]["instances"].append({"id": "prop_" + corner, "component": name})
        specification["components"][name] = {"nodes": [{"id": f"blade_{i}", "op": "propeller_blade", "args": {"handedness": sign, "sections": [{"twist_deg": 13.5}]}} for i in range(1, 4)]}
    return specification


def test_direction_is_verified_from_blade_pitch_not_cw_filenames(authority):
    specification = pitch_fixture(authority)
    assert len(check_numeric_pitch(specification, authority)) == 4
    specification["components"]["pitch_FL"]["nodes"][0]["args"]["handedness"] *= -1
    with pytest.raises(ValueError, match="numeric blade pitch"):
        check_numeric_pitch(specification, authority)


def test_triangle_identity_ignores_start_index_but_retains_winding_and_material():
    keys = [struct.pack("<6f", x, y, 0, 0, 0, 1) for x, y in ((0, 0), (1, 0), (0, 1))]
    assert triangle_fingerprint("steel", keys) == triangle_fingerprint("steel", keys[1:] + keys[:1])
    assert triangle_fingerprint("steel", keys) != triangle_fingerprint("steel", list(reversed(keys)))
    assert triangle_fingerprint("steel", keys) != triangle_fingerprint("motor_purple", keys)


def test_child_pivot_cannot_shift_the_zero_angle_geometry():
    gltf = {"nodes": [{"name": "motor_FL", "translation": [-.02298, 0, -.02298], "children": [1]}, {"name": "motor_FL_rotor", "translation": [0, .001, 0], "mesh": 0}], "meshes": [{"primitives": [{}]}]}
    with pytest.raises(ValueError, match="changes static geometry"):
        list(component_primitives(gltf, 0))


@pytest.fixture
def exported():
    directory = ROOT / "output/web_motion"
    if not (directory / "model-metadata.json").exists():
        pytest.skip("Run the headless motion export to populate integration artifacts")
    return directory, json.loads((directory / "model-metadata.json").read_text())


def test_generated_rotor_and_stator_semantics(exported, authority):
    directory, metadata = exported
    result = validate_motion_glb(directory / "air65-ii.glb", metadata["components"], authority)
    assert result["status"] == "pass"
    for check in result["checks"]:
        if check["component"].startswith("motor_"):
            assert check["roles"]["rotor"]["objects"] == 9
            assert check["roles"]["stator"]["objects"] == 37
        else:
            assert check["roles"]["blades"]["objects"] == 3
            assert check["roles"]["hub"]["objects"] == 5


def test_generated_asset_preserves_static_geometry_normals_uvs_materials(exported):
    directory, _ = exported
    result = compare_static_glb(directory / "air65-ii.glb", directory / "static_reference.glb")
    assert result["status"] == "pass", result["checks"]
    assert len(result["components"]) == 13


def test_only_thirteen_component_anchors_and_eight_rotor_transforms(exported):
    directory, _ = exported
    gltf, _ = read_glb(directory / "air65-ii.glb")
    assert sum("instance_id" in node.get("extras", {}) for node in gltf["nodes"]) == 13
    assert sum(node.get("extras", {}).get("motion_role") == "rotor" for node in gltf["nodes"]) == 8
    assert sum(node.get("extras", {}).get("surface_role") == "blades" for node in gltf["nodes"]) == 4
    for index in gltf["nodes"][0]["children"]:
        list(component_primitives(gltf, index))


def write_fixture_glb(path, gltf, binary):
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode()
    json_bytes += b" " * (-len(json_bytes) % 4)
    binary += b"\0" * (-len(binary) % 4)
    data = struct.pack("<4sII", b"glTF", 2, 28 + len(json_bytes) + len(binary))
    data += struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes
    data += struct.pack("<I4s", len(binary), b"BIN\0") + binary
    path.write_bytes(data)


def test_validator_rejects_whole_motor_rotor_tag(exported, authority, tmp_path):
    directory, metadata = exported
    gltf, binary = read_glb(directory / "air65-ii.glb")
    next(node for node in gltf["nodes"] if node["name"] == "motor_FL")["extras"]["motion_role"] = "rotor"
    path = tmp_path / "bad.glb"
    write_fixture_glb(path, gltf, binary)
    with pytest.raises(ValueError, match="complete motor anchor"):
        validate_motion_glb(path, metadata["components"], authority)


def test_validator_rejects_geometry_routed_into_wrong_role(exported, authority, tmp_path):
    directory, metadata = exported
    gltf, binary = read_glb(directory / "air65-ii.glb")
    rotor = next(node for node in gltf["nodes"] if node["name"] == "motor_FL_rotor")
    stator = next(node for node in gltf["nodes"] if node["name"] == "motor_FL_stator")
    rotor["mesh"], stator["mesh"] = stator["mesh"], rotor["mesh"]
    path = tmp_path / "bad.glb"
    write_fixture_glb(path, gltf, binary)
    with pytest.raises(ValueError, match="semantic boundary"):
        validate_motion_glb(path, metadata["components"], authority)
