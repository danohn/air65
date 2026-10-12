# Canopy diagnostic audit before the next refinement

The current canopy preserves the important Air II topology and the shared mounting arrangement, but it still reads as several intersecting strips around a circular collar. The highest-value change is a continuous moulded transition between the collar, protective cap, arch and mounting-leg roots. The evidence does **not** currently justify moving the camera, altering the 10.2 mm clamp, or changing the arch height.

This is an audit and proposed scope, not an implementation. No component JSON, shared specification, renderer, material or Site asset was edited. The older Sketchfab Air65 was not used as dimensional or geometric ground truth.

## Baseline and evidence inspected

Current component: `specs/components/canopy.json`, SHA-256 `334fc32ef511f73c69aec64fefb14ce88d8b09238aabd249727b731966520f68`.

Shared architecture: `specs/spatial_architecture.json`, SHA-256 `e6f146406d3d3ac2e6e41b399e9a51d3a692c30736b488815bceb32c953b2036`.

The audit read `research/sketchfab_comparison_handoff.md`, the current JSON nodes and scalar registry, `output/final/metrics.json`, and the current final render manifest. It visually inspected `hero.png`, `front.png`, `right.png`, `top.png` and `reference.png` in `output/final/`.

References inspected:

- `references/air_ii_canopy_structure.webp`: **left Air II panel only**. The right panel is the older part and was excluded.
- `references/air_ii_canopy_side.webp`: **left Air II panel only**, for assembled side contour.
- `references/air_ii_canopy_black.webp`: moulded collar, shoulder, leg-root and opening contours.
- `references/air_ii_canopy_diagram.webp`: aperture topology and published nominal openings.
- `references/air65_ii_racing_oblique.webp`: the selected Racing assembly.
- `references/photo_racing_oblique.webp` and `references/photo_freestyle_side_oblique.webp`: physical specimens, used for the shared Air II canopy only. The Freestyle frame and other component differences were excluded.

The closest assembly comparison is the model's perspective `reference.png` against the manufacturer's Racing oblique. They show comparable front-side regions but are not camera-calibrated matches. The orthographic `right.png` is useful against the left Air II side panel after accounting for opposite on-screen nose directions. The black isolated part and line drawing establish contour and topology, but they do not establish installed 3D dimensions from pixel lengths. The physical photographs confirm the moulded-part appearance under real lighting; their lens distortion, pose and selected tilt are unknown.

No image-registration error, physical dimensional error percentage or absolute thickness measurement is claimed.

## Ranked findings and proposed geometry scope

### 1. Collar and brow still look like a ring with an attached band — highest priority

**Observed:** The final front view shows a fairly uniform white annular halo around the lens, with small ledges where the upper brow ends. The perspective reference view makes the brow's cut ends and the arch-to-collar connection apparent. The Air II black part and structural illustration instead show a shaped cap whose side cheeks flow into the shoulder and leg root. The physical photographs show the same transition, including a small genuine opening above the lens.

The current node structure explains the appearance: a separate annulus, a shallow annular shoulder sheet and a separate upper swept cap overlap. The exposed boundaries are not a common moulded surface. The shoulder is approximately 13.0 mm wide in the current evaluated model; simply making it wider is unlikely to solve the problem.

**Affected nodes:**

- `lens_clamp_annulus`
- `formed_collar_shoulders_with_vent`
- `continuous_curved_protective_brow`
- the collar ends of `left_leg`, `right_leg` and `formed_rear_arch_with_rounded_apertures`

**Proposed fix:** Rebuild the visible collar/shoulder/cap junction as a common surface patch network, with matching boundary positions and tangents. Retain an exact cylindrical 10.2 mm inner clamping land. Replace the uniformly exposed outer halo with the Air II's asymmetric local contour: thin lower clamping rim, shaped side cheeks and an upper protective cap. Taper the cap's axial projection down into both cheek roots so its ends disappear into the shoulder instead of ending in visible rectangular ledges. Keep the small real vent behind the cap. Retain approximately the existing maximum shoulder width for the first comparison render; change surface distribution and axial form before changing the overall width.

The existing cap's ends retain substantial forward projection rather than fading into the body. Adjusting that local transition is more directly supported than increasing global shell thickness or closing the camera sides.

**Confidence:** High that the exposed seams/step changes are wrong; medium for the proposed unmeasured cheek and cap contours. No verified dimension change is required.

### 2. Leg roots and mounting feet need continuous contour transitions — high priority

**Observed:** In the model front and perspective views, the side strips arrive at the collar as blunt, widened ends. The front tongue and two clamp-tab rings also read as distinct attached pieces. At the lower end, circular feet resemble washers intersected by strips. The black Air II reference shows gradual necks and rounded transition regions; the physical photographs retain that continuous contour despite the translucent material.

The long portions of the side legs already have a useful low sweep and preserve the large open side triangles. Their overall endpoints should remain fixed.

**Affected nodes:**

- `left_leg`, `right_leg`
- `foot_left`, `foot_right`, `foot_front`, `foot_rear`
- `formed_front_tongue_with_slot`
- `clamp_tab_neg1`, `clamp_tab_1`
- adjoining lower portions of `formed_collar_shoulders_with_vent`

**Proposed fix:** Preserve the long leg centerlines and all screw axes. Replace only the final few millimetres of each collar junction with a smooth taper into the shoulder, sharing the visible surface boundary. Blend each strip into a modest teardrop/rounded foot neck around its existing bore instead of intersecting a separate circular washer outline. Form the front tongue's upper end and clamp tabs as a connected split clamping root while preserving the genuine longitudinal slot and 1.1 mm screw bore. Keep the screw and head separate as real hardware.

The root-blend length and outer foot contour are image estimates; an initial local blend over roughly 2–4 mm is a modelling proposal, not a measured Air II dimension. Local refinement must not push the feet off their nominal axes or close the open side triangles.

**Confidence:** High for the need for smoother visible roots; medium for their exact radii and foot outline. No mounting-point change is required.

### 3. The revised arch openings are plausible, but their surrounding section remains too planar — medium priority

**Observed:** The current top view now contains a rounded trapezoidal opening and an oval opening, so the earlier ladder defect is substantially improved. It would be incorrect to report that the current model still consists of rectangular crossbars. The remaining problem is the broad, almost uniform flat strip and abrupt width/curvature transition where that strip meets the upper collar. In the Air II black part, the opening edges, shoulder and central web are integrated into the surrounding moulded contour.

**Affected node:** `formed_rear_arch_with_rounded_apertures`, chiefly its front-most opening/web and the collar attachment; adjoining `formed_collar_shoulders_with_vent`.

**Proposed fix:** Keep the opening order and the 4.9 mm nominal oval width. Refine the front trapezoid's boundary and surrounding web together with the collar patch, rather than reshaping only its hole. Use a gently crowned/rounded local strip section and smooth width transitions through the oval and upper web. Preserve real through-openings and the documented arch centerline/peak. Small adjustment holes that are occluded by the antenna in an assembly photograph should not be removed merely because they cannot be seen there.

The source images do not support a precise numerical claim that the current large opening is too long or too short. The unmounted part is already shaped and projected, so treating its apparent length as a flat developed length would be unreliable.

**Confidence:** Medium for local contour/cross-section improvement; low for any change to total arch length or opening length from these views alone. No arch-height change is proposed.

### 4. Thickness should vary locally through joints, not be increased everywhere — medium priority

**Observed:** Thin rectangular strips, separately thickened shoulder surfaces and the cap create changes in section that remain visible under the final lighting. The side view also exposes an almost uniform thin ribbon across the arch. The physical part has thin edges with modest moulded rounding and reinforced roots; it does not resemble a uniformly thick shell.

**Affected nodes:** `left_leg`, `right_leg`, `formed_front_tongue_with_slot`, `formed_rear_arch_with_rounded_apertures`, `formed_collar_shoulders_with_vent`, `continuous_curved_protective_brow`.

**Proposed fix:** Retain the selected 0.65 mm strap thickness as the initial datum. Shape the cross-section so the strips have rounded edges and shallow crown, with local fillets/tapers at the roots. Transition the shoulder/cap wall into that section without exposed overlaps. Use enough topology to support curvature, but do not increase angular or longitudinal sampling simply to raise the polygon count. A shared boundary and better normal continuity matter more than extra subdivisions.

Material changes may improve translucency, but should follow the geometry check. They should not be used to hide these structural seams.

**Confidence:** Medium. Exact mould wall thickness and fillet radii remain unverified.

## Anchors and parameter-change requests

**No geometry-driving shared parameter change is requested for this first refinement.** Preserve:

- Frame/assembled mounting axes at the verified 25.5 mm pattern, and current support plane.
- The 10.2 mm clamp opening and 1.1 mm cross bore.
- The 4.9 mm canopy aperture width.
- Camera pose, 10 mm lens, 15 mm camera depth and its shared lens/PCB anchors.
- The selected 39.4 mm arch centerline peak and its current position.
- Open side triangles and exposure of the camera PCB.

The installed side reference broadly supports the chosen arch-rise/mount-span relationship. Differences in apparent camera-PCB-to-arch clearance could partly reflect a different selected camera angle or projection; they are not sufficient evidence to move the camera or lower the arch now. A later camera-matched comparison can revisit those estimates centrally if needed.

There is one **metadata consistency request** for the main integrator: `canopy_half_width` is currently 19.0 mm and is described as the installed envelope including mounting feet, while the evaluated final canopy reaches X = ±20.3812 mm. The existing side foot centers are ±18.0312 mm and their estimated outer radii are 2.35 mm, which explains the discrepancy. Do not scale the mounting pattern to satisfy the 19.0 mm estimate. Either derive/report this envelope from the revised evaluated geometry, or update the central estimate to approximately 20.4 mm for the existing baseline and document its estimated status. If the foot outline changes during the approved refinement, recompute the value afterward. This is not a request to enlarge the canopy.

## Proposed implementation boundary and acceptance

If approved, the geometry pass should be confined to the canopy JSON and its authoring/reporting files. Camera and electronics remain separately owned. The scope is the common collar/shoulder/leg-root surface, foot necks and local strip sections described above; it excludes whole-aircraft scaling, a closed camera enclosure, new ornament or adoption of the older Sketchfab canopy.

Acceptance should use preserved baseline and new renders at identical camera/lighting settings, then compare the model's perspective reference view with the actual Racing reference and the side profile with the left Air II side illustration. Include an isolated canopy view to make seams and opening topology inspectable without PCB/antenna occlusion. Check that:

1. The cap has no abrupt cut-end ledges and the collar/shoulder/leg roots read as a single moulded contour.
2. Openings remain genuinely open; no hidden sheet or new bubble encloses the camera PCB.
3. Mounting axes, clamp/aperture nominals and the selected arch peak remain numerically unchanged.
4. The large side triangles and thin low mounting legs are retained.
5. Surface normal continuity and local wall thickness improve without a large increase in polygon count.
6. An independent reviewer compares the revised part against the **Air II** evidence and explicitly states remaining uncertainty.

Successful schema or render checks will establish technical validity only. The proposed scope still requires a new visual assessment before any claim of improved Air II fidelity.
