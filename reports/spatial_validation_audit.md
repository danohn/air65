# Independent spatial and dimensional audit

Audit date:12 October2026. Auditor: spatial-architecture agent. Scope: frozen shared architecture, current component JSON, `scripts/validate_model.py`, and the completed dry-aircraft `output/review_v2` build. The main integrator owns all geometry and code changes; this audit changes no model files.

**Finding:** the evaluated reconstruction conforms to the checked principal published dimensions, but the53 passing validator checks do not establish complete mechanical fit or physical-object accuracy. One concrete assembly-screw engagement error was found outside those checks and reported to the main integrator for correction. The installed height, canopy bend, antenna dimensions and numerous small details remain estimates.

## Build identity and freshness

The audit confirmed that `metrics.json.geometry_input_sha256` matched a fresh `contracts.prepare(specs/assembly.json)` calculation before examining the measurements. The build log subsequently contained `AIR65_BUILD_COMPLETE` for the same evaluated geometry fingerprint. This is the revised72-node frame, enlarged estimated2.4mm prop-hub radius, and revised canopy build, not stale first-review geometry.

- Geometry-input SHA-256: `0c6428695c64b9a414b9b216698517fc22d1a44f5dfe85b2b4672b6441bc8376`
- Evaluated-geometry fingerprint: `9276066d5dffff0725766bd5028cfa7f20804a0b37115b33b6252470bb9dd409`
- Evaluated objects:691; evaluated vertices:267,405.
- Blender:5.2.2 LTS. All eight expected view files existed at completion.

The validator was run with its output-writing function temporarily replaced in memory, to respect audit ownership of only this report. It returned53/53 passing numeric checks. No validation output or source file was edited by the auditor. Any later screw correction changes the geometry fingerprint and requires another build/validation; the values below describe the identified review_v2 geometry.

## Independently checked dimensions and placements

| Quantity | Evaluated result | Interpretation |
| --- | --- | --- |
| Frame XY bounds | −41.299995 to+41.299995mm on both axes | Matches published82.6mm frame footprint to floating-point construction precision |
| Frame height and datum | Z0 to15.099999mm | Matches published15.1mm frame-only height |
| Diagonal motor arrangement |65mm nominal; four motor shaft centers exactly coincident with corresponding duct and hub centers in reported world XY | Independently checked motor/duct/hub concentricity, beyond the validator's duct-center proxy |
| Duct upper band |11.299999 to15.099999mm;3.800000mm high | Correct shallow continuous wall; lower basket remains open |
| Duct inner vertex diameter | Approximately32.999996mm | Published33mm ID is represented by a256-sided ring; between-vertex faces lie very slightly inward |
| Four evaluated prop diameters |31.000003806,30.999998358,31.000000259,31.000000953mm | Complete blade vertices, including chord, twist and sweep, remain at nominal31mm envelope within numerical tolerance |
| Hub axial thickness |3.300000mm | Published3.3mm hub value retained after visual radius revision |
| Motor shaft |1mm local diameter;3.4mm modeled length | Published shaft nominals retained; most of this length is inside the hub |
| Camera front center |(0,9.999999,31.499998)mm | Estimated installed location is faithfully rendered |
| Camera PCB center |(0,−3.594617,25.160725)mm |15mm behind front center along selected optical axis |
| Camera barrel |9.999999mm local diameter | Published10mm OD retained |
| Camera PCB |10.999999 ×14mm local outline | Published11×14mm outline retained;0.8mm thickness remains estimated |
| Lens optical axis |(0,0.906307817,0.422618240) |25degree selected elevation reproduced |
| Clamp inner vertex radius |5.099999mm | Nominal10.2mm aperture retained; nominal radial lens gap0.1mm |
| FC substrate |Z14.999999 to15.999998mm | Published1mm PCB thickness retained; XY outline is estimated |
| Whole dry-aircraft evaluated height |54.809998mm | Model output only; no published full-aircraft-height measurement supports this value |

The3D model's numerical agreement must not be described as corresponding real-object measurement accuracy. In particular, five or six decimal places in a renderer metric reflect numerical output, not evidence precision. The rings approximate continuous circles with polygonal faces: the256-sided inner ring's between-vertex inward deviation is about0.00124mm radially. That is immaterial for this visual model and within the present numeric comparison thresholds, but the vertex-radius check is not an analytic continuous-surface measurement.

The FC's24mm nominal central-square estimate produces a shaped, clipped outline rather than an untouched diamond: evaluated substrate span is32×30.2mm, with three corners clipped to avoid filling the lug holes and the front clipped atY14.2. This is compatible with an estimated PCB outline, not a contradiction of any verified board-outline measurement. The24mm parameter should not be advertised as the board's evaluated maximum XY extent.

## Detected fit defect: assembly screws

**SP-01 — correction required before claiming the modeled screws engage the frame.** All four `electronics.assembly_screw_shank_*` meshes occupy approximatelyZ14.25..18.75. The four frame mounting bosses terminate atZ13.0. Consequently each shank stops1.25mm above its boss and never enters the pilot hole. At the other end, the shank projects0.34mm beyond the screw-head mesh, which ends nearZ18.41. Existing validation tests mount-axis spacing but do not test axial engagement or containment, so all53 tests pass despite this defect.

The main integrator was notified and accepted the correction. At the time of this report, a main-owned fix is pending. Suggested model extent: **Z11.8..17.98** (6.18mm depth, centerZ14.89). That enters the boss by1.2mm, overlaps the head startingZ17.57, and ends against the underside of the recess-floor disc atZ17.97..18.07. These lengths are estimated visual hardware construction, not manufacturer screw specifications. They preserve every verified frame dimension and mounting axis.

The existing shank radius0.61mm can represent a simplified thread core; it does not model the publishedM1.4 major thread diameter. The frame's1.2mm pilot must remain unchanged. A future validator should separately test positive boss engagement, shank containment beneath the recess/head, and correct mount axes. It should not assert smooth-cylinder clearance as if a self-tapping threaded fit were a precision slip fit.

## Mounting discrepancy is correctly retained

Frame mounting pitch remains25.5mm. Nominal board-lug pitch remains26mm, with only left, right and rear lugs. Their cardinal radii differ by0.3535533906mm. Evaluated origins confirm both patterns independently. Assembled screws and canopy feet follow frame axes; the silicone-waist geometry follows board-lug centers while its bore/flanges follow frame screws. No global scaling hides the mismatch.

The inferred compliant grommet deformation is plausible assembly geometry, **not a verified manufacturer tolerance or a material simulation**. The canopy feet and silicone occupy slightly overlapping vertical layers because the authored foot center is atZ17.2, also the grommet top. This may represent compression/interference, but the model does not establish actual elastic contact pressure, torque or clamp preload. It must not be described as a validated functional mount.

## Numerical-validation scope gaps

The validator's present claims are appropriately limited at top level, but the following distinctions should remain explicit in the final report:

1. Several checks use registry arithmetic rather than rendered geometry: camera axial depth, nominal collar gap, battery slot height and derived mounting offsets. The corresponding camera origins and collar radius were independently checked in this audit and are consistent. The battery check alone does not prove that an evaluated cradle has that clear opening.
2. The evaluated wheelbase check uses duct-object bounds as its centers. It does not itself verify motor or prop placement. This audit independently found exact reported XY coincidence between all four shaft, hub and duct origins, so the current build is correct at those anchors.
3. The check called "evaluated exposed shaft length" measures the complete shaft mesh, including its buried portion. The verified3.4mm extension is represented, but3.4mm is not externally exposed once the3.3mm prop hub is installed.
4. Neither pass/fail status nor the presence of all images demonstrates complete collision freedom, part connectivity, screw engagement, correct topology, or correspondence to a physical specimen. The architecture's16 constraints are not automatically executed as a general constraint system; the script implements a selected set of checks.
5. Render presence checks file existence. The matching geometry-input hash guards metrics, not the age or identity of each PNG. This audit also checked the completed build-log marker, but a clean output directory or per-render manifest would make rerun provenance stronger.
6. This audit's evaluated metrics cover the **dry assembly**. Optional-battery dimensions and nominal0.7mm side/0.1mm vertical clearances follow the selected specification, but the dry build cannot certify the separately assembled battery and connector's detailed fit. Battery labels, wires and insertion depth remain estimated.

## Parametric limitations

The architecture is a shared scalar registry, not a dependency-solving CAD system. Derived values such as motor-axis offset, duct radius, camera PCB center and mount radii are stored numbers. The renderer resolves a single parameter with scale/offset; it does not recompute trigonometric or multivariable dependencies. A change to wheelbase, camera tilt, frame pitch or source nominal therefore needs coordinated regeneration of dependent registry values and any generated mesh offsets. Editing only one source scalar can produce an inconsistent design while leaving other numbers apparently valid.

There is also a specific unintended coupling in the canopy revision: all65 X coordinates of `canopy.left_leg` reference `canopy_antenna_aperture_width`, including the mounting root. At the frozen4.9mm aperture value the root correctly meetsX−18.0312229mm. Changing only that aperture to5.0mm would move the leg root about0.368mm away from the fixed foot, whose position references `frame_mount_cardinal_offset`. The right side has the analogous issue. This does not invalidate the current frozen geometry, but **independent aperture editing is not safe without regenerating or repairing those references**. The main integrator has been informed.

Frame pad-hole center offsets are another documented limited case: bore circumferences reference shared diameters, but combined bolt-circle/contour offsets were generated for the frozen6.6mm PCD. Arbitrary independent PCD edits require regeneration. This is acceptable for a deterministic configurable reconstruction when stated clearly; it is not a fully constrained mechanical CAD assembly.

## Accuracy conclusion

The current build provides strong numerical evidence for the selected frame footprint, wheelbase, rim opening/band, rotor swept envelope, motor shaft dimensions, PCB thicknesses, camera outline/depth and the preserved mounting-pattern discrepancy. The review_v2 screw-engagement defect should be fixed and rechecked. Remaining accuracy is bounded by uncalibrated reference imagery and estimated installed geometry, especially the Z stack, flexible canopy, propeller airfoil, antenna and electronics layout. A successful visual recreation and a dimension-consistent reconstruction are supported; caliper-level agreement, manufacturing interchangeability and aerodynamic or structural validity are not established.
