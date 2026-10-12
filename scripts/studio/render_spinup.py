"""Render rotor phases and integrate their radiance over real shutter intervals.

Headless Blender: --background --factory-startup --python-exit-code 1
--python scripts/studio/render_spinup.py -- [options]. Source model and studio
are preserved. Relative paths start at the repository root. --dry-run needs no bpy.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import platform
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import (MotionProfile, cache_identity, cached_phase, check_cache,
                      json_hash, portable_path, read_json, repo_path, sha256_file,
                      source_code_hashes, write_json)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='specs/studio/motion.json')
    parser.add_argument('--source',help='Input studio blend; default from config')
    parser.add_argument('--output',help='Output directory; default from config')
    parser.add_argument('--stage',choices=['all','atlas','compose','rig','validate'],default='all')
    parser.add_argument('--phase-limit',type=int,help='Render only this many atlas phases; --stage atlas only')
    parser.add_argument('--width',type=int)
    parser.add_argument('--height',type=int)
    parser.add_argument('--samples',type=int)
    parser.add_argument('--cpu',action='store_true',help='Force CPU; default uses Metal when available')
    parser.add_argument('--dry-run',action='store_true',help='Validate/print the plan without Blender or writes')
    args=parser.parse_args(argv)
    config_path=repo_path(args.config)
    spec=read_json(config_path)
    for argument,key in [('width','width'),('height','height'),('samples','cycles_samples')]:
        if getattr(args,argument) is not None:spec[key]=getattr(args,argument)
    profile=MotionProfile(spec)
    if args.phase_limit is not None and (args.stage!='atlas' or not 1<=args.phase_limit<=spec['atlas_phases']):
        parser.error('--phase-limit requires --stage atlas and a value from 1 to atlas_phases')
    source=repo_path(args.source or spec['source_blend'])
    OUT=repo_path(args.output or spec.get('output_directory','output/prop_spinup'))
    if not source.is_file():raise ValueError(f'Source studio blend missing: {source}; render or restore it first')
    if source==OUT/'air65_ii_spinup.blend':raise ValueError('Output project would overwrite source blend')
    source_sha=sha256_file(source)
    spec_sha=sha256_file(config_path)
    atlas_dir,frames_dir=OUT/'atlas',OUT/'frames'
    fps=spec['fps']
    width,height=spec['width'],spec['height']
    N=spec['atlas_phases']
    period_turns=profile.period_turns
    rest,up,down=profile.rest,profile.up,profile.down
    hold,total_turns=profile.hold,profile.total_turns
    t_up_end,t_hold_end,t_stop=profile.up_end,profile.hold_end,profile.stop
    if args.dry_run:
        print(json.dumps({'source':portable_path(source),'source_sha256':source_sha,'output':portable_path(OUT),
                          'stage':args.stage,'dimensions':[width,height],'frame_count':profile.frame_count,
                          'timing':profile.timing(),'peak_rpm':spec['peak_rpm'],'atlas_phases':N,
                          'samples':spec['cycles_samples'],'atlas_float32_bytes':N*width*height*4*4},indent=2))
        return
    import bpy
    import numpy as np

    def rpm_at(t):return profile.rpm_at(np.asarray(t,dtype=np.float64),clip=np.clip)
    def turns_at(t):return profile.turns_at(np.asarray(t,dtype=np.float64),clip=np.clip)
    for t in [rest+up*0.2,rest+up*0.6,t_up_end+hold*0.5,t_hold_end+down*0.2,t_hold_end+down*0.8]:
        derivative=float(turns_at(t+1e-5)-turns_at(t-1e-5))/(2e-5)*60
        if abs(derivative-float(rpm_at(t)))>=0.01:raise ValueError('Angle integral does not match RPM')

    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene=bpy.context.scene
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.fps=fps
    scene.render.fps_base=1
    scene.frame_start=1
    scene.frame_end=round(spec['duration_s']*fps)
    scene.render.engine='CYCLES'
    scene.render.use_motion_blur=False
    scene.render.use_persistent_data=True
    scene.cycles.samples=spec['cycles_samples']
    scene.cycles.seed=6512
    scene.cycles.use_animated_seed=False
    scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=0.02
    scene.cycles.adaptive_min_samples=32
    scene.cycles.use_denoising=True
    scene.cycles.device='CPU'
    device='CPU'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    if not args.cpu and 'METAL' in {x[0] for x in prefs.get_device_types(bpy.context)}:
        prefs.compute_device_type='METAL'
        prefs.get_devices()
        for d in prefs.devices:d.use=d.type=='METAL'
        if any(d.use for d in prefs.devices):
            scene.cycles.device='GPU';device='METAL'

    rotors=[]
    rotating_names=[]
    initial_world={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type in {'MESH','CURVE','FONT'}}
    for corner,sign in spec['motion']['sign_by_corner'].items():
        motor_parent=bpy.data.objects[f'motor_{corner}.origin']
        parent=bpy.data.objects.new(f'ANIM.motor_rotor_{corner}',None)
        motor_parent.users_collection[0].objects.link(parent)
        parent.parent=motor_parent
        parent.rotation_mode='XYZ'
        parent['angular_sign']=sign
        for part in spec['motion']['rotating_motor_parts']:
            obj=bpy.data.objects[f'motor_{corner}.{part}']
            assert obj.parent==motor_parent
            obj.parent=parent
            rotating_names.append(obj.name)
        prop=bpy.data.objects[f'prop_{corner}.origin']
        prop.rotation_mode='XYZ'
        prop['angular_sign']=sign
        rotating_names.extend(x.name for x in prop.children)
        rotors.extend([(parent,sign,0.0),(prop,sign,prop.rotation_euler.z)])
    bpy.context.view_layer.update()
    for name,matrix in initial_world.items():
        error=max(abs(a-b) for row_a,row_b in zip(matrix,bpy.data.objects[name].matrix_world) for a,b in zip(row_a,row_b))
        assert error<1e-8,(name,error)
    stationary={name:matrix for name,matrix in initial_world.items() if name not in rotating_names}

    def set_phase(angle):
        for obj,sign,offset in rotors:obj.rotation_euler.z=offset+sign*angle
        bpy.context.view_layer.update()

    set_phase(0.23)
    for name,matrix in stationary.items():
        error=max(abs(a-b) for ra,rb in zip(matrix,bpy.data.objects[name].matrix_world) for a,b in zip(ra,rb))
        assert error<1e-8,(name,error)
    set_phase(0)

    external_assets={}
    for image in bpy.data.images:
        if image.source=='FILE' and not image.packed_file:
            asset=Path(bpy.path.abspath(image.filepath,library=image.library)).resolve()
            if not asset.is_file():raise ValueError(f"Unpacked source image missing: {asset}")
            external_assets['image:'+image.name]=sha256_file(asset)
    for library in bpy.data.libraries:
        external_assets['library:'+library.name]=sha256_file(Path(bpy.path.abspath(library.filepath)).resolve())
    runtime={'blender':bpy.app.version_string,'blender_build':bpy.app.build_hash.decode(),
             'device':device,'devices':sorted(d.name for d in prefs.devices if d.use) if device!='CPU' else ['CPU'],
             'machine':platform.machine()}
    identity=cache_identity(source,spec,source_code_hashes('render_spinup.py','pipeline.py'),runtime,external_assets)
    if args.stage=='validate':
        if sha256_file(source)!=source_sha:raise RuntimeError('Source blend changed during validation')
        print(json.dumps({'stage':'validate','source':portable_path(source),'source_unchanged':True,
                          'moving_object_count':len(rotating_names),'stationary_object_count':len(stationary),
                          'initial_world_transforms_preserved':True,'stationary_geometry_does_not_move':True,
                          'timing':profile.timing(),'cache_identity':identity},indent=2),flush=True)
        return
    OUT.mkdir(parents=True,exist_ok=True)
    phase_records={}
    if args.stage in {'all','atlas','compose'}:
        phase_records=check_cache(atlas_dir,identity,require_existing=args.stage=='compose')
        atlas_dir.mkdir(parents=True,exist_ok=True)
        if not (atlas_dir/'identity.json').exists():write_json(atlas_dir/'identity.json',identity)
    if args.stage in {'all','compose'}:frames_dir.mkdir(parents=True,exist_ok=True)

    if args.stage in {'all','atlas'}:
        scene.render.image_settings.file_format='OPEN_EXR'
        scene.render.image_settings.color_mode='RGBA'
        scene.render.image_settings.color_depth='16'
        scene.render.image_settings.exr_codec='ZIP'
        limit=args.phase_limit or N
        for index in range(min(N,limit)):
            path=atlas_dir/f'phase_{index:03}.exr'
            if cached_phase(path,phase_records):
                print(f'ATLAS_CACHED {index+1}/{N}',flush=True)
                continue
            start=time.monotonic()
            set_phase(index/N*math.tau*period_turns)
            scene.render.filepath=str(path)
            bpy.ops.render.render(write_still=True)
            phase_records[path.name]={'bytes':path.stat().st_size,'sha256':sha256_file(path)}
            write_json(atlas_dir/'files.json',phase_records)
            if index in {0,N//4,N//2}:
                scene.render.image_settings.file_format='PNG'
                scene.render.image_settings.color_depth='8'
                bpy.data.images['Render Result'].save_render(str(OUT/f'phase_preview_{index:03}.png'),scene=scene)
                scene.render.image_settings.file_format='OPEN_EXR'
                scene.render.image_settings.color_depth='16'
            print(f'ATLAS_RENDERED {index+1}/{N} seconds={time.monotonic()-start:.2f}',flush=True)

    frame_records=[]
    if args.stage in {'all','compose'}:
        if not all(cached_phase(atlas_dir/f'phase_{i:03}.exr',phase_records) for i in range(N)):
            raise ValueError('Atlas is incomplete; finish --stage atlas before composing')
        # Scene-linear half-float EXRs enter a float32 accumulation buffer.
        atlas=np.empty((N,height,width,4),dtype=np.float32)
        source_colorspace=None
        for i in range(N):
            img=bpy.data.images.load(str(atlas_dir/f'phase_{i:03}.exr'),check_existing=False)
            assert tuple(img.size)==(width,height)
            source_colorspace=img.colorspace_settings.name
            img.pixels.foreach_get(atlas[i].reshape(-1))
            bpy.data.images.remove(img)
        assert np.isfinite(atlas).all()
        assert source_colorspace and source_colorspace!='sRGB',source_colorspace
        print('LINEAR_ATLAS',source_colorspace,'max',float(atlas.max()),'bytes',atlas.nbytes,flush=True)
        image=bpy.data.images.new('Temporally integrated exposure',width=width,height=height,alpha=True,float_buffer=True)
        image.colorspace_settings.name=source_colorspace
        scene.render.image_settings.file_format='PNG'
        scene.render.image_settings.color_mode='RGB'
        scene.render.image_settings.color_depth='8'
        scene.render.image_settings.compression=15
        quadrature=spec['exposure_integration']['quadrature_samples_per_frame']
        times=(np.arange(quadrature,dtype=np.float64)+0.5)/quadrature-0.5
        times*=spec['shutter_s']
        cache={}
        for frame in range(round(spec['duration_s']*fps)):
            t=frame/fps
            phase=(turns_at(t+times)/period_turns*N)%N
            # Make mathematically exact resting phase zero robust to floating error.
            phase[np.isclose(phase,N,atol=1e-7,rtol=0)]=0
            left=np.floor(phase).astype(np.int32)
            fraction=phase-left
            weights=(np.bincount(left,weights=1-fraction,minlength=N)+np.bincount((left+1)%N,weights=fraction,minlength=N))/quadrature
            assert abs(weights.sum()-1)<1e-8
            path=frames_dir/f'frame_{frame:04}.png'
            key=tuple(np.round(weights,8))
            if key in cache:
                shutil.copyfile(cache[key],path)
            else:
                active=np.flatnonzero(weights>1e-12)
                if len(active)==1:rgba=atlas[active[0]]
                else:rgba=np.einsum('n,nhwc->hwc',weights.astype(np.float32),atlas,optimize=False)
                image.pixels.foreach_set(rgba.reshape(-1))
                image.update()
                image.save_render(str(path),scene=scene)
                cache[key]=path
            frame_records.append({'frame':frame,'time_s':t,'rpm':round(float(rpm_at(t)),3),'turns':round(float(turns_at(t)),8),'angular_travel_during_shutter_turns':round(float(turns_at(t+spec['shutter_s']/2)-turns_at(t-spec['shutter_s']/2)),6)})
            if frame%25==0:print(f'EXPOSURE_FRAME {frame+1}/{scene.frame_end}',flush=True)
        for index,label in [(0,'still'),(round((rest+up*0.12)*fps),'starting'),(round((rest+up*0.4)*fps),'accelerating'),(round((t_up_end+hold*0.5)*fps),'full_speed'),(round((t_hold_end+down*0.64)*fps),'slowing')]:
            shutil.copyfile(frames_dir/f'frame_{index:04}.png',OUT/f'{label}.png')
        assert (frames_dir/'frame_0000.png').read_bytes()==(frames_dir/f'frame_{profile.frame_count-1:04}.png').read_bytes()
        print('LOOP_ENDPOINT_PIXELS_MATCH',flush=True)

    if args.stage in {'all','rig'}:
        # The source remains editable, with real unwrapped angular keyframes.
        for sample in range(scene.frame_end*4+1):
            frame=1+sample/4
            t=(frame-1)/fps
            angle=float(turns_at(t))*math.tau
            for obj,sign,offset in rotors:
                obj.rotation_euler.z=offset+sign*angle
                obj.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
        for obj,_,_ in rotors:
            action=obj.animation_data.action
            curves=getattr(action,'fcurves',None)
            if curves is None:
                curves=[fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
            for curve in curves:
                for key in curve.keyframe_points:key.interpolation='LINEAR'
        scene.frame_set(1)
        scene['animation_rpm_reference']=f"{spec['source']['motor']}/{spec['source']['propeller']}; reference peak {spec['peak_rpm']} RPM. {spec['source']['qualification']}"
        scene['animation_render_method']='GIF uses time-integrated scene-linear phase atlas. Single-frame real-time playback can strobe at these RPMs. Reproduce with scripts/studio/render_spinup.py and specs/studio/motion.json.'
        scene['animation_scope']=spec['motion']['simulation_scope']
        scene.render.image_settings.file_format='PNG'
        scene.render.image_settings.color_depth='8'
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'air65_ii_spinup.blend'))

    if sha256_file(source)!=source_sha:raise RuntimeError('Source blend changed during the build')
    manifest={
        'stage':args.stage,'config':portable_path(config_path),'cache_identity':identity,'source_blend':portable_path(source),'source_sha256':source_sha,'source_unchanged':True,
        'spec_sha256':spec_sha,'effective_spec_sha256':json_hash(spec),'duration_s':spec['duration_s'],'fps':fps,'frame_count':round(spec['duration_s']*fps),
        'dimensions':[width,height],'device':device,'peak_rpm':spec['peak_rpm'],
        'timing':{'rest_until_s':rest,'spinup_until_s':t_up_end,'hold_until_s':t_hold_end,'stopped_at_s':t_stop,'total_rotor_revolutions':total_turns},
        'moving_objects':rotating_names,'stationary_object_count':len(stationary),
        'checks':{'initial_world_transforms_preserved':True,'stationary_geometry_does_not_move':True,'angle_derivative_matches_rpm':True,'end_orientation_matches_start':True},
        'render_method':spec['exposure_integration'],'rpm_provenance':spec['source'],'frames':frame_records,
    }
    manifest_name={'all':'animation_manifest.json','compose':'animation_manifest.json','atlas':'atlas_manifest.json','rig':'rig_manifest.json'}[args.stage]
    write_json(OUT/manifest_name,manifest)
    print('ANIMATION_STAGE_COMPLETE',args.stage,flush=True)


if __name__=='__main__':
    arguments=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    try:
        main(arguments)
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        print(f'spinup: {exc}',file=sys.stderr)
        raise
