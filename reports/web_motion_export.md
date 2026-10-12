# Air65 II web motion export

The motion-capable GLB preserves the completed static web model at zero angle. The change separates moving motor parts from stationary parts, and separates propeller blades from hubs. It changes node organization and batching only. The editable Blender source and component JSON files were not modified.

The delivered asset is [air65-ii.glb](../output/web_motion/air65-ii.glb), with [model-metadata.json](../output/web_motion/model-metadata.json), [motion-validation.json](../output/web_motion/motion-validation.json), and [Khronos validation](../output/web_motion/gltf-validator.json). The exporter is [export_web_model.py](../scripts/export_web_model.py); targeted tests are [test_web_rotors.py](../tests/test_web_rotors.py).

The authoritative motion configuration is [specs/studio/motion.json](../specs/studio/motion.json), SHA-256 `f0402b8123a48798f87c3265003f4a59859fbc1c9e83c32eff9d78b18da58ddb`. The exporter reads its exact motor part membership and corner signs, and checks those signs against the numerical handedness and twist of all three blades at each corner. It does not derive direction from the historic `prop_cw` and `prop_ccw` component names.

| Property | Frozen static baseline | Motion export |
|---|---:|---:|
| Component anchors | 13 | 13 |
| Meshes | 13 | 21 |
| Material primitives | 72 | 84 |
| Triangles | 262,810 | 262,810 |
| Exported vertices | 206,782 | 206,782 |
| Materials | 30 | 30 |
| Embedded images | 5 | 5 |
| File bytes | 10,417,808 | 10,441,784 |

The extra 12 primitives permit independent rotor motion and blade visibility. Primitive count describes one geometry pass; transmission, shadows and other renderer passes can increase actual draw calls. There are no baked animation channels. The browser supplies the rotation angle at runtime.

The existing anchors remain `battery`, `camera`, `canopy`, `electronics`, `frame`, `motor_FL`, `motor_FR`, `motor_RL`, `motor_RR`, `prop_FL`, `prop_FR`, `prop_RL`, and `prop_RR`. Only these anchors carry `instance_id`. Component visibility and exploded positions should continue to act on them.

Each motor now has two identity-transform children, for example:

```text
motor_FL                       unchanged component anchor
  motor_FL_rotor               extras.motion_role = "rotor"
  motor_FL_stator              extras.motion_role = "stator"
```

The rotor child contains exactly nine source objects: `silver_bell`, `bell_lower_rolled_edge`, `open_purple_crown_rim`, `purple_crown_spoke_1`, `purple_crown_spoke_2`, `purple_crown_spoke_3`, `crown_center_boss`, `upper_shaft`, and `lower_axle_tip`. Each motor's rotor contains 2,148 triangles; its remaining 37 objects contain 24,688 triangles and stay stationary. This retains the copper windings, stator, bushings, mounts, screws and electrical terminals. Membership follows source object identity, because stationary and rotating pieces share some purple and steel materials.

Each propeller retains its existing anchor as its rotor transform:

```text
prop_FL                        extras.motion_role = "rotor"
  prop_FL_blades               extras.surface_role = "blades"
  prop_FL_hub                  extras.surface_role = "hub"
```

The blades child contains precisely `blade_1`, `blade_2`, and `blade_3`, totaling 4,596 triangles. The other five source objects—the barrel, shaft socket and three radial webs—remain in the hub child, totaling 1,284 triangles. Both children rotate with the propeller anchor. Hiding the blade child for a blur preview keeps the hub and socket visible. Children do not add `instance_id` or duplicate component anchors.

All rotor nodes include `rotation_axis: [0, 1, 0]` and `angular_sign`. Coordinates use metres, glTF +Y up, +X right and −Z forward. The motor and propeller pivot at each corner share the same unchanged X/Z coordinate; pivot Y is zero, which lies on the same vertical shaft axis as the geometry.

| Corner | Local angular sign about +Y | Anchor X, Z in metres |
|---|---:|---|
| FL | +1 | −0.02298097126185894, −0.02298097126185894 |
| FR | −1 | +0.02298097126185894, −0.02298097126185894 |
| RL | −1 | −0.02298097126185894, +0.02298097126185894 |
| RR | +1 | +0.02298097126185894, +0.02298097126185894 |

The initial propeller and motor phases are already baked into their vertices. New child transforms are identity. Set runtime quaternion to the saved initial quaternion multiplied by a rotation about local +Y; do not reapply the original assembly phase angles or rotate the complete motor anchor. Resetting the angle to zero reconstructs the static pose exactly.

Each semantic child includes geometry-derived local bounds and radial extents in `extras.geometry`, plus source names and triangle count. For the FL blade group, outer vertex radius is `0.015500001268085187` m, inner vertex radius is `0.002137326242627353` m, local Y range is `0.011519990861415863` to `0.013925885781645775` m, and its bounds center/height are `0.012722938321530819` / `0.002405894920229912` m. Other propeller results differ only at floating-point scale. These are extrema of mesh vertices; an inner vertex radius is not a certified minimum distance to every point of every triangle. Deriving a radial coverage texture from the actual triangles, as the viewer does, captures the blade footprint more faithfully than an arbitrary filled disc.

The asset was generated with Blender 5.2.2 LTS. The command below records the local frozen reference used for the audit. After restoring v0.1.0 in a fresh clone, use `--compare-static-glb output/web_optimized/air65-ii.glb` instead; it has the same reference hash and is included in that release.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/export_web_model.py -- \
  --source output/with_battery/air65_ii.blend \
  --mode optimized \
  --motion-spec specs/studio/motion.json \
  --compare-static-glb output/web_motion/static_reference.glb \
  --output output/web_motion/air65-ii.glb
```

`--motion-spec` is optional. Omitting it retains the original static hierarchy and material batching. The default export mode remains `lossless`; the command above explicitly uses the existing bounded optimization profile to match the current web asset. Motion partitioning itself neither simplifies nor moves geometry. The same motion flag is also available with lossless mode. The exporter writes only the requested output files and checks that the source Blender file hash is unchanged.

The source is `output/with_battery/air65_ii.blend`, SHA-256 `1c9424baa3c92dde8e2ff1fc77fa05cf8c3136f20f21e76cee3351ad59b63e8a`, with recorded source geometry fingerprint `da3ecbc92189f1d4569bfa665412e2d0746c78d1c33aa5207f0bf989193875e4`. The motion GLB SHA-256 is `4721b58072d8f5cacca84b873e626163061e4317ec158477046d85d49a332b2d`. The frozen static reference SHA-256 is `8ddbc0195e22c59bc8dcf6de34885021e5cc099aea5b33a08817a11a7b6395a7`.

Validation compares every exported triangle attribute against the frozen static GLB, independently of new batching or index ordering. Per-triangle fingerprints include material name, serialized position, split normal, UV where present, and winding. Per-component multiset hashes retain triangle multiplicity. The comparison also requires identical anchor translations, material JSON and embedded image bytes. All 13 components pass. All mesh bounds checks pass at a serialization tolerance of 0.0001 mm. The complete zero-angle bounds remain X/Z ±0.04129999876022339 m and Y 0 through 0.05481000244617462 m.

Semantic validation separately checks exact source membership, complete and nonoverlapping rotor/stator and blade/hub coverage, identity child transforms, the eight intended rotor transforms, and geometry fingerprints for each role before and after batching. Negative tests reject a shifted child pivot, a complete motor incorrectly marked as rotating, swapped rotor/stator geometry, duplicate rotor IDs, reversed corner signs, and numerical blade pitch that disagrees with the authority.

`uv run pytest -q tests/test_web_rotors.py` passed all 12 targeted tests. `uv run pytest -q` passed all 48 project tests. The static regression export, made without `--motion-spec` into `output/web_motion/static_regression/`, reproduced the frozen reference byte for byte, including its SHA-256 above. A second motion export under `output/web_motion/repeat/` also reproduced the delivered motion asset byte for byte. The source-preservation, static-regression and motion-repeatability hash checks are recorded in [regression-checks.json](../output/web_motion/regression-checks.json).

Khronos glTF Validator 2.0.0-dev.3.10 reports zero errors and zero warnings. Its three informational messages concern one 1536 × 320 image and 192 pre-existing degenerate electronics triangles across two primitives. These surfaces and image bytes were intentionally retained to preserve the static model; the motion split introduced neither issue. Material factors, supported transmission/IOR/clearcoat extensions, active loop UVs and all five base-color image bytes are unchanged. Existing web-versus-Cycles lighting and thin-surface transmission limitations still apply.

The read-only review of `site/dist/rotor-motion.js` confirmed the local axis and signs, metre-to-viewer-unit cancellation when deriving the blur footprint, inherited exploded positions/visibility, preserved hub rotation, and zero-angle reset. The built-in physical material supports the viewer's logarithmic depth path. One integration finding was sent to the main agent: Three.js raycasting does not honor node visibility or texture alpha, so invisible square blur proxy geometry can intercept selection. Disable raycasting on the proxy and exclude hits beneath hidden ancestors. Browser appearance and actual runtime performance checks remain the main agent's integration responsibility.

This validation establishes an unchanged zero-angle web surface and correct semantic motion partitioning. It does not establish measured rotor mechanics, aerodynamic performance, or photographic shutter integration. The inexpensive blur remains a documented coverage approximation. Published dimensions and the confidence of estimated component geometry retain the qualifications in the original design and validation reports.
