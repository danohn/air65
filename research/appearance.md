# Air65 II appearance research

Research date: 12 October 2026. Target corrected from the original Air65 to **Air65 II** before the modelling specification was established. This report supplies visual evidence and tentative proportions; the main integrator and spatial architect own the canonical dimensions.

## Coherent configuration

Use the **Air65 II Racing** variant with the standard Air65 II frame. Its current manufacturer gallery shows translucent lavender/purple plastic, a milky translucent white Air II canopy, clear three-blade GF1207 propellers, short silver motors with purple upper spokes, and a substantial black copper-tube antenna. The manufacturer distinguishes this from the lighter Champion frame and whip antenna and from the Freestyle propulsion combination. [Manufacturer product page](https://betafpv.com/products/air65-ii-brushless-whoop-quadcopter).

The actual Racing specimen in the June 2026 hands-on review has the same purple frame and white canopy but turquoise motor accents. Record that as a sample/color discrepancy; current gallery purple is a defensible styling choice, not a verified universal color. The reviewer also photographed the three models together. Use that page for its firsthand visual evidence; its prose contains technical mistakes and is not the authority for measurements. [Demetrios, The Drone Vortex](https://thedronevortex.com/betafpv-air65ii-review/).

The clean manufacturer imagery appears rendered or heavily retouched; the capture method is not labelled. It is identified as **manufacturer reference imagery**, not asserted to be an unedited photograph. The files beginning `photo_` show physical hardware in a person's hand or on a table.

## Most useful reference files

| File in `references/` | Evidence and limitations |
|---|---|
| `air65_ii_racing_oblique.webp` | Exact selected manufacturer's configuration; whole-aircraft silhouette, open canopy, board and wire layout. Perspective, no camera calibration. |
| `photo_racing_oblique.webp` | Physical purple Racing specimen; lens, canopy thickness, exposed PCB, negative spaces. Perspective, shallow depth of field, some parts occluded by hand. |
| `photo_variants_low_front.webp` | Physical side-height comparison. Racing is the middle purple craft; Freestyle left, Champion right. Camera perspective makes apparent size incomparable across the three. |
| `photo_freestyle_side_oblique.webp` | Physical side view of shared standard II frame and Air II canopy; use for structural layering only, not Racing colors or propeller shape. |
| `air65_ii_frame_black_top.webp` | Excellent near-plan outline for tracing four circles, motor pads, four braces per duct, mounting bosses, battery cradle, and bridges. The image does not establish which symmetric end is front. |
| `air65_ii_frame_diagram.webp` | Manufacturer dimensioned frame plan/elevation. Canonical dimensions should come from the dimensions research. |
| `air65_ii_frame_details.webp` | Especially useful lower-right side section: low upper rim and deep bowed spokes. Other panels show screw protection and mounting structure. |
| `air65_ii_racing_propulsion.webp` | Exact Racing propeller and motor closeup, with open winding/top-spoke structure. |
| `air65_ii_racing_underside.webp` | Motor screws, black three-wire bundles, white connectors, integrated cradle and optional green LAVA II battery. |
| `air_ii_canopy_black.webp` / `air_ii_canopy_diagram.webp` | Unmounted flexible canopy topology and openings. Do not use its unbent length as the installed front-to-rear length. |
| `air_ii_canopy_side.webp` | Mounted side silhouette. **Only the left panel is Air II**; the right panel is the original Air canopy comparison. |

All 21 captured images have source URL, source page, variant, intended use, pixel dimensions, SHA-256 and individual visual-inspection status in `references/manifest.json`. Images remain copyrighted by their source owners; no open-content licence was identified. They are retained as local research references, not relicensed assets.

## Major geometry observations

The visual signature is four shallow round rims supported above low motor pads by curved, thin ribs. Every standard II duct has **four** braces, with irregular angular spacing, terminating around a roughly triangular three-bolt motor pad. Three small retaining/screw-protection features surround each pad. The ribs descend strongly in side elevation. Flat spokes at the ring plane would produce a major shape error even if the top outline looked recognisable. [Frame source and drawings](https://betafpv.com/products/air65-ii-brushless-whoop-frame).

The central frame is mostly empty space. Front and rear have narrow connecting bridges with small outward triangular markers; the sides use curved connecting braces. Four cardinal mounting bosses surround a narrow longitudinal battery cradle. The FC sits above this structure and appears as a square rotated relative to the motor grid. It remains highly visible.

The Air II canopy is a flexible **open skeleton**. A camera collar joins a front tongue, two slender lateral mounting legs and a narrow perforated rear strip. Installing the rear strip bends it into an arch over/behind the camera. Large openings reveal the camera PCB and board. A small upper lip and cap opening surround the lens; there is no broad enclosed fuselage. The manufacturer provides discrete 15°, 25°, 35° and 45° camera positions. [Canopy source and drawings](https://betafpv.com/products/air-ii-canopy).

The lens is a dark circular barrel with a smaller recessed green/blue optical surface. Its rectangular camera PCB sits directly behind it and tilts back from vertical. Real photos show this board prominently through the side opening. The short motors have metallic cylindrical bells, colored open upper spokes, exposed copper windings and black bases. Their three black wires stay together in parallel bundles to small white plugs. The clear propellers have three curved paddle-like blades with swept edges and rounded ends, narrow roots and raised hubs; they need visible pitch/twist rather than three flat rectangles.

The Racing antenna is a long dark tube with a tapered thicker base emerging from the canopy rear and rising backwards. The optional battery runs lengthwise below the board; narrow purple loops hold it, leaving much of its green/yellow/black label and foil sides exposed. White/blue U-shaped battery wiring and a white BT2.0 connector are visible at the rear/bottom. Cable positions are sample-dependent.

## Proportions and uncertainty

The following are **cross-check estimates**, not a second dimensional authority. They must be reconciled with the architecture specification.

| Ratio | Estimate | Basis and confidence |
|---|---:|---|
| Duct outer diameter / full frame width | 0.442 ± 0.005 | Near-plan black frame image, about 359 / 811 pixels; high visual confidence. |
| Adjacent motor-center separation / full frame width | 0.553 ± 0.004 | About 449 / 811 pixels; high visual confidence. Use the verified wheelbase for canonical placement. |
| Clear duct diameter / full frame width | 0.398 ± 0.006 | About 323 / 811 pixels; rim highlight makes edge choice uncertain. |
| Mounted canopy arch height above screw plane / front-to-rear screw span | 0.62 ± 0.07 | Left Air II side panel, about 307 / 490 pixels; medium confidence, angle-dependent. |
| Lens-center height above screw plane / front-to-rear screw span | 0.42 ± 0.07 | Same side panel; medium confidence. |
| Slender canopy leg width / lens opening diameter | 0.15 ± 0.05 | Unmounted drawing cross-checked against physical side photo; medium confidence. |
| Camera optical elevation in example imagery | Approximately 25° ± 10° | Low confidence. Adopt one documented mounting setting centrally; do not pretend an exact factory setting was measured. |

The approximate 1080-pixel frame-image landmarks and all uncertainty fields are machine-readable in `research/appearance.json`. These give the architect reproducible tracing hints without imposing an independent coordinate system.

## Modelling and review priorities

1. Match motor-center geometry, round rim silhouette, overall footprint and propeller clearances in top view.
2. Match the low rim, deep bowed four-brace supports, low motor pads and open central battery structure in elevation.
3. Match the skeletal canopy, lens diameter/pose, exposed camera PCB and antenna silhouette. Avoid a generic enclosed bubble.
4. Match the short motor bell, tall prop hub, swept blades, blade count and alternating handedness.
5. Match FC layering, grommets, connectors, cable bundles and optional battery placement before tiny board markings.
6. Tune translucency, colors and reflections only after silhouette and component proportions are stable.

For independent review, compare a frame-only top render with `air65_ii_frame_black_top.webp`, a frame side view with the manufacturer elevation and detail panel, a whole-craft oblique with both the manufacturer Racing reference and `photo_racing_oblique.webp`, a low front/side view with the middle craft in `photo_variants_low_front.webp`, and an underside with the manufacturer's battery view.

No calibrated whole-craft orthographic top/front/side photograph set was found. The physical images have unknown lens intrinsics, perspective, exact mounting setting and sample date. This evidence can support a careful visual recreation and dimension-consistent assembly, but not a claim of caliper-level reverse engineering or manufacturing interchangeability.
