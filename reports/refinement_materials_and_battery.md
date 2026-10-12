# Material and LAVA II 280 mAh refinement

The same assembly cameras, studio lights, exposure and colour management are retained for before/after renders. Optical parameters are estimates from the actual Air65 II and component photographs, not measured BRDFs or calibrated colour samples. No Sketchfab material or texture is copied.

The frame moves toward the warmer violet and milky transmission visible in Racing photographs. The Air II canopy has lower roughness and greater transmission to keep its thin moulded walls readable. Propeller transmission is reduced modestly from 0.93 to 0.84 and roughness increased from 0.075 to 0.115 to retain visible blade surfaces while preserving clarity. The silver motor bell has a more metallic response; copper windings are darker. The lens coating is greener and still explicitly approximates an optical surface rather than ray tracing a real multi-element camera.

All values and individual provenance notes are in `specs/materials.json`. The source renderer and browser use different physically based renderers, and material appearance must be assessed separately in each.

The selected LAVA II 280 reference established black terminal/cap surfaces, green BETAFPV print, the lime/yellow/black angular wrapper, and readable LAVA,280,95C,mAh and LiHV3.8V1.06Wh text. `scripts/refine_battery.py` draws the wrapper from geometric paths and Pillow's bundled font; it does not load the reference photograph. Typeface, exact motif positions, colour, cap geometry, local folds and all reverse-face graphics remain estimates. The reverse face repeats the front artwork because independent reverse-face evidence was unavailable.

The cell uses a rounded multi-section pouch with curved printed top/bottom skins, narrow foil seams and a folded end lip. Printed detail has no raised text geometry. The black BT2.0 nose has two dark recessed contacts and thin metallic rims. The published 54 × 10 × 6 mm body envelope is retained; the projecting connector nose is excluded as in the original nominal convention. The display pose is unplugged.

The optional assembly receives a fresh body-envelope and frame-intersection check, plus independent visual comparison. Those checks do not certify insertion motion, internal cell shape, electrical contact mating or manufacture.

## Independent-review corrections

The first wrapper draft used type that was too thin. The revised generator adds a deterministic italic shear, thicker dark capacity text and broader yellow LAVA fill with white/black outlines, plus slightly stronger lime saturation. The cap UV handedness is corrected so its top-side BETAFPV text is not mirrored. Exact branding typography is still an approximation.

The final independent review found that a single planar cap projection also printed a mirrored logo on the underside. The correction makes the cap body plain black and assigns its observed logo to a separate top print surface. The unevidenced underside is blank. The ink surface stays inside the nominal 6 mm body envelope; the cap support is recessed by 0.002 mm.
