# Air65 II dimensional research

Research date: 12 October 2026. The target was changed from original Air65 to **Air65 II** while research was active. Only Air65 II-compatible values are proposed for the model. The machine-readable evidence ledger is `dimensions.json`.

## Recommended coherent version

Use **Air65 II Racing, 2026 configuration**: standard Air65 II frame, Air II canopy, Matrix 1S 5IN1 II FC with motor sockets, 0702 (2026) 30000KV motors, GF1207 three-blade props, C03 camera and copper-pipe VTX antenna. Published dry mass is 17.7 g. The current official Racing image has a transparent purple frame, translucent white canopy, transparent propellers and purple/silver motors. A LAVA II 280mAh or 320mAh battery is optional; the design specification should choose explicitly. [Product specification](https://betafpv.com/products/air65-ii-brushless-whoop-quadcopter), [Racing assembly image](https://betafpv.com/cdn/shop/files/Air65_II_Brushless_Whoop_Quadcopter_Racing.jpg?v=1779348712).

Champion has a different 2.20 g frame, 36000KV dual-bearing motors, direct motor soldering and a whip antenna. Freestyle uses the standard frame, 25000KV motors and GF1219S props. Wisp combines an Air65 II frame with older Air FC and motors. These configurations must not be mixed. [Air65 II variants](https://betafpv.com/products/air65-ii-brushless-whoop-quadcopter), [Wisp specification](https://betafpv.com/products/air65-air75-wisp-brushless-whoop-quadcopter-limited-edition).

## Published frame dimensions

| Quantity | Nominal | Interpretation |
| --- | --- | --- |
| Wheelbase | 65 mm | Diagonally opposite motor axes |
| Frame envelope | 82.6 × 82.6 × 15.1 mm | Frame only |
| Duct opening | Ø33 mm | **Inner** circle in drawing |
| Upper duct wall band | 3.8 mm | Continuous band, excluding open basket below |
| FC frame mounting pattern | 25.5 × 25.5 mm | Rotated square; four mounts at cardinal body directions |
| FC screw pilot hole | 1.2 mm | Prose; designed for M1.4 screws |
| Battery slot | 11.4 × 6.2 mm | Internal width × height |
| Motor mounting | 3 × M1.4 on Ø6.6 mm | Equal angular spacing; 6.6 is bolt-circle diameter |
| Central motor opening | Ø4 mm | Frame drawing |

The side drawing clearly distinguishes 3.8 mm upper band and 15.1 mm maximum frame height. The prose additionally mentions 12.4 mm lowered ducts without defining its datum; do not substitute it for either dimension. Material is PP and nominal mass is 2.65 g. There are four braces per motor. No manufacturing tolerances are published. [Frame specification](https://betafpv.com/products/air65-ii-brushless-whoop-frame), [dimensioned plan and side drawing](https://cdn.shopify.com/s/files/1/1778/6615/files/Air65_II_Brushless_Whoop_Frame_diagram.jpg?v=1750838480).

## Other verified nominal dimensions

| Component | Published dimensions | Evidence |
| --- | --- | --- |
| 0702 motor (2026) | Ø9 body; 8.55 mm base-to-shoulder; Ø1 shaft; 3.4 mm upper extension; 35 mm wire with connector | [Motor page](https://betafpv.com/products/0702-brushless-motors-2026), [dimension image](https://cdn.shopify.com/s/files/1/1778/6615/files/0702_Brushless_Motors_2026_diagram.jpg?v=1769070401) |
| GF1207 propeller | Ø31 swept diameter; 3.3 mm central thickness; 6.8 mm maximum blade width; Ø1 bore; 0.7 inch pitch | [Propeller specification](https://betafpv.com/products/gemfan-1207-3-blade-propellers-1-0mm-shaft) |
| Matrix 1S 5IN1 II | 1 mm PCB; nominal 26 × 26 mm pattern; three mounting lugs, front omitted | [FC specification](https://betafpv.com/products/matrix-1s-5in1-ii-brushless-flight-controller), [top image](https://cdn.shopify.com/s/files/1/1778/6615/files/Matrix_1S_5IN1_II_Brushless_Flight_Controller_top_front_gyro_update.jpg?v=1777532692) |
| C03 V2 | PCB 11 mm wide × 14 mm high; front lens-to-board depth 15 mm; lens outer diameter 10 mm; wire 40 mm | [Camera specification](https://betafpv.com/products/c03-fpv-micro-camera), [dimension image](https://cdn.shopify.com/s/files/1/1778/6615/files/C03_FPV_Micro_Camera_V2_diagram.jpg?v=1752743122) |
| Air II canopy | Camera aperture Ø10.2; large tail opening width 4.9; front foot bore Ø1.5; transverse clamp screw bore Ø1.1 mm | [Canopy drawing](https://cdn.shopify.com/s/files/1/1778/6615/files/Air_II_Canopy_Diagram.jpg?v=1760929267) |
| Air II canopy tilt | 15°, 25°, 35°, 45° nominal settings; stock angle not stated | [Canopy page](https://betafpv.com/products/air-ii-canopy) |
| LAVA II 280mAh | 54 × 10 × 6 mm body; 6.8 g | [Battery page](https://betafpv.com/products/lava-ii-1s-battery), [dimension image](https://cdn.shopify.com/s/files/1/1778/6615/files/LAVA_II_1S_280mAh_Battery_dimensions.jpg?v=1763610020) |
| LAVA II 320mAh | 64 × 10 × 6 mm; 8.2 g | [Battery page](https://betafpv.com/products/lava-ii-1s-battery) |

Motor nomenclature **0702 does not mean a 7 mm outside diameter**. Use the published Ø9 envelope. The motor diagram shows Champion coloring, although it is the shared family dimension image; Racing should retain its own purple/silver appearance. The older motor's 4.2 mm shaft extension must not carry over.

The battery length drawing includes the main terminal cap and excludes the projecting connector nose. Camera depth is shown to the PCB plane; rear chip projection has no separate published dimension. The current C03 drawing is explicitly V2. Older search results quote 11 × 14.1 × 13.5 mm; those should not override the current V2 drawing.

## Calculations for the spatial architect

These are derived values, **not additional verified measurements**. They assume the square and diamond layouts shown in the frame drawing:

- Adjacent motor-axis distance: `65 / sqrt(2) = 45.96194 mm`.
- Motor x/y offsets about body center: `±22.98097 mm`; the architect supplies axis signs and z datum.
- Frame mounting-hole cardinal offset: `25.5 / sqrt(2) = 18.03122 mm`.
- FC nominal mounting-hole cardinal offset: `26 / sqrt(2) = 18.38478 mm`.
- Maximum duct outer diameter: `82.6 - 45.96194 = 36.63806 mm`, assuming the outer rings define the XY envelope. This is an outer envelope, **not proof of a uniform 1.819 mm wall**: the profile can taper or have a flange.
- Nominal radial prop clearance: `(33 - 31) / 2 = 1 mm`.
- Nominal radial camera-clamp clearance: `(10.2 - 10) / 2 = 0.1 mm` before clamping.

The **25.5 mm frame / 26 mm FC mismatch is real in the reviewed manufacturer pages**. Keep both source values in the specification. Grommet compliance could accommodate the 0.354 mm radial offset, but this is an assembly inference, not a published tolerance. If the model chooses a common assembled mount axis, name that choice rather than labeling both dimensions verified and equal.

## Missing dimensions and accuracy limits

No reviewed source provides a complete aircraft bounding box, antenna dimensions, exact canopy bend, assembled camera center, PCB outline, component heights, frame rib widths, detailed duct wall cross-section, or motor mounting z datum. These must be image-derived or design assumptions. Published 0.7-inch pitch does not uniquely determine propeller twist, camber or airfoil.

Manufacturer dimensions have high evidence confidence, but no physical specimen was measured. All unlisted tolerances remain unknown. The catalog assembly image is highly polished and may be rendered or retouched; it is not calibrated metrology photography. A final validation report should distinguish conformance to source nominals from conformance to a real physical sample.

The search located dimensioned raster drawings for the frame, canopy, motor, camera, propeller and battery, plus FC component images. No applicable official Air65 II STEP/STL/CAD download was found. The aircraft product page's download section supplies firmware/CLI files. This is a bounded search result, not proof that proprietary CAD does not exist.
