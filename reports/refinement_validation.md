# Air65 II Racing — refinement validation

Completed 12 October 2026. This report supersedes the original delivery claims for the current artifacts. The original project, renders and reports remain under `output/refinement_baseline/`. The Sketchfab comparison is retained in `research/sketchfab_comparison_handoff.md`; it is a qualitative workmanship benchmark for an older Air65 configuration, not Air65 II dimensional authority.

The refinement improves the continuous Air II canopy, Matrix II board shape and surface detail, material response and selected LAVA II 280 mAh battery. It also supplies a separate optimized browser asset. **All 35 published scalar anchors are unchanged.** The current assembly passes **93 numerical checks and 16 software tests**. Those results establish conformance to the declared model, not a physical accuracy percentage.

The public viewer is [Air65 II Explorer](https://air65-ii-explorer.danohn.chatgpt.site). It provides orbit, zoom, pan, camera presets, component visibility/selection, optional battery, illustrative exploded spacing, wireframe and model download. No OpenAI API integration or application API key is used.

Public Site version 2 is deployed from commit `a127b54bce472d9e8ec3615589aa1c57a3b7cff2`. Anonymous HTTPS checks returned 200 for the page and GLB; the hosted GLB, metadata, JavaScript and CSS match the reviewed local build by SHA-256. The published viewer loaded without console errors/warnings and was checked at desktop and phone sizes. Receipts and screenshots are in `reports/site/`.

![Refined Air65 II Racing](../output/final/hero.png)

## Geometry and visual changes

| Area | Implemented change | Evidence and limits |
| --- | --- | --- |
| Air II canopy | Continuous collar, cap, cheeks, leg roots and foot necks; matched boundary positions and authored normals across editable patches; real openings retained | Actual Air II photographs; closed joined surface verified. Detailed fillets, thickness variations and installed deformation remain estimates. |
| Matrix II outline | Estimated body side revised from 24 to 26.4 mm, with safe 16.3 mm side/rear clipping and 16.2 mm front clipping | Manufacturer photo scaled from the fixed mount pattern; medium-confidence estimate, not a published body size. All bores remain open. |
| PCB surfaces | Own top/bottom silkscreen and chip artwork, corrected pad count, four MCU lead rows, varied underside packages and 17 selected small passive bodies | Matrix II references. Package positions, exact lead counts, small-component detail and some markings remain simplified. Source photos are not projected onto the model. |
| Battery | Rounded pouch, curved printed wrapper, foil seams and folded end, black cap/BT2.0 nose and recessed contacts | Selected 280 mAh references. Published 54 × 10 × 6 mm body retained. Typeface and reverse-face artwork remain estimates. |
| Materials | Warmer milky violet frame, revised thin canopy transmission/roughness, more readable clear blades, metal/copper/lens adjustments | Visual estimates under unchanged source studio/cameras; no measured optical properties or calibrated color target. |
| Browser representation | Geometry-aware sampling and conservative planar simplification with sampled surface/bounds checks; UVs, textures, component transforms and canopy custom normals protected | Static web meshes are distinct from the detailed editable source. Three.js material response differs from Cycles. |

Fresh independent review: [refinement_independent_visual_review.md](refinement_independent_visual_review.md). The reviewer did not author geometry/materials and compared actual references, preserved before/after views, final source renders, optimized mesh previews, re-imported serialized GLB and actual Three.js screenshots. Earlier signoff is historical defect closure, not proof of high fidelity.

Comparison sheets are in `reports/refinement/`: assembly, canopy, PCB, optional battery and battery close-up. These preserve identical authored camera and studio settings. Reference photographs are not camera-calibrated to those views.

## Measurement registry

The shared registry contains **122 scalars: 35 verified, 39 derived and 48 estimated**. Verified means supported by a manufacturer statement/drawing, not physically measured. Every scalar has status, confidence and source IDs. Derived entries inherit uncertainty from their inputs. JSON uses millimetres, +X right, +Y forward, +Z up; Blender uses metres internally.

| Revised parameter | Before | After | Evidence status / confidence |
| --- | ---: | ---: | --- |
| `fc_body_side` | 24 | 26.4 | estimated / medium |
| `fc_body_corner_radius` | 16.970563 | 18.667619 | derived / medium |
| `fc_front_clip_y` | 14.2 | 16.2 | estimated / medium |
| `canopy_half_width` | 19 | 20.23 | estimated / medium |

Three additional PCB clipping parameters make the safe outline explicit. Detailed measurement reasoning is in [refinement_pcb_dimension_check.md](refinement_pcb_dimension_check.md). The source drawing's 25.5 mm frame pitch and 26 mm FC pitch remain distinct; inferred elastomer compliance is not a measured fit tolerance.

## Numerical and persistence checks

| Gate | Result | Evidence |
| --- | --- | --- |
| Published scalar values vs preserved baseline | All 35 unchanged | `reports/refinement_verified_anchors.json` |
| Frame, motor, duct, prop, camera, board and mounting constraints | 93/93 pass | `output/final/validation.json` and optional assembly validation |
| Contract, safe references, stale-source handling, UV schema and dependency regressions | 16/16 pass | `reports/test_results.txt` |
| Eight final 1400 × 1400 source views, 64 samples | Input hash and each PNG checksum verified | `output/final/render_manifest.json` |
| Source `.blend` reopened | Geometry, authored normals, UVs and all five packed image hashes unchanged | `output/final/reopen_validation.json` |
| Independent headless regeneration | Geometry, surface and input fingerprints match | `output/final/reproducibility.json` |
| Optional battery | Nominal body dimensions pass; no detected intersections against 72 frame objects or frame vertices inside the conservative body box | `output/with_battery/fit_validation.json` |
| Optimized important dimensions | 27/27 pass on frame, prop, motor, camera and mounting geometry | `output/web_optimized/anchor-validation.json` |
| Web export component alignment | All 13 groups pass serialized bounds, index, normal and triangle checks | Both export metadata files |
| Optimized export repeatability | Byte-identical GLB | `output/web_optimized/reproducibility.json` |
| Independent Khronos validator | Both files: 0 errors, 0 warnings | Both `khronos-validation.json` files; informational messages retained |

The battery check covers its saved unplugged pose and excludes the projecting connector nose from the body convention. It does not prove an insertion path, electrical mating or general solid collision freedom. Numerical thresholds are CAD conformance thresholds, not manufacturing tolerances.

The reopened dry project retains **928 geometry objects: 874 meshes and 54 curves**, 176 modifiers, 12 component collections and 8 cameras. Source JSON and texture images are packed. Manual Blender edits remain editable but are not written back to JSON.

Runtime: Blender 5.2.2 LTS (`d13f752e3b9c`), CPU Cycles, seed 6502; external tooling uses uv-managed Python 3.14. All agent orchestration remained inside Codex. Repeatability here is evaluated geometry/surface identity in that runtime, not byte-identical `.blend` files or cross-device pixel identity.

Source input SHA-256: `118130e29685d692a02af0b37c6e2bcdc4232419a92dc864c805a80953eedc35`

Dry geometry fingerprint: `630df06fdb96e43bbb6f372527c5e34baa45f05895e39a1de1e9ada1772d46e9`

## Web asset efficiency

| Representation | Triangles | Exported vertices | Materials | Embedded images | Bytes / binary size |
| --- | ---: | ---: | ---: | ---: | ---: |
| Preserved original | 534,490 | 357,745 | 27 | 0 | 11,850,856 / 11.30 MiB |
| Refined full export | 488,054 | 338,478 | 30 | 5 | 14,935,792 / 14.24 MiB |
| Refined public web asset | 262,810 | 206,782 | 30 | 5 | 10,417,808 / 9.94 MiB |

The optimized representation removes **46.15%** of the refined full export's triangles and **30.25%** of its file bytes. It uses **50.83%** fewer triangles than the preserved original. Images increase the full export's byte size; triangle count alone does not predict loading or frame rate.

Maximum accepted sampled source-surface deviation: **0.034158 mm**. Maximum component bound change: **0.009634 mm**. 22 candidate objects were reverted when they failed their gates. Canopy patches with authored custom normals and the complete camera component are protected from retessellation. Independent review rejected visible lens-ring faceting in an earlier candidate despite its passing distance gates; the final profile retains the original camera geometry. The surface test uses two-way vertex and triangle-centroid samples against the source triangle surface; it is not a certified continuous Hausdorff bound and says nothing about unmeasured physical error.

The GLBs embed all images. UV splits, transforms and all 13 component controls are retained. Evaluated UV coordinates are canonicalized to six decimal places after modifier interpolation, bounding coordinate rounding at 0.001024 pixel for 2048-pixel textures; this removes observed one-ULP process variation. Source UVs and vertex positions are unchanged. The web asset remains above the older Sketchfab example's roughly 33,000 triangles; this pass prioritizes bounded geometry preservation rather than matching that count by aggressive simplification.

Public GLB SHA-256: `8ddbc0195e22c59bc8dcf6de34885021e5cc099aea5b33a08817a11a7b6395a7`

## Actual browser measurement

The benchmark runs in the real Chromium-based in-app browser with a fixed 960 × 720 drawing buffer, DPR 1, logarithmic depth precision, the same studio, camera path and battery visibility. Three interleaved rounds per asset use 60 warmup and 240 measured frames each. All Blender work is complete before timing. Raw browser/GPU identity, round results and local load/parse times are in `reports/browser_performance.json`.

| Asset | Median CPU submission ms | Median round p95 CPU ms | Mean round FPS | Median GPU elapsed ms |
| --- | ---: | ---: | ---: | ---: |
| Original | 1.400 | 1.900 | 93.46 | 8.015 |
| Refined full | 1.500 | 2.100 | 94.83 | 7.892 |
| Refined optimized | 1.300 | 1.700 | 119.54 | 6.344 |

Recorded GPU: `ANGLE (Apple, ANGLE Metal Renderer: Apple M1 Pro, Unspecified Version)`. Browser: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36`. The run was not invalidated by backgrounding or GPU disjoint state.

In this run, median GPU elapsed time decreased from 7.892 to 6.344 ms (19.6% lower) between the refined full and optimized representations. Mean frame cadence rose from 94.83 to 119.54 FPS. The optimized result is near the observed 120 Hz cadence ceiling; this is a local controlled comparison, not a general device guarantee.

CPU columns summarize medians across rounds. CPU submission measures `renderer.render`, not end-to-end GPU latency. Frame cadence uses requestAnimationFrame and may be limited by display refresh. GPU timers are optional. Local HTTP/parse timing is not internet loading speed; one browser/GPU/viewport is not a cross-device guarantee. No comparative Sketchfab frame-rate claim is made.

## Remaining uncertainty

The canopy's exact mold curvature, installed vertical stack, prop airfoil, concealed motor construction, PCB micro-layout, antenna pose and optical properties remain estimates. Battery reverse-face artwork is not independently evidenced. No calibrated photo set, original manufacturer CAD or physical caliper survey was available. More detail does not eliminate those uncertainties, and this project provides no physical accuracy percentage, aerodynamic/structural validation or manufacturing-ready solid.

The parametric layer is a shared scalar registry and procedural mesh interpreter, not a general constraint solver. Dependent stored values and authored mesh helpers must be regenerated together when changing configuration. The implementation plan, minimal prototype, original independent research, spatial contract and component provenance remain in the complete project archive.
