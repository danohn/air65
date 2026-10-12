"""Reopen a saved blend and verify editability and evaluated-geometry persistence."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_render import evaluated_metrics

parser=argparse.ArgumentParser()
parser.add_argument("--output",required=True)
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
scene=bpy.context.scene
embedded=bpy.data.texts.get("SOURCE — resolved assembly.json")
if embedded is None:
    raise RuntimeError("Source JSON Text datablock missing")
data=json.loads(embedded.as_string())
objects=[o for o in bpy.data.objects if o.parent and "component_id" in o.parent]
metrics=evaluated_metrics(objects)
expected=scene["geometry_fingerprint_sha256"]
if metrics["geometry_fingerprint_sha256"]!=expected:
    raise RuntimeError("Geometry changed after saving/reopening")
if scene.get("surface_fingerprint_sha256")!=metrics["surface_fingerprint_sha256"]:
    raise RuntimeError("Authored normals or UVs changed after saving/reopening")
result={"status":"pass","saved_project":bpy.data.filepath,"reopened_geometry_fingerprint_sha256":metrics["geometry_fingerprint_sha256"],"source_input_sha256":data["geometry_input_sha256"],"geometry_object_count":len(objects),"editable_mesh_objects":sum(o.type=="MESH" for o in objects),"editable_curves":sum(o.type=="CURVE" for o in objects),"editable_fonts":sum(o.type=="FONT" for o in objects),"retained_modifiers":sum(len(o.modifiers) for o in objects),"component_collections":[i["id"] for i in data["assembly"]["instances"]],"camera_count":sum(o.type=="CAMERA" for o in bpy.data.objects),"embedded_source_present":True}
packed={Path(image.filepath).name:hashlib.sha256(image.packed_file.data).hexdigest() for image in bpy.data.images if image.packed_file}
for path,expected in data.get("surface_assets_sha256",{}).items():
    if packed.get(Path(path).name)!=expected:
        raise RuntimeError("Packed surface texture missing or changed: "+path)
result["packed_texture_sha256"]=packed
result["reopened_surface_fingerprint_sha256"]=metrics["surface_fingerprint_sha256"]
result["editable_uv_meshes"]=sum(o.type=="MESH" and len(o.data.uv_layers)>0 for o in objects)
Path(args.output).write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
