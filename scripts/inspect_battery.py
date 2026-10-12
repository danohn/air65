"""Targeted optional-battery dimensions and frame-intersection checks in Blender."""
import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils.bvhtree import BVHTree


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output",required=True)
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
data=json.loads(bpy.data.texts["SOURCE — resolved assembly.json"].as_string())
p={key:value["value"] for key,value in data["architecture"]["parameters"].items()}
depsgraph=bpy.context.evaluated_depsgraph_get()
cache={}
for obj in bpy.data.objects:
    if obj.type not in {"MESH","CURVE","FONT"} or not obj.name.startswith(("battery.","frame.")):
        continue
    evaluated=obj.evaluated_get(depsgraph)
    mesh=evaluated.to_mesh()
    vertices=[evaluated.matrix_world@v.co for v in mesh.vertices]
    polygons=[list(poly.vertices) for poly in mesh.polygons]
    cache[obj.name]={"vertices":vertices,"bvh":BVHTree.FromPolygons(vertices,polygons,all_triangles=False,epsilon=0.0)}
    evaluated.to_mesh_clear()

frame={k:v for k,v in cache.items() if k.startswith("frame.")}
battery={k:v for k,v in cache.items() if k.startswith("battery.")}
if not frame or not battery:
    raise RuntimeError("Saved assembly must include both frame and battery")
body_names=["battery.foil_cell","battery.terminal_cap","battery.label_top","battery.label_bottom"]
points=[co/0.001 for name in body_names for co in battery[name]["vertices"]]
low=[min(v[i] for v in points) for i in range(3)]
high=[max(v[i] for v in points) for i in range(3)]
dimensions=[b-a for a,b in zip(low,high)]
expected=[p["battery_width"],p["battery_length"],p["battery_height"]]
dimension_pass=all(abs(a-b)<0.005 for a,b in zip(dimensions,expected))
overlaps=[]
for bname,bmesh in battery.items():
    for fname,fmesh in frame.items():
        pairs=bmesh["bvh"].overlap(fmesh["bvh"])
        if pairs:
            overlaps.append({"battery_object":bname,"frame_object":fname,"intersecting_face_pairs":len(pairs)})
interior=[]
for name,mesh in frame.items():
    count=sum(all(low[i]+0.0001<v[i]/0.001<high[i]-0.0001 for i in range(3)) for v in mesh["vertices"])
    if count:
        interior.append({"frame_object":name,"vertices_inside_conservative_body_envelope":count})
result={
    "status":"pass" if dimension_pass and not overlaps and not interior else "fail",
    "saved_project":bpy.data.filepath,
    "geometry_input_sha256":data["geometry_input_sha256"],
    "body_dimensions_mm":dimensions,
    "body_nominal_mm":expected,
    "body_bounds_min_mm":low,
    "body_bounds_max_mm":high,
    "body_dimensions_pass":dimension_pass,
    "frame_surface_intersections":overlaps,
    "frame_vertices_inside_conservative_body_box":interior,
    "battery_objects_checked":len(battery),
    "frame_objects_checked":len(frame),
    "claim":"No detected frame/battery surface intersections or frame vertices inside the conservative nominal body envelope in this saved display pose. Body excludes the connector nose; printed graphics are UV textures on the curved wrapper.",
    "limitations":["Targeted geometric check, not a general solid collision/containment proof or insertion-path simulation.","Cradle construction, battery placement, labels and connector are estimates.","Power pigtail is displayed unplugged; mechanical/electrical connector mating is not modelled."]
}
Path(args.output).write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
if result["status"]!="pass":
    raise RuntimeError("Optional battery inspection failed")
