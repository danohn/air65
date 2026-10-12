"""Export the evaluated Air65 assembly to a deterministic, self-contained GLB.

Run with Blender, not the system Python:
  blender --background --factory-startup --python scripts/export_web_model.py -- \
    --source output/with_battery/air65_ii.blend --output output/web/air65-ii.glb

This is deliberately a small glTF 2.0 writer: it preserves evaluated triangle
surfaces and split normals, groups by component/material, and does not decimate.
The source blend is opened read-only and is never saved by this script.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def y_up(values):
    """Right-handed Blender Z-up to right-handed glTF Y-up, in metres."""
    return (float(values[0]), float(values[2]), -float(values[1]))


def bounds(points):
    return {
        "min": [min(p[axis] for p in points) for axis in range(3)],
        "max": [max(p[axis] for p in points) for axis in range(3)],
    }


def join_bounds(boxes):
    return bounds([box[edge] for box in boxes for edge in ("min", "max")])


def millimetres(box):
    return {key: [value * 1000 for value in values] for key, values in box.items()}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def principled_material(material, writer):
    nodes = [n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"]
    if len(nodes) != 1:
        raise ValueError(f"Expected one Principled shader: {material.name}")
    node = nodes[0]

    def scalar(name):
        socket = node.inputs[name]
        if socket.is_linked:
            raise ValueError(f"Unsupported texture/shader input: {material.name}/{name}")
        return float(socket.default_value)

    color = node.inputs["Base Color"]
    rgba = [float(v) for v in color.default_value]
    rgba[3] *= scalar("Alpha")
    texture_index = None
    if color.is_linked:
        links = list(color.links)
        image_node = links[0].from_node if len(links) == 1 else None
        if image_node is None or image_node.type != "TEX_IMAGE" or links[0].from_socket.name != "Color" or image_node.image is None:
            raise ValueError(f"Expected one direct image Color -> Principled Base Color link: {material.name}")
        if image_node.inputs["Vector"].is_linked:
            vector_node = image_node.inputs["Vector"].links[0].from_node
            if vector_node.type != "UVMAP":
                raise ValueError(f"Only active UV or direct UV Map vectors are supported: {material.name}")
        texture_index = writer.image_texture(image_node.image, image_node)
        rgba = [1.0, 1.0, 1.0, scalar("Alpha")]
        writer.textured_materials.add(material.name)
    result = {
        "name": material.name,
        "pbrMetallicRoughness": {
            "baseColorFactor": rgba,
            "metallicFactor": scalar("Metallic"),
            "roughnessFactor": scalar("Roughness"),
        },
        "doubleSided": not material.use_backface_culling,
    }
    if texture_index is not None:
        result["pbrMetallicRoughness"]["baseColorTexture"] = {"index": texture_index, "texCoord": 0}
    extensions = {}
    transmission = scalar("Transmission Weight")
    if transmission:
        extensions["KHR_materials_transmission"] = {"transmissionFactor": transmission}
    ior = scalar("IOR")
    if ior != 1.5:
        extensions["KHR_materials_ior"] = {"ior": ior}
    coat = scalar("Coat Weight")
    if coat:
        extensions["KHR_materials_clearcoat"] = {
            "clearcoatFactor": coat,
            "clearcoatRoughnessFactor": scalar("Coat Roughness"),
        }
    if extensions:
        result["extensions"] = extensions
    if rgba[3] < 1.0:
        result["alphaMode"] = "BLEND"
    return result


class GLBWriter:
    def __init__(self):
        self.binary = bytearray()
        self.textured_materials = set()
        self.texture_cache = {}
        self.image_records = []
        self.gltf = {
            "asset": {"version": "2.0", "generator": "Air65 deterministic evaluated-geometry exporter v1"},
            "scene": 0,
            "scenes": [{"name": "Air65 II Racing", "nodes": [0]}],
            "nodes": [{"name": "Air65 II Racing", "children": [], "extras": {"units": "metres", "up_axis": "+Y", "forward_axis": "-Z"}}],
            "meshes": [], "materials": [], "accessors": [], "bufferViews": [],
        }

    def image_texture(self, image, image_node):
        if image.source != "FILE":
            raise ValueError(f"Texture must be a file-backed PNG or JPEG: {image.name}")
        if image.packed_file:
            raw = bytes(image.packed_file.data)
        else:
            raw = Path(bpy.path.abspath(image.filepath, library=image.library)).read_bytes()
        if raw.startswith(b"\x89PNG\r\n\x1a\n"):
            mime = "image/png"
        elif raw.startswith(b"\xff\xd8"):
            mime = "image/jpeg"
        else:
            raise ValueError(f"Texture must be PNG or JPEG: {image.name}")
        digest = hashlib.sha256(raw).hexdigest()
        wrap = 33071 if image_node.extension in {"EXTEND", "CLIP"} else 10497
        key = (digest, wrap)
        if key in self.texture_cache:
            return self.texture_cache[key]
        self.binary.extend(b"\0" * (-len(self.binary) % 4))
        view_index = len(self.gltf["bufferViews"])
        self.gltf["bufferViews"].append({"buffer": 0, "byteOffset": len(self.binary), "byteLength": len(raw)})
        self.binary.extend(raw)
        image_index = len(self.gltf.setdefault("images", []))
        self.gltf["images"].append({"name": image.name, "bufferView": view_index, "mimeType": mime})
        sampler_index = len(self.gltf.setdefault("samplers", []))
        self.gltf["samplers"].append({"magFilter": 9729, "minFilter": 9987, "wrapS": wrap, "wrapT": wrap})
        index = len(self.gltf.setdefault("textures", []))
        self.gltf["textures"].append({"source": image_index, "sampler": sampler_index})
        self.texture_cache[key] = index
        self.image_records.append({"name": image.name, "sha256": digest, "bytes": len(raw), "mime_type": mime})
        return index

    def accessor(self, raw, component_type, count, shape, target, box=None):
        self.binary.extend(b"\0" * (-len(self.binary) % 4))
        view_index = len(self.gltf["bufferViews"])
        self.gltf["bufferViews"].append({"buffer": 0, "byteOffset": len(self.binary), "byteLength": len(raw), "target": target})
        self.binary.extend(raw)
        accessor = {"bufferView": view_index, "componentType": component_type, "count": count, "type": shape}
        if box is not None:
            accessor.update(box)
        self.gltf["accessors"].append(accessor)
        return len(self.gltf["accessors"]) - 1

    def primitive(self, batch, material_index):
        vertices, normals, indices = batch["vertices"], batch["normals"], batch["indices"]
        p = self.accessor(b"".join(struct.pack("<3f", *v) for v in vertices), 5126, len(vertices), "VEC3", 34962, bounds(vertices))
        n = self.accessor(b"".join(struct.pack("<3f", *v) for v in normals), 5126, len(normals), "VEC3", 34962)
        index_type, pack_format = (5123, "<H") if len(vertices) <= 65535 else (5125, "<I")
        i = self.accessor(b"".join(struct.pack(pack_format, index) for index in indices), index_type, len(indices), "SCALAR", 34963)
        attributes = {"POSITION": p, "NORMAL": n}
        if batch.get("uvs"):
            attributes["TEXCOORD_0"] = self.accessor(b"".join(struct.pack("<2f", *uv) for uv in batch["uvs"]), 5126, len(batch["uvs"]), "VEC2", 34962)
        return {"attributes": attributes, "indices": i, "material": material_index, "mode": 4}

    def write(self, path):
        self.gltf["buffers"] = [{"byteLength": len(self.binary)}]
        self.gltf["extensionsUsed"] = sorted({key for material in self.gltf["materials"] for key in material.get("extensions", {})})
        raw_json = json.dumps(self.gltf, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        raw_json += b" " * (-len(raw_json) % 4)
        raw_bin = bytes(self.binary) + b"\0" * (-len(self.binary) % 4)
        size = 12 + 8 + len(raw_json) + 8 + len(raw_bin)
        data = struct.pack("<4sII", b"glTF", 2, size)
        data += struct.pack("<I4s", len(raw_json), b"JSON") + raw_json
        data += struct.pack("<I4s", len(raw_bin), b"BIN\0") + raw_bin
        path.write_bytes(data)


def evaluate_component(parent, depsgraph, textured_materials=None, overrides=None):
    textured_materials = textured_materials or set()
    overrides = overrides or {}
    batches = defaultdict(lambda: {"vertices": [], "normals": [], "uvs": [], "indices": [], "lookup": {}})
    all_world_points = []
    origin = parent.matrix_world.translation.copy()
    children = sorted((o for o in parent.children if o.type in {"MESH", "CURVE", "FONT"}), key=lambda o: o.name)
    source_vertices = source_triangles = 0
    for obj in children:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = overrides.get(obj.name)
        if mesh is None:
            mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        if mesh is None:
            raise ValueError(f"Could not evaluate {obj.name}")
        mesh.calc_loop_triangles()
        matrix = evaluated.matrix_world
        normal_matrix = matrix.to_3x3().inverted().transposed()
        positions = [matrix @ vertex.co for vertex in mesh.vertices]
        all_world_points.extend(tuple(p) for p in positions)
        source_vertices += len(positions)
        source_triangles += len(mesh.loop_triangles)
        split_normals = [normal.vector.copy() for normal in mesh.corner_normals]
        if matrix.to_3x3().determinant() <= 0:
            raise ValueError(f"Negative or singular transform requires explicit winding handling: {obj.name}")
        for triangle in mesh.loop_triangles:
            material = mesh.materials[triangle.material_index]
            if material is None:
                raise ValueError(f"No material on {obj.name}")
            batch = batches[material.name]
            textured = material.name in textured_materials
            if textured and mesh.uv_layers.active is None:
                raise ValueError(f"Textured mesh has no active UV layer: {obj.name}")
            for vertex_index, loop_index in zip(triangle.vertices, triangle.loops):
                position = y_up(positions[vertex_index] - origin)
                normal = y_up((normal_matrix @ split_normals[loop_index]).normalized())
                # Position/normal equality uses stored IEEE float32 bytes without
                # geometric quantization. Canonicalize UVs separately: evaluated
                # bevel interpolation can vary by one float ULP between processes.
                uv = tuple(mesh.uv_layers.active.data[loop_index].uv) if textured else None
                uv = (round(uv[0], 6), round(1.0 - uv[1], 6)) if uv is not None else None
                fmt = "<8f" if textured else "<6f"
                key = struct.pack(fmt, *position, *normal, *(uv or ()))
                index = batch["lookup"].get(key)
                if index is None:
                    index = len(batch["vertices"])
                    f32 = struct.unpack(fmt, key)
                    batch["vertices"].append(f32[:3])
                    batch["normals"].append(f32[3:6])
                    if textured:
                        batch["uvs"].append(f32[6:8])
                    batch["lookup"][key] = index
                batch["indices"].append(index)
        if obj.name not in overrides:
            evaluated.to_mesh_clear()
    return batches, {
        "id": parent.name.removesuffix(".origin"),
        "component_id": parent["component_id"],
        "source_object_count": len(children),
        "source_evaluated_vertices": source_vertices,
        "triangles": source_triangles,
        "source_bounds_z_up_mm": millimetres(bounds(all_world_points)),
        "expected_bounds_y_up_m": bounds([y_up(p) for p in all_world_points]),
        "translation_y_up_m": list(y_up(origin)),
        "source_objects": [obj.name for obj in children],
    }


def polyline_keep_indices(points, tolerance):
    """Ramer-Douglas-Peucker simplification in metres, preserving endpoints."""
    if len(points) < 3:
        return list(range(len(points)))
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        segment = points[last] - points[first]
        length2 = segment.length_squared
        furthest, max_distance = None, -1.0
        for i in range(first + 1, last):
            t = max(0.0, min(1.0, (points[i] - points[first]).dot(segment) / length2)) if length2 else 0.0
            distance = (points[i] - points[first] - segment * t).length
            if distance > max_distance:
                furthest, max_distance = i, distance
        if furthest is not None and max_distance > tolerance:
            keep.add(furthest)
            stack.extend([(first, furthest), (furthest, last)])
    return sorted(keep)


def radial_sample_count(original, radius_m, config):
    tolerance = config["radial_sagitta_mm"] * 0.001
    angle = math.acos(max(-1.0, 1 - tolerance / max(radius_m, 1e-12)))
    required = max(config["minimum_radial_segments"], math.ceil(math.pi / angle)) if angle else original
    candidates = [n for n in range(4, original + 1, 4) if original % n == 0 and n >= required]
    return min(candidates) if candidates else original


def sampled_mesh_data(obj, node, config):
    """Sample the authored vertex lattice of supported parametric primitives."""
    if obj.type != "MESH" or obj.data.uv_layers.active is not None or node is None:
        return None, None
    operation, args = node["op"], node["args"]
    original = [tuple(v.co) for v in obj.data.vertices]
    vertices, faces = [], []

    def bridge(rings, cyclic=True, capped=False):
        vv = [v for ring in rings for v in ring]
        width = len(rings[0])
        ff = []
        for row in range(len(rings) - 1):
            for i in range(width if cyclic else width - 1):
                j = (i + 1) % width
                ff.append([row * width + i, row * width + j, (row + 1) * width + j, (row + 1) * width + i])
        if capped:
            ff.extend([list(range(width - 1, -1, -1)), list(range((len(rings) - 1) * width, len(rings) * width))])
        return vv, ff

    if operation in {"cylinder", "annulus", "ring_profile"}:
        original_segments = args.get("segments", 64 if operation == "cylinder" else 96)
        radius = max(math.hypot(p[0], p[1]) for p in original)
        target = radial_sample_count(original_segments, radius, config)
        if target == original_segments:
            return None, None
        step = original_segments // target
        if operation == "cylinder":
            if len(original) != original_segments * 2:
                return None, None
            rings = [[original[row * original_segments + i] for i in range(0, original_segments, step)] for row in range(2)]
            vertices, faces = bridge(rings, True, True)
        else:
            profile_count = len(args["profile"]) if operation == "ring_profile" else 4
            if len(original) != original_segments * profile_count:
                return None, None
            rings = [[original[i * profile_count + j] for j in range(profile_count)] for i in range(0, original_segments, step)]
            vertices, faces = bridge(rings)
            for j in range(profile_count):
                k = (j + 1) % profile_count
                faces.append([(target - 1) * profile_count + j, (target - 1) * profile_count + k, k, j])
        action = {"kind": "radial_sampling", "from_segments": original_segments, "to_segments": target}
    elif operation == "propeller_blade":
        profiles = args.get("profile_segments", 12)
        count = len(args["sections"])
        if len(original) != count * profiles:
            return None, None
        pstep = config["propeller_profile_stride"] if profiles % config["propeller_profile_stride"] == 0 else 1
        section_indices = sorted(set(range(0, count, config["propeller_section_stride"])) | {count - 1})
        # Preserve section extrema, including the broad paddle tip and airfoil changes.
        for field in ("radius", "chord", "sweep", "z", "twist_deg", "thickness"):
            section_indices = sorted(set(section_indices) | {min(range(count), key=lambda i: args["sections"][i][field]), max(range(count), key=lambda i: args["sections"][i][field])})
        rings = [[original[row * profiles + i] for i in range(0, profiles, pstep)] for row in section_indices]
        vertices, faces = bridge(rings, True, True)
        action = {"kind": "airfoil_sampling", "from_sections": count, "to_sections": len(section_indices), "from_profile_samples": profiles, "to_profile_samples": len(rings[0])}
    elif operation == "sphere":
        segments, rows = args.get("segments", 32), args.get("rings", 16)
        if len(original) != 2 + segments * (rows - 1):
            return None, None
        radius = max(math.hypot(p[0], p[1]) for p in original)
        target = radial_sample_count(segments, radius, config)
        step = segments // target
        selected_rows = list(range(1, rows, config["sphere_latitude_stride"]))
        if rows // 2 not in selected_rows:
            selected_rows = sorted(selected_rows + [rows // 2])
        vertices = [original[0]]
        for row in selected_rows:
            vertices.extend(original[1 + (row - 1) * segments + i] for i in range(0, segments, step))
        vertices.append(original[-1])
        faces.extend([0, 1 + i, 1 + (i + 1) % target] for i in range(target))
        for row in range(len(selected_rows) - 1):
            for i in range(target):
                j = (i + 1) % target
                faces.append([1 + row * target + i, 1 + (row + 1) * target + i, 1 + (row + 1) * target + j, 1 + row * target + j])
        last = len(vertices) - 1
        faces.extend([last, 1 + (len(selected_rows) - 1) * target + (i + 1) % target, 1 + (len(selected_rows) - 1) * target + i] for i in range(target))
        action = {"kind": "sphere_sampling", "from_segments": segments, "to_segments": target, "from_latitudes": rows - 1, "to_latitudes": len(selected_rows)}
    else:
        return None, None
    mesh = bpy.data.meshes.new(obj.name + ".web_sampled")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for material in obj.data.materials:
        mesh.materials.append(material)
    smooth = all(p.use_smooth for p in obj.data.polygons)
    for polygon in mesh.polygons:
        polygon.use_smooth = smooth
    return mesh, action


def mesh_snapshot(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
    mesh.calc_loop_triangles()
    return mesh


def mesh_surface(mesh, matrix):
    mesh.calc_loop_triangles()
    vertices = [matrix @ vertex.co for vertex in mesh.vertices]
    triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
    return vertices, triangles


def sampled_surface_difference(source, candidate, matrix, limit):
    source_vertices, source_triangles = mesh_surface(source, matrix)
    candidate_vertices, candidate_triangles = mesh_surface(candidate, matrix)
    source_bvh = BVHTree.FromPolygons(source_vertices, source_triangles, all_triangles=True)
    candidate_bvh = BVHTree.FromPolygons(candidate_vertices, candidate_triangles, all_triangles=True)

    def samples(vertices, triangles):
        points = list(vertices)
        points.extend((vertices[a] + vertices[b] + vertices[c]) / 3 for a, b, c in triangles)
        if len(points) > limit:
            return [points[round(i * (len(points) - 1) / (limit - 1))] for i in range(limit)]
        return points

    def direction(points, bvh):
        distances = [bvh.find_nearest(point)[3] * 1000 for point in points]
        return {"samples": len(distances), "maximum_mm": max(distances, default=0.0), "rms_mm": math.sqrt(sum(d * d for d in distances) / max(1, len(distances)))}

    forward = direction(samples(source_vertices, source_triangles), candidate_bvh)
    reverse = direction(samples(candidate_vertices, candidate_triangles), source_bvh)
    a, b = bounds(source_vertices), bounds(candidate_vertices)
    return {
        "source_to_candidate": forward, "candidate_to_source": reverse,
        "maximum_sampled_deviation_mm": max(forward["maximum_mm"], reverse["maximum_mm"]),
        "maximum_bound_delta_mm": max(abs(a[edge][i] - b[edge][i]) * 1000 for edge in ("min", "max") for i in range(3)),
        "source_bounds_z_up_mm": millimetres(a), "optimized_bounds_z_up_mm": millimetres(b),
    }


def optimize_geometry(parents, config):
    """Build transient evaluated web meshes; never mutate the source objects."""
    embedded = bpy.data.texts.get("SOURCE — resolved assembly.json")
    if embedded is None:
        raise ValueError("Optimized mode requires the source's embedded assembly specification")
    specification = json.loads(embedded.as_string())
    node_lookup = {component: {n["id"]: n for n in value["nodes"]} for component, value in specification["components"].items()}
    overrides, records = {}, []
    source_group_bounds, source_group_vertices = {}, {}
    for parent in parents:
        component = parent["component_id"]
        group_id = parent.name.removesuffix(".origin")
        group_records = []
        for obj in sorted(parent.children, key=lambda o: o.name):
            if obj.type not in {"MESH", "CURVE", "FONT"}:
                continue
            depsgraph = bpy.context.evaluated_depsgraph_get()
            source = mesh_snapshot(obj, depsgraph)
            original_vertices, original_triangles = mesh_surface(source, obj.matrix_world)
            visually_protected = any(obj.name.startswith(prefix) for prefix in config.get("retessellation_excluded_prefixes", []))
            if source.has_custom_normals or visually_protected:
                # Coincident canopy patches carry shared authored boundary
                # normals. Geometry-only distance gates cannot certify their
                # appearance after retessellation, so preserve them verbatim.
                original_box = millimetres(bounds(original_vertices))
                reason = "Visual-review protected component; no retessellation" if visually_protected else "Authored custom normals protected; no retessellation"
                record = {"object":obj.name,"component":group_id,"operation":obj.get("json_operation",obj.type),"source_vertices":len(source.vertices),"source_triangles":len(source.loop_triangles),"source_bounds_z_up_mm":original_box,"actions":[],"status":"unchanged","reason":reason,"optimized_vertices":len(source.vertices),"optimized_triangles":len(source.loop_triangles),"optimized_bounds_z_up_mm":original_box,"maximum_sampled_deviation_mm":0.0,"maximum_bound_delta_mm":0.0}
                overrides[obj.name]=source
                records.append(record)
                group_records.append(record)
                continue
            actions = []
            temporary = obj.copy()
            temporary.data = obj.data.copy()
            temporary.name = obj.name + ".web_candidate"
            bpy.context.scene.collection.objects.link(temporary)
            node = node_lookup.get(component, {}).get(obj.name.split(".", 1)[1])
            if obj.type == "MESH":
                sampled, action = sampled_mesh_data(temporary, node, config)
                if sampled is not None:
                    previous = temporary.data
                    temporary.data = sampled
                    bpy.data.meshes.remove(previous)
                    actions.append(action)
            elif obj.type == "CURVE":
                if temporary.data.bevel_resolution > config["curve_bevel_resolution"]:
                    actions.append({"kind": "curve_bevel_resolution", "from": temporary.data.bevel_resolution, "to": config["curve_bevel_resolution"]})
                    temporary.data.bevel_resolution = config["curve_bevel_resolution"]
                if temporary.data.resolution_u > config["curve_bezier_resolution"]:
                    actions.append({"kind": "bezier_resolution", "from": temporary.data.resolution_u, "to": config["curve_bezier_resolution"]})
                    temporary.data.resolution_u = config["curve_bezier_resolution"]
                for spline in list(temporary.data.splines):
                    if spline.type == "POLY" and not spline.use_cyclic_u and len(spline.points) > 4:
                        points = [Vector(p.co[:3]) for p in spline.points]
                        indices = polyline_keep_indices(points, config["curve_polyline_tolerance_mm"] * 0.001)
                        if len(indices) < len(points):
                            new_spline = temporary.data.splines.new("POLY")
                            new_spline.points.add(len(indices) - 1)
                            for point, index in zip(new_spline.points, indices):
                                point.co = (*points[index], 1.0)
                            temporary.data.splines.remove(spline)
                            actions.append({"kind": "bounded_polyline_simplification", "from_points": len(points), "to_points": len(indices), "tolerance_mm": config["curve_polyline_tolerance_mm"]})
            elif obj.type == "FONT" and temporary.data.resolution_u > config["font_resolution"]:
                actions.append({"kind": "font_resolution", "from": temporary.data.resolution_u, "to": config["font_resolution"]})
                temporary.data.resolution_u = config["font_resolution"]
            for modifier in temporary.modifiers:
                if modifier.type == "BEVEL" and modifier.segments > config["bevel_segments"]:
                    actions.append({"kind": "bevel_segments", "from": modifier.segments, "to": config["bevel_segments"]})
                    modifier.segments = config["bevel_segments"]
                elif modifier.type == "SUBSURF" and modifier.levels > config["subdivision_levels"]:
                    actions.append({"kind": "subdivision_levels", "from": modifier.levels, "to": config["subdivision_levels"]})
                    modifier.levels = modifier.render_levels = config["subdivision_levels"]
            bpy.context.view_layer.update()
            candidate = mesh_snapshot(temporary, bpy.context.evaluated_depsgraph_get())
            temporary_data = temporary.data
            bpy.data.objects.remove(temporary, do_unlink=True)
            if temporary_data.users == 0:
                (bpy.data.meshes if isinstance(temporary_data, bpy.types.Mesh) else bpy.data.curves).remove(temporary_data)
            before_dissolve = len(candidate.loop_triangles)
            bm = bmesh.new()
            bm.from_mesh(candidate)
            # Explicit sharp/open boundaries are excluded; material, UV, normal
            # and seam delimiters protect shading and future image artwork.
            edges = [edge for edge in bm.edges if not edge.is_boundary and edge.smooth and not edge.seam]
            bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(config["planar_dissolve_degrees"]), use_dissolve_boundaries=False, verts=list(bm.verts), edges=edges, delimit={"NORMAL", "MATERIAL", "SEAM", "SHARP", "UV"})
            bm.to_mesh(candidate)
            bm.free()
            candidate.update()
            candidate.calc_loop_triangles()
            if len(candidate.loop_triangles) < before_dissolve:
                actions.append({"kind": "planar_dissolve", "before_triangles": before_dissolve, "after_triangles": len(candidate.loop_triangles), "angle_degrees": config["planar_dissolve_degrees"]})
            original_box = millimetres(bounds(original_vertices))
            record = {"object": obj.name, "component": group_id, "operation": obj.get("json_operation", obj.type), "source_vertices": len(source.vertices), "source_triangles": len(source.loop_triangles), "source_bounds_z_up_mm": original_box, "actions": actions}
            if len(candidate.loop_triangles) >= len(source.loop_triangles):
                record.update({"status": "unchanged", "reason": "Candidate does not reduce triangle count", "optimized_vertices": len(source.vertices), "optimized_triangles": len(source.loop_triangles), "optimized_bounds_z_up_mm": original_box, "maximum_sampled_deviation_mm": 0.0, "maximum_bound_delta_mm": 0.0})
                bpy.data.meshes.remove(candidate)
                overrides[obj.name] = source
            else:
                difference = sampled_surface_difference(source, candidate, obj.matrix_world, config["surface_samples_per_direction"])
                protected = any(obj.name.startswith(prefix) for prefix in config["protected_object_prefixes"]) or any(obj.name.endswith(suffix) for suffix in config["protected_object_suffixes"])
                bound_limit = config["protected_object_bound_delta_mm"] if protected else config["max_object_bound_delta_mm"]
                reasons = []
                if difference["maximum_sampled_deviation_mm"] > config["max_sampled_surface_deviation_mm"]:
                    reasons.append("Sampled surface deviation exceeds limit")
                if difference["maximum_bound_delta_mm"] > bound_limit:
                    reasons.append("Object bound delta exceeds protected limit" if protected else "Object bound delta exceeds limit")
                if component.startswith("prop_"):
                    origin = parent.matrix_world.translation
                    before_radius = max(math.hypot(p.x - origin.x, p.y - origin.y) for p in original_vertices)
                    candidate_points, _ = mesh_surface(candidate, obj.matrix_world)
                    after_radius = max(math.hypot(p.x - origin.x, p.y - origin.y) for p in candidate_points)
                    difference["maximum_swept_radius_delta_mm"] = abs(before_radius - after_radius) * 1000
                    if difference["maximum_swept_radius_delta_mm"] > config["propeller_max_swept_radius_delta_mm"]:
                        reasons.append("Propeller swept radius changed")
                record["candidate_comparison"] = difference
                if reasons:
                    record.update({"status": "reverted", "reason": "; ".join(reasons), "optimized_vertices": len(source.vertices), "optimized_triangles": len(source.loop_triangles), "optimized_bounds_z_up_mm": original_box, "maximum_sampled_deviation_mm": 0.0, "maximum_bound_delta_mm": 0.0})
                    bpy.data.meshes.remove(candidate)
                    overrides[obj.name] = source
                else:
                    record.update({"status": "accepted", "optimized_vertices": len(candidate.vertices), "optimized_triangles": len(candidate.loop_triangles), **difference})
                    bpy.data.meshes.remove(source)
                    overrides[obj.name] = candidate
            records.append(record)
            group_records.append(record)
        source_group_bounds[group_id] = join_bounds([record["source_bounds_z_up_mm"] for record in group_records])
        source_group_vertices[group_id] = sum(record["source_vertices"] for record in group_records)
        print(f"Optimized {group_id}: {sum(r['source_triangles'] for r in group_records)} -> {sum(r['optimized_triangles'] for r in group_records)} triangles; {sum(r['status']=='reverted' for r in group_records)} candidates reverted", flush=True)
    return overrides, records, source_group_bounds, source_group_vertices


def validate_glb(path, groups):
    """Independently parse stored GLB bytes and compare reconstructed group bounds."""
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", raw)
    if magic != b"glTF" or version != 2 or length != len(raw):
        raise ValueError("Invalid GLB header")
    offset, chunks = 12, {}
    while offset < length:
        size, kind = struct.unpack_from("<I4s", raw, offset)
        offset += 8
        if size % 4 or offset + size > length:
            raise ValueError("Invalid GLB chunk")
        chunks[kind] = raw[offset:offset + size]
        offset += size
    gltf, binary = json.loads(chunks[b"JSON"]), chunks[b"BIN\0"]
    if gltf["buffers"][0]["byteLength"] > len(binary):
        raise ValueError("Binary buffer truncated")
    if any("uri" in item for items in (gltf.get("buffers", []), gltf.get("images", [])) for item in items):
        raise ValueError("GLB is not self contained")

    def read_accessor(index):
        accessor = gltf["accessors"][index]
        view = gltf["bufferViews"][accessor["bufferView"]]
        element = {5126: "f", 5123: "H", 5125: "I"}[accessor["componentType"]]
        width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}[accessor["type"]]
        size = struct.calcsize("<" + element * width)
        count = accessor["count"]
        start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        if count * size != view["byteLength"] or start + size * count > len(binary):
            raise ValueError("Accessor length mismatch")
        values = list(struct.iter_unpack("<" + element * width, binary[start:start + size * count]))
        if not all(math.isfinite(v) for row in values for v in row):
            raise ValueError("Nonfinite accessor data")
        return values

    groups_by_id = {group["id"]: group for group in groups}
    checks = []
    actual_boxes = []
    exported_vertices = exported_triangles = primitives = 0
    if len(gltf["nodes"][0]["children"]) != 13:
        raise ValueError("Expected 13 component groups")
    for node_index in gltf["nodes"][0]["children"]:
        node = gltf["nodes"][node_index]
        group = groups_by_id[node["name"]]
        positions = []
        triangle_count = 0
        for primitive in gltf["meshes"][node["mesh"]]["primitives"]:
            points = read_accessor(primitive["attributes"]["POSITION"])
            normals = read_accessor(primitive["attributes"]["NORMAL"])
            indices = read_accessor(primitive["indices"])
            if len(points) != len(normals) or len(indices) % 3 or max(i[0] for i in indices) >= len(points):
                raise ValueError("Triangle indices/normals mismatch")
            if any(abs(sum(v * v for v in n) - 1.0) > 1e-5 for n in normals):
                raise ValueError("Exported normal is not a unit vector")
            if "TEXCOORD_0" in primitive["attributes"]:
                if len(read_accessor(primitive["attributes"]["TEXCOORD_0"])) != len(points):
                    raise ValueError("UV count mismatch")
            positions.extend(tuple(p[i] + node["translation"][i] for i in range(3)) for p in points)
            exported_vertices += len(points)
            triangle_count += len(indices) // 3
            primitives += 1
        actual = bounds(positions)
        expected = group["expected_bounds_y_up_m"]
        error_mm = max(abs(actual[edge][axis] - expected[edge][axis]) * 1000 for edge in ("min", "max") for axis in range(3))
        if error_mm > 0.0001 or triangle_count != group["triangles"]:
            raise ValueError(f"Geometry mismatch in {node['name']}: {error_mm} mm, {triangle_count} triangles")
        group.update({"exported_bounds_y_up_m": actual, "maximum_bound_error_mm": error_mm, "material_primitives": len(gltf["meshes"][node["mesh"]]["primitives"])})
        checks.append({"group": node["name"], "status": "pass", "maximum_bound_error_mm": error_mm, "triangle_count": triangle_count})
        actual_boxes.append(actual)
        exported_triangles += triangle_count
    return {
        "status": "pass", "self_contained": True, "component_count": len(groups),
        "mesh_count": len(gltf["meshes"]), "material_count": len(gltf["materials"]),
        "material_primitives": primitives, "single_pass_draw_calls_upper_bound": primitives,
        "exported_vertices": exported_vertices, "exported_triangles": exported_triangles,
        "bounds_y_up_m": join_bounds(actual_boxes), "group_checks": checks,
        "tolerance_mm": 0.0001,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("output/with_battery/air65_ii.blend"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--mode", choices=("lossless", "optimized"), default="lossless")
    parser.add_argument("--optimization-config", type=Path, default=Path(__file__).with_name("web_optimization.json"))
    parser.add_argument("--save-preview-blend", action="store_true", help="Save the evaluated web meshes with source studio/cameras for visual review; optimized mode only")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    source = args.source.resolve()
    output = (args.output or Path("output/web_optimized/air65-ii.glb" if args.mode == "optimized" else "output/web/air65-ii.glb")).resolve()
    if args.mode == "optimized" and output.is_relative_to(Path(__file__).resolve().parents[1] / "output/web"):
        raise ValueError("Optimized mode cannot overwrite the preserved lossless output/web directory")
    source_sha = sha256(source)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    source_scene = bpy.context.scene
    parents = sorted((o for o in bpy.data.objects if "component_id" in o), key=lambda o: o.name)
    if len(parents) != 13:
        raise ValueError(f"Expected 13 components including battery; got {len(parents)}")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    writer, groups = GLBWriter(), []
    overrides, optimization_records, source_group_bounds, source_group_vertices = {}, [], {}, {}
    optimization_config = None
    if args.mode == "optimized":
        optimization_config = json.loads(args.optimization_config.read_text())
        overrides, optimization_records, source_group_bounds, source_group_vertices = optimize_geometry(parents, optimization_config)
        depsgraph = bpy.context.evaluated_depsgraph_get()
    material_names = sorted({slot.material.name for parent in parents for obj in parent.children for slot in obj.material_slots if slot.material})
    writer.gltf["materials"] = [principled_material(bpy.data.materials[name], writer) for name in material_names]
    material_indices = {name: i for i, name in enumerate(material_names)}
    for parent in parents:
        batches, group = evaluate_component(parent, depsgraph, writer.textured_materials, overrides)
        if optimization_records:
            selected_records = [record for record in optimization_records if record["component"] == group["id"]]
            group["optimized_bounds_z_up_mm"] = group["source_bounds_z_up_mm"]
            group["source_bounds_z_up_mm"] = source_group_bounds[group["id"]]
            group["optimized_evaluated_vertices"] = group["source_evaluated_vertices"]
            group["source_evaluated_vertices"] = source_group_vertices[group["id"]]
            group["source_triangles"] = sum(record["source_triangles"] for record in selected_records)
            group["triangle_reduction_percent"] = 100 * (1 - group["triangles"] / group["source_triangles"])
            group["maximum_sampled_surface_deviation_mm"] = max(record["maximum_sampled_deviation_mm"] for record in selected_records)
            group["bound_delta_mm"] = {edge: [group["optimized_bounds_z_up_mm"][edge][i] - group["source_bounds_z_up_mm"][edge][i] for i in range(3)] for edge in ("min", "max")}
        primitives = [writer.primitive(batches[name], material_indices[name]) for name in sorted(batches)]
        mesh_index = len(writer.gltf["meshes"])
        writer.gltf["meshes"].append({"name": group["id"], "primitives": primitives})
        node = {
            "name": group["id"], "mesh": mesh_index, "translation": group["translation_y_up_m"],
            "extras": {
                "instance_id": group["id"], "component_id": group["component_id"],
                "default_visible": group["component_id"] != "battery",
                "source_object_count": group["source_object_count"],
                "source_bounds_z_up_mm": group["source_bounds_z_up_mm"],
            },
        }
        writer.gltf["nodes"][0]["children"].append(len(writer.gltf["nodes"]))
        writer.gltf["nodes"].append(node)
        groups.append(group)
        print(f"Exported {group['id']}: {group['source_object_count']} source objects, {len(primitives)} material primitives, {group['triangles']} triangles", flush=True)
    writer.gltf["nodes"][0]["extras"].update({
        "source_geometry_fingerprint_sha256": source_scene.get("geometry_fingerprint_sha256", ""),
        "source_blend_sha256": source_sha,
        "source_configuration": "Air65 II Racing, optional LAVA II 280 mAh battery",
        "copyright_notice": "Independent visual reconstruction; brand names identify the reference product. Reference photographs are not embedded.",
    })
    if args.mode == "optimized":
        writer.gltf["nodes"][0]["extras"]["web_optimization"] = optimization_config["name"]
    output.parent.mkdir(parents=True, exist_ok=True)
    writer.write(output)
    validation = validate_glb(output, groups)
    if sha256(source) != source_sha:
        raise RuntimeError("Source blend changed during export")
    if output.stat().st_size >= 25 * 1024 * 1024:
        raise ValueError("Export exceeds the 25 MiB delivery budget")
    metadata = {
        "schema_version": 1, "title": "BETAFPV Air65 II Racing", "configuration": "Air65 II Racing, optional 280 mAh battery",
        "asset": output.name, "asset_sha256": sha256(output), "asset_bytes": output.stat().st_size,
        "source_blend": str(source.relative_to(Path(__file__).resolve().parents[1])) if source.is_relative_to(Path(__file__).resolve().parents[1]) else str(source), "source_blend_sha256": source_sha,
        "export_mode": args.mode,
        "source_geometry_fingerprint_sha256": source_scene.get("geometry_fingerprint_sha256", ""),
        "export_script_sha256": sha256(Path(__file__).resolve()),
        "blender_version": bpy.app.version_string, "coordinate_system": {"units": "metres", "up": "+Y", "forward": "-Z", "right": "+X", "source_to_glTF": "(x, y, z) -> (x, z, -y)"},
        "source_geometry_object_count": sum(g["source_object_count"] for g in groups),
        "source_evaluated_vertex_count": sum(g["source_evaluated_vertices"] for g in groups),
        "nominal_dimensions_mm": {"frame_width": 82.6, "frame_length": 82.6, "frame_height": 15.1, "motor_diagonal": 65.0, "propeller_diameter": 31.0},
        "source_bounds_z_up_mm": join_bounds([g["source_bounds_z_up_mm"] for g in groups]),
        "validation": validation, "components": groups,
        "gltf_extensions": writer.gltf["extensionsUsed"],
        "embedded_textures": writer.image_records,
        "uv_serialization": {"decimal_places": 6, "maximum_normalized_rounding_error": 0.0000005, "note": "Canonicalized after evaluated modifier interpolation for deterministic serialization. At 2048 pixels this is at most 0.001024 pixel per coordinate; geometry and source UVs are unchanged."},
        "web_material_limitations": [
            "Principled base colour, metallic, roughness, alpha, IOR, transmission and clearcoat are preserved as glTF factors. Direct base-colour image textures and active loop UVs are supported; PNG/JPEG bytes are embedded unchanged.",
            "Blender area lights, world illumination, Cycles path tracing and AgX display transform are not part of the model asset. Web lighting and tone mapping will affect appearance.",
            "glTF transmission is a thin-surface approximation: source solid refraction thickness, internal multiple scattering, nested optics and caustics are not reproduced as Cycles renders them.",
            "All source components remain present. Lossless mode retains evaluated surfaces; explicit optimized mode uses geometry-aware sampling with reported deviation checks. Editable source modifiers, curves and text become static mesh surfaces in GLB.",
            "The single-pass draw-call count counts material primitives. Transmission, shadows and other Three.js rendering passes may increase real frame draw calls.",
        ],
        "accuracy_note": "The web asset preserves the completed model; it does not increase the certainty of dimensions estimated from uncalibrated reference photographs.",
    }
    if optimization_records:
        original_triangles = sum(record["source_triangles"] for record in optimization_records)
        optimized_triangles = sum(record["optimized_triangles"] for record in optimization_records)
        summary = {
            "profile": optimization_config["name"], "config_sha256": sha256(args.optimization_config),
            "source_triangles": original_triangles, "optimized_triangles": optimized_triangles,
            "triangle_reduction_percent": 100 * (1 - optimized_triangles / original_triangles),
            "accepted_objects": sum(record["status"] == "accepted" for record in optimization_records),
            "unchanged_objects": sum(record["status"] == "unchanged" for record in optimization_records),
            "reverted_objects": sum(record["status"] == "reverted" for record in optimization_records),
            "maximum_sampled_surface_deviation_mm": max(record["maximum_sampled_deviation_mm"] for record in optimization_records),
            "maximum_component_bound_delta_mm": max(abs(v) for group in groups for values in group["bound_delta_mm"].values() for v in values),
            "deviation_method": "Two-way evaluated vertex and triangle-centroid samples against closest triangle surfaces, capped deterministically per object and direction; not a certified continuous Hausdorff bound.",
            "metrics_file": "optimization-metrics.json",
        }
        metadata["optimization"] = summary
        (output.parent / "optimization-metrics.json").write_text(json.dumps({"summary": summary, "source_blend_sha256": source_sha, "source_geometry_fingerprint_sha256": metadata["source_geometry_fingerprint_sha256"], "configuration": optimization_config, "groups": groups, "objects": optimization_records}, indent=2, sort_keys=True) + "\n")
    metadata_path = output.parent / "model-metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    if args.save_preview_blend:
        if args.mode != "optimized":
            raise ValueError("--save-preview-blend requires --mode optimized")
        for parent in parents:
            for obj in list(parent.children):
                if obj.name not in overrides:
                    continue
                old_name, matrix, collections = obj.name, obj.matrix_world.copy(), list(obj.users_collection)
                obj.name += ".original_for_removal"
                replacement = bpy.data.objects.new(old_name, overrides[old_name])
                for collection in collections:
                    collection.objects.link(replacement)
                replacement.parent = parent
                replacement.matrix_world = matrix
                for key, value in obj.items():
                    replacement[key] = value
                replacement["web_optimization_profile"] = optimization_config["name"]
                bpy.data.objects.remove(obj, do_unlink=True)
        source_scene["web_optimization_profile"] = optimization_config["name"]
        source_scene["web_optimized_geometry_is_not_source"] = True
        source_scene["web_source_blend_sha256"] = source_sha
        bpy.ops.wm.save_as_mainfile(filepath=str(output.parent / "preview.blend"), copy=True)
    print(json.dumps({"asset": str(output), "metadata": str(metadata_path), "bytes": metadata["asset_bytes"], "sha256": metadata["asset_sha256"], "validation": validation}, indent=2))


if __name__ == "__main__":
    main()
