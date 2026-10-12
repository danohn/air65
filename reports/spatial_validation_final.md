# Final spatial-validation closure

Date:12 October2026. This is a targeted follow-up to `spatial_validation_audit.md`; that original audit remains unchanged. Only the reported screw-engagement defect, canopy-parameter coupling, saved-project identity, render provenance and optional-battery fit evidence were revisited. No model or implementation files were modified by this auditor.

**The two actionable geometry/parameter findings from the initial audit are closed in the final geometry.** Remaining qualifications concern the limits of the source evidence and the supported parameter-editing model, not unresolved instances of those two defects.

## Final geometry identity

The current-source calculation matches `output/final/metrics.json`:

- Geometry-input SHA-256: `5928b70183e65d340785ca736d60c3eeb96abc0059d3f0ea36b4f258c0899cfb`.
- Evaluated-geometry fingerprint: `b7717341231c9fe97b6481735403833f0324cb75c8719d1c625e16cca6ba50c1`.

`output/final/reopen_validation.json` reports a successful reopening of the saved `.blend` with that same evaluated fingerprint. The saved project retains691 geometry objects, including633 editable meshes,54 curves and4 font objects,165 modifiers,12 component collections,8 cameras and embedded resolved source JSON. These results substantiate the saved artifact's editability and identity; they are not measurements of the physical aircraft.

## SP-01 closed: screw engagement

Independent inspection of the final evaluated bounds gives the same result for all four assembly screws:

| Check | Final evaluated result |
| --- | ---: |
| Shank bottom | Z11.800000mm |
| Shank top | Z17.980000mm |
| Axial engagement below frame boss top |1.199999mm |
| Axial overlap with head |0.410000mm |
| Shank termination below head top |0.430000mm |
| Screw/boss XY axis separation |0mm at reported precision |

The previous shank floating above the boss and projecting through the head is corrected. Beam endpoints now derive from `frame_mount_top_z−1.2` and `canopy_mount_z+0.78`, so this fix follows the shared layer anchors. The validator adds16 evaluated checks covering XY alignment, boss engagement, head connection and containment for the four screws.

The unchanged0.61mm shank radius is a **schematic thread-core representation**. The publishedM1.4 nominal major thread and1.2mm frame pilot remain distinct. The modeled1.2mm engagement is a chosen reconstruction detail, not a verified screw length, thread profile, material tolerance, torque or functional fastening certification.

## Canopy aperture/leg coupling closed

An independent in-memory parameter perturbation changed only `canopy_antenna_aperture_width` from4.9 to5.0mm. Both left- and right-leg argument structures remained exactly unchanged. Their roots remained at `(−18.0312229203,0,17.2)` and `(+18.0312229203,0,17.2)`mm and coincided with their respective feet. The leg X references now use `frame_mount_cardinal_offset`. A dedicated regression test encodes this case.

This closes the specific unrelated-aperture edit defect. It does not turn the scalar registry into a complete mechanical constraint solver: derived coordinates, trigonometric camera placement and some generated multivariable mesh offsets still require coordinated recalculation or regeneration when their source parameters change.

## Render provenance

The renderer now writes a `render_manifest.json` only after finishing all views. It records the source-input hash and individual SHA-256 values for the PNGs. The validator checks both the source hash and actual PNG bytes against that manifest, closing the earlier file-existence-only provenance gap.

After the final build completed, this auditor directly verified the manifest against the current-source hash and all eight PNG byte hashes: hero, top, front, right, left, rear, underside and reference. Verification passed with no errors. The final build log ends with the same geometry fingerprint listed above. A read-only execution of the current validator returned **87/87 passing numeric checks and a passing render-manifest result**; its file-writing function was replaced only in memory, so this auditor wrote no validation artifact. The integrator had added further evaluated checks beyond the initially planned69, including motor/duct and prop/duct concentricity, motor geometry, FC substrate thickness and camera axial reference depth.

## Optional battery: bounded saved-fit evidence

The saved optional-battery test in `output/with_battery/fit_validation.json` passes. The independently inspected inspection script evaluates the reopened project's meshes, checks body dimensions and tests all12 battery objects against72 frame objects for triangle-surface intersections. It also checks for frame vertices inside the nominal battery-body bounding box.

The evaluated body is approximately **10.000000 ×53.999996 ×6.000000mm** in XYZ, corresponding to the published54mm length,10mm width and6mm height. Its Z bounds are1.200000..7.199999mm. The result reports no detected frame/battery surface intersections and no frame vertices inside the tested body box.

This is stronger evidence than the dry assembly's registry-only opening check, but remains a targeted check of the saved display pose. It is not a general solid-containment proof, an insertion-path simulation or connector-mating validation. The nominal body measurement excludes the connector nose and raised text. The displayed power pigtail is unplugged; electrical connection is not modeled. Cradle form, insertion depth and connector details remain estimates.

## Remaining accuracy and parameter limits

- The verified25.5mm frame mounting pitch and26mm nominal FC pitch remain separate. The0.353553mm radial difference is accommodated by estimated grommet deformation; no manufacturer tolerance or mechanical simulation is implied.
- Passing numeric checks establishes selected source-nominal and declared-model conformance. Camera axial reference depth, motor/prop concentricity and FC substrate thickness now have evaluated-geometry checks in addition to registry relationships. Some aperture/slot relationships still use registry arithmetic; the complete check set does not prove general assembly collision freedom or mechanical fitness.
- The shaft check is now accurately labelled extension-mesh length, with a note that most of it is buried in the installed hub. It is not3.4mm of visible exposed shaft.
- The frame's82.6×82.6×15.1mm envelope remains a frame-only published measurement. Whole-aircraft height, canopy bend, installed Z stack, antenna shape, propeller airfoil and electronics layout remain reference-based estimates.
- The independently verified aperture edit is safe for the mounting legs. Other changes to wheelbase, pitch, tilt or generated hole positions may still require coordinated derived-value updates and mesh regeneration. The report does not promise arbitrary independent scalar edits will preserve all constraints.
- Neither high geometric precision in Blender nor repeatable rendering substitutes for calibrated photographs, physical measurements or original CAD. Real-world manufacturing interchangeability, flight performance and structural strength remain unverified.
