# Independent PCB proportional check

The manufacturer top-view photograph supports enlarging the estimated central PCB body from **24.0 mm to approximately 26.4 mm square-side equivalent**. The evidence suggests roughly a **10% increase**, rather than 15%. The existing 14.2 mm front clip is also too close to the board center; approximately **16.2 mm** is better supported. These remain **image-derived estimates**, not published body measurements.

No JSON or model files were edited during this check. The current 26 mm nominal PCB mounting pitch, 25.5 mm frame pitch, and 1 mm PCB thickness should remain unchanged.

## Reference and method

Inspected local references:

- `references/fc_diagram.jpg`, 1600 × 1600 pixels, the annotated manufacturer photograph with an upward front arrow.
- `references/air65_ii_electronics.webp`, 1600 × 900 pixels, the manufacturer marketing composite. Its oblique boards support the topology but are unsuitable for a direct uniform scale measurement.
- `specs/spatial_architecture.json` and the substrate/lug nodes in `specs/components/electronics.json`.

Source: [Matrix 1S 5IN1 II product page](https://betafpv.com/products/matrix-1s-5in1-ii-brushless-flight-controller) and [manufacturer top/front image](https://cdn.shopify.com/s/files/1/1778/6615/files/Matrix_1S_5IN1_II_Brushless_Flight_Controller_top_front_gyro_update.jpg?v=1777532692).

The diagram is effectively a near-normal photo. Approximate mounting-hole centers in image coordinates, with origin at the top left, are:

| Anchor | Pixel x | Pixel y | Comment |
| --- | ---: | ---: | --- |
| Left lug hole | 363.5 | 835 | White-hole run midpoints; blue leader lines cross some rows |
| Right lug hole | 1243 | 834 | White-hole run midpoints |
| Rear lug hole | 803.5 | 1276 | Visual/cross-row estimate; provides a scale check |
| Board center | 803.25 | 834.5 | Midpoint of left/right hole centers |
| Front outline maximum | approximately 762–839 | 448 | Clipped/rounded tip; exact transition is not a sharp corner |

The left/right span is approximately **879.5 pixels**. A 26 mm square mounting pattern has an opposite-hole diagonal of `26 * sqrt(2) = 36.76955 mm`, giving approximately **23.919 pixels/mm**. Rear-hole distance from the center is approximately 441.5 pixels, compared with a lateral half-span of 439.75 pixels, a roughly 0.4% cross-check discrepancy. This supports using the image for a rough metric estimate while retaining uncertainty.

I checked the actual substrate edge rather than large-package positions. Non-white/non-blue pixel scans in narrow windows around the visible straight board edges gave:

| Edge | Pixel line | Example sampled boundary points |
| --- | --- | --- |
| Front-left/NW | `x + y ≈ 1194` | (684,510), (624,570), (564,630), (504,690), (444,750) |
| Front-right/NE | `x − y ≈ 411` | (951,540), (1011,600), (1071,660), (1161,750) |
| Rear-left/SW | `x − y ≈ −482` | (528,1010), (558,1040), (588,1070); edge slopes slightly in this photo |
| Rear-right/SE | `x + y ≈ 2085` | (1045,1040), (1015,1070), (925,1160) |

The scan classified darker board pixels while excluding cyan annotation lines. It was not a fully automated segmentation: edge windows were selected from visual inspection, and text, solder, gold edge color, perspective and antialiasing can perturb individual samples.

Perpendicular separation between the NW/SE lines yields `(2085−1194)/(sqrt(2)*23.919) = 26.34 mm`. NE/SW gives `(411−(−482))/(sqrt(2)*23.919) = 26.40 mm`. These independent estimates agree closely enough to recommend **26.4 mm**, with a conservative reconstruction range **25.9–26.9 mm**. This range is not a physical manufacturing tolerance.

## Proposal for central integration

| Parameter | Current | Proposed | Status |
| --- | ---: | ---: | --- |
| `fc_body_side` | 24.0 | **26.4 mm** | Estimated; medium confidence; suggested range 25.9–26.9 |
| `fc_body_corner_radius` | 16.97056 | **18.66762 mm** | Derived as `26.4/sqrt(2)`; extrapolated diamond vertex, not literal material at all corners |
| `fc_front_clip_y` | 14.2 | **16.2 mm** | Estimated; medium confidence; suggested range 15.8–16.6 |
| Side/rear body clip magnitude | implicit 16.0 | **16.3 mm absolute** | Estimated integration choice; keep independent of body-side scale |

The front clip follows `(834.5−448)/23.919 = 16.16 mm`. The front corners are rounded/chamfered in the photograph, so a square clipping plane with sharp endpoints exaggerates their width. An optional planar shoulder transition around `x = ±1.7 mm, y = 16.2 mm` to the straight diamond edges near `x = ±3.0 mm, y ≈ 15.67 mm` would better resemble the observed short front flat; these extra points are lower-confidence estimates. No forward mounting lug should be added.

**Do not scale the existing substrate's side/rear clipping fractions with the larger corner radius.** Its current `0.9428090416 * corner_radius` clip would rise from 16.0 to **17.6 mm**, covering part of the lug holes. Preserve an absolute clip before the nearest inner-hole edge.

With the existing lug centers at `18.384776 mm`, outer radius `2.45 mm` and inner radius `1.55 mm`:

- The nearest inner-hole edge is `18.384776−1.55 = 16.834776 mm`.
- A body clip at **16.3 mm** stays **0.535 mm** clear of that edge.
- The inner-most outer-annulus edge is `18.384776−2.45 = 15.934776 mm`; a 16.3 mm body clip overlaps the lug annulus by **0.365 mm** at its inward centerline.
- At diamond radius 18.667619 and clip 16.3, the transverse endpoint magnitude is **2.367619 mm**, preserving the enlarged straight body edges while trimming the cardinal tips.

A simple safe outline before any optional front rounding is therefore:

```text
(-2.467619, 16.2), (2.467619, 16.2),
(16.3, 2.367619), (16.3, -2.367619),
(2.367619, -16.3), (-2.367619, -16.3),
(-16.3, -2.367619), (-16.3, 2.367619)
```

This polygon is an integration proposal, not a claimed exact manufacturing contour. Keep the existing annular lugs, their center locations, hole radii, board thickness and front-lug omission. Apply the same perimeter to substrate, top/bottom solder-mask sheets and any perimeter edge detail so layers remain coincident. Afterwards inspect the top view and verify that side/rear holes remain fully open.

Changing `fc_body_side` will also move any component locations expressed as fractions of that parameter. That is useful for the previously compressed surface layout, but do not enlarge externally anchored lug/grommet/screw coordinates or uniformly scale the whole electronics assembly.
