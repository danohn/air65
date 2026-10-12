"""Render the sourced Air65 II in the published photographic studio.

Blender owns bpy. Run with Blender --background --factory-startup
--python-exit-code 1 --python scripts/studio/render_studio.py -- [options].
Relative paths start at the repository root. --dry-run also works under uv.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import (json_hash, portable_path, read_json, repo_path, sha256_file,
                      source_code_hashes, validate_studio, write_json)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="specs/studio/studio.json")
    parser.add_argument("--source", help="Input blend; default from config")
    parser.add_argument("--output", help="Output directory; default from config")
    parser.add_argument("--width", type=int, help="Override configured image width")
    parser.add_argument("--samples", type=int, help="Override configured Cycles samples")
    parser.add_argument("--preview", action="store_true", help="Use preview sampling; do not save a blend")
    parser.add_argument("--cpu", action="store_true", help="Force CPU; default selects Metal when available")
    parser.add_argument("--no-render", action="store_true", help="Build/save the studio without rendering")
    parser.add_argument("--dry-run", action="store_true", help="Validate paths/config and print plan without Blender or writes")
    args = parser.parse_args(argv)
    config_path = repo_path(args.config)
    spec = read_json(config_path)
    if args.width is not None: spec["width"] = args.width
    if args.samples is not None: spec["cycles_samples"] = args.samples
    validate_studio(spec)
    args.width, args.samples = spec["width"], spec["cycles_samples"]
    source = repo_path(args.source or spec["source_blend"])
    if not source.is_file():
        raise ValueError(f"Source blend missing: {source}; build or restore the with-battery model first")
    if source == repo_path(args.output or spec["output_directory"]) / "air65_ii_studio.blend":
        raise ValueError("Output project would overwrite the source blend; choose another output directory")
    if args.dry_run:
        print(json.dumps({"source":portable_path(source),"source_sha256":sha256_file(source),
                          "output":portable_path(repo_path(args.output or spec["output_directory"])),
                          "resolution":[args.width,round(args.width*spec["height_ratio"])],
                          "samples":args.samples,"preview":args.preview,"render":not args.no_render},indent=2))
        return
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    source = repo_path(args.source or spec["source_blend"])
    out = repo_path(args.output or spec["output_directory"])
    if source == out / "air65_ii_studio.blend":
        raise ValueError("Output project would overwrite the source blend; choose another output directory")
    out.mkdir(parents=True, exist_ok=True)
    source_hash = sha256_file(source)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene

    # Remove only the original presentation environment and cameras.
    for collection in list(bpy.data.collections):
        if collection.name.startswith('STUDIO'):
            for obj in list(collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(collection)
    for obj in list(bpy.data.objects):
        if obj.type in {'LIGHT', 'CAMERA'}:
            bpy.data.objects.remove(obj, do_unlink=True)
    model = [obj for obj in bpy.data.objects if obj.type in {'MESH', 'CURVE', 'FONT'}]
    for obj in model:
        obj.hide_render = False

    # Clear polycarbonate in this studio: less diffuse veil, readable reflections.
    # This is a presentation-only estimate, not a change to the source asset.
    material_overrides = []
    for mat in bpy.data.materials:
        if mat.name == 'prop_clear' and mat.use_nodes:
            shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            for key, value in spec["presentation_material_overrides"]["prop_clear"].items():
                material_overrides.append({'material':mat.name,'input':key,'source':shader.inputs[key].default_value,'portrait':value})
                shader.inputs[key].default_value = value

    studio = bpy.data.collections.new('PORTRAIT STUDIO — camera, lights and backdrop')
    scene.collection.children.link(studio)
    def link(obj):
        studio.objects.link(obj)
        return obj
    def aim(obj, point):
        obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()

    depsgraph = bpy.context.evaluated_depsgraph_get()
    corners = [obj.matrix_world @ Vector(corner) for obj in model for corner in obj.evaluated_get(depsgraph).bound_box]
    minimum_z = min(v.z for v in corners)

    floor_mesh = bpy.data.meshes.new('Continuous satin backdrop')
    extent=spec["floor"]["half_extent_m"]
    floor_z=minimum_z-spec["floor"]["below_model_m"]
    floor_mesh.from_pydata([(-extent,-extent,floor_z),(extent,-extent,floor_z),(extent,extent,floor_z),(-extent,extent,floor_z)], [], [(0,1,2,3)])
    floor = link(bpy.data.objects.new('Charcoal satin studio surface', floor_mesh))
    material = bpy.data.materials.new('Charcoal satin — studio only')
    material.use_nodes = True
    bsdf = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = spec["floor"]['base_color']
    bsdf.inputs['Roughness'].default_value = spec["floor"]['roughness']
    bsdf.inputs['Metallic'].default_value = spec["floor"]['metallic']
    bsdf.inputs['Specular IOR Level'].default_value = spec["floor"]['specular_ior_level']
    floor.data.materials.append(material)

    world = bpy.data.worlds.new('Dark photographic studio')
    world.use_nodes = True
    background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    background.inputs["Color"].default_value = spec["world"]["color"]
    background.inputs["Strength"].default_value = spec["world"]["strength"]
    scene.world = world

    light_specs = spec["lights"]
    for light in light_specs:
        data = bpy.data.lights.new(light['name'], 'AREA')
        data.energy = light['energy']
        data.shape = 'RECTANGLE'
        data.size = light['size']
        data.size_y = light['size_y']
        data.color = light['color']
        obj = link(bpy.data.objects.new(light['name'], data))
        obj.location = light['position']
        aim(obj, light['target'])

    camera_data = bpy.data.cameras.new('Portrait macro lens')
    camera = link(bpy.data.objects.new('Portrait camera', camera_data))
    camera_data.type = 'PERSP'
    camera_data.lens = spec["camera"]["lens_mm"]
    camera_data.sensor_width = spec["camera"]["sensor_width_mm"]
    camera_data.sensor_fit = 'HORIZONTAL'
    camera_data.clip_start = spec["camera"]["clip_start_m"]
    camera_data.clip_end = spec["camera"]["clip_end_m"]
    target = Vector(spec["camera"]["target_m"])
    direction = Vector(spec["camera"]["direction"]).normalized()
    distance = spec["camera"]["initial_distance_m"]
    scene.camera = camera
    scene.render.resolution_x = args.width
    scene.render.resolution_y = round(args.width * spec["height_ratio"])
    scene.render.resolution_percentage = 100

    # Fit the entire existing aircraft with breathing room, including the antenna.
    for _ in range(spec["camera"]["fit_steps"]):
        camera.location = target + direction * distance
        aim(camera, target)
        bpy.context.view_layer.update()
        projected = [world_to_camera_view(scene, camera, p) for p in corners]
        if min(p.x for p in projected) >= spec["camera"]["margin_x"] and max(p.x for p in projected) <= 1-spec["camera"]["margin_x"] and min(p.y for p in projected) >= spec["camera"]["margin_y"] and max(p.y for p in projected) <= 1-spec["camera"]["margin_y"]:
            break
        distance *= spec["camera"]["distance_multiplier"]
    else:
        raise RuntimeError('Could not fit portrait camera')

    # A focus-stacked product-photography look: crisp aircraft and subtle depth falloff.
    focus = link(bpy.data.objects.new('Focus — central aircraft', None))
    focus.location = spec["camera"]["focus_m"]
    camera_data.dof.use_dof = True
    camera_data.dof.focus_object = focus
    camera_data.dof.aperture_fstop = spec["camera"]["f_stop"]
    camera_data.dof.aperture_blades = spec["camera"]["aperture_blades"]

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    device = 'CPU'
    if not args.cpu:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        available = {x[0] for x in prefs.get_device_types(bpy.context)}
        if 'METAL' in available:
            prefs.compute_device_type = 'METAL'
            prefs.get_devices()
            for d in prefs.devices:
                d.use = d.type == 'METAL'
            if any(d.use for d in prefs.devices):
                scene.cycles.device = 'GPU'
                device = 'METAL'
    scene.cycles.samples = args.samples
    scene.cycles.seed = spec["seed"]
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = spec["cycles"]["preview_adaptive_threshold" if args.preview else "adaptive_threshold"]
    scene.cycles.adaptive_min_samples = spec["cycles"]["preview_adaptive_min_samples" if args.preview else "adaptive_min_samples"]
    scene.cycles.max_bounces = spec["cycles"]['max_bounces']
    scene.cycles.transmission_bounces = spec["cycles"]['transmission_bounces']
    scene.cycles.glossy_bounces = spec["cycles"]['glossy_bounces']
    scene.cycles.diffuse_bounces = spec["cycles"]['diffuse_bounces']
    scene.cycles.transparent_max_bounces = spec["cycles"]['transparent_max_bounces']
    scene.cycles.sample_clamp_indirect = spec["cycles"]['sample_clamp_indirect']
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = spec["cycles"]["threads"]
    scene.view_settings.view_transform = spec["color_management"]["view_transform"]
    scene.view_settings.exposure = spec["color_management"]["exposure"]
    scene.view_settings.gamma = spec["color_management"]["gamma"]
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '16'
    scene.render.image_settings.compression = 20
    stem = 'preview' if args.preview else 'air65_ii_studio'
    scene.render.filepath = str(out / (stem + '.png'))
    scene.render.use_file_extension = True
    scene['portrait_source_blend_sha256'] = source_hash
    scene['portrait_note'] = 'Original aircraft geometry retained. Separate studio, camera and lighting; clear-prop roughness/transmission overridden in this copy only.'
    if not args.preview:
        bpy.ops.wm.save_as_mainfile(filepath=str(out / 'air65_ii_studio.blend'))
    print('PORTRAIT_CONFIG', json.dumps({'device':device,'samples':args.samples,'size':[scene.render.resolution_x,scene.render.resolution_y],'distance':distance}), flush=True)
    if not args.no_render:
        bpy.ops.render.render(write_still=True)

        image = bpy.data.images.get('Render Result')
        scene.render.image_settings.file_format = 'JPEG'
        scene.render.image_settings.color_depth = '8'
        scene.render.image_settings.quality = 96
        image.save_render(str(out / (stem + '.jpg')), scene=scene)
    if sha256_file(source) != source_hash:
        raise RuntimeError("Source blend changed during the build")
    manifest = {
        'config':portable_path(config_path),'config_sha256':sha256_file(config_path),'effective_config_sha256':json_hash(spec),'renderer_sha256':source_code_hashes('render_studio.py','pipeline.py'),'rendered':not args.no_render,'source':portable_path(source),'source_sha256':source_hash,'source_file_unchanged':True,'aircraft_geometry_preserved':True,
        'presentation_material_overrides':material_overrides,
        'model_geometry_objects':len(model),'blender':bpy.app.version_string,
        'render_engine':'Cycles','device':device,'samples':args.samples,'seed':spec['seed'],
        'resolution':[scene.render.resolution_x,scene.render.resolution_y],
        'camera':{'lens_mm':camera_data.lens,'location_m':list(camera.location),'target_m':list(target),'f_stop':camera_data.dof.aperture_fstop},
        'color_management':{'view_transform':scene.view_settings.view_transform,'exposure':scene.view_settings.exposure},
        'lights':light_specs,
        'outputs':{ext:{'path':stem+'.'+ext,'sha256':hashlib.sha256((out/(stem+'.'+ext)).read_bytes()).hexdigest()} for ext in ('png','jpg') if not args.no_render},
    }
    if not args.preview:
        manifest["outputs"]["blend"]={"path":"air65_ii_studio.blend","sha256":sha256_file(out/"air65_ii_studio.blend")}
    write_json(out / (stem + "_manifest.json"),manifest)
    completed = stem + '_manifest.json' if args.no_render else stem + '.png'
    print('PORTRAIT_COMPLETE', str(out / completed), flush=True)


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    try:
        main(arguments)
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        print(f"studio: {exc}", file=sys.stderr)
        raise
