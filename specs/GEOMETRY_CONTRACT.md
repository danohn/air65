# Shared component contract, version 1.0

Every component is plain JSON validated by `component.schema.json`. The assembly chooses instances and their transforms. All authored lengths and locations are **millimetres**, all authored rotations are **degrees**, Euler XYZ. Blender receives metres using one uniform conversion in the renderer.

Top level: `schema_version: "1.0"`, unique `id`, locked `contract`, `description`, `provenance`, `nodes`. Each provenance item has `feature`, `status` (verified/derived/estimated/simplified), `source_ids`, `confidence` (high/medium/low), and `note`.

A node contains `id`, `op`, `material`, `args`, optional `transform`, optional `modifiers`, optional `smooth`, `evidence`, `notes`. Transform keys: `location` (XYZ mm), `rotation_deg` (XYZ degrees), `scale` (XYZ factors). Objects start at the local origin; cylinder/annulus axes are Z and box/cylinder depths are centred about zero. Component and instance rotations are applied after geometry construction.

Every scalar dimension can be a literal or `{ "param": "shared_parameter_id" }`; optional `scale` and `offset` implement only `value * scale + offset`. No expressions, formulas, arbitrary Python or external scripts. Derived dimensions belong in the central registry. Important dimensions must reference that registry. Tiny cosmetic dimensions may be local estimates, explicitly recorded in provenance.

## Supported operations

- `box`: `size: [x,y,z]`. Centred cuboid.
- `cylinder`: `radius`, `depth`, optional `segments` (default 64). Closed.
- `annulus`: `inner_radius`, `outer_radius`, `depth`, optional `segments`. Closed hollow ring.
- `ring_profile`: `profile: [[radius,z], ...]`, optional `segments`. A **closed cross-section** revolved about Z; last profile point connects to first. Ideal for a duct's inner wall, lip and outer wall.
- `sphere`: `size: [x,y,z]` is full diameter per axis; optional `segments`, `rings`.
- `beam`: `start`, `end`, `radius`, optional `segments`. Closed straight cylinder with explicit endpoints.
- `tube`: `points: [[x,y,z], ...]`, `radius`, optional `cyclic`, `smooth` (Bezier automatic handles if true; default false), `resolution`. Editable 3D Curve with round section.
- `ribbon`: `points`, `width`, optional `widths` (one width per point), `width_axis: [x,y,z]`, `thickness`. Closed rectangular-section strip following the path. The width vector is projected perpendicular to the path tangent; thickness follows the cross product. Supply enough points for a smooth curved brace or canopy strap. Optional subdivision can round it, but alters the silhouette.
- `polygon_extrude`: `outline: [[x,y], ...]`, `depth`. A simple non-self-intersecting polygon extruded along Z, centred about zero. No holes; use explicitly constructed annuli or mesh apertures.
- `mesh`: `vertices: [[x,y,z], ...]`, `faces: [[i,j,k,...], ...]`. Editable mesh; normals are consistently recalculated. Indices must be in range.
- `loft_shell`: `sections: [{"y": number, "profile": [[x,z], ...]}, ...]`, optional `closed_profile`, `cap_ends` (both false by default). Matching profile vertex counts are required. Use `solidify` modifier for wall thickness. Omit faces to retain real openings.
- `propeller_blade`: `sections: [{"radius", "chord", "sweep", "z", "twist_deg", "thickness"}, ...]`, `handedness` (+1 or -1), optional `profile_segments` (default 12). Blade runs along +X; the chord/sweep are tangential Y, and pitch rotates the airfoil section. Root and tip are capped. Repeat with Z rotations of 0/120/240 degrees for three blades. Hub is a separate annulus.
- `text`: `body`, `size`, optional `extrude`, `align`. Local XY text, editable Blender font.

Modifiers: `bevel` (mm, three segments), `subdivision` (0–3), `solidify` (mm). Modifier order: subdivision, solidify, bevel. Dimensions with a physically constrained envelope should be checked after evaluation. Prefer explicit opening topology over Boolean cutters.

Material IDs come only from `specs/materials.json`. Components cannot redefine materials or shared dimensions.

Optional node `uv_projection` defines a planar local-millimetre mapping: `axes:[0,1]`, `bounds:[minX,minY,maxX,maxY]`, optional `flip_u`/`flip_v`. Axes are distinct indices 0–2; mapping happens before node/instance transforms. Mesh UVs remain editable and are carried through modifiers. A material may reference a project PNG through `base_color_texture: "assets/textures/name.png"`. Images use sRGB, are packed into the saved Blender file, and their SHA-256 values are included in source-input identity. Printed detail is a surface texture, not a dimensional protrusion. This backward-compatible addition does not revise the frozen architecture contract.

## Ownership and revision

The main agent owns the schema, design specification, material registry, assembly, renderer and integration. The spatial architect owns its designated architecture outputs until handoff. Component agents own only assigned component JSON and any explicitly assigned modelling notes. Architecture changes must be returned to the main agent. Every component carries the same architecture contract string; the resolved build records the exact architecture and geometry SHA-256 digests.

Mesh nodes may carry `args.vertex_normals`: one normalized local-space vector per vertex. The renderer validates count and length, then assigns explicit split normals before modifiers. This permits independently editable, position-matched patches to share smooth boundary normals. It must never be used to conceal gaps. The optimized exporter preserves any custom-normal mesh without retessellation because geometric distance gates alone do not establish shading equivalence. Saved UVs, custom normals and packed image bytes receive separate persistence checks.
