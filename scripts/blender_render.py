"""Deterministic allowlisted JSON geometry interpreter, run by Blender --background."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

MM = 0.001
ROOT = Path(__file__).resolve().parents[1]


def mesh_object(name, vertices, faces, recalc_normals=True):
    if not vertices or not faces:
        raise ValueError(f"Empty mesh: {name}")
    if any(not math.isfinite(float(c)) for v in vertices for c in v):
        raise ValueError(f"Nonfinite mesh: {name}")
    if any(len(f) < 3 or any(i < 0 or i >= len(vertices) for i in f) for f in faces):
        raise ValueError(f"Invalid face indices: {name}")
    mesh = bpy.data.meshes.new(name + ".mesh")
    mesh.from_pydata([[c * MM for c in v] for v in vertices], [], faces)
    if mesh.validate(verbose=False):
        raise ValueError(f"Blender had to repair invalid mesh: {name}")
    if recalc_normals:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
    mesh.update()
    return bpy.data.objects.new(name, mesh)


def bridge_rings(rings, closed_profile=False, cap_ends=False):
    n = len(rings[0])
    if n < 2 or any(len(r) != n for r in rings):
        raise ValueError("Inconsistent loft profiles")
    vertices = [v for r in rings for v in r]
    faces = []
    for row in range(len(rings) - 1):
        for j in range(n if closed_profile else n - 1):
            k = (j + 1) % n
            faces.append([row*n+j, row*n+k, (row+1)*n+k, (row+1)*n+j])
    if cap_ends:
        faces.extend([list(range(n - 1, -1, -1)), list(range((len(rings)-1)*n, len(rings)*n))])
    return vertices, faces


def ring_profile(name, profile, segments=96):
    if len(profile) < 3 or any(r <= 0 for r, _ in profile):
        raise ValueError(f"Invalid annular profile: {name}")
    rings = [[[r*math.cos(a*math.tau/segments), r*math.sin(a*math.tau/segments), z] for r,z in profile] for a in range(segments+1)]
    # Wrap the angular seam by indexing, avoiding coincident duplicate vertices.
    vertices, faces = bridge_rings(rings[:-1], True)
    n = len(profile)
    for j in range(n):
        k = (j+1) % n
        faces.append([(segments-1)*n+j, (segments-1)*n+k, k, j])
    return mesh_object(name, vertices, faces)


def cylinder(name, radius, depth, segments=64):
    if radius <= 0 or depth <= 0:
        raise ValueError(f"Invalid cylinder: {name}")
    rings = [[[radius*math.cos(a*math.tau/segments), radius*math.sin(a*math.tau/segments), z] for a in range(segments)] for z in [-depth/2, depth/2]]
    return mesh_object(name, *bridge_rings(rings, True, True))


def make_node(name, node):
    a, op = node["args"], node["op"]
    if op == "box":
        x,y,z = [v/2 for v in a["size"]]
        if min(x,y,z) <= 0:
            raise ValueError(f"Nonpositive box: {name}")
        obj = mesh_object(name, [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)], [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    elif op == "cylinder":
        obj = cylinder(name, **a)
    elif op == "annulus":
        ri,ro,d = a["inner_radius"],a["outer_radius"],a["depth"]
        if not 0 < ri < ro or d <= 0:
            raise ValueError(f"Invalid annulus: {name}")
        obj = ring_profile(name, [[ri,-d/2],[ro,-d/2],[ro,d/2],[ri,d/2]], a.get("segments",96))
    elif op == "ring_profile":
        obj = ring_profile(name, a["profile"], a.get("segments",96))
    elif op == "sphere":
        seg, rows = a.get("segments",32),a.get("rings",16)
        rx,ry,rz = [s/2 for s in a["size"]]
        vertices = [[0,0,rz]]
        for j in range(1, rows):
            theta = math.pi*j/rows
            vertices.extend([[rx*math.sin(theta)*math.cos(math.tau*i/seg),ry*math.sin(theta)*math.sin(math.tau*i/seg),rz*math.cos(theta)] for i in range(seg)])
        vertices.append([0,0,-rz])
        faces = [[0,1+i,1+(i+1)%seg] for i in range(seg)]
        for j in range(rows-2):
            for i in range(seg):
                k=(i+1)%seg
                faces.append([1+j*seg+i,1+(j+1)*seg+i,1+(j+1)*seg+k,1+j*seg+k])
        bottom=len(vertices)-1
        faces.extend([[bottom,1+(rows-2)*seg+(i+1)%seg,1+(rows-2)*seg+i] for i in range(seg)])
        obj=mesh_object(name,vertices,faces)
    elif op == "beam":
        start,end=Vector(a["start"]),Vector(a["end"])
        delta=end-start
        obj=cylinder(name,a["radius"],delta.length,a.get("segments",20))
        # Bake beam orientation and centre into mesh, leaving node transforms composable.
        rot=Vector((0,0,1)).rotation_difference(delta.normalized()).to_matrix().to_4x4()
        for v in obj.data.vertices:
            v.co=rot@v.co+(start+end)*0.5*MM
    elif op == "tube":
        curve=bpy.data.curves.new(name+".curve","CURVE")
        curve.dimensions="3D"
        curve.resolution_u=a.get("resolution",12)
        curve.bevel_depth=a["radius"]*MM
        curve.bevel_resolution=4
        curve.use_fill_caps=True
        if a.get("smooth",False):
            spline=curve.splines.new("BEZIER")
            spline.bezier_points.add(len(a["points"])-1)
            for p,co in zip(spline.bezier_points,a["points"]):
                p.co=Vector(co)*MM
                p.handle_left_type=p.handle_right_type="AUTO"
        else:
            spline=curve.splines.new("POLY")
            spline.points.add(len(a["points"])-1)
            for p,co in zip(spline.points,a["points"]):
                p.co=(*[c*MM for c in co],1)
        spline.use_cyclic_u=a.get("cyclic",False)
        obj=bpy.data.objects.new(name,curve)
    elif op == "ribbon":
        points=[Vector(p) for p in a["points"]]
        widths=a.get("widths",[a["width"]]*len(points))
        if len(points)<2 or len(widths)!=len(points):
            raise ValueError(f"Invalid ribbon path/widths: {name}")
        rings=[]
        for i,p in enumerate(points):
            tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
            width=Vector(a["width_axis"])
            width=(width-tangent*width.dot(tangent)).normalized()
            normal=tangent.cross(width).normalized()
            rings.append([list(p+width*widths[i]*s/2+normal*a["thickness"]*t/2) for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]])
        obj=mesh_object(name,*bridge_rings(rings,True,True))
    elif op == "polygon_extrude":
        rings=[[[x,y,z] for x,y in a["outline"]] for z in [-a["depth"]/2,a["depth"]/2]]
        obj=mesh_object(name,*bridge_rings(rings,True,True))
    elif op == "mesh":
        obj=mesh_object(name,a["vertices"],a["faces"],recalc_normals="vertex_normals" not in a)
    elif op == "loft_shell":
        rings=[[[x,s["y"],z] for x,z in s["profile"]] for s in a["sections"]]
        obj=mesh_object(name,*bridge_rings(rings,a.get("closed_profile",False),a.get("cap_ends",False)))
    elif op == "propeller_blade":
        rings=[]
        samples=a.get("profile_segments",12)
        hand=a["handedness"]
        for s in a["sections"]:
            ring=[]
            angle=math.radians(s["twist_deg"])
            for j in range(samples):
                phi=math.tau*j/samples
                chord=s["chord"]*0.5*math.cos(phi)
                thick=s["thickness"]*0.5*math.sin(phi)
                ring.append([s["radius"],hand*(s["sweep"]+chord*math.cos(angle)-thick*math.sin(angle)),s["z"]+chord*math.sin(angle)+thick*math.cos(angle)])
            rings.append(ring)
        obj=mesh_object(name,*bridge_rings(rings,True,True))
    elif op == "text":
        curve=bpy.data.curves.new(name+".font","FONT")
        curve.body=a["body"]
        curve.size=a["size"]*MM
        curve.extrude=a.get("extrude",0)*MM
        curve.align_x=a.get("align","CENTER")
        obj=bpy.data.objects.new(name,curve)
    else:
        raise ValueError(f"Operation is not allowlisted: {op}")
    tr=node.get("transform",{})
    obj.location=[x*MM for x in tr.get("location",[0,0,0])]
    obj.rotation_euler=[math.radians(x) for x in tr.get("rotation_deg",[0,0,0])]
    obj.scale=tr.get("scale",[1,1,1])
    if obj.type=="MESH":
        if "uv_projection" in node:
            projection=node["uv_projection"]
            ax,ay=projection["axes"]
            x0,y0,x1,y1=projection["bounds"]
            if x1<=x0 or y1<=y0:
                raise ValueError(f"Invalid UV bounds: {name}")
            uv=obj.data.uv_layers.new(name="Surface UV")
            for loop in obj.data.loops:
                co=obj.data.vertices[loop.vertex_index].co/MM
                u,v=(co[ax]-x0)/(x1-x0),(co[ay]-y0)/(y1-y0)
                uv.data[loop.index].uv=(1-u if projection.get("flip_u") else u,1-v if projection.get("flip_v") else v)
        for p in obj.data.polygons:
            p.use_smooth=node.get("smooth",op in {"sphere","cylinder","annulus","ring_profile","propeller_blade","loft_shell"})
        if "vertex_normals" in a:
            normals=a["vertex_normals"]
            if len(normals)!=len(obj.data.vertices) or any(abs(Vector(n).length-1)>0.001 for n in normals):
                raise ValueError(f"Invalid local-space vertex normals: {name}")
            obj.data.normals_split_custom_set_from_vertices(normals)
        mods=node.get("modifiers",{})
        if mods.get("subdivision",0):
            m=obj.modifiers.new("Editable surface subdivision","SUBSURF")
            m.levels=m.render_levels=mods["subdivision"]
        if mods.get("solidify",0):
            m=obj.modifiers.new("Editable shell thickness","SOLIDIFY")
            m.thickness=mods["solidify"]*MM
            m.offset=0
        if mods.get("bevel",0):
            m=obj.modifiers.new("Moulded edge fillet","BEVEL")
            m.width=mods["bevel"]*MM
            m.segments=3
            m.limit_method="ANGLE"
    obj["json_operation"]=op
    obj["evidence"]=json.dumps(node.get("evidence",[]))
    obj["modelling_notes"]=node.get("notes","")
    return obj


def material(name,spec):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    bsdf=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    inputs={"Base Color":spec.get("base_color",[0.5,0.5,0.5,1]),"Roughness":spec.get("roughness",0.4),"Metallic":spec.get("metallic",0),"Transmission Weight":spec.get("transmission",0),"IOR":spec.get("ior",1.46),"Coat Weight":spec.get("coat",0)}
    for key,value in inputs.items():
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value=value
    if "base_color_texture" in spec:
        relative=spec["base_color_texture"]
        path=(ROOT/relative).resolve()
        if not path.is_relative_to(ROOT/"assets/textures") or not path.is_file():
            raise ValueError(f"Texture must be an existing project asset: {relative}")
        texture=m.node_tree.nodes.new("ShaderNodeTexImage")
        texture.name="Authored surface print"
        texture.image=bpy.data.images.load(str(path),check_existing=True)
        texture.image.colorspace_settings.name="sRGB"
        texture.image.pack()
        texture.extension="EXTEND"
        m.node_tree.links.new(texture.outputs["Color"],bsdf.inputs["Base Color"])
        m["base_color_texture"]=relative
    m.diffuse_color=spec.get("base_color",[0.5,0.5,0.5,1])
    m["provenance"]=spec.get("note","Estimated optical appearance from references")
    return m


def evaluated_metrics(objects):
    bpy.context.view_layer.update()
    depsgraph=bpy.context.evaluated_depsgraph_get()
    metrics=[]
    h=hashlib.sha256()
    surface_hash=hashlib.sha256()
    allcoords=[]
    for obj in sorted(objects,key=lambda x:x.name):
        if obj.type not in {"MESH","CURVE","FONT"}:
            continue
        evaluated=obj.evaluated_get(depsgraph)
        mesh=evaluated.to_mesh()
        coords=[list(evaluated.matrix_world@v.co/MM) for v in mesh.vertices]
        if not coords:
            evaluated.to_mesh_clear()
            continue
        allcoords.extend(coords)
        low=[min(v[i] for v in coords) for i in range(3)]
        high=[max(v[i] for v in coords) for i in range(3)]
        localcoords=[list(v.co/MM) for v in mesh.vertices]
        locallow=[min(v[i] for v in localcoords) for i in range(3)]
        localhigh=[max(v[i] for v in localcoords) for i in range(3)]
        origin=obj.parent.matrix_world.translation/MM if obj.parent else Vector((0,0,0))
        radial=max(math.hypot(v[0]-origin.x,v[1]-origin.y) for v in coords)
        axis=(evaluated.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        signature={"name":obj.name,"vertices":[[round(c,6) for c in v] for v in coords],"faces":[list(p.vertices) for p in mesh.polygons],"material":obj.data.materials[0].name if len(obj.data.materials) else None}
        h.update(json.dumps(signature,sort_keys=True,separators=(",",":")).encode())
        if mesh.has_custom_normals or mesh.uv_layers:
            surface={"name":obj.name,"normals":[[round(c,6) for c in n.vector] for n in mesh.corner_normals],"uv":[[[round(c,6) for c in loop.uv] for loop in layer.data] for layer in mesh.uv_layers]}
            surface_hash.update(json.dumps(surface,sort_keys=True,separators=(",",":")).encode())
        metrics.append({"name":obj.name,"type":obj.type,"json_operation":obj["json_operation"],"material":obj.data.materials[0].name,"vertices":len(coords),"faces":len(mesh.polygons),"bounds_min_mm":low,"bounds_max_mm":high,"dimensions_mm":[high[i]-low[i] for i in range(3)],"local_dimensions_mm":[localhigh[i]-locallow[i] for i in range(3)],"local_xy_vertex_radius_min_mm":min(math.hypot(v[0],v[1]) for v in localcoords),"world_origin_mm":list(evaluated.matrix_world.translation/MM),"maximum_radius_from_parent_axis_mm":radial,"world_axis_z":list(axis),"modifiers":[m.type for m in obj.modifiers]})
        evaluated.to_mesh_clear()
    return {"geometry_fingerprint_sha256":h.hexdigest(),"surface_fingerprint_sha256":surface_hash.hexdigest(),"objects":metrics,"geometry_object_count":len(metrics),"total_vertices":sum(m["vertices"] for m in metrics),"assembly_bounds_min_mm":[min(v[i] for v in allcoords) for i in range(3)],"assembly_bounds_max_mm":[max(v[i] for v in allcoords) for i in range(3)]}


def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def studio(scene,minimum_z):
    collection=bpy.data.collections.new("STUDIO — hide for editing")
    scene.collection.children.link(collection)
    ground=make_node("Studio ground",{"op":"box","args":{"size":[2000,2000,0.3]},"transform":{"location":[0,0,minimum_z-0.4]},"smooth":False})
    ground.data.materials.append(material("Studio porcelain",{"base_color":[0.82,0.84,0.87,1],"roughness":0.72}))
    collection.objects.link(ground)
    for name,position,energy,size in [("Large softbox",(0.03,0.06,0.18),0.35,0.15),("Cool fill",(-0.13,0.02,0.09),0.22,0.12),("Rim light",(0.04,-0.12,0.12),0.3,0.10)]:
        data=bpy.data.lights.new(name,"AREA")
        data.energy=energy
        data.shape="DISK"
        data.size=size
        light=bpy.data.objects.new(name,data)
        light.location=position
        aim(light,(0,0,0.01))
        collection.objects.link(light)
    scene.world=bpy.data.worlds.new("Neutral studio world")
    scene.world.use_nodes=True
    bg=next(n for n in scene.world.node_tree.nodes if n.type=="BACKGROUND")
    bg.inputs["Color"].default_value=(0.78,0.82,0.90,1)
    bg.inputs["Strength"].default_value=0.45
    return ground


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--resolution",type=int,default=1100)
    parser.add_argument("--samples",type=int,default=48)
    parser.add_argument("--views",default="hero,top,front,right,rear,underside")
    parser.add_argument("--no-render",action="store_true")
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    data=json.loads(Path(args.input).read_text())
    output=Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    # A partial rerun must never retain an old successful render manifest.
    (output/"render_manifest.json").unlink(missing_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system="METRIC"
    scene.unit_settings.scale_length=1.0
    scene.unit_settings.length_unit="MILLIMETERS"
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=args.samples
    scene.cycles.seed=6502
    scene.cycles.use_denoising=True
    scene.cycles.use_adaptive_sampling=False
    scene.cycles.max_bounces=10
    scene.cycles.transmission_bounces=8
    scene.render.threads_mode="FIXED"
    scene.render.threads=8
    scene.render.resolution_x=scene.render.resolution_y=args.resolution
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGBA"
    scene.render.film_transparent=False
    scene.view_settings.view_transform="AgX"
    mats={name:material(name,spec) for name,spec in sorted(data["materials"].items())}
    objects=[]
    for instance in data["assembly"]["instances"]:
        component=data["components"][instance["component"]]
        collection=bpy.data.collections.new(instance["id"])
        scene.collection.children.link(collection)
        parent=bpy.data.objects.new(instance["id"]+".origin",None)
        parent.empty_display_size=0.002
        tr=instance.get("transform",{})
        parent.location=[x*MM for x in tr.get("location",[0,0,0])]
        parent.rotation_euler=[math.radians(x) for x in tr.get("rotation_deg",[0,0,0])]
        parent.scale=tr.get("scale",[1,1,1])
        parent["component_id"]=component["id"]
        collection.objects.link(parent)
        for node in component["nodes"]:
            obj=make_node(instance["id"]+"."+node["id"],node)
            obj.parent=parent
            collection.objects.link(obj)
            obj.data.materials.append(mats[node["material"]])
            objects.append(obj)
    metrics=evaluated_metrics(objects)
    ground=studio(scene,metrics["assembly_bounds_min_mm"][2])
    default_views={
        "hero":{"position":[115,145,112],"target":[0,0,12],"projection":"ORTHO","scale":120},
        "top":{"position":[0,0,200],"target":[0,0,0],"projection":"ORTHO","scale":102},
        "front":{"position":[0,200,18],"target":[0,0,18],"projection":"ORTHO","scale":102},
        "right":{"position":[200,0,18],"target":[0,0,18],"projection":"ORTHO","scale":102},
        "left":{"position":[-200,0,18],"target":[0,0,18],"projection":"ORTHO","scale":102},
        "rear":{"position":[0,-200,18],"target":[0,0,18],"projection":"ORTHO","scale":102},
        "underside":{"position":[0,0,-200],"target":[0,0,0],"projection":"ORTHO","scale":102},
        "reference":{"position":[-115,170,110],"target":[0,0,12],"projection":"PERSP","lens":68},
    }
    default_views.update(data["assembly"].get("views",{}))
    requested_views=args.views.split(",")
    unknown=set(requested_views)-set(default_views)
    if unknown:
        raise ValueError(f"Unknown views: {sorted(unknown)}")
    cameras={}
    for name,spec in default_views.items():
        camdata=bpy.data.cameras.new(name+" camera")
        camdata.type=spec.get("projection","ORTHO")
        camdata.ortho_scale=spec.get("scale",110)*MM
        camdata.lens=spec.get("lens",60)
        camdata.clip_start=0.0001
        camdata.clip_end=10
        cam=bpy.data.objects.new("VIEW "+name,camdata)
        scene.collection.objects.link(cam)
        cam.location=[c*MM for c in spec["position"]]
        aim(cam,[c*MM for c in spec["target"]])
        cameras[name]=cam
    scene.camera=cameras["hero"]
    scene["contract"]=data["contract"]
    scene["geometry_input_sha256"]=data["geometry_input_sha256"]
    scene["architecture_sha256"]=data["architecture_sha256"]
    scene["geometry_fingerprint_sha256"]=metrics["geometry_fingerprint_sha256"]
    scene["surface_fingerprint_sha256"]=metrics["surface_fingerprint_sha256"]
    scene["axis_convention"]="+X right, +Y forward, +Z up; JSON mm converted to SI metres"
    text=bpy.data.texts.new("SOURCE — resolved assembly.json")
    text.write(json.dumps(data,indent=2))
    # Leave a helpful material viewport and camera view when the project is opened.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.clip_start=0.0001
                area.spaces.active.clip_end=100
                area.spaces.active.region_3d.view_distance=0.18
                area.spaces.active.region_3d.view_location=(0,0,0.013)
                area.spaces.active.region_3d.view_perspective="CAMERA"
                area.spaces.active.shading.type="MATERIAL"
    metrics.update({"blender_version":bpy.app.version_string,"blender_build_hash":bpy.app.build_hash.decode(),"geometry_input_sha256":data["geometry_input_sha256"],"architecture_sha256":data["architecture_sha256"],"render":{"engine":"CYCLES","device":"CPU","samples":args.samples,"resolution":args.resolution,"seed":6502},"views":default_views})
    metrics["packed_surface_textures"]=[{"name":img.name,"size":list(img.size),"packed":bool(img.packed_file)} for img in bpy.data.images if img.source=="FILE"]
    (output/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    scene.render.filepath=str(output/"hero.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(output/"air65_ii.blend"))
    if not args.no_render:
        rendered={}
        for name in requested_views:
            scene.camera=cameras[name]
            ground.hide_render=name in {"underside","front","right","left","rear"}
            scene.render.filepath=str(output/(name+".png"))
            bpy.ops.render.render(write_still=True)
            rendered[name]={"file":name+".png","sha256":hashlib.sha256((output/(name+".png")).read_bytes()).hexdigest(),"camera":default_views[name]}
        manifest={"geometry_input_sha256":data["geometry_input_sha256"],"geometry_fingerprint_sha256":metrics["geometry_fingerprint_sha256"],"blender_version":bpy.app.version_string,"settings":metrics["render"],"views":rendered}
        (output/"render_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("AIR65_BUILD_COMPLETE "+metrics["geometry_fingerprint_sha256"],flush=True)


if __name__=="__main__":
    main()
