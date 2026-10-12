"""Inspect authored canopy normals inside Blender without modifying the model.

Load the matching saved .blend, then run with --python and optionally append
-- --resolved output/canopy_refinement/isolated_final/resolved_assembly.json.
"""
import argparse,sys
import bpy,json,math
from mathutils import Vector
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--resolved",default="output/canopy_refinement/isolated_final/resolved_assembly.json")
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
r=json.loads(Path(args.resolved).read_text())
nodes={"canopy."+n["id"]:n for n in r["components"]["canopy"]["nodes"]}
for obj in bpy.data.objects:
 if obj.type!="MESH" or not obj.name.startswith("canopy."):continue
 node=nodes[obj.name]
 if "vertex_normals" not in node["args"]:continue
 vv=[Vector(v) for v in node["args"]["vertices"]];faces=node["args"]["faces"];ns=[Vector(v) for v in node["args"]["vertex_normals"]]
 flipped=[];badinput=[]
 for face,f in zip(obj.data.polygons,faces):
  normal=Vector((0,0,0));average=Vector((0,0,0))
  for a,b in zip(f[1:],f[2:]):normal+=(vv[a]-vv[f[0]]).cross(vv[b]-vv[f[0]])
  for i in f:average+=ns[i]
  if normal.normalized().dot(face.normal)<0:flipped.append(face.index)
  if normal.normalized().dot(average.normalized())<0:badinput.append(face.index)
 print(obj.name,"flipped",len(flipped),"input_bad",len(badinput),"bad_first",badinput[:8])
