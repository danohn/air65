# Matrix II and LAVA II surface audit

This audit separates readable physical markings from manufacturer diagram callouts. It was made against the selected **Matrix 1S 5IN1 II** board and **LAVA II 280 mAh** battery, not the older Air65 components in the Sketchfab comparison. Appearance and placement observations are image estimates. An independent dimension audit and main-agent approval subsequently revised the central board-outline estimate; this subagent consumes those approved parameters and does not edit the shared registry.

## Evidence

| Source ID | Evidence | Confidence and limits |
|---|---|---|
| `fc_top_image` | [Manufacturer top-front macro](https://cdn.shopify.com/s/files/1/1778/6615/files/Matrix_1S_5IN1_II_Brushless_Flight_Controller_top_front_gyro_update.jpg?v=1777532692), saved as `references/fc_diagram.jpg` | High for readable labels and pad counts; diagram lines obscure small areas. Actual package outlines and positions remain estimates. |
| `fc_top_surface_photo` | [Unobstructed manufacturer top photograph](https://betafpv.com/cdn/shop/files/Matrix_1S_5IN1_II_Brushless_Flight_Controller_unsoldered_front.jpg?v=1769154868) | High for visible print and surface appearance. Different gyro samples may exist; do not fix a gyro label from this one photograph. |
| `fc_bottom_surface_diagram` | [Manufacturer bottom-front macro](https://cdn.shopify.com/s/files/1/1778/6615/files/Matrix_1S_5IN1_II_Brushless_Flight_Controller_bottom_front.jpg?v=1769053662) | High for visible print and component presence. A photograph viewed from below mirrors the top-view X axis. |
| `air65_ii_electronics` | `references/air65_ii_electronics.webp`, manufacturer marketing panel | Useful for both-side layering and reflective surfaces; its rendered package faces are schematic, so it is not the source of exact chip text. |
| `lava_ii_280_surface_photo` | [Manufacturer 280 mAh top-view photograph](https://betafpv.com/cdn/shop/files/LAVA_II_1S_280mAh_Battery_top_view.jpg?v=1763545157), saved as `references/lava_ii_280_top.jpg` | High for this face's text, livery, black cap and connector. Repeated packs show the same face, not the reverse face. |
| Existing battery drawing | `references/battery_diagram.jpg`; [manufacturer dimension image](https://cdn.shopify.com/s/files/1/1778/6615/files/LAVA_II_1S_280mAh_Battery_dimensions.jpg?v=1763610020) | High for the printed nominal size; moderate for pouch/seam appearance in perspective. |

The [Matrix II product page](https://betafpv.com/products/matrix-1s-5in1-ii-brushless-flight-controller) explicitly lists several substituted gyros. Full serial/lot markings therefore must not be inferred from the part family. These manufacturer images have no open reuse licence stated on the inspected pages. They are research references; the implementation must draw its own artwork, not map photograph pixels onto the model.

## PCB findings

The mask is very dark neutral grey with subtle texture and faint tracks. White print is sparse around some packages but dense at connection points. Gold pads, tiny silver terminations, tan ceramic bodies and slightly varied black IC tops create most of the fine texture. Heavy bright circuit traces would be inaccurate.

| Region, with aircraft front up | Readable evidence | Implementation decision |
|---|---|---|
| Left mounting lug | Four rounded square gold pads. Physical print reads `G`, `T1`, `R1`, `5V`, in that order from front to rear. Large diagram callouts expand these to GND/TX1/RX1. | Preserve the four pads and draw the abbreviated physical labels. Do not place the expanded callout text on the board. High confidence in spelling/count; exact text location estimated. |
| Right mounting lug | **Three** rounded pads with `5V`, `L`, `GND` from front to rear. | Correct the current four-pad symmetric copy to three pads. Main integrator approved this local estimated correction. Preserve board and mount coordinates. |
| Right of central u.FL socket | A diagonal group of three broad rounded rectangular pads labelled `CAM`, `GND`, `5V`. | Add flat drawn pads and readable print at estimated locations. Retain the existing camera socket geometry. The external `CAM IN` diagram callout is not copied as printed text. |
| Rear-left battery connection | Large round plated contacts beside a white `+` and short `−`; a smaller RX antenna contact follows them. | Draw polarity marks, preserving the existing contact geometry. Through-hole appearance remains a geometry limitation of the present solid test-pad cylinders. |
| Rear centre | A stylised white forward arrow. | Draw an arrow silhouette, replacing the generic raised `>` text. |
| Top ICs | ST logo on the main MCU, `PUYA` on flash, `R001` on the shunt are readable. Package faces contain much smaller etching. | Use only these legible markings, with approximate typeface/placement and low contrast. Do not invent serials, date codes, or complete part numbers from partially legible etching. |
| Top IC identification | Diagram callouts establish STM32G473, MM32F003, ESP8285 and SX128X families. | These are component identities, not proof of the exact visible printing. No full MCU/receiver/gyro string is added merely because the callout identifies the part. |
| Package boundaries | Thin white L-shaped corner marks; occasional pin-one dots; small gold circular test points and perimeter motor contact groups. | Draw restrained corner marks around existing estimated packages and small reference-inspired surface details. These positions are estimates and are not an electrical layout or connectivity model. |
| Bottom | Physical print `Matrix 5IN1`, `V2.1`, and polarity marks is visible. | Add those readable marks using the correct bottom-view handedness. Do not add `II` to a label that does not visibly contain it. |

The baseline component had 318 nodes but only four raised text objects. Those text objects included a large approximate BETAFPV wordmark whose top-side position was unsupported by the close-up. The refinement removes those four raised objects and uses printed texture artwork instead. Existing large top-side IC dimensions and mounting coordinates are preserved. The subsequently authorised substrate-outline revision and bounded gyro/passive shifts are recorded below.

The bottom photograph revealed a substantive geometry gap: a large central **AT7456E**, a forward VTX package and four controller regions were absent from the baseline's eight uniform underside power rectangles. The main integrator subsequently authorised a bounded geometry correction. Fourteen reference-estimated package bodies now replace those eight placeholders: VTX, AT7456E, four controller packages and eight visibly distinct outer power package outlines. The product page's count of twelve MOS devices must not be confused with a verified count of externally separate package bodies. The simplified reconstruction makes no electrical or complete internal-device claim.

The [unobstructed underside photograph](https://betafpv.com/cdn/shop/files/Matrix_1S_5IN1_II_Brushless_Flight_Controller_unsoldered_back.jpg?v=1769154868) (`fc_bottom_surface_photo`) was inspected to locate these package regions. It depicts a V2.0 solder-required sample, while the solder-free diagram visibly reads V2.1. Their broadly matching layout supports the reconstruction, but does not establish exact specimen identity. The selected bottom print follows the solder-free V2.1 diagram. `AT7456E` is legible on the physical package in that diagram and is therefore included in the subdued chip atlas; its smaller second line is omitted.

An early visual estimate suggested that the 24 mm body was too small, but its rough numerical ratio proved unreliable. The independent dimensions agent then sampled actual substrate-edge pixels and calibrated them against the 26 mm mounting pitch. The main agent adopted **26.4 ± 0.5 mm** body side, **16.2 ± 0.4 mm** front clip, and **16.3 mm** side/rear clip (estimated range 16.0–16.6 mm). Corner radius and clip half-widths are derived centrally. These remain image-derived estimates, not manufacturer dimensions. The substrate and mask use those exact registry references; side/rear clipping preserves the existing lug bores. The provisional 0.85 fit is removed.

Four outer underside power bodies shift 0.50 mm inward in X and 0.50 mm farther toward the front/rear along the diagonal edge, so they do not intersect the fixed-size motor connector housings. That 0.71 mm local adjustment is an explicit model-fit estimate. All other new underside positions are the photo-normalised estimates listed below. They are converted to parameter expressions using the actual current registry value, rather than a hard-coded 24 mm denominator.

The four underside motor connector centres move from `(±9.15, ±8.00)` to `(±12.40, ±5.20)` mm, with the signs identifying their quadrant. Their 4.7 × 2.5 × 1.75 mm dimensions, Z centre 13.85 mm and rotations stay unchanged. Each three-wire bundle retains its motor-end coordinates and Z path; only the last two XY control points are refitted, with the middle conductor ending at the connector centre and the two flanking conductors retaining offsets derived from their unchanged motor ends. These visible external fits require review in the assembled render.

The original top pins, passive solder caps and camera contacts encoded their small offsets as fractions of the former 24 mm body. Blindly increasing that parameter would pull the contacts away from unchanged package sizes. The writer migrates those child offsets to rigid millimetre offsets relative to each component centre. The only retained 24 mm constant is this explicit one-time legacy-offset conversion; new component placement reads the current registry.

The removed underside IDs are `fc_underside_power_n1_0` through `_3` and `fc_underside_power_1_0` through `_3`, each previously 2.8 × 3.6 × 0.9 mm. Replacement bodies have the prefix `fc_refine_bottom_`; their package dimensions and heights are unverified visual estimates:

| ID suffix | Centre X,Y (mm) | Width × length × height (mm) | Rotation about Z |
|---|---:|---:|---:|
| `vtx` | 1.05, 8.35 | 6.00 × 6.00 × 0.72 | 45° |
| `at7456e` | 0.70, 0.35 | 6.80 × 4.50 × 0.72 | 135° |
| `esc_control_fl` | 6.35, 3.20 | 2.65 × 2.65 × 0.58 | 45° |
| `esc_control_fr` | −6.65, 3.50 | 2.65 × 2.65 × 0.58 | 45° |
| `esc_control_rl` | 5.25, −5.40 | 2.65 × 2.65 × 0.58 | 45° |
| `esc_control_rr` | −5.80, −4.40 | 2.65 × 2.65 × 0.58 | 45° |
| `power_fl_outer` | 9.00, 7.50 | 2.65 × 2.85 × 0.52 | 45° |
| `power_fr_outer` | −9.00, 7.50 | 2.65 × 2.85 × 0.52 | 45° |
| `power_left_mid` | 10.80, 0.10 | 2.65 × 2.85 × 0.52 | 45° |
| `power_right_mid` | −10.80, 0.10 | 2.65 × 2.85 × 0.52 | 45° |
| `power_left_inner` | 8.40, −2.65 | 2.65 × 2.85 × 0.52 | 45° |
| `power_right_inner` | −8.20, −2.65 | 2.65 × 2.85 × 0.52 | 45° |
| `power_rl_outer` | 8.50, −7.25 | 2.65 × 2.85 × 0.52 | 45° |
| `power_rr_outer` | −8.90, −7.15 | 2.65 × 2.85 × 0.52 | 45° |

Each body is attached 0.035 mm below the PCB's underside via simplified visible lead rows. Pin count is a display approximation, not an electrical specification. The historical FL/FR suffixes are layout identifiers, not proof of motor electrical assignment.

## Battery findings handed to the integrator

The actual 280 mAh graphic is bright lime/yellow-green with angular black shards and thin white lightning streaks. On the connector end it has large `280`, smaller `95C` above `mAh`, and the lower line **`LiHV 3.8V 1.06Wh`**. The opposite half carries large yellow **`LAVA`**, edged in black and white. The photographed face has no visible `II` or `1S` text. The black end cap carries green `BETAFPV` text. The short BT2.0 connector is also black, with recessed round contact sockets visible in the oblique drawing.

The current battery's plain `LAVA II` text, white connector, uniformly flat green panels and large yellow rectangle do not match this evidence. The recommended wrapper is an original vector reconstruction of the visible graphic hierarchy and factual markings. It should retain the frozen 54 × 10 × 6 mm nominal envelope and show narrow dark wrapper edges, a small reflective foil seam, slight pouch rounding, and a moulded black cap. The reverse face was not established; a duplicate front label on both faces is an explicit estimate, not verified evidence. Battery JSON and texture implementation belong to the main integrator.

## Deterministic texture implementation

The surface generator uses Pillow 12.2.0 with its embedded default font, explicit vector paths, and deterministic low-amplitude surface grain. It never loads reference images. Board textures cover a fixed local XY domain of −20 to +20 mm and use +Y as front. The bottom UV projection flips U so the underside print reads correctly when viewed from below. Text placement is estimated from the photographs and fitted to the frozen component layout.

Required materials are `fc_top_print`, `fc_bottom_print`, and `chip_markings_print`. Their base-colour images are `assets/textures/fc_top.png`, `fc_bottom.png`, and `chip_markings.png`. Board base colour is sRGB (27,30,31); package base is (24,25,25). Roughness around 0.65–0.70 is a visual starting point, not measured material data. Printed gold colour is only a surface approximation; existing raised metal pads retain their separate gold material.

The top and bottom images are 2048 × 2048. A 1024 × 1024 chip atlas has four 512 × 512 tiles: ST, PUYA, R001 and AT7456E. Package-local XY UV bounds select a tile without adding geometry. Readable etch text is kept subdued, except the high-contrast shunt marking visible in the reference. All other package faces retain unmarked materials rather than invented part codes. Texture files are RGB PNG with no source-photo pixels or baked reference lighting.

Validation should compare an unobstructed top and bottom board render, then the installed assembly, with the cited photographs. Successful schema or collision checks do not establish visual fidelity. Material, renderer, shared-registry and final assembly integration remain owned by the main agent.

## First surface-pass verification

This section records the 489-node surface/underside-package milestone. The later independent-review correction is described in the following section. Its geometry count and regenerated board-texture hashes supersede this snapshot.

- `uv run scripts/refine_electronics.py` generates the three RGB PNGs and applies the component update. Baseline 318 nodes becomes 489 nodes, primarily simple package and lead boxes; four raised text objects are removed.
- The component passes the current JSON Schema. Re-applying the writer in memory produces exactly the same JSON data.
- An oriented-box separating-axis check finds no intersections larger than 0.02 mm among the fourteen new package bodies and four motor connector housings. This is a bounded package/housing check, not a whole-aircraft collision guarantee.
- The farthest new package-body corner has `|x| + |y| = 18.5153 mm`, within the central sloped-edge value `18.6676 mm`. Side/rear substrate clipping leaves about 0.535 mm to the nearest lug-bore edge and about 0.365 mm overlap with the outer lug.
- Repeated texture generation after the final geometry update gives identical file hashes. Direct inspection of the textures confirms original drawn marks, correct spellings, blank unverified chip areas and no reference-photo lighting.
- No battery file, renderer, schema, material definition, source registry, or shared architectural parameter was edited by this subagent. The saved 280 mAh photograph and independent source manifest are provided for the main agent's battery implementation.

| Asset | SHA-256 |
|---|---|
| `fc_top.png` | `422d8eb6a516dfd82ba304c8416a51156d63e9164c6e4c47d08884b85b6211c0` |
| `fc_bottom.png` | `bde7ed3dcbbe1474ac596358475e66a81e632fea8dbb4ee6a65aece9e10a536f` |
| `chip_markings.png` | `f4be8868b9df6f2c65101ca059ca96703d5127ef3043d3f2065e76e54f89f3dd` |

The installed render, material response and exact print orientation remain for the main agent's build and independent review. Geometry placement, letterform style, tiny traces, surface grain and package heights remain estimates. The model is not an electrical PCB reconstruction.

## Follow-up after independent PCB review

The independent reviewer compared `output/pcb_refinement/inspection/pcb_top.png` with the retained manufacturer top photograph and identified two overhanging passive bodies. The review also found that the main MCU had only two opposing lead rows although all four sides have leads in the photograph, and that the underside was missing visible passive banks. This bounded correction changes only the electronics component, its deterministic generator and this audit. The shared board outline, mounting axes, mounting dimensions and all large top package sizes remain fixed.

The original centres of `fc_passive_0` and `fc_passive_1` were (−5.50,14.30) and (−6.655,13.09) mm. Their body corners exceeded the sloped NW board boundary by approximately 1.93 and 1.88 mm; the outer solder ends extended slightly farther. Both parts move to the small fore-tip passive region observed in the top reference, with their two solder terminations translated and rotated rigidly. The NW gyro cluster moves from (−4.235,12.10) to (−3.935,11.80) mm, including every existing lead; its formerly outermost pin corner exceeded that same edge by approximately 0.30 mm. The gyro's identity, package dimensions and height are unchanged.

The four-sided MCU lead check also exposed small contacts between neighbouring passives and IC leads. The following local placements resolve those contacts. These are photo-informed estimates fitted within the existing package layout; they are not measured manufacturing locations. Body dimensions and Z positions remain unchanged, and both solder ends follow each correction.

| Existing passive ID suffix | Final centre X,Y (mm) | Z rotation | Correction |
|---|---:|---:|---|
| `0` | −1.50,15.10 | 45° | Move from NW overhang to observed fore-tip cluster. |
| `1` | −2.60,14.00 | 45° | Move from NW overhang to observed fore-tip cluster. |
| `5` | −9.57,8.25 | 135° | Rotate in place to clear the neighbouring lead row. |
| `6` | −11.88,5.94 | 135° | Rotate in place to fit the perimeter/lead gap. |
| `7` | −11.06,3.46 | 45° | Local inward/gap fit. |
| `9` | −12.54,−0.77 | 135° | Rotate in place to clear neighbouring pins. |
| `10` | 9.10,7.29 | 45° | Shift approximately 0.08 mm per axis to clear its outer solder cap from a VTX-processor pin row. |
| `20` | −7.09,−7.87 | 45° | Local gap fit. |
| `21` | −6.25,−9.05 | 45° | Local gap fit. |
| `23` | 3.60,−13.10 | 45° | Local fit in the rear passive region. |
| `24` | 3.60,−11.25 | 45° | Local fit in the rear passive region. |

The main STM MCU now has four lead rows. The two original rows are retained and two orthogonal rows of eight simple metal leads are added. **Eight leads per side is a display estimate**, not a claim that the physical MCU has 32 pins. The source establishes the presence of four rows; the model does not resolve the full fine-pitch pin count. No new readable part markings are invented.

Seventeen small underside bodies with two metal terminations each are added at visible fore-tip and central-package banks. The source positions are interpreted in bottom view, so image-left maps to positive aircraft X. Package centres and sizes below are explicitly estimated from the two retained underside references. Heights, exact package types and electrical functions remain unverified. The labels here identify model regions only.

| Added underside ID suffix (`fc_refine_bottom_passive_…`) | Centre X,Y (mm) | Body W × L × H (mm) | Rotation |
|---|---:|---:|---:|
| `fore_cap_a` | 1.90,13.10 | 0.50 × 1.00 × 0.40 | 45° |
| `fore_cap_b` | 2.95,12.40 | 0.50 × 1.00 × 0.40 | 45° |
| `fore_dark_a` | 0.10,14.50 | 0.50 × 0.75 × 0.28 | −45° |
| `fore_dark_b` | −1.40,13.40 | 0.45 × 0.75 × 0.26 | 45° |
| `between_cap_a` | 3.25,3.20 | 0.65 × 1.25 × 0.46 | 45° |
| `between_cap_c` | 4.55,2.00 | 0.65 × 1.20 × 0.43 | 45° |
| `between_dark` | −2.80,4.20 | 0.60 × 1.40 × 0.33 | 45° |
| `right_cap_a` | −3.90,3.30 | 0.65 × 1.25 × 0.46 | 45° |
| `right_cap_b` | −4.60,2.20 | 0.65 × 1.20 × 0.40 | 45° |
| `right_dark` | −4.00,0.80 | 0.45 × 0.80 × 0.24 | 45° |
| `right_cap_c` | −3.00,−1.10 | 0.70 × 1.20 × 0.43 | 45° |
| `right_rear_dark` | −4.20,−2.00 | 0.50 × 0.80 × 0.25 | 45° |
| `left_rear_cap_a` | 3.25,−3.30 | 0.65 × 1.20 × 0.43 | 45° |
| `left_rear_cap_b` | 2.40,−4.35 | 0.70 × 1.25 × 0.43 | 45° |
| `centre_rear_dark` | 1.35,−4.80 | 0.45 × 0.75 × 0.22 | 45° |
| `centre_rear_cap_a` | −1.50,−4.10 | 0.65 × 1.20 × 0.40 | 45° |
| `centre_rear_cap_b` | −2.50,−5.20 | 0.65 × 1.20 × 0.40 | 45° |

One ambiguous candidate between the VTX and central package was omitted because its estimated footprint conflicted with a VTX lead row. The `right_cap_b` centre received a final 0.10 mm shift in each axis to clear its termination from a controller lead. The reconstruction intentionally covers selected visible banks; it does not claim exhaustive passive population. Each body begins 0.035 mm below the board underside, with simplified metal end geometry. Passive outlines do not receive automatic printed corner marks, avoiding an unsupported repeated silkscreen pattern.

The integrator's narrowed lug rim is preserved: its outer radius remains `fc_lug_hole_radius + 0.10` mm. The board uses the central 26.4 mm side, 16.2 mm front clip and 16.3 mm side/rear clip; no values in the shared registry were modified. The underside texture retains mirrored U projection, and the legacy top-pin/solder-cap migration continues to preserve rigid offsets from the original 24 mm layout rather than scaling the pin spacing.

Validation of this final **556-node** specification:

- JSON Schema validation passes, and a second application of `apply_spec` produces exactly equal JSON data.
- All top box-body, IC-pin and passive-cap corners, plus all added underside passive and termination corners, lie within the clipped board polygon in XY. The calculation includes the sloped edges and absolute front/side/rear clips.
- An oriented-box separating-axis check of every passive body/termination against other electronics boxes reports no cross-component intersections exceeding 0.03 mm. Expected contact between a passive and its own metal ends is excluded. This is a bounded PCB detail check, not a whole-assembly clearance certificate.
- The top MCU has 32 simplified lead objects across four sides. The underside addition is 17 bodies and 34 terminations. Large package geometry, motor connector dimensions, wire endpoints and mounting geometry are preserved from the prior approved milestone.
- Only `uv run scripts/refine_electronics.py --spec-only` was executed for this follow-up. The main integrator must run `uv run scripts/refine_electronics.py --textures-only` before the final render so board artwork follows the corrected component positions. The historical hashes above are not asserted for that regenerated output.

Final visual acceptance remains with the independent reviewer and main integrator. In the existing isolated bottom-render orientation, aircraft front is at the bottom of the image; rotate it 180° for comparison with the manufacturer reference, which places front at the top. Photo perspective, source sample/version differences and unresolved small-package details continue to limit exact positional accuracy.
