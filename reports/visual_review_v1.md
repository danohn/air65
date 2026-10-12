# Independent visual review — complete assembly v1

Reviewed on 2026-10-12 against `air65-ii-racing-v1`. This is an independent reviewer pass: no model, component, architecture, renderer or material file was changed. The first-render baseline remains in `output/review_v1/`.

**Verdict: the assembly captures the correct Air65 II structural layout and published nominal envelope, but is not yet a close visual reconstruction.** The most important remaining difference is the canopy's formed hood and arch topology. The propeller terminal outline is next. Local frame surface defects should be corrected before cosmetic refinement. Passing the numerical checks does not resolve these visual differences.

## What was actually inspected

Actual image-viewer inspection covered all seven assembly images: `hero.png`, `top.png`, `front.png`, `right.png`, `rear.png`, `underside.png` and `reference.png` under `output/review_v1/`. It also covered all four images under `output/frame/` (`hero`, `top`, `front`, `underside`) and the isolated propulsion renders listed in `propulsion_visual_review.md`.

Reference images inspected:

| Local reference file | Source ID | Role |
|---|---|---|
| `references/air65_ii_racing_oblique.webp` | `air65_ii_racing_oblique` | Current Racing catalog assembly and visual hierarchy |
| `references/air65_ii_racing_propulsion.webp` | `air65_ii_racing_propulsion` | Propeller, motor and duct close-up |
| `references/air65_ii_racing_underside.webp` | `air65_ii_racing_underside` | Frame, motor pads and wire bundles; its optional battery differs from this battery-free baseline |
| `references/air65_ii_frame_diagram.webp` | `air65_ii_frame_diagram` / `frame_drawing` | Dimensioned frame layout and side profile |
| `references/air65_ii_frame_black_top.webp` | `air65_ii_frame_black_top` | Strong plan-view reference for pad shape, support arrangement and cradle apertures |
| `references/air65_ii_frame_details.webp` | `air65_ii_frame_details` | Open basket and local mounting details |
| `references/air_ii_canopy_black.webp` | `air_ii_canopy_black` | Formed collar/hood, side legs and perforated tail |
| `references/air_ii_canopy_structure.webp` | `air_ii_canopy_structure` | II-specific cap, vent and aperture topology |
| `references/air_ii_canopy_side.webp` | `air_ii_canopy_side` | Installed arch and open side profile; left panel is the II version |
| `references/air_ii_canopy_diagram.webp` | `air_ii_canopy_diagram` / `canopy_drawing` | Clamp and aperture form; explicitly dimensioned holes |
| `references/camera_diagram.jpg` | `camera_drawing` | Camera envelope, barrel and optical-face appearance |
| `references/prop_diagram.jpg` | `prop_drawing` | Propeller nominal diameter/bore and qualitative outline |
| `references/motor_diagram.jpg` | `motor_drawing` | Motor nominal envelope and side-profile layers |
| `references/air65_ii_electronics.webp` | `air65_ii_electronics` | Board shape, component density and finish |
| `references/photo_racing_oblique.webp` | `photo_racing_oblique` | Physical Racing specimen cross-check |
| `references/photo_freestyle_side_oblique.webp` | `photo_freestyle_side_oblique` | Physical Air II canopy/camera form; Freestyle colors and props are not Racing targets |
| `references/photo_variants_low_front.webp` | `photo_variants_low_front` | Low-angle physical basket and canopy profile cross-check |

Source URLs and provenance resolve through `references/manifest.json`, `references/technical_manifest.json` and `specs/design_spec.json`. Manufacturer catalog views may be rendered or retouched. Physical photos have perspective, blur and occlusion; their motor accent colors also differ from the selected current catalog version.

The shared convention is millimetres, +X right, +Y forward, +Z up, frame-plastic bottom datum z=0. The independent reviewer read the frozen design/spatial specification. The integrator's `output/review_v1/validation.json` reports `status: pass` across 31 checks. This review did not rerun those checks or independently certify physical dimensions. No calibrated pose match, silhouette-overlap metric or physical metrology was performed.

## Ranked actionable findings

### VR-01 — formed canopy reads as a ladder and simple lens ring

**Severity: high for visual identity. Confidence: high.** In the front, hero, top and reference views, the canopy reads as two thin rails with rectangular crossbars and an exposed circular lens collar. The real Air II canopy has a broader, smoothly formed hood around the lens, a small vent in the cap, and rounded trapezoidal/oval apertures along the upper/rear strap. The current model contains a hood object and real openings, but their visible shape and proportions are too slight and rectilinear. This difference is strongly supported by both manufacturer canopy images and physical photos.

Revise the estimated surface around the upper collar and its shoulders into the broader curved cap, blend it into the side legs, and shape the arch openings with rounded edges and changing width. Preserve the open side spaces, camera PCB visibility, published 10.2 mm clamp opening, mounting anchors and current camera pose. Do not turn the canopy into a closed shell. Keep the current arch height initially: the cap and aperture contour need correction before a global height change can be justified. Evidence: `air_ii_canopy_black`, `air_ii_canopy_structure`, `air_ii_canopy_diagram`, `air_ii_canopy_side`, both oblique physical photographs.

### VR-02 — GF1207 tips remain too continuously tapered

**Severity: medium. Confidence: high for mismatch, medium for exact contour.** The full model repeats the leaf-like outer blade taper identified as PR-01 in `propulsion_visual_review.md`. The reference has broader round-cornered paddle ends and a straighter edge on one side. Revise only estimated chord/sweep/terminal stations, retaining the published 31 mm envelope and 6.8 mm maximum chord. Recheck after pitch and sweep. The shared hub-radius trial of 2.4 mm is an integrator decision within an existing estimate range, not a newly measured dimension. Evidence: `prop_drawing`, `air65_ii_racing_propulsion`; assembly `top`/`hero` and isolated propulsion `top`.

### VR-03 — local frame surface artifacts at mounting pads and bridges

**Severity: medium. Confidence: high for visible dark slivers, medium for their cause.** Frame-only `top` and `hero` reveal hard black crescents/slivers around the motor-pad bores and dark lines along the front/rear inter-duct bridge. Some rib-to-rim joins also have abrupt bright/dark discontinuities. These are much stronger than the smooth, continuous moulded surfaces in the frame reference and remain visible in the battery-free underside assembly.

Inspect evaluated pad/bridge topology for coincident faces, non-planar polygon triangulation, incorrect normals, touching Boolean boundaries and modifier artifacts. Correct the geometry when defects are found; do not hide them with opaque materials. Confirm that each motor pad is a continuous rounded triangular plate around the three bores and central hole, and that the upper/lower screw-protection lips remain separate intended geometry. Preserve the motor bolt circle, bore sizes, support count and frame envelope. Shadows can darken a real hole edge, so an isolated diagnostic material or normal inspection should distinguish a real topology fault from lighting. Evidence: `air65_ii_frame_black_top`, `air65_ii_frame_details`, `frame_drawing`.

### VR-04 — battery cradle plan topology omits two narrow windows

**Severity: low to medium, most visible in bare frame/underside. Confidence: high for plan-view difference, medium for construction.** The black frame plan and dimension drawing show a large central opening plus narrow transverse openings immediately ahead and behind it. The model shows the large opening between two simple bands, without the corresponding narrow windows.

Refine the estimated cradle-band form to recover those fore/aft windows, checking whether the reference comes from an offset/sloped upper-versus-lower band rather than adding arbitrary solid bars. Preserve the verified 11.4 by 6.2 mm battery opening and the optional battery clearance. This is secondary to the canopy and prop outline but is a visible frame topology difference. Evidence: `air65_ii_frame_black_top`, `frame_drawing`; `output/frame/top.png`, `output/frame/underside.png`.

### VR-05 — camera PCB face and front optical appearance

**Severity: low after silhouette fixes. Confidence: high for the PCB finish mismatch; medium for optical details.** The v1 camera PCB is visibly olive green over most of its exposed face, while the references have black solder mask with a narrow substrate edge. The main integrator identified buried mask faces and reported a correction in progress; this baseline review confirms the visible symptom but has not reviewed the correction. The front optical element also reads as a flat green disk with decorative concentric rings; the camera reference has a darker recessed optical stack with stronger local glass reflections.

Verify the black mask surfaces in the next render. Then improve the estimated lens recess and glass shading while preserving the published 10 mm outer barrel and 15 mm front-to-board depth. The physical specimen's optical tint varies with view, so no exact color is certified. Evidence: `camera_drawing`, `photo_racing_oblique`, `photo_freestyle_side_oblique`.

### VR-06 — material contrast weakens transparent parts and board detail

**Severity: low. Confidence: high for appearance, medium for cause.** Frame and canopy look more opaque and uniformly pastel than the translucent reference parts; props are cloudy against the grey background. The catalog's polished white-background lighting exaggerates clarity, but the physical photos still support some transmission. Board component density is simplified, especially the exposed underside, and the model lacks much of the small solder-pad/trace pattern. Those are secondary appearance limitations, not reasons to move mounts or enlarge parts.

After geometry corrections, tune transmission, roughness and lighting for visible edges, keep a separate diagnostic material for geometry inspection, and add only well-supported electronic surface detail. Do not reproduce unverifiable chip labeling. Evidence: both oblique physical photos, `air65_ii_racing_oblique`, `air65_ii_electronics`, `air65_ii_racing_propulsion`.

## Supported layout and limits

- The four circular ducts, square motor layout, rotated central board/mount pattern, large open duct baskets, four support arms per duct and narrow central cradle are recognizably the II frame architecture. The frame side profile agrees qualitatively with the dimension drawing. No global frame-envelope or motor-center change is supported by this review.
- The canopy remains an open framework, the camera sits above the FC, and the antenna points rearward/upward. These are appropriate overall choices. Exact camera/antenna installed positions remain estimates. The view poses are not matched closely enough to justify shortening the antenna or lowering the camera solely from apparent image height.
- The layered motor can, visible copper/open crown and prop seating are plausible. Individual winding topology remains unverified. Integrated three-wire bundles are now present, resolving the isolated-component deferral; their exact bends and length remain approximate. Motor-side heatshrink is more visually subdued than in the catalog close-up and can be refined after major shape work.
- The optional battery is absent from this baseline. Its absence is not a defect: the specification assigns it to a separate removable collection, and the underside catalog comparison includes a different capacity pack.
- Numerical compliance, image-based proportion checks, visually plausible appearance and manufacturing accuracy are separate claims. This model currently supports the first two only within the documented sources and estimates; it does not establish a physical reconstruction tolerance or flight-ready replacement suitability.

Next review should inspect the same preserved camera views after canopy/prop changes, verify that pad/bridge slivers are resolved, and record the disposition of VR-04 through VR-06. Do not claim the entire visual review has passed if only the numerical checks pass.
