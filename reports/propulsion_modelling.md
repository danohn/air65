# Air65 II Racing propulsion modelling handoff

This component handoff follows frozen contract `air65-ii-racing-v1`. Initial ownership was `specs/components/motor.json`, `prop_cw.json`, `prop_ccw.json`, and this report. The independent-review revision changes only the two propeller files and this report; `motor.json` is unchanged. No architecture, material, schema, or renderer file was changed.

## Assembly contract

All three components use the motor axis as local XY origin, and **frame world datum as local z=0**. Translate instances in XY only. The motor mounting screws follow the +Y-first triangle at 90, 210 and 330 degrees on the 6.6 mm bolt circle. Rotate motor instances to match the frame agent's pad rotations (FL/RL +30 degrees; FR/RR -30 degrees); rotate propeller instances independently if desired. CW/CCW names are a modelling convention: JSON `handedness` is +1/-1 respectively and gives exactly mirrored rotor geometry. No flight-controller motor numbering or motor output configuration is implied.

## Important dimensions and evidence

| Feature | Model value | Evidence status |
|---|---:|---|
| Motor maximum outside diameter | 9 mm | Published motor family drawing; high confidence |
| Motor base to shaft shoulder | 8.55 mm | Published motor family drawing; high confidence |
| Exposed shaft | 1 mm diameter, 3.4 mm length | Published drawing/product; high confidence |
| Motor mounting circle | 6.6 mm, three axes | Published frame/motor dimensions; high confidence |
| Motor base z | 2.7 mm | Frozen assembly estimate; medium confidence |
| Silver bell only | z=5.75 to 9.32 mm | Image-based subdivision; medium confidence |
| Shaft shoulder / tip z | 11.25 / 14.65 mm | Derived from shared nominal sizes and estimated base |
| Propeller swept diameter | 31.000000 mm | Published nominal plus computed geometry validation |
| Maximum blade section chord | 6.8 mm | Published nominal |
| Hub height / through bore | 3.3 mm / 1 mm | Published nominal |
| Hub lower / upper face z | 11.35 / 14.65 mm | Frozen shared assembly estimate / derived placement |
| Hub outer radius | 2.4 mm | Shared visual estimate; PR-02 centrally approved revision |
| Blade actual z interval | 11.517568 to 13.927714 mm | Estimated surface, calculated after twist |

The important published dimensions are JSON parameter references. Cosmetic subdivisions use documented local values or proportional parameter references. Exact manufacturing tolerances remain unknown.

## Visual form

The family diagram clearly shows that the 8.55 mm body height includes the lower base, terminal plate, neck, short silver bell, raised top crown and shaft shoulder. Modelling the whole height as a silver cylinder would make a visibly incorrect motor. The reconstruction keeps those parts separate. The upper crown has a genuine open center, curved purple spokes, and visible individual copper windings. The lower hardware includes visible screw heads with physical cruciform recesses. External motor wires and their connector are intentionally assigned to assembly integration.

The GF1207 has broad rounded blades with curved edges, a swept root, taper and spanwise twist. Each revised blade uses 61 stations and 48 profile samples, with an elliptical closed section. The two rotor files mirror handedness without changing the envelope. The hub is an outer annulus plus a central bored socket and three radial webs, leaving three genuine apertures. It is not a solid transparent cylinder.

## Validation performed

- All three files passed the shared Draft 2020-12 JSON Schema.
- Every scalar reference resolved against the frozen architecture and every material ID exists in the shared registry.
- Node IDs are unique per component. Component IDs and contract match the requested names.
- The exact `propeller_blade` sampling formula from `scripts/blender_render.py` was reproduced against final JSON. Both hands give maximum radius **15.499999999999 mm**, maximum chord **6.8 mm**, and matching z limits. Planar cap interiors cannot exceed the convex radial bound of their vertices. Blades have no geometry-changing modifiers. Hub bevels remain far inside the blade radius.
- Span normalization factor after PR-01 revision is 1.007633427339; X station coordinates were normalized while preserving chord width. This avoids the common error of setting the station center to radius 15.5 mm and then allowing swept/twisted chord points to exceed that radius.
- This is pre-render geometry validation. Main integration must check evaluated Blender geometry and review the multiview images.

## Remaining estimates and limitations

The exact motor crown topology, subpart heights, coil count/turns, hidden magnets, stator details and screw dimensions were not published. Three crown spokes, nine coil packs and 13 representative turns per coil are visually inferred construction, with low confidence for topology. The silver/purple finish follows current Racing manufacturer imagery; the real review sample uses turquoise accents. Coil curves are editable visual geometry, not an electromagnetic motor reconstruction. No arbitrary etched label was added.

Propeller camber, precise twist, blade thickness, hub outside diameter, side ridges and moulding marks were not available as CAD or calibrated measurements. The elliptical section is explicitly a simplification. The nominal 0.7-inch pitch informed the estimated span twist but cannot uniquely determine it. No aerodynamic or flight-ready replacement claim is made.

## Sources

- [BETAFPV 0702 motors 2026](https://betafpv.com/products/0702-brushless-motors-2026), family dimensions in `references/motor_diagram.jpg`.
- [BETAFPV GF1207 three-blade propellers](https://betafpv.com/products/gemfan-1207-3-blade-propellers-1-0mm-shaft), outline in `references/prop_diagram.jpg`.
- Current Racing close-up `references/air65_ii_racing_propulsion.webp`; underside `references/air65_ii_racing_underside.webp`.
- Physical appearance cross-check `references/photo_racing_oblique.webp`, from the first-hand review listed in the shared reference manifest.


## Independent review revision: PR-01 / PR-02

The first rendered top view was independently compared to the GF1207 diameter diagram. Its outer blade chord collapsed too early, producing a pointed leaf silhouette. This revision changes only `prop_cw.json`, `prop_ccw.json` and this report. The motor JSON SHA-256 remained `e17e6fa5fc30d7425908cf7e37980dc106c2045ce1f1345f45cbef9cb5fb347a` before and after revision.

The corrected blade has **61 span stations**, increased from 58. The terminal region retains much more chord, with a **1.44 mm terminal cap** rather than a 0.06 mm endpoint. Short closely spaced terminal stations provide rounded corners while retaining a broad end. The side facing the neighboring blade follows a straighter edge through most of the span. Representative stations before final X normalization are:

| Radial X station | Previous chord | Revised chord | Revised sweep |
|---:|---:|---:|---:|
| 12.85 mm | 4.92 mm | 5.05 mm | 0.91 mm |
| 13.55 mm | 4.38 mm | 4.63 mm | 0.65 mm |
| 14.10 mm | 3.73 mm | 4.25 mm | 0.34 mm |
| 14.55 mm | 2.97 mm | 3.91 mm | 0.18 mm |
| 14.85 mm | about 2.20 mm | 3.60 mm | 0.13 mm |
| 15.05 mm | about 1.48 mm | 3.29 mm | 0.10 mm |
| New terminal 15.36 mm | old terminal was 0.06 mm at 15.43 mm | 1.44 mm | 0.13 mm |

The upper reference blade was qualitatively traced using image edge positions at rows 370–725. Neutral-pixel checks support a broad terminal: row 370 spans approximately x=997–1075; row 400 x=969–1083; row 450 x=944–1075; row 575 x=896–1064. These positions are **image observations**, not new physical dimensions. The projected blade is affected by pitch, possible perspective, pale transparency and image processing. The revised chord/sweep values remain estimates rather than a calibrated CAD trace.

The root now begins at approximately 2.136183 mm X. Its sampled radius is **2.136303–2.250383 mm**, entirely within the enlarged barrel's 2.02–2.4 mm annular wall; this attaches the blade without projecting through the hub's open cavities. Inboard chord and sweep were adjusted to blend smoothly to that root.

Main integration centrally approved the PR-02 hub-radius change from 2.2 to **2.4 mm**. Components read that updated registry parameter. Hub radial webs now also depend on that parameter and reach from radius 0.85 to 2.15 mm, overlapping both the 0.93 mm center socket and the outer barrel beginning at 2.02 mm. Three open cavities remain. Hub height remains **3.3 mm**, bore remains **1 mm**.

Post-revision validation passed for both hands: schema, material IDs, parameter resolution, distinct node IDs, root attachment and full sampled blade radius. The final radius is **15.499999999999 mm**, maximum chord **6.8 mm**, and blade z range **11.517568–13.927714 mm**. X normalization factor is **1.007633427339** and does not scale chord. Caps are planar and cannot exceed their vertices' radial bound; blade modifiers remain absent.

PR-03 material and lighting changes are assigned to the main integrator. A new rendered top/oblique comparison is still required to assess whether the corrected shape improves agreement. Exact airfoil, camber, twist and uncalibrated reference projection remain uncertain.
