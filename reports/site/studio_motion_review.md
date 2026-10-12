# Independent Studio and RPM presentation review

Reviewed 2026-10-12. Scope: the saved browser screenshots and the shipped HTML/JavaScript/CSS for the Studio page and interactive motor controls. The reviewer did not control the shared browser, change the model or site, or independently replay the embedded video. Dynamic browser behavior and deployment checks belong to the main integration review.

**Conclusion:** the additions are visually coherent and the important RPM, slow-motion, and blur qualifications are honest. No major layout or visible rendering defect was found in the inspected desktop/mobile states. The one low-severity video-label visibility issue was corrected and independently re-inspected; no actionable finding remains open in this review's scope. This review does not establish physical accuracy, real motor transient response, or geometry preservation.

**Images actually inspected:**

- [Motion desktop: maximum RPM with slow motion](motion-desktop.png)
- [Motion desktop: maximum RPM at normal time](motion-blur-desktop.png)
- [Motion mobile: 120 RPM](motion-mobile.png)
- [Studio desktop, full page](studio-desktop.png)
- [Studio mobile, full page](studio-mobile.png)
- [Corrected web-video caption proof](../../output/prop_spinup_web/web-caption-proof.png)

**Resolved finding — SM-01, P3 / low: native video controls obscured the burned-in RPM and stage labels.** The original web encode placed the labels at y=641 and y=676 in a 720-pixel-high video, inside the native controls' screen region. This affected inspection while pausing or scrubbing. The encoder now offers `--labels-position top`, placing the RPM at upper-right y=51 and the stage at y=85; the original bottom placement remains available for standalone output. The reviewer inspected the replaced desktop/mobile Studio screenshots and `output/prop_spinup_web/web-caption-proof.png`. The desktop screenshot shows native controls visible at the bottom while the top-right RPM and stage remain unobstructed. The mobile screenshot shows the labels in the same clear upper region, with no overlap with the aircraft or page content. The full-size proof shows readable 60,394 rpm / AT SPEED text below the manufacturer-reference caption. The correction is visually satisfactory and SM-01 is closed. Re-encoding duration, frame-count and seamless-loop verification remain part of the integration report, not a conclusion drawn from these still images.

**Visual clarity and mobile layout:**

- The desktop motor card has a clear numerical hierarchy: RPM, play/pause, range, presets, then slow motion and explanatory copy. It leaves the aircraft unobstructed.
- The mobile screenshot keeps the complete aircraft above the open inspector rather than covering it with the controls. The speed, pause, presets and slow-motion option fit within the visible card. The close control and inspector scrollbar are visible. No horizontal clipping was found at the captured width.
- Both Studio layouts preserve the full aircraft silhouette in the portrait and video. The mobile page stacks the introduction, portrait, motion explanation and video in a readable order. Links and download controls are separated clearly. The desktop page makes good use of the wider portrait and adjacent motion explanation.
- The normal-speed maximum-RPM screenshot shows faint swept propeller coverage without an obvious square proxy boundary, clipped disc, displaced rotor axis or stray blade silhouette. The slow-motion screenshot keeps individual blades readable. These are still-image observations; they cannot rule out temporal aliasing, flicker or pointer-interaction problems.

**Labels and implementation cross-check:**

- `studio.html` identifies the image as a digital portrait rendered from the editable model. It identifies 60,394 RPM as a BETAFPV bench sample and states that the ramp timing is authored. It does not present the animation as measured aircraft telemetry.
- `index.html` identifies the maximum as a manufacturer bench sample. In `app.js`, slow-motion help explicitly distinguishes the slider's simulated RPM from displayed motion. At the maximum, 60,394 / 500 = 120.788 RPM; the inspected desktop screenshot correctly shows 120.8 displayed RPM alongside the 60,394 RPM readout.
- `rotor-motion.js` uses the stated 1/500 time factor. The high-speed browser treatment is a radial coverage approximation derived from blade geometry, not a physically integrated camera exposure. The active help calls it a blur preview; the About text and Studio footnote explain that limitation and distinguish the integrated Blender video.
- The fixed airframe, authored timing, unplugged optional-battery pose, and absence of flight/thrust simulation are disclosed. The Studio copy does not imply that the existing connector gap has been corrected.
- Stop, pause/resume and slow-motion labels correspond to distinct state variables in the inspected code. Wireframe pauses motion, and reset restores zero RPM. This is a source review, not an independent interactive test of those controls.

**Investigated and dismissed:** a preliminary concern about stale individual-blade shadows at high RPM does not apply. `app.js` explicitly disables shadow casting for the prop category, including the stopped geometry. The normal-speed maximum screenshot is consistent with shadows from frame structure. Cached motor-bell shading remains within the documented lightweight browser approximation; this review does not request physically integrated interactive motor shadows.

The pre-existing model-fidelity limitations from the independent model reviews remain in force. Attractive Studio lighting and a working RPM control do not establish improved dimensional accuracy or parity with a physical reference.
