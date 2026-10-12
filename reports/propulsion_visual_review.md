# Independent visual review — propulsion, first pass

Reviewed on 2026-10-12 against frozen `air65-ii-racing-v1`. The reviewer did not author or modify the model, renderer, material registry or architecture. This pass visually inspected the actual `output/propulsion/hero.png` and `output/propulsion/top.png` using the image viewer. It concerns the isolated propulsion unit; duct placement, assembled visibility and aircraft proportions await the full assembly.

**Result: useful component prototype, with one material blade-outline correction recommended before final acceptance.** The motor's layered construction is substantially closer to the references than a full-height cylindrical can would be. The GF1207 blades retain too much of a continuously tapered, leaf-like outline. Matching the terminal paddle shape is the first priority.

## Evidence and limits

| Inspected file | Source ID | What it supports |
|---|---|---|
| `references/prop_diagram.jpg` | `prop_drawing` | Published 31 mm swept diameter and 1 mm bore; clear qualitative GF1207 planform, curved root, asymmetric blade edges and broad round-cornered terminal shape. It is not a dimensioned blade tracing. |
| `references/motor_diagram.jpg` | `motor_drawing` | Published 9 mm diameter, 8.55 mm mounting-base to shoulder height and 3.4 mm shaft extension; useful side-profile layer proportions. Orange Champion finish is not the Racing color target. |
| `references/air65_ii_racing_propulsion.webp` | `air65_ii_racing_propulsion` | Current manufacturer Racing close-up: clear hub, open crown, short silver bell and broad propeller ends. Highly polished manufacturer imagery may be rendered or retouched. |
| `references/photo_racing_oblique.webp` | `photo_racing_oblique` | Physical specimen cross-check: narrow silver motor can, raised translucent hub, broad clear blades and visibility through the canopy/frame. It has turquoise motor accents, unlike the purple current catalog target. Perspective, blur, occlusion and a different specimen limit fine comparisons. |

The coordinate contract was read: millimetres, +X aircraft right, +Y forward, +Z up, frame-plastic low datum z=0. Motor/prop component z values already use that shared datum. Published sizes remain fixed; estimated subdivisions do not acquire verified status through visual agreement. No camera calibration, aligned silhouette mask, pixel-error measurement or physical metrology was performed. This report does **not** independently certify any numerical dimension from rendered or perspective photographs.

## Ranked findings

### PR-01 — blade terminal shape and outer chord distribution

- **Severity:** medium, highest priority in this pass. **Confidence:** high for a visible mismatch; medium for the exact corrective contour.
- **Observed:** the model's top view narrows progressively through the outer blade into a relatively small curved tip. The diameter diagram has a more paddle-like terminal region with a broad, round-cornered end, a straighter edge on one side and a pronounced convex edge on the other. The close-up independently shows the broad end rather than a long leaf-like taper. The current blades are recognizably three-blade GF1207-type props, but this difference affects every rotor silhouette.
- **Action:** revise the *estimated* outer chord and sweep stations, concentrating on approximately the outer fifth of the span. Retain useful chord farther outward, make the straighter edge remain straighter toward the end, and finish with a short rounded cap rather than a long taper. Align hand and azimuth with the diameter reference before assessing. Preserve the published 31 mm swept envelope, 6.8 mm maximum chord, 3.3 mm hub height and 1 mm bore; recheck the maximum radius after twist and sweep.
- **Uncertainty:** the reference is a rendered/photographic product image rather than exact orthographic CAD, and its blade pitch affects the projected outline. Do not convert traced pixels into newly verified dimensions. Exact airfoil, camber and twist remain unknown.
- **Evidence:** `output/propulsion/top.png`, `output/propulsion/hero.png`; `prop_drawing`, `air65_ii_racing_propulsion`.

### PR-02 — hub appears modestly narrow relative to the rotor and motor

- **Severity:** low to medium. **Confidence:** medium.
- **Observed:** the three-spoke open hub topology is supported and clearly present. Its current outer diameter appears modestly narrow compared with both the diameter diagram and manufacturer close-up. The model's cylindrical hub looks comparatively slender in the oblique render. This is a visual inference, not a measured tolerance failure.
- **Action requiring main-integrator decision:** test a shared `prop_hub_radius` of **2.4 mm**, with **2.5 mm** as the upper comparison within the architecture's existing 1.9–2.5 mm estimate range. These are proposed trial estimates, not new verified dimensions. Keep the 3.3 mm height, 1 mm bore and shared axial seating fixed. Preserve three real apertures and review blade-root transitions after changing the radius. Accept the increase only if matched top and oblique comparisons improve together.
- **Uncertainty:** lens perspective, transmission and background contrast alter the apparent outer edge; the isolated model's grey studio background differs strongly from the white catalog reference. A hub-radius change is optional until evaluated together with clear material.
- **Evidence:** `output/propulsion/top.png`, `output/propulsion/hero.png`; `prop_drawing`, `air65_ii_racing_propulsion`.

### PR-03 — clear propeller reads as frosted grey

- **Severity:** low; cosmetic, after PR-01. **Confidence:** high for rendered appearance, medium for material-only cause.
- **Observed:** the model hub and blades are more cloudy than the Racing close-up. The reference shows crisp transmission through the hub and stronger clear-polymer edge highlights. This also makes the model's blade edges less legible against the grey background.
- **Action:** after geometric revision, adjust transmission/roughness and lighting or use a contrasting inspection background so the hub apertures and blade contour remain visible. Compare with the physical specimen as well as the polished catalog image; avoid forcing the real polypropylene parts to behave like optical glass.
- **Uncertainty:** lighting and image processing contribute. No change to physical blade thickness is justified by this appearance alone.
- **Evidence:** `output/propulsion/hero.png`, `output/propulsion/top.png`; `air65_ii_racing_propulsion`, `photo_racing_oblique`.

## Supported form and unresolved checks

- The silver bell occupies only part of the complete base-to-shoulder height. The model's distinct bottom mount/terminal plate, narrow lower neck, short can, raised open crown and shaft/hub stack are qualitatively consistent with `motor_drawing` and the current Racing close-up. No compelling motor layer-height correction is supported by these views. Preserve the published overall dimensions.
- Purple open crown spokes and visible copper are consistent with the current catalog variant. The individual winding count and detailed crown topology are not verifiable from the supplied photographs; do not present those internals as production-accurate.
- The physical photograph corroborates a raised hub and exposed silver can, but it cannot resolve numerical motor-height errors or establish a universal motor accent color.
- The isolated motor exposes screw heads and an unsupported gap where frame plastic would normally sit. Do not shorten the stack or move the screws to compensate before full assembly review.
- The three black motor wires and heatshrink bundle in the close-up are absent from this isolated render. The handoff assigns those to assembly integration; verify their presence and route in the full model before treating this as an omission.
- Rotor-to-duct 1 mm nominal clearance, opposite-handed prop arrangement, frame support occlusion and assembled rotor height require the full assembly and evaluated geometry checks. They are not visually validated by this isolated-component pass.

Acceptance for the next pass: improved broad terminal blade outline in top and oblique views, stable shared dimensions, and a documented decision on the estimated hub radius. Numerical validation remains the integrator's separate task.
