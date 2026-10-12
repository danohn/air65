"""Check important nominal anchors on the optimized evaluated-mesh preview."""
import argparse
import json
import math
from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blender_render import evaluated_metrics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
objects = [o for o in bpy.data.objects if o.parent and 'component_id' in o.parent]
m = evaluated_metrics(objects)
named = {o['name']: o for o in m['objects']}
rows = []

def check(name, actual, expected, tolerance):
    rows.append({'check': name, 'actual_mm': actual, 'expected_mm': expected,
                 'numerical_tolerance_mm': tolerance, 'difference_mm': abs(actual-expected),
                 'status': 'pass' if abs(actual-expected) <= tolerance else 'fail'})

frame = [o for o in m['objects'] if o['name'].startswith('frame.')]
for i, axis in enumerate('XYZ'):
    size = max(o['bounds_max_mm'][i] for o in frame)-min(o['bounds_min_mm'][i] for o in frame)
    check('Frame envelope '+axis, size, [82.6,82.6,15.1][i], .02)
check('Diagonal motor axes', math.dist(named['motor_FL.upper_shaft']['world_origin_mm'], named['motor_RR.upper_shaft']['world_origin_mm']), 65, .001)
for label in ['FL','FR','RL','RR']:
    prop = [o for o in m['objects'] if o['name'].startswith('prop_'+label+'.')]
    motor = [o for o in m['objects'] if o['name'].startswith('motor_'+label+'.')]
    radius = max(o['maximum_radius_from_parent_axis_mm'] for o in prop)
    check(label+' prop swept diameter', radius*2, 31, .03)
    check(label+' motor maximum diameter', 2*max(o['maximum_radius_from_parent_axis_mm'] for o in motor), 9, .02)
    check(label+' duct clear vertex diameter', 2*named['frame.duct_'+label]['local_xy_vertex_radius_min_mm'], 33, .02)
    check(label+' prop-to-duct nominal radial clearance', named['frame.duct_'+label]['local_xy_vertex_radius_min_mm']-radius, 1, .025)
    check(label+' prop/motor concentricity', math.dist(named['prop_'+label+'.outer_hub_barrel']['world_origin_mm'][:2], named['motor_'+label+'.upper_shaft']['world_origin_mm'][:2]), 0, .001)
check('Frame mount pitch',math.dist(named['frame.mount_boss_front']['world_origin_mm'],named['frame.mount_boss_right']['world_origin_mm']),25.5,.001)
check('FC lug pitch',math.dist(named['electronics.fc_lug_left']['world_origin_mm'],named['electronics.fc_lug_rear']['world_origin_mm']),26,.001)
check('Camera barrel diameter',named['camera.lens_front_cup']['local_dimensions_mm'][0],10,.02)
result = {'status': 'pass' if all(r['status']=='pass' for r in rows) else 'fail',
          'source': bpy.data.filepath, 'checks':rows,
          'claim':'Nominal anchors on the exact evaluated meshes supplied to the GLB writer. Serialized GLB group bounds and vertex/index counts are checked separately by the exporter.',
          'limits':['Numerical export tolerances are not physical manufacturing tolerances.','Ring clear diameter is sampled at vertices; the polygonal opening has smaller chord radii between vertices.']}
Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(rows),'failed':[r for r in rows if r['status']!='pass']},indent=2))
if result['status']!='pass': raise RuntimeError('Optimized anchor check failed')
