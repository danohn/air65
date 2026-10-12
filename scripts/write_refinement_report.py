"""Publish human-readable reports from the completed refinement evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(path): return json.loads((ROOT / path).read_text())
def write(path, text): (ROOT / path).write_text(text.strip() + '\n')


def main():
    r = read('reports/refinement_validation.json')
    v = read('output/final/validation.json')
    reopen = r['reopen']
    optimized = read('output/web_optimized/model-metadata.json')
    full = read('output/web/model-metadata.json')
    repeat = read('output/web_optimized/reproducibility.json')
    assert all(x == 'pass' for x in [r['dry_validation'], reopen['status'], r['repeatability']['status'], r['battery_fit']['status'], repeat['status']])
    kh = {key: read(f'output/{key}/khronos-validation.json') for key in ['web', 'web_optimized']}
    assert all(k['issues']['numErrors'] == k['issues']['numWarnings'] == 0 for k in kh.values())
    assets = r['assets']
    rows = '\n'.join(f"| {label} | {a['triangles']:,} | {a['vertices']:,} | {a['materials']} | {a['textures']} | {a['bytes']:,} / {a['bytes']/1048576:.2f} MiB |" for key, label in [('original','Preserved original'),('refined_full','Refined full export'),('refined_optimized','Refined public web asset')] for a in [assets[key]])
    timing = r['browser_timing_summary']
    benchmark = read('reports/browser_performance.json')
    gpu_full = timing['refined_full']['median_of_round_gpu_medians_ms']
    gpu_opt = timing['refined_optimized']['median_of_round_gpu_medians_ms']
    measured_interpretation = (f"In this run, median GPU elapsed time decreased from {gpu_full:.3f} to {gpu_opt:.3f} ms ({100*(1-gpu_opt/gpu_full):.1f}% lower) between the refined full and optimized representations. " if gpu_full is not None and gpu_opt is not None else '')
    measured_interpretation += f"Mean frame cadence rose from {timing['refined_full']['mean_of_round_fps']:.2f} to {timing['refined_optimized']['mean_of_round_fps']:.2f} FPS. The optimized result is near the observed 120 Hz cadence ceiling; this is a local controlled comparison, not a general device guarantee."
    timing_rows = '\n'.join(f"| {label} | {t['median_of_round_cpu_medians_ms']:.3f} | {t['median_of_round_cpu_p95_ms']:.3f} | {t['mean_of_round_fps']:.2f} | {format(t['median_of_round_gpu_medians_ms'],'.3f') if t['median_of_round_gpu_medians_ms'] is not None else 'Unavailable'} |" for key, label in [('original','Original'),('refined_full','Refined full'),('refined_optimized','Refined optimized')] for t in [timing[key]])
    changed = '\n'.join(f"| `{key}` | {value['before']:.8g} | {value['after']:.8g} | {value['status']} / {value['confidence']} |" for key, value in r['revised_parameters'].items())
    opt = r['optimization']
    saved = 100 * (1 - assets['refined_optimized']['bytes'] / assets['refined_full']['bytes'])
    vs_original = 100 * (1 - assets['refined_optimized']['triangles'] / assets['original']['triangles'])
    publication = r.get('publication')
    publication_note = (f"Public Site version {publication['version_number']} is deployed from commit `{publication['commit_sha']}`. Anonymous HTTPS checks returned 200 for the page and GLB; the hosted GLB, metadata, JavaScript and CSS match the reviewed local build by SHA-256. The published viewer loaded without console errors/warnings and was checked at desktop and phone sizes. Receipts and screenshots are in `reports/site/`." if publication else 'Publication verification is recorded separately in `reports/site/`.')
    write('reports/refinement_validation.md', f'''
# Air65 II Racing — refinement validation

Completed 12 October 2026. This report supersedes the original delivery claims for the current artifacts. The original project, renders and reports remain under `output/refinement_baseline/`. The Sketchfab comparison is retained in `research/sketchfab_comparison_handoff.md`; it is a qualitative workmanship benchmark for an older Air65 configuration, not Air65 II dimensional authority.

The refinement improves the continuous Air II canopy, Matrix II board shape and surface detail, material response and selected LAVA II 280 mAh battery. It also supplies a separate optimized browser asset. **All {r['published_anchor_count']} published scalar anchors are unchanged.** The current assembly passes **{r['numeric_checks']} numerical checks and 16 software tests**. Those results establish conformance to the declared model, not a physical accuracy percentage.

The public viewer is [Air65 II Explorer](https://air65-ii-explorer.danohn.chatgpt.site). It provides orbit, zoom, pan, camera presets, component visibility/selection, optional battery, illustrative exploded spacing, wireframe and model download. No OpenAI API integration or application API key is used.

{publication_note}

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
{changed}

Three additional PCB clipping parameters make the safe outline explicit. Detailed measurement reasoning is in [refinement_pcb_dimension_check.md](refinement_pcb_dimension_check.md). The source drawing's 25.5 mm frame pitch and 26 mm FC pitch remain distinct; inferred elastomer compliance is not a measured fit tolerance.

## Numerical and persistence checks

| Gate | Result | Evidence |
| --- | --- | --- |
| Published scalar values vs preserved baseline | All 35 unchanged | `reports/refinement_verified_anchors.json` |
| Frame, motor, duct, prop, camera, board and mounting constraints | {r['numeric_checks']}/{r['numeric_checks']} pass | `output/final/validation.json` and optional assembly validation |
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

The reopened dry project retains **{reopen['geometry_object_count']} geometry objects: {reopen['editable_mesh_objects']} meshes and {reopen['editable_curves']} curves**, {reopen['retained_modifiers']} modifiers, 12 component collections and 8 cameras. Source JSON and texture images are packed. Manual Blender edits remain editable but are not written back to JSON.

Runtime: Blender 5.2.2 LTS (`d13f752e3b9c`), CPU Cycles, seed 6502; external tooling uses uv-managed Python 3.14. All agent orchestration remained inside Codex. Repeatability here is evaluated geometry/surface identity in that runtime, not byte-identical `.blend` files or cross-device pixel identity.

Source input SHA-256: `{r['source_input_sha256']}`

Dry geometry fingerprint: `{r['source_geometry_fingerprint_sha256']}`

## Web asset efficiency

| Representation | Triangles | Exported vertices | Materials | Embedded images | Bytes / binary size |
| --- | ---: | ---: | ---: | ---: | ---: |
{rows}

The optimized representation removes **{opt['triangle_reduction_percent']:.2f}%** of the refined full export's triangles and **{saved:.2f}%** of its file bytes. It uses **{vs_original:.2f}%** fewer triangles than the preserved original. Images increase the full export's byte size; triangle count alone does not predict loading or frame rate.

Maximum accepted sampled source-surface deviation: **{opt['maximum_sampled_surface_deviation_mm']:.6f} mm**. Maximum component bound change: **{opt['maximum_component_bound_delta_mm']:.6f} mm**. {opt['reverted_objects']} candidate objects were reverted when they failed their gates. Canopy patches with authored custom normals and the complete camera component are protected from retessellation. Independent review rejected visible lens-ring faceting in an earlier candidate despite its passing distance gates; the final profile retains the original camera geometry. The surface test uses two-way vertex and triangle-centroid samples against the source triangle surface; it is not a certified continuous Hausdorff bound and says nothing about unmeasured physical error.

The GLBs embed all images. UV splits, transforms and all 13 component controls are retained. Evaluated UV coordinates are canonicalized to six decimal places after modifier interpolation, bounding coordinate rounding at 0.001024 pixel for 2048-pixel textures; this removes observed one-ULP process variation. Source UVs and vertex positions are unchanged. The web asset remains above the older Sketchfab example's roughly 33,000 triangles; this pass prioritizes bounded geometry preservation rather than matching that count by aggressive simplification.

Public GLB SHA-256: `{assets['refined_optimized']['sha256']}`

## Actual browser measurement

The benchmark runs in the real Chromium-based in-app browser with a fixed 960 × 720 drawing buffer, DPR 1, logarithmic depth precision, the same studio, camera path and battery visibility. Three interleaved rounds per asset use 60 warmup and 240 measured frames each. All Blender work is complete before timing. Raw browser/GPU identity, round results and local load/parse times are in `reports/browser_performance.json`.

| Asset | Median CPU submission ms | Median round p95 CPU ms | Mean round FPS | Median GPU elapsed ms |
| --- | ---: | ---: | ---: | ---: |
{timing_rows}

Recorded GPU: `{benchmark['gpu']}`. Browser: `{benchmark['browser']}`. The run was not invalidated by backgrounding or GPU disjoint state.

{measured_interpretation}

CPU columns summarize medians across rounds. CPU submission measures `renderer.render`, not end-to-end GPU latency. Frame cadence uses requestAnimationFrame and may be limited by display refresh. GPU timers are optional. Local HTTP/parse timing is not internet loading speed; one browser/GPU/viewport is not a cross-device guarantee. No comparative Sketchfab frame-rate claim is made.

## Remaining uncertainty

The canopy's exact mold curvature, installed vertical stack, prop airfoil, concealed motor construction, PCB micro-layout, antenna pose and optical properties remain estimates. Battery reverse-face artwork is not independently evidenced. No calibrated photo set, original manufacturer CAD or physical caliper survey was available. More detail does not eliminate those uncertainties, and this project provides no physical accuracy percentage, aerodynamic/structural validation or manufacturing-ready solid.

The parametric layer is a shared scalar registry and procedural mesh interpreter, not a general constraint solver. Dependent stored values and authored mesh helpers must be regenerated together when changing configuration. The implementation plan, minimal prototype, original independent research, spatial contract and component provenance remain in the complete project archive.
''')
    write('reports/validation_report.md', '''
# Air65 II Racing — current validation report

The current authoritative report is [refinement_validation.md](refinement_validation.md), with machine-readable evidence in [refinement_validation.json](refinement_validation.json). It records the refined source model, dimensional checks, independent visual review, optimized public asset and actual browser performance.

This supersedes the original delivery report. The original report and its model/renders are preserved under `output/refinement_baseline/`; their former signoff closed the defects found in that review and did not establish high physical fidelity.

The complete deliverable is `dist/air65_ii_project.zip`. Editable projects are `output/final/air65_ii.blend` and `output/with_battery/air65_ii.blend`; JSON specifications are under `specs/`, deterministic builders under `scripts/`, reference provenance under `research/` and `references/`, and current multiview renders under `output/final/`.
''')
    write('reports/final_visual_signoff.md', f'''
# Current independent visual assessment

The fresh independent assessment is [refinement_independent_visual_review.md](refinement_independent_visual_review.md). Use its evidence-specific conclusion and residual findings for the current delivery. It separately considers reference fidelity, source-to-optimized geometry, serialized GLB and actual Three.js appearance.

Current dry geometry fingerprint: `{r['source_geometry_fingerprint_sha256']}`.

Current public GLB SHA-256: `{assets['refined_optimized']['sha256']}`.

The earlier visual signoff is preserved at `output/refinement_baseline/reports/final_visual_signoff.md`. It described defect closure for that older revision; it is not a physical accuracy certification or a substitute for the fresh review. Numeric conformance and browser timing are reported separately in [refinement_validation.md](refinement_validation.md).
''')
    write('reports/web_model_export.md', f'''
# Current web model exports

Both files are deterministic local exports of the refined optional-battery Blender project. The source `.blend` remains unchanged and editable. The browser defaults to hiding the optional battery.

| Representation | Triangles | Exported vertices | Materials | Embedded images | Bytes / binary size |
| --- | ---: | ---: | ---: | ---: | ---: |
{rows}

`output/web/air65-ii.glb` retains the full evaluated surfaces. `output/web_optimized/air65-ii.glb` is the separately optimized public asset, copied exactly to `site/dist/assets/air65-ii.glb`. Each directory contains source identity, serialized component bounds and validation metadata. Five PNG images are embedded unchanged from the authored assets; no reference photograph is embedded.

Both pass Khronos validation with 0 errors and 0 warnings. Informational notices are retained in their JSON reports. Optimized serialization is byte-identical on repetition. Group transforms and all 13 component controls remain intact. Coordinates map `(x, y, z)` millimetres in the source to `(x, z, -y)` metres in glTF.

Detailed current optimization statistics, measured browser timings, material limits, source fingerprints and accuracy limits are in [refinement_validation.md](refinement_validation.md). The initial optimization experiment on the preserved original model is documented in [web_optimization.md](web_optimization.md); its numbers are historical and do not describe the final refined asset.

Full GLB SHA-256: `{full['asset_sha256']}`.

Optimized GLB SHA-256: `{optimized['asset_sha256']}`.

The source studio lights and Cycles/AgX pipeline are not glTF model data. Web transmission, tone mapping and lighting produce a different material response; final browser screenshots and independent review assess that representation directly.
''')
    print('Wrote current refinement, validation, visual-assessment pointer and web-export reports.')


if __name__ == '__main__': main()
