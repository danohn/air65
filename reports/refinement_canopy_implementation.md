# Air II canopy refinement implementation

The canopy now uses a continuous formed collar/cap surface, crowned open straps, and foot necks whose boundary samples and surface normals coincide. The implementation follows the scope approved in `reports/refinement_canopy_audit.md`; shared dimensions, camera pose, mounting axes, and arch construction anchors were retained. This is the Air II canopy. Older Air65/Sketchfab canopy features were not imported.

## Deliverables and reproducibility

- `specs/components/canopy.json`: 15 editable nodes, including ten explicit moulded-surface meshes and the five retained clamp hardware/tab nodes.
- `scripts/refine_canopy.py`: deterministic authoring helper. It reads the frozen architecture and retains the existing five hardware/tab definitions, regenerates the moulded surfaces, validates them, then writes only the canopy JSON and its assigned validation output.
- `output/canopy_refinement/authoring_validation.json`: topology, shared-interface, winding, and parameter checks.
- `output/canopy_refinement/component_validation.json`: byte-identical authoring check, dimensions, bounds, and parameter independence results.
- `output/canopy_refinement/isolated_final/`: editable isolated `.blend`, hero/front/right/top PNGs, resolved input, render manifest, metrics and build log.
- `output/canopy_refinement/context_final/`: assembled context `.blend` and hero/reference/front/right/top views using the assembly cameras. Other components reflect the shared workspace snapshot at the time of this context build; the main integration remains authoritative for final assembly review.

Reproduce from the repository root:

```sh
uv run --python 3.14 python scripts/refine_canopy.py
uv run --python 3.14 python scripts/build.py --assembly output/canopy_refinement/isolated_assembly.json --output output/canopy_refinement/isolated_final --resolution 900 --samples 32 --views hero,front,right,top
uv run --python 3.14 python scripts/build.py --assembly output/canopy_refinement/context_assembly.json --output output/canopy_refinement/context_final --resolution 900 --samples 32 --views hero,reference,front,right,top
```

The frozen parameters are consumed when authoring the curved surfaces. If the architecture is intentionally revised later, rerun the authoring helper before rendering so section geometry and its explicit normals are regenerated together.

## Changed geometry

| Node | Final change |
| --- | --- |
| `formed_collar_shoulders_with_vent` | One annular patch network now forms the protective upper cap, side cheeks, four branch roots, and real upper vent. Curved transition contours and tapered ends replace the separate cut-ended brow. |
| `continuous_curved_protective_brow` | Removed. Its protective-lip function is included in the common collar surface. |
| `lens_clamp_annulus` | ID retained; converted from an annulus operation to an explicit annular mesh so its exact inner land and outer boundary can share tessellation/normals with the collar. The 10.2 mm nominal opening, pose and thickness references are preserved. |
| `left_leg`, `right_leg` | Replaced ribbon operations with crowned explicit surfaces. The long paths are unchanged; widths flare into collar roots and mounting necks. |
| `formed_front_tongue_with_slot` | Crowned surface with a genuine through slot and matching collar/foot interfaces. |
| `formed_rear_arch_with_rounded_apertures` | Crowned cross-section along the frozen arched path. Three small adjustment holes, narrow slot, 4.9 mm oval and upper rounded trapezoidal opening retain their order. The upper root becomes part of the common collar web. |
| `foot_front`, `foot_rear`, `foot_left`, `foot_right` | Rounded pads become necks meeting the incoming strips, rather than separate overlapping washers. IDs and exact central screw axes are unchanged. |

The old rear-path terminal remains an unchanged construction anchor. A draft forced that point onto one upper skin vertex and produced a visible brow dimple; the main agent approved removing that artificial skin constraint. The smooth root now passes into the collar without changing the stored anchor or the actual clamp, pose or opening constraints.

Open side triangles, the exposed PCB region and all through openings remain open. No closed shell was added over the electronics.

## Continuous interfaces and explicit normals

Independent smooth shading on touching objects initially left false seams, even when positions matched. The authorer now matches both sides of every interface and removes T junctions, computes an edge-orientation traversal on the positionally joined shell, verifies positive outward signed volume, and derives angle-weighted vertex normals on that physical surface. It transforms those normals back to each editable object's local space. The main agent added schema/renderer support for `mesh.args.vertex_normals` and preservation of authored face winding for those explicit meshes.

This is not a normal-based gap concealment: at a 0.0000001 mm positional tolerance, the ten moulded meshes form one connected, closed shell, and all 19,276 joined edges have exactly two incident faces. Each strip/foot and strip/collar interface shares 14 vertices; the clamp/collar interface shares 264. The separate editable meshes intentionally have open interface edges, which close only when their matching neighbouring patches are considered together. Unrelated tabs and metal fasteners are separate retained geometry.

The shell contains 9,968 stored mesh vertices before joining duplicate interface samples. All explicit normal lengths are within approximately 0.000000000001 of one. A draft with conflicting local normal recalculation caused black patches; it was rejected. The final isolated renders show no such black patches, and the artificial brow dimple is removed.

## Retained measurements and estimates

| Feature | Value | Status and source/confidence |
| --- | --- | --- |
| Lens clamp clear nominal diameter | 10.2 mm | Verified manufacturer canopy drawing; high confidence. Mesh inner-circle vertex radius measures 5.099999999998 mm. |
| Front canopy mounting bore | 1.5 mm | Verified canopy drawing; high confidence. Other foot bore diameters remain symmetry estimates. |
| Clamp screw bore | 1.1 mm | Verified canopy drawing; high confidence; original tab definitions retained. |
| Oval antenna opening width | 4.9 mm | Verified canopy drawing; high confidence; inner-edge vertices retain `canopy_antenna_aperture_width` references. |
| Four mounting origins | `(0, ±18.0312229203, 17.2)` and `(±18.0312229203, 0, 17.2)` mm | Frozen assembly architecture derived from the frame mounting arrangement. Unchanged. |
| Clamp origin | `(0, 8.1873844259, 30.6547634765)` mm | Frozen camera/collar alignment. Unchanged. |
| Clamp local-Z rotation | X = −65° | Derived from the selected optical direction at +25° camera tilt. Unchanged. |
| Rear arch peak construction point | Y = −2, Z = 39.4 mm | Image-derived estimate from the shared architecture. Unchanged. |
| Wall thickness / shallow crown | 0.65 / 0.055 mm | Estimated section values. Thickness reference retained; crown is a local refinement estimate. |
| Cap depth, cheek width, root taper and detailed opening contours | Explicit surface controls in authoring helper | Image-derived estimates, medium confidence in overall form, lower confidence in unmeasured local curvature. |

Actual moulded mesh bounds are X `[-20.2298621, 20.2298621]`, Y `[-20.2283126, 20.0086447]`, Z `[16.8634892, 39.7527308]` mm. The maximum surface height includes wall thickness and section crown above the construction path. These values were sent to the main agent for reconciliation of the estimated `canopy_half_width` metadata; this agent did not change that shared scalar.

## Visual evidence and limitations

The shape decisions use `references/air_ii_canopy_structure.webp` and `references/air_ii_canopy_side.webp` (left Air II panels only), `air_ii_canopy_black.webp`, the canopy drawing, and Air65 II Racing/physical photos. The black product canopy is particularly useful for the merged collar-to-leg transition; physical white/translucent photos are more useful for the assembled silhouette. Their camera angle, material and mounting deformation differ, so they do not support a precise millimetre claim for every local curve.

The main visible improvement is the continuous cap/cheek/root form with preserved real apertures. Individual foot necks and shoulder transitions are now geometrically connected with matching normals. Fine curvature and local section thickness remain estimated, and the final assembly still needs the independent matched-view review led by the main agent. This does not establish mould-tool or production-part accuracy. The final isolated renders use the main agent's current estimated canopy material (roughness 0.26, transmission 0.46); this agent did not edit materials, lighting, renderer or schema.

## Validation result

- JSON schema, parameter resolution, unique IDs, face indices, nondegenerate faces, joined surface orientation, joined edge incidence and all explicit normal lengths passed.
- Re-running the authoring helper produced byte-identical canopy JSON. SHA-256: `3ba42266ce0ac07e2137880b7a3ea7e134096eabfec0303e50dff7f55d639aa5`.
- Changing only the antenna aperture parameter from 4.9 to 5.0 mm left both leg meshes and foot transforms unchanged.
- `uv run --python 3.14 pytest tests/test_contracts.py -q`: **16 passed**. Main updated the legacy ribbon-point assertion to mesh-argument and mounting-transform invariance, because the legs now use explicit meshes.
- Headless Blender 5.2.2 LTS constructed and rendered the final isolated project without mesh repair or validation failure. Final in-context views use the same deterministic interpreter.

No camera, electronics, shared architecture, shared material, renderer, schema, site or test file was modified by this subagent during this implementation pass.
