# Air65 II Racing spatial architecture

Contract: `air65-ii-racing-v1`. The scalar authority is `spatial_architecture.json`. This is a reference-based reconstruction of the standard Air65 II Racing configuration, using the published frame dimensions and explicitly estimated assembly placement. It does not establish manufacturing interchangeability.

All geometry uses millimetres and degrees. The right-handed world axes are +X aircraft right, +Y forward and +Z up. XY zero is the center of the motor square. Z zero is the lowest frame-plastic datum. The published **82.6 × 82.6 × 15.1 mm envelope applies to the frame only**, not the canopy or antenna. No physical manufacturing tolerances were found. The JSON `uncertainty` ranges are reconstruction estimates, never claimed production tolerances.

## Placement and dimensional authority

The four motor axes lie at X and Y = ±22.9809703886 mm, giving exactly 65 mm between diagonal motors. Each duct has a verified 16.5 mm clear inner radius. The maximum outer rim radius is derived as 18.3190296114 mm from the overall frame footprint; it is not a uniform wall thickness. The upper continuous band occupies **Z11.3 to15.1**, retaining the verified 3.8 mm height. Four slender bowed supports descend from each ring to the low motor pad. The walls must not be extruded down to the bottom of the frame.

| Feature | World Z, mm | Evidence status |
| --- | ---: | --- |
| Lowest frame plastic | 0 | Chosen datum |
| Motor pad lower surface | 1.45 | Derived from estimated pad thickness |
| Motor mounting plane | 2.70 | Estimated from frame side imagery |
| Motor upper shoulder | 11.25 | Estimated placement + verified8.55mm body height |
| Duct band bottom / top | 11.30 /15.10 | Published3.8mm band within published frame envelope |
| Prop hub bottom / top | 11.35 /14.65 | Estimated seating + verified3.3mm hub height |
| Prop blade reference plane | 12.50 | Estimated; blade twist changes local heights |
| Frame FC boss top | 13.00 | Estimated |
| FC PCB bottom / center / top | 15.00 /15.50 /16.00 | Estimated placement, verified1mm thickness |
| Canopy mounting feet | 17.20 | Estimated |
| Camera PCB center | 25.160726 | Derived from chosen camera pose |
| Lens front center | 31.50 | Estimated |
| Canopy arch peak | 39.40 | Estimated |
| Antenna tip center | 54.00 | Estimated, not a verified whole-craft height |

The 12.4 mm lowered-duct annotation is compatible with a motor pad2.7mm below the15.1mm top, but its reference datum remains ambiguous. Consequently the2.7mm mounting elevation is still labelled **estimated**. The motor pad thickness is1.25mm and the lowest screw-protection feet may reachZ0. The motor retains its verified9mm diameter,8.55mm body height and3.4mm shaft extension.

Propellers have a31mm swept diameter and3.3mm hub thickness. The resulting nominal radial clearance is1mm. That constraint applies to the farthest evaluated blade vertex, including chord, sweep and modifiers; using15.5mm as a station centerline radius would make a wide blade exceed the allowed envelope. Opposite corners share handedness; no real flight-controller motor numbering is inferred.

## Two mounting patterns preserved

The frame's25.5mm square pitch gives four cardinal axes at radius18.0312229203mm. The FC's published26mm pitch gives three nominal board-lug centers at radius18.3847763109mm; the forward lug is absent. Both values remain unchanged. The chosen assembled screw axes coincide with the frame axes. The model represents a0.3535533906mm inward radial grommet deformation/eccentricity at the board interface. This is a plausible assembly inference, not a published silicone tolerance. Grommet holes and screw heads must follow the frame axes; nominal PCB lugs retain the26mm pattern.

The FC central body is an estimated26.4mm square rotated45degrees, with front tip clipped atY16.2mm and side/rear tips at16.3mm and three rear/side lugs. Outline, lug radius and package placement are visual estimates; the1mm board thickness is verified. All four canopy feet shareZ17.2mm; the front foot mounts independently of the three-lug PCB.

## Camera, canopy and antenna

The camera front center is **(0,10,31.5)**. Its chosen optical elevation is25degrees, one of the manufacturer's documented settings; the actual photo setting is unknown. The optical unit vector is `(0,0.9063077870,0.4226182617)`. The camera PCB plane center is **(0,-3.5946168055,25.1607260739)**, exactly15mm behind the front plane along this vector. The board's right vector is `(1,0,0)` and its up vector is `(0,-0.4226182617,0.9063077870)`. Camera-local+Y is optical forward and camera-local+Z is image up; apply EulerX=25degrees. Cylinders authored along localZ need an additional localX=-90degrees to point along camera-local+Y.

Keep the verified11mm board width,14mm board height,15mm axial depth,10mm lens diameter and10.2mm canopy clamp diameter. The PCB's estimated0.8mm thickness is separate. The nominal lower camera-board edge isZ18.8166mm, approximately2.8166mm above the bare FC top; check individual chips/connectors separately. The collar center is2mm behind the front lens plane, an explicit estimate.

The canopy is an open skeleton: collar, front tongue, slender side legs and perforated rear arch. The JSON contains representative shared centerline paths and exact mount endpoints. Preserve large side openings exposing the camera PCB and FC. Estimated strap width/thickness are1.6/0.65mm. The arch rises22.2mm above the screw plane; the rise-to-front/rear-mount-span ratio0.616 matches the photographic estimate0.62±0.07. Lens rise ratio0.397 lies within the visual estimate0.42±0.07. These are photograph-derived plausibility checks, not tolerances.

The rear antenna centerline runs from `(0,-9,34)` to `(0,-24,54)` with estimated1.35mm main-tube radius and2.65mm maximum tapered base radius. Keep it black and appreciably thicker than the Champion whip antenna. All antenna dimensions remain uncertain and centrally editable.

## Battery cradle

The verified retention opening is11.4mm wide and6.2mm high. Estimated internal floorZ1.1 and ceilingZ7.3 retain that opening within the15.1mm frame envelope. Two loops center atY±7.2mm. The optional280mAh battery is54mm alongY,10mm acrossX and6mm high, centered at `(0,0,4.2)`. This gives0.7mm nominal side clearance and0.1mm vertical clearance on each side. Its terminal connector points rearward. The underside reference shows a320mAh label; do not copy that longer pack into the selected280mAh assembly.

## Component-author obligations

Use the registry's shared scalar names through `{ "param": "id" }`. Only the main integrator may approve architecture changes. Tiny local cosmetic dimensions can be estimated and documented, but component authors must not rescale the frame, motor square, FC pitch, camera depth or propeller envelope to make parts fit. Canonical placement names are `motor_body_center_z`, `prop_swept_radius`, `prop_blade_reference_z`, and `fc_pcb_center_z`; no duplicate aliases are supplied.

The JSON supplies four motor anchors, four frame mounts, four assembled screw axes, three nominal PCB lugs, camera plane basis, collar, arch paths, antenna endpoints and battery anchor. Numeric checks distinguish renderer tolerances from evidence uncertainty. Remaining high-priority uncertainty is the exact assembled vertical stack, compliant mounting detail, actual propeller airfoil and flexible canopy bend. Those should be assessed by independent visual review before cosmetic refinement.

## Main-integrator revision after independent review

The estimated propeller hub radius was revised from2.2 to2.4mm for reviewPR-02, within its original1.9–2.5mm uncertainty interval. This improves the visual hub-to-blade proportion without changing any verified dimension or mounting anchor. The JSON revision history records this change; final builds capture its exact hash.


Refinement12 October2026: the central PCB outline estimate was revised from24 to26.4mm using lug-normalized manufacturer image edge spacing. The verified26mm mounting pitch and1mm substrate thickness are unchanged. Photographic outline uncertainty is±0.5mm; side/rear clips preserve lug bore clearance. See `reports/refinement_pcb_dimension_check.md`.
