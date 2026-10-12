"""Safe JSON contracts shared by the CLI, tests and build preparation."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def resolve(value: Any, parameters: dict) -> Any:
    """Resolve explicit numeric parameter references. Never evaluate source text."""
    if isinstance(value, dict):
        if "param" in value:
            if set(value) - {"param", "scale", "offset"}:
                raise ValueError(f"Unknown reference fields: {value}")
            key = value["param"]
            if key not in parameters:
                raise ValueError(f"Unknown shared parameter: {key}")
            number = parameters[key]["value"]
            if isinstance(number, bool) or not isinstance(number, (int, float)):
                raise ValueError(f"Parameter {key} is not a scalar")
            result = number * value.get("scale", 1) + value.get("offset", 0)
            if not math.isfinite(result):
                raise ValueError(f"Non-finite parameter: {key}")
            return result
        return {key: resolve(item, parameters) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve(item, parameters) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite JSON number")
    return value


def prepare(assembly_path: Path) -> dict:
    assembly = read_json(assembly_path)
    architecture = read_json(ROOT / assembly["architecture"])
    parameters = architecture["parameters"]
    schema = read_json(ROOT / "specs/component.schema.json")
    materials = read_json(ROOT / assembly["materials"])
    surface_assets={}
    for name,material in materials.items():
        if "base_color_texture" not in material:
            continue
        relative=material["base_color_texture"]
        path=(ROOT/relative).resolve()
        if not path.is_relative_to(ROOT/"assets/textures") or not path.is_file():
            raise ValueError(f"Missing or non-project surface asset for {name}: {relative}")
        surface_assets[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
    components = {}
    for component_id, relpath in assembly["components"].items():
        component = read_json(ROOT / relpath)
        jsonschema.Draft202012Validator(schema).validate(component)
        if component["contract"] != architecture["contract"]:
            raise ValueError(f"Stale architecture contract in {relpath}")
        if component["id"] != component_id:
            raise ValueError(f"Component ID does not match assembly: {relpath}")
        names = [node["id"] for node in component["nodes"]]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate object IDs in {relpath}")
        for node in component["nodes"]:
            if node["material"] not in materials:
                raise ValueError(f"Unknown material {node['material']} in {relpath}")
        components[component_id] = resolve(component, parameters)
        for node in components[component_id]["nodes"]:
            args=node["args"]
            if "vertex_normals" in args:
                if len(args["vertex_normals"])!=len(args["vertices"]) or any(abs(math.sqrt(sum(x*x for x in n))-1)>0.001 for n in args["vertex_normals"]):
                    raise ValueError(f"Invalid per-vertex normals in {relpath}: {node['id']}")
    names = [inst["id"] for inst in assembly["instances"]]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate assembly instance IDs")
    for instance in assembly["instances"]:
        if instance["component"] not in components:
            raise ValueError(f"Unknown component in {instance['id']}")
    result = {
        "schema_version": "1.0",
        "contract": architecture["contract"],
        "units": "mm",
        "assembly": resolve(assembly, parameters),
        "architecture": architecture,
        "components": components,
        "materials": materials,
        "surface_assets_sha256":surface_assets,
        "architecture_sha256": digest(architecture),
        "runtime_source_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in ["scripts/blender_render.py", "scripts/contracts.py", "scripts/build.py", "specs/component.schema.json"]
        },
    }
    result["geometry_input_sha256"] = digest(result)
    return result
