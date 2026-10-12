"""Generate the strict, shared component data contract (no executable expressions)."""
from pathlib import Path
import json

SCALAR = {"oneOf": [{"type": "number"}, {"type": "object", "required": ["param"], "properties": {"param": {"type": "string", "minLength": 1}, "scale": {"type": "number"}, "offset": {"type": "number"}}, "additionalProperties": False}]}

def arr(items, count=None):
    value = {"type": "array", "items": items}
    if count is not None:
        value.update(minItems=count, maxItems=count)
    return value

V3, V2 = arr(SCALAR, 3), arr(SCALAR, 2)
INT = {"type": "integer", "minimum": 3, "maximum": 512}
BOOL = {"type": "boolean"}

def obj(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}

OPS = {
    "box": obj({"size": V3}, ["size"]),
    "cylinder": obj({"radius": SCALAR, "depth": SCALAR, "segments": INT}, ["radius", "depth"]),
    "annulus": obj({"inner_radius": SCALAR, "outer_radius": SCALAR, "depth": SCALAR, "segments": INT}, ["inner_radius", "outer_radius", "depth"]),
    "ring_profile": obj({"profile": arr(V2), "segments": INT}, ["profile"]),
    "sphere": obj({"size": V3, "segments": INT, "rings": INT}, ["size"]),
    "beam": obj({"start": V3, "end": V3, "radius": SCALAR, "segments": INT}, ["start", "end", "radius"]),
    "tube": obj({"points": arr(V3), "radius": SCALAR, "cyclic": BOOL, "smooth": BOOL, "resolution": INT}, ["points", "radius"]),
    "ribbon": obj({"points": arr(V3), "width": SCALAR, "widths": arr(SCALAR), "width_axis": V3, "thickness": SCALAR}, ["points", "width", "width_axis", "thickness"]),
    "polygon_extrude": obj({"outline": arr(V2), "depth": SCALAR}, ["outline", "depth"]),
    "mesh": obj({"vertices": arr(V3), "vertex_normals": arr(V3), "faces": arr(arr({"type": "integer", "minimum": 0}))}, ["vertices", "faces"]),
    "loft_shell": obj({"sections": arr(obj({"y": SCALAR, "profile": arr(V2)}, ["y", "profile"])), "closed_profile": BOOL, "cap_ends": BOOL}, ["sections"]),
    "propeller_blade": obj({"sections": arr(obj({"radius": SCALAR, "chord": SCALAR, "sweep": SCALAR, "z": SCALAR, "twist_deg": SCALAR, "thickness": SCALAR}, ["radius", "chord", "sweep", "z", "twist_deg", "thickness"])), "handedness": {"enum": [-1, 1]}, "profile_segments": INT}, ["sections", "handedness"]),
    "text": obj({"body": {"type": "string"}, "size": SCALAR, "extrude": SCALAR, "align": {"enum": ["LEFT", "CENTER", "RIGHT"]}}, ["body", "size"]),
}

node = obj({
    "id": {"type": "string", "pattern": "^[A-Za-z0-9_.-]+$"},
    "op": {"enum": list(OPS)},
    "material": {"type": "string"},
    "transform": obj({"location": V3, "rotation_deg": V3, "scale": arr({"type": "number"}, 3)}),
    "args": {"type": "object"},
    "modifiers": obj({"bevel": SCALAR, "subdivision": {"type": "integer", "minimum": 0, "maximum": 3}, "solidify": SCALAR}),
    "smooth": BOOL,
    "uv_projection": obj({"axes": {"type":"array","items":{"type":"integer","minimum":0,"maximum":2},"minItems":2,"maxItems":2,"uniqueItems":True}, "bounds":arr(SCALAR,4), "flip_u":BOOL, "flip_v":BOOL}, ["axes","bounds"]),
    "evidence": arr({"type": "string"}),
    "notes": {"type": "string"},
}, ["id", "op", "material", "args"])
node["allOf"] = [{"if": {"properties": {"op": {"const": op}}}, "then": {"properties": {"args": args}}} for op, args in OPS.items()]

schema = obj({
    "schema_version": {"const": "1.0"},
    "id": {"type": "string", "pattern": "^[A-Za-z0-9_.-]+$"},
    "contract": {"type": "string"},
    "description": {"type": "string"},
    "provenance": arr(obj({"feature": {"type": "string"}, "status": {"enum": ["verified", "derived", "estimated", "simplified"]}, "source_ids": arr({"type": "string"}), "confidence": {"enum": ["high", "medium", "low"]}, "note": {"type": "string"}}, ["feature", "status", "source_ids", "confidence", "note"])),
    "nodes": {"type": "array", "items": node, "minItems": 1},
}, ["schema_version", "id", "contract", "description", "provenance", "nodes"])
schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://local.air65/component.schema.json", "title": "Air65 II shared component contract"})
path = Path(__file__).resolve().parents[1] / "specs/component.schema.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(schema, indent=2) + "\n")
