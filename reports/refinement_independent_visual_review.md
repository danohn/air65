# Independent visual review of the Air65 II refinement

Review date: 12 October 2026. Reviewer: the independent Codex visual-review subagent. The reviewer did not author or edit model geometry, dimensions, materials, textures, rendering scripts or exports.

Publication note: navigation links were made portable for GitHub without changing the review findings. [Restore the release artifacts](../docs/RELEASES.md) to open linked `output/` images locally. Reference photographs remain at their original source URLs.

**Status: completed; refinement accepted within the inspected scope.** The finished source is a substantial visual improvement over the preserved baseline, especially in the canopy transitions, PCB hierarchy and optional battery. The final optimized asset preserves those gains in the inspected evaluated-mesh, serialized GLB and actual browser views after correcting the lens-reduction regression and mobile framing. No remaining major silhouette/proportion error or new delivery regression was found in those views. Meaningful residuals remain in PCB detail density, local canopy curvature and optical material agreement. This is a bounded visual assessment, not a claim of physical replication accuracy or an exact photographic match.

## Scope and evidence rules

This is a fresh review prompted by `research/sketchfab_comparison_handoff.md` and `REFINEMENT_PLAN.md`. Earlier v2 and delivery reviews are historical records, not evidence that this refinement is visually accurate. The older Air65 Sketchfab example is a workmanship benchmark only; its geometry, materials and dimensions are not ground truth for the Air65 II.

The comparison target is the selected Air65 II Racing assembly, the shared Air II canopy, the Matrix 1S 5IN1 II flight controller and the optional LAVA II 280 mAh battery. The Freestyle physical photo is used only for its shared canopy and camera. The manufacturer's installed underside image uses a different, longer 320 mAh battery, so it cannot determine the selected 280 mAh pack length.

Reference photographs are not calibrated to the renderer's cameras or lighting. Lens distortion, pose, exposure and specimen variation limit comparisons. Published nominal dimensions remain distinct from photographic estimates. In particular, the centrally approved 26.4 ± 0.5 mm PCB body is an image-derived estimate; the 26 mm mounting pitch and 1 mm board thickness are separate fixed anchors. No physical accuracy percentage, fit certification or dimensional metrology result is inferred from these pictures. Numerical conformance checks do not establish photo fidelity.

Source-render versus optimized evaluated-mesh comparisons, re-imported serialized GLB comparisons and actual Three.js/browser comparisons are different tests. Agreement in Blender does not establish browser material agreement or rendering performance.

## References inspected

| Source ID | Local evidence | Use and limitation |
| --- | --- | --- |
| `air_ii_canopy_black` | `references/air_ii_canopy_black.webp` | Formed collar, leg roots, foot necks and opening topology; uninstalled shape and perspective are not installed dimensions. |
| `air_ii_canopy_side` | `references/air_ii_canopy_side.webp` | Left Air II panel only; installed side contour and open camera sides. Right older-part panel excluded. |
| `air_ii_canopy_structure` | `references/air_ii_canopy_structure.webp` | Left Air II panel only; structural relationships. |
| `photo_racing_oblique` | `references/photo_racing_oblique.webp` | Physical Racing specimen; whole-assembly silhouette, thin milky canopy, clear blades and violet frame. |
| `photo_freestyle_side_oblique` | `references/photo_freestyle_side_oblique.webp` | Physical shared canopy/camera shape only. |
| `fc_top_surface_photo` | `references/matrix_ii_front.jpg` | Matrix II front package distribution, 4-versus-3 side pads, print and black mounting lugs. |
| `fc_bottom_surface_diagram` | `references/matrix_ii_bottom.jpg` | V2.1 solder-free underside, sockets and major component hierarchy; external annotation arrows are not board print. |
| `fc_bottom_surface_photo` | `references/matrix_ii_back.jpg` | Unobstructed underside package density; V2.0 sample differs from selected V2.1 diagram. |
| `fc_top_image` | `references/fc_diagram.jpg` | Annotated manufacturer front photograph; dimensions and body outline are handled centrally. |
| `lava_ii_280_surface_photo` | `references/lava_ii_280_top.jpg` | Actual 280 mAh wrapper, black cap/nose, lettering hierarchy and mild pouch rounding. Reverse face not independently evidenced. |
| `battery_drawing` | `references/battery_diagram.jpg` | Selected 54 × 10 × 6 mm body convention and component appearance; projecting nose excluded from that nominal body. |

Reference URLs, IDs and file hashes are retained in `references/manifest.json`, `references/technical_manifest.json` and `references/refinement_surface_sources.json`. Manufacturer sources support visible appearance; they do not provide measured optical material properties.

## Preserved baseline and inspection validity

The reviewer actually viewed the preserved `output/refinement_baseline/final/hero.png`, `top.png` and `right.png`, the preserved optional `output/refinement_baseline/with_battery/underside.png`, and all six corrected close-ups under `output/refinement_baseline/inspection/`: `canopy_oblique.png`, `canopy_front.png`, `canopy_right.png`, `pcb_top.png`, `pcb_bottom.png` and `battery_closeup.png`.

An earlier inspection-helper close-up had a 100 mm near clip and was excluded from evidence after the integrator identified it. The baseline close-ups listed here were re-inspected after regeneration with a 0.1 mm near clip. The original preserved assembly renders were unaffected.

The baseline visibly has abrupt cap/shoulder/arch joins and blunt leg roots, a sparse top PCB, an underside reduced to eight uniform packages, oversized gold mounting eyelets, and a plain box-like battery with a white nose. These are substantive comparison targets. The baseline already has the correct broad family of arch openings; this review does not revive the earlier, already-resolved rectangular-ladder criticism.

Additional diagnostic evidence included all four stable canopy images under `output/canopy_refinement/isolated_final/` (`hero`, `front`, `right`, `top`) and its assembled `output/canopy_refinement/context_final/hero.png`. Intermediate PCB and battery drafts were also inspected to return concrete defects before final rendering; those drafts are not acceptance evidence. The completed corrections are assessed below.

## Completed source comparison

The finished source was independently viewed in `output/final/hero.png`, all six images in `output/refinement_inspection/`, and `output/with_battery/hero.png`, `underside.png` and `right.png`. The six isolated images are 1100 px, 48-sample renders from the saved optional assembly; their individual hashes are retained in `output/refinement_inspection/inspection_manifest.json`. The integrator identifies the stable dry geometry fingerprint as `630df06fdb96e43bbb6f372527c5e34baa45f05895e39a1de1e9ada1772d46e9`. That identifier ties the review to a revision; it is not an accuracy score.

| Comparison | Preserved before | Finished source | Relevant actual reference |
| --- | --- | --- | --- |
| Assembly | [Before hero](../output/refinement_baseline/final/hero.png) | [After hero](../output/final/hero.png) | [Physical Racing specimen](https://thedronevortex.com/wp-content/uploads/2026/06/BETAFPV-Air65-II-Review-Which-Version-Should-You-Buy_3.webp) |
| Canopy | [Before close-up](../output/refinement_baseline/inspection/canopy_oblique.png) | [After close-up](../output/refinement_inspection/canopy_oblique.png) | [Uninstalled Air II canopy](https://betafpv.com/cdn/shop/files/Air_II_Canopy_Black_1080x.jpg?v=1760929544) |
| PCB top | [Before top](../output/refinement_baseline/inspection/pcb_top.png) | [After top](../output/refinement_inspection/pcb_top.png) | [Manufacturer front photo](https://betafpv.com/cdn/shop/files/Matrix_1S_5IN1_II_Brushless_Flight_Controller_unsoldered_front.jpg?v=1769154868) |
| PCB bottom | [Before bottom](../output/refinement_baseline/inspection/pcb_bottom.png) | [After bottom](../output/refinement_inspection/pcb_bottom.png) | [Selected underside diagram](https://cdn.shopify.com/s/files/1/1778/6615/files/Matrix_1S_5IN1_II_Brushless_Flight_Controller_bottom_front.jpg?v=1769053662) |
| Battery | [Before close-up](../output/refinement_baseline/inspection/battery_closeup.png) | [After close-up](../output/refinement_inspection/battery_closeup.png) | [Actual 280 mAh front](https://betafpv.com/cdn/shop/files/LAVA_II_1S_280mAh_Battery_top_view.jpg?v=1763545157) |

### RV-01 — Canopy continuity: major baseline defect improved

**Evidence:** final hero and isolated canopy oblique/front/right against their preserved counterparts, the black Air II part, left Air II side illustration and physical Racing photograph.

The completed canopy eliminates the obvious cap cut ends and separate ring/strip appearance at its major visible junctions. The brow flows into the side cheeks, the side legs join the shaped collar, and the arch meets the shoulder without the old abrupt butt joint. The camera PCB remains exposed, the large side triangle is open, and the fore tongue slot and arch openings remain real holes. The installed hero retains those gains without a black shoulder patch or a new coarse silhouette break.

**Unresolved:** the close-ups still show small waviness/creases at the low leg bends and foot necks, and the brow vent is a crisp rectangular opening compared with the softer small opening in the physical image. These are visible local approximations, not evidence that a new global camera/arch dimension is required. Exact cap curvature, wall section and mould fillets remain unmeasured. Priority for future visual work: local curvature continuity at those locations before more tiny ornament. Confidence: high for the before/after improvement, medium for the remaining photographic contour judgment. Residual severity: low to medium in isolated close-up, low at whole-assembly size.

### RV-02 — PCB body and package composition: clear improvement, incomplete physical density

**Evidence:** final `pcb_top.png` and `pcb_bottom.png` against the preserved close-ups and `matrix_ii_front.jpg`, `matrix_ii_bottom.jpg`, `matrix_ii_back.jpg`; final hero for installed scale.

The larger centrally approved body better supports the observed package distribution while preserving the mounting relationship. The reviewer-returned top passives now sit on the board, the large MCU has leads on all four sides, and the three lugs now read as black board with a thin inner metallic edge rather than raised gold eyelets. The underside has a recognizable central rectangular AT7456E region, a larger forward VTX region, outer controller/power-package hierarchy and added passive banks. This is materially more informative than the baseline's eight equal rectangles. The 4-versus-3 side pad groups, camera-pad labels, polarity/arrow markings and subdued component print improve the visible composition. Bottom text is not mirrored; it can be read by rotating the underside view.

The corrected footprints do not visibly extend outside the substrate in these final views. The helper hides separately named camera/antenna connection objects, so the empty center in the isolated top image must not be interpreted as their absence from the assembly.

**Unresolved:** the physical photographs still show much denser and less regular small-component, solder and trace coverage, especially around the underside center and the aft interface area. Several model packages use simple generic bodies and pin arrangements. The model should not be presented as a component-exact board reproduction or an electrical layout. Further fidelity would come from measured/photo-registered package positions and selectively reproducing the missing observed small-feature clusters, rather than filling gaps with arbitrary circuit motifs. Confidence: high for the corrected overhang, lead rows, rims and improved hierarchy; medium for photographic proportion; low for exact unmeasured placement. Residual severity: medium for a PCB macro view, low for overall silhouette. No new major regression found.

### RV-03 — Optional battery: body and graphic agreement improved

**Evidence:** final `battery_closeup.png` and optional assembly hero/underside/right against the baseline battery and the actual 280 mAh top photograph/diagram.

The cap and projecting connector are correctly black in appearance, and the recessed contacts replace the baseline's white block and protruding gold dots. Softened pouch edges, narrow seams and an end fold make the body less like a featureless rectangular solid. The angular green/yellow/black wrapper, bold 280/95C hierarchy, LiHV line and filled LAVA lettering are visible on the final curved surface. There is no large image stretch or broken wrapper seam in the inspected views. The installed pack reads as the selected short 280 mAh accessory, with an explicitly unplugged lead; the longer 320 mAh installed reference was not used to enlarge it.

**Correction verified:** an intermediate optional underside exposed mirrored BETAFPV cap lettering. The integrator limited that artwork to the evidenced top surface and left the unevidenced underside plain black. The refreshed final `battery_closeup.png` and optional `underside.png` were actually re-inspected: top branding remains visible and the mirrored underside print is gone. That finding is closed.

**Unresolved:** the final print is an authored approximation of the typeface and motif, the pouch remains unusually regular, and the broad reverse-face wrapper artwork is repeated without independent reference evidence. Confidence: high for color/label hierarchy improvements; medium for pouch shape; low for reverse-face details. Residual severity: low, confined to close inspection of the optional pack.

### RV-04 — Materials: modest improvement with unresolved optical uncertainty

The new source preserves a violet Racing frame, thin pale canopy, reflective motor bells, green lens tint and transparent blades. The canopy gains most of its improved credibility from contour continuity. The frame is slightly warmer and the lens coating more visibly green; those are directionally compatible with the actual photographs. Clear blades retain visible edges and highlights in the final source images, including from below.

The studio render remains cleaner and more uniform than the physical specimen: broad frame regions appear fairly opaque, tiny solder/PCB finish variation is simplified, and canopy reflections reveal local curvature waviness. The real photos contain more transmitted light, background-dependent reflections and small manufacturing variation. Lighting and exposure are not matched, so this review cannot separate every color difference from illumination or declare a measured material match. Gloss/transmission values are estimates. Residual severity: low to medium for photographic realism; not a newly broken material assignment.

## Export comparison

All six first optimized evaluated-mesh close-ups in `output/web_optimized/inspection/` were inspected against their corresponding final source close-ups. These use the saved candidate meshes with the source studio; they are not serialized GLB/browser evidence.

### RV-05 — Visible optics reduction: new candidate regression corrected

The first optimized `canopy_front.png` and `canopy_oblique.png` showed distinctly polygonal/wavy black concentric lens rings, while the source front optics were smooth. The lens is the visual focal feature, so this was a salient loss at the supplied inspection scale even though small in physical extent. The reviewer requested preservation of the visible front cup, retainer/coating rings and optical boundary rather than a blanket increase to all model geometry. The integrator preserved the [rejected front close-up](refinement/rejected_web_lens.png) and protected the entire camera component in the next export.

**Correction verified:** the regenerated final [front](../output/web_optimized/inspection/canopy_front.png), [oblique](../output/web_optimized/inspection/canopy_oblique.png) and [right](../output/web_optimized/inspection/canopy_right.png) close-ups were inspected against source. The concentric rings and optical boundary are smooth again; the obvious reduction artifact is gone. RV-05 is closed for the evaluated-mesh preview. Confidence: high, from the same-view comparison. The rejected first candidate is not used for final acceptance.

The rest of the first candidate preserves canopy continuity, PCB markings/package hierarchy and battery typography. Lesser reduction effects are polygonal PCB mounting bores in the isolated macro views and a narrow triangular edge highlight/crease on the battery wrapper. Those do not erase the component improvements, but they are real differences and should not be described as pixel-identical output. No missing texture or broad UV scrambling was seen in these six views.

The final optimized GLB file hash was independently read from `output/web_optimized/air65-ii.glb`: `8ddbc0195e22c59bc8dcf6de34885021e5cc099aea5b33a08817a11a7b6395a7`. The integrator reports 262,810 triangles and 10,417,808 bytes for that asset. File size/triangle reduction and technical validation are not visual-fidelity evidence.

### RV-06 — Actual browser appearance and mobile framing

The reviewer inspected the supplied actual-browser [desktop assembled screenshot](site/refined_desktop.jpg), [top PCB screenshot](site/refined_top_pcb.jpg), [optional battery bottom screenshot](site/refined_battery_bottom.jpg) and [mobile screenshot](site/refined_mobile.jpg) from the final hashed asset. The reviewer did not conduct an independent interactive performance run. These screenshots are a separate browser test, not Blender renders relabelled as browser evidence.

Desktop views preserve the formed canopy, exposed camera PCB, richer flight-controller print/package layout and selected battery artwork. The optional bottom cap is plain black. No broad missing texture or black shoulder patch is visible. The browser is brighter and the blade faces appear milkier/whiter than in the source studio render. Therefore the browser can be described as preserving the main shapes and details in these views, but not as a calibrated or identical material match. Lighting, environment and renderer differences remain material to appearance.

The integrator reports a logarithmic depth buffer correction for thin-PCB-surface flicker. The supplied stills show a stable-looking board surface, but still images cannot certify stability over every camera motion. Performance conclusions belong to the [separately measured browser benchmark](browser_performance.json), not this visual report.

**Mobile correction verified:** the first mobile capture clipped the rightmost duct at the viewport edge and its zoom toolbar covered much of that duct. The refreshed final [390 × 844 mobile capture](site/refined_mobile.jpg) was independently inspected after the toolbar moved to a horizontal strip above the aircraft. All duct outlines now have visible margin and the controls do not obscure the aircraft. The [mobile parts panel](site/refined_mobile_parts.jpg) was also inspected; its overlay is intentional, with a visible close control. The framing finding is closed. These screenshots establish the displayed result at the captured viewport, not a universal responsive-layout guarantee.

### RV-07 — Serialized GLB round-trip: no new material or assembly loss observed

The final [hero](../output/web_optimized/roundtrip/hero.png), [underside](../output/web_optimized/roundtrip/underside.png) and [right](../output/web_optimized/roundtrip/right.png) were inspected after re-import of the actual hashed GLB. The manifest records `imported_glb: output/web_optimized/air65-ii.glb`, 1400 px resolution and 64 samples. This is a serialization check distinct from the evaluated-mesh preview.

Compared with the corresponding optional source views, the round-trip retains the assembled envelope, continuous canopy contour, smooth front optics, exposed camera PCB, flight-controller marks, wire routing, propeller planforms and battery graphics/pose. The black reverse cap remains unprinted. No new large hole, detached component, missing texture, mirrored body label or returned camera-ring faceting was observed. Motor crowns and wire bundles remain legible at assembly scale. Small specular/edge differences remain visible around reduced circular parts and thin surfaces; no claim of pixel identity or preservation at unlimited magnification is made. The round-trip passes this bounded visual delivery check.

## Residual priorities and final conclusion

| Priority | Remaining limitation | Practical implication / next useful evidence |
| --- | --- | --- |
| Medium, chiefly macro views | PCB still has fewer small components, simplified solder/trace coverage and generic package detail compared with actual Matrix II photographs. | Do not describe it as a component-exact board replica. A future pass should register observed package groups to clearer top/bottom evidence and measured footprints rather than add arbitrary texture noise. |
| Low to medium | Canopy local waviness, foot-neck creases and simplified vent/fillet contour remain visible in the isolated close-ups. | Preserve the established mount/clamp/arch anchors; improve local curvature with better physical close-ups or section measurements before revising global dimensions. |
| Low to medium | Frame/canopy transmission, blade clarity, lens coating and small surface finish differ with renderer and lighting. | Optical material properties and color are estimates. Controlled lighting/color references would be needed for a stronger material match; browser and Blender results must remain separately described. |
| Low | Optimized mounting bores and a battery-wrapper edge show minor macro faceting/highlight differences. | Acceptable for the inspected assembly/browser presentation; use the detailed source for close component inspection. This is a quality tradeoff, not perfect visual equivalence. |
| Low / evidence gap | Battery typeface/motif, highly regular pouch form and repeated reverse-face wrapper remain estimates. | The selected 280 mAh front appearance is better supported than the unseen reverse artwork. Obtain a matching reverse/side photograph before claiming exact packaging. |

The review accepts the finished refinement and final GLB `8ddbc0195e22c59bc8dcf6de34885021e5cc099aea5b33a08817a11a7b6395a7` for the documented visual presentation. The acceptance is based on actual inspected source, optimized, serialized and browser images, including re-inspection after the concrete overhang, cap-print, lens-reduction and mobile-framing findings. It does not inherit acceptance from the earlier v2 or delivery signoff.

No further major shape correction is indicated by the supplied views, and no mandatory visual delivery fix remains open. That conclusion does not erase the medium-priority fidelity limits above: the model is a more convincing, better-supported parametric recreation, with an editable detailed source and a visibly bounded optimized derivative. The photographs are not calibrated, several contours and placements are estimates, and no physical accuracy percentage or manufactured-fit certification is justified. Numerical anchor/schema/export checks support reproducibility and conformance to the chosen specification; they are not evidence of correspondence to every feature of a real Air65 II specimen.
