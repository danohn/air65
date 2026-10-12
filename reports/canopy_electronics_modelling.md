# Canopy, camera and electronics component handoff

Contract: `air65-ii-racing-v1`. Each component is authored in the shared aircraft coordinate system and must be instantiated with an identity transform. No shared architecture, renderer or material file was modified.

| File | Objects | Geometry |
|---|---:|---|
| `specs/components/canopy.json` | 16 | Four bored feet, flowing side legs, a continuous slotted front tongue, a continuous perforated rear arch, formed collar shoulders, a real upper vent, protective brow and cross screw |
| `specs/components/camera.json` | 69 | Shaped camera PCB, exposed component rows, sensor mount, stepped focusing barrel, recessed front cup and optical elements |
| `specs/components/electronics.json` | 318 | Diamond PCB with three bored lugs, eccentric grommets, screws, mapped electronic packages and contacts, motor connectors/wires, camera harness, tube antenna, power pigtail |

The relatively high electronics count comes primarily from orderly solder-contact rows and passive terminations around explicitly placed packages. Chip positions do not use a random distribution. All nodes are separately editable and named; component collections can be hidden independently.

## References inspected

The actual physical photographs `photo_racing_oblique.webp` and `photo_freestyle_side_oblique.webp` were inspected before authoring. They establish the open canopy, exposed camera PCB, substantial thin arch, black tube antenna and wire harnesses. `air_ii_canopy_black.webp`, `air_ii_canopy_diagram.webp` and the left panel of `air_ii_canopy_side.webp` establish the flattened strap topology, split front tongue, lens clamp, small hood vent and flexible installed curvature. The old-generation canopy in the right panel was excluded.

`air65_ii_racing_oblique.webp` guided the current white/lavender Racing assembly details. `air65_ii_electronics.webp` and `fc_diagram.jpg` establish the three-point PCB and named package neighbourhoods. `camera_diagram.jpg` establishes the C03 V2 dimensions and visible barrel/PCB structure. These images are already indexed by the central reference manifest and source registry; no new unsourced product variant was introduced.

## Dimension and confidence handling

| Feature | Authority | Representation |
|---|---|---|
| Camera PCB 11 × 14 mm | Verified C03 manufacturer dimension image | A shaped outline includes the lower tab; broad body does not become a generic rectangular camera housing |
| Lens outside diameter 10 mm | Verified C03 manufacturer dimension image | Front lens cup maximum radius references `camera_lens_radius` |
| Camera optical-axis depth 15 mm | Verified C03 manufacturer dimension image | Lens plane and PCB-reference plane use the two frozen architecture anchors |
| Camera tilt 25° | A documented available setting, selected as an assembly estimate | Every camera rotation uses `camera_tilt_deg`; cylinder Z axes rotate by tilt minus 90°, giving +Y forward and +Z elevation |
| Clamp bore 10.2 mm | Verified canopy drawing | An open annulus references `canopy_clamp_inner_radius`; nominal radial gap to the lens is 0.1 mm |
| Front bore 1.5 mm and clamp cross bore 1.1 mm | Verified canopy drawing | Real annular openings; side/rear foot bores are an explicit symmetric reconstruction assumption |
| Antenna aperture width 4.9 mm | Verified canopy drawing | Rear rail centers in the widened portion leave a nominal 4.9 mm opening before edge fillets |
| Canopy mounting plane 17.2 mm, arch centerline peak 39.4 mm | Shared image estimates | Feet and path samples reference the registry; actual strip surfaces extend by approximately half their 0.65 mm thickness around centerlines |
| FC substrate 1.0 mm | Verified FC specification | Substrate spans z15–16; these installed Z locations remain estimates |
| FC mounting pitch 26 mm | Verified FC specification | Only left, right and rear lugs are present at nominal PCB axes |
| Assembled screw pitch 25.5 mm | Verified frame specification | Screws, grommet bores and canopy feet use the frame axes |
| Grommet radial deformation 0.353553 mm | Derived discrepancy; physical accommodation unverified | Mesh waist outer centers follow the nominal PCB lugs while bore and flange centers follow frame screws; no board or frame rescaling hides the discrepancy |
| FC body side approximately 24 mm | Shared image estimate | Diamond outline with a clipped front and clipped side/rear tips joining bored lugs |
| Antenna endpoints, radii and heatshrink taper | Shared image estimates | Beam references the frozen base and tip, and a hollow tapered profile surrounds its lower portion |

All important dimensions and assembly positions remain JSON parameter references. Small package sizes, pin widths, screw-head details, curvature samples and cable routing are explicitly estimated or simplified in each component's provenance. A component JSON is data only: no Python expression or executable text is needed by the renderer.

## Geometric choices and limitations

The revised canopy has a continuous thin rear strap around real rounded trapezoidal, oval, capsule and adjustment apertures. Its front tongue is also one continuous thin mesh around a long rounded slot. There is no hidden surface filling the arch windows, tongue slit, lens aperture or open side triangles. A shallow formed collar shoulder wraps the lens aperture, with a real vent above the lens and a continuous thin curved protective brow. These unmeasured surface contours remain photo estimates. Centerline sampling is bounded so that it does not overshoot the selected arch peak; bevels and half thickness still affect the final surface envelope.

The C03 lens is stepped and recessed. Its front cup stops at the shared lens-front plane. Small optical elements and coating rings sit behind that plane. The glass materials convey the observed optical appearance; this is not an optical prescription. The PCB edge and both solder masks are visible. The focusing-ring pitch, mount block, pad and passive dimensions are visual estimates.

The FC's main regions follow the labelled source: STM32 at left-forward, gyro and MM32 forward, VTX processor right-forward, flash left-rear, ESP/SX rear, u.FL central-forward and CAM IN central-right. Package and pin count accuracy is deliberately lower than silhouette accuracy. Underside packages are a restrained schematic arrangement. These shapes are not a verified electrical board layout.

Motor wires leave the inboard motor bases near z4.5 and route to four underside white connectors. Their visible routes stay beneath the rotor plane while crossing motor-disc regions. Camera wires are red, black and yellow. The antenna feed passes behind the camera. Harness paths are shortened visual representations; they do not claim to preserve the published loose wire length or electrical connectivity.

The white/blue power pigtail is displayed unplugged behind the rear canopy mount. The separate optional battery model is not mechanically connected by this geometry. This is a documented display-pose limitation for the battery-equipped assembly.

## Validation completed

1. Each JSON passed `Draft202012Validator` against the shared `component.schema.json`.
2. All node IDs were unique within their components, every material existed in the shared material registry and every scalar parameter reference resolved against the frozen architecture.
3. Every node was constructed successfully through the actual `scripts/blender_render.py` interpreter in local Blender 5.2.2 LTS, using background mode and `--python-exit-code 1`. The check reported 24 canopy, 69 camera and 318 electronics nodes without requiring mesh repairs or encountering unsupported operations.
4. Following that check, the rear aperture X coordinates were explicitly bound to the aperture-width registry parameter and the PCB front clipping Y coordinates were explicitly bound to `fc_front_clip_y`; these reference-only substitutions retain the same numeric geometry and all three JSON files passed validation again.

The integrated assembly render and independent visual review remain the main integrator's responsibility. Highest-value review targets are the arch's front connection to the collar, side-leg curvature, camera front height and apparent FC density. Exact mould fillets, hidden electronics and complete harness lengths should not displace silhouette corrections.

## Integrated-render correction: PCB surface visibility

The main integrator identified that the camera's first solder-mask layers lay just inside the opaque substrate and therefore rendered as an olive board. The first integrated hero was inspected and confirmed the issue. Both 0.016 mm camera mask layers now sit at ±0.409 mm optical offset from the PCB reference plane, just outside the nominal ±0.4 mm substrate faces. This changes the cosmetic finish only; the registered PCB width, height, substrate thickness and 15 mm optical reference depth are unchanged.

The FC masks originally ended exactly coplanar with the substrate faces. To avoid coincident surfaces, they are now 0.012 mm thick, centered at z16.006 and z14.994, immediately outside the verified 1.0 mm substrate. The painted finish adds at most 0.012 mm to each physical surface and is not represented as a change to the nominal substrate measurement.

All three component files passed schema/reference/material checks again, and all 411 nodes were reconstructed successfully through the actual headless Blender interpreter after this correction.


## Independent-review revision: formed canopy silhouette

The independent review identified the canopy as the largest remaining shape error: the first top render read as a ladder of narrow rails around a exposed circular collar. The `hero`, `top` and `right` renders were rechecked against `air_ii_canopy_black.webp`, `air_ii_canopy_diagram.webp`, the **left Air II panel only** of `air_ii_canopy_structure.webp`, and the two physical reference photographs.

The replacement keeps every shared anchor and nominal measurement. It changes the local estimated surface construction as follows:

- The rear arch is now one closed thin mesh with genuine rounded trapezoidal, oval, narrow slot and small adjustment apertures. Its outer width grows smoothly toward the lens. No separate crossbars produce rectangular ladder windows.
- The nominal oval opening reaches 4.9 mm clear width at its widest sampled section. Its coordinates remain linked to `canopy_antenna_aperture_width`.
- The front tongue is one shaped strip around a long rounded slot, with a solid land near its mounting foot and clamp.
- Side legs retain the exact frozen centerlines and foot endpoints, widening smoothly into the collar shoulders.
- The lens collar has broader shallow formed shoulders and a true vent immediately above the aperture. A continuous thin curved brow protects the upper lens half. The 10.2 mm circular clamping aperture is retained, and the camera PCB remains exposed from the sides and rear.

The revised canopy contains 16 named editable objects. Every new explicit mesh passed an authoring topology check: each face has distinct valid vertex indices and every closed-mesh edge has exactly two incident faces. This checks the intentional aperture walls as well as outer surfaces. The JSON also passed the shared schema, parameter-resolution and duplicate-ID checks. All 16 canopy nodes then constructed successfully through the actual local headless Blender interpreter.

Only `specs/components/canopy.json` and this report were modified in this revision pass. Camera/electronics JSON were read for a constructor check but not written; subsequent optical-stack work belongs to the main integrator. The revised canopy is ready for the second integrated render and independent visual reassessment.
