"""Test meaningful failure boundaries of the data interpreter before launching Blender."""
import math
import copy
import hashlib
import json
from pathlib import Path
import sys

import jsonschema
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from contracts import ROOT, digest, read_json, resolve
from validate_model import verify_render_manifest


def test_references_are_explicit_and_preserve_nested_structure():
    assert resolve({"x":[{"param":"radius","scale":2,"offset":1},3]}, {"radius":{"value":16.5}})=={"x":[34,3]}


@pytest.mark.parametrize("value",[{"param":"missing"},{"param":"radius","expression":"__import__('os')"},float("nan"),float("inf")])
def test_unsafe_or_unresolved_data_fails(value):
    with pytest.raises(ValueError):
        resolve(value,{"radius":{"value":16.5}})


def component(node):
    return {"schema_version":"1.0","id":"fixture","contract":"test","description":"fixture","provenance":[],"nodes":[node]}


@pytest.mark.parametrize("node",[
    {"id":"bad","op":"python","material":"frame","args":{"code":"print(1)"}},
    {"id":"bad","op":"box","material":"frame","args":{"size":[1,2]}},
    {"id":"bad","op":"cylinder","material":"frame","args":{"radius":1,"depth":2,"file":"/tmp/anything"}},
    {"id":"bad","op":"box","material":"frame","args":{"size":[1,2,3]},"extra":1},
])
def test_schema_rejects_unknown_operations_and_malformed_dimensions(node):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(component(node),read_json(ROOT/"specs/component.schema.json"))


def test_fingerprint_is_independent_of_dictionary_key_order():
    assert digest({"a":1,"b":2})==digest({"b":2,"a":1})
    assert digest({"a":1,"b":2})!=digest({"a":1,"b":3})


@pytest.mark.parametrize("axes", [[0,0],[-1,1],[0,3],[0,1,2]])
def test_surface_uv_mapping_rejects_ambiguous_axes(axes):
    node={"id":"printed","op":"box","material":"print","args":{"size":[1,2,3]},"uv_projection":{"axes":axes,"bounds":[-1,-1,1,1]}}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(component(node),read_json(ROOT/"specs/component.schema.json"))


def test_aperture_edit_does_not_move_canopy_mount_legs():
    """Regression for the spatial audit's unrelated-parameter coupling defect."""
    source=read_json(ROOT/"specs/components/canopy.json")
    parameters=read_json(ROOT/"specs/spatial_architecture.json")["parameters"]
    changed=copy.deepcopy(parameters)
    changed["canopy_antenna_aperture_width"]["value"]=5.0
    old={n["id"]:n for n in resolve(source,parameters)["nodes"]}
    new={n["id"]:n for n in resolve(source,changed)["nodes"]}
    for side in ["left","right"]:
        assert old[side+"_leg"]["args"]==new[side+"_leg"]["args"]
        assert old["foot_"+side]["transform"]==new["foot_"+side]["transform"]
        # The formed leg is now an explicit surface; its full control mesh must
        # remain independent of the unrelated aperture-width parameter.
        assert new[side+"_leg"]["op"]=="mesh"


def test_missing_or_changed_render_is_not_accepted(tmp_path):
    assert verify_render_manifest(tmp_path,"source",["hero"])["status"]=="fail"
    image=tmp_path/"hero.png"
    image.write_bytes(b"known render bytes")
    manifest={"geometry_input_sha256":"source","views":{"hero":{"sha256":hashlib.sha256(image.read_bytes()).hexdigest()}}}
    (tmp_path/"render_manifest.json").write_text(json.dumps(manifest))
    assert verify_render_manifest(tmp_path,"source",["hero"])["status"]=="pass"
    assert verify_render_manifest(tmp_path,"different-source",["hero"])["status"]=="fail"
    image.write_bytes(b"stale or replaced render bytes")
    assert verify_render_manifest(tmp_path,"source",["hero"])["status"]=="fail"
