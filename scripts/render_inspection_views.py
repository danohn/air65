"""Render identical close inspection views from any saved detailed/optimized blend.

Run inside headless Blender with the source .blend loaded. This never resaves it.
Studio lights, materials and colour management come from that saved project.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',required=True)
parser.add_argument('--views',default='canopy_oblique,canopy_front,canopy_right,pcb_top,pcb_bottom,battery_closeup')
parser.add_argument('--resolution',type=int,default=1100)
parser.add_argument('--samples',type=int,default=48)
parser.add_argument('--import-glb',help='Replace source component geometry with the serialized glTF asset before rendering saved cameras.')
parser.add_argument('--hide-battery',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
dest=Path(args.output);dest.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
scene.render.resolution_x=scene.render.resolution_y=args.resolution
scene.render.resolution_percentage=100
scene.cycles.samples=args.samples
scene.cycles.seed=6502
views={
 'canopy_oblique':((57,92,73),(0,0,29),52,'canopy'),
 'canopy_front':((0,100,35),(0,0,29),49,'canopy'),
 'canopy_right':((100,0,29),(0,0,29),50,'canopy'),
 'pcb_top':((0,0,95),(0,0,15),46,'pcb'),
 'pcb_bottom':((0,0,-65),(0,0,15),46,'pcb'),
 'battery_closeup':((40,-65,58),(0,-1,4),68,'battery'),
}
geometry=[o for o in bpy.data.objects if o.parent and 'component_id' in o.parent]
if args.import_glb:
    parents={o.parent for o in geometry}
    for obj in geometry:bpy.data.objects.remove(obj,do_unlink=True)
    for obj in parents:bpy.data.objects.remove(obj,do_unlink=True)
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(Path(args.import_glb).resolve()))
    geometry=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
if args.hide_battery:
    for obj in geometry:
        if obj.name=='battery' or obj.name.startswith('battery.'):obj.hide_render=True
original_visibility={o.name:o.hide_render for o in bpy.data.objects}
camera_data=bpy.data.cameras.new('Inspection camera')
camera=bpy.data.objects.new('Inspection camera',camera_data)
scene.collection.objects.link(camera)
camera_data.type='ORTHO'
camera_data.clip_start=.0001
camera_data.clip_end=10
manifest={'saved_source':bpy.data.filepath,'imported_glb':args.import_glb,'battery_hidden':args.hide_battery,'samples':args.samples,'resolution':args.resolution,'views':{}}
for name in args.views.split(','):
    for obj in bpy.data.objects:
        if obj.name in original_visibility:obj.hide_render=original_visibility[obj.name]
    if name in views:
        position,target,scale,scope=views[name]
        for obj in geometry:
            obj.hide_render=not (obj.name.startswith(('canopy.','camera.')) if scope=='canopy' else obj.name.startswith('battery.') if scope=='battery' else obj.name.startswith(('electronics.fc_','electronics.motor_connector_')))
        for obj in bpy.data.objects:
            if obj.type=='MESH' and obj not in geometry:obj.hide_render=True
        camera.location=Vector(position)*.001
        camera.rotation_euler=(Vector(target)*.001-camera.location).to_track_quat('-Z','Y').to_euler()
        camera_data.ortho_scale=scale*.001
        scene.camera=camera
    else:
        candidates=[o for o in bpy.data.objects if o.type=='CAMERA' and o.data.name==name+' camera']
        if len(candidates)!=1:raise ValueError('Unknown saved camera '+name)
        scene.camera=candidates[0]
        for obj in bpy.data.objects:
            if obj.type=='MESH' and obj not in geometry:obj.hide_render=name in {'underside','front','right','left','rear'}
    scene.render.filepath=str(dest/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    manifest['views'][name]={'file':name+'.png','sha256':hashlib.sha256((dest/(name+'.png')).read_bytes()).hexdigest()}
(dest/'inspection_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
