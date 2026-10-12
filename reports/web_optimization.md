# Air65 II web representation: bounded geometry optimization

The exporter now has a separate, explicit optimized mode. Its default remains the original lossless export. Neither mode modifies the detailed source `.blend` or component JSON. The original `output/web/` export is preserved, and optimized mode refuses to write into that directory.

This report describes the **preserved pre-refinement baseline** at `output/refinement_baseline/with_battery/air65_ii.blend`. It establishes the export mechanism and a comparison baseline. New canopy, artwork, material or battery refinements require a new export and their own visual/browser review; the results below must not be silently attributed to a later model.

## Results on the preserved baseline

| Metric | Detailed web export | Optimized web export |
|---|---:|---:|
| Triangles | 534,490 | **258,220** |
| Exported vertices including split normals | 357,745 | **196,897** |
| GLB bytes | 11,850,856 | **6,332,752** |
| Component nodes | 13 | **13** |
| Material primitives | 70 | **70** |
| Materials | 27 | **27** |

Triangle count fell **51.69%** and file size fell **46.56%**. This is a geometry and transfer-size improvement. It is **not a measured frame-rate claim**: browser performance, transparent-material passes, lighting and device-pixel ratio remain the main site's responsibility.

| Component | Source triangles | Optimized triangles | Maximum group bound delta, mm | Maximum sampled surface deviation, mm |
|---|---:|---:|---:|---:|
| Battery | 5,920 | 3,320 | 0 | 0.029263 |
| Camera | 38,684 | 11,020 | 0 | 0.037182 |
| Canopy | 70,934 | 45,380 | 0 | 0.039729 |
| Electronics | 57,240 | 40,572 | 0 | 0.034158 |
| Frame | 49,744 | 27,064 | 0 | 0.022920 |
| Each motor | 54,752 | 26,836 | 0.009634 | 0.029208 |
| Prop FL | 23,240 | 5,880 | 0.003004 | 0.034096 |
| Prop FR | 23,240 | 5,880 | 0.002303 | 0.034096 |
| Prop RL | 23,240 | 5,880 | 0.000399 | 0.034096 |
| Prop RR | 23,240 | 5,880 | 0.002304 | 0.034096 |

Full assembly bounds are unchanged. All component origins and transforms, including optional-battery separation and visibility metadata, are retained. The coordinates remain metres, +Y up and −Z forward. **344 objects** accepted a reduction, **337** remained unchanged and **22** candidates were reverted. The reverted candidates include all four motor shafts and several wires, because their proposed changes exceeded the selected gates.

The asset is at `output/web_optimization_baseline/air65-ii.glb`. Its SHA-256 is:

```text
20e51b87eb7d5cf73a8277aad0debfef1df7fa5834e7d741654fa67495e4d86e
```

The source geometry fingerprint remains:

```text
24fac51870fd4fcd8f6c67cab71eba7ed23a69e5d5ace57ce66f40e9fcec4411
```

## Method and limits

The first cost inspection identified the most expensive surfaces: 36 copper-winding curves account for 157,968 source triangles; each frame duct has 256 angular samples; each propeller blade uses 61 span sections and 48 airfoil samples; small edge fillets use three bevel segments.

The exporter does not apply a blanket decimation ratio. It makes a transient copy of each source object and applies operations according to its geometry:

- Circular cylinders, annuli and revolved profiles select a lower angular count using a 0.035 mm sagitta target. Counts divide the original sampling and retain cardinal directions. The sampled vertices are actual authored vertices, not a replacement shape fitted to the object.
- Propeller blades sample every second span section and airfoil sample, retaining end sections and extrema of the authored section parameters. A separate 0.0001 mm swept-radius check protects the 31 mm nominal sweep.
- Curves use a lower cross-section bevel resolution. Open polylines may use Ramer–Douglas–Peucker simplification with a 0.012 mm path tolerance; baseline winding points proved necessary at that tolerance and were retained. Bezier and font resolution can be capped independently.
- Bevel modifiers use two segments; subdivision levels above one can be capped before evaluation. The deviation checks still apply, so a candidate that changes a contour excessively is discarded.
- Evaluated meshes receive a conservative **0.02° planar dissolve**, respecting sharp, material, UV, normal, seam and open-boundary delimiters. There is no ratio-based collapse stage.
- Meshes with authored UVs retain their original primitive lattice; this avoids invalidating the new PCB and battery artwork. Their modifiers and delimiter-aware planar cleanup can still be evaluated and checked.

All retained candidate surfaces are checked against the original evaluated object. The maximum allowed sampled surface deviation is **0.04 mm** and the ordinary per-object bounding-box delta is **0.035 mm**. Frame ducts, frame mounting bosses, the lens front cup and motor shafts have a stricter **0.0001 mm** bounding-box gate. A failed candidate is replaced by its complete source evaluated mesh.

These are **web representation error thresholds**, not manufacturing tolerances or evidence of physical measurement accuracy.

Surface deviation is a two-way nearest-triangle distance calculation. Samples come from evaluated vertices and triangle centroids, with a deterministic cap of 12,000 samples per object per direction. It checks both source-to-candidate and candidate-to-source distances, including newly formed faces. This is more informative than bounding boxes alone, but it is **not a certified continuous Hausdorff bound**: it can miss a maximum between samples and does not prove silhouette, topology, normals, optics, material or texture equivalence. Matched visual review remains necessary, especially at grazing angles and close zoom.

## Texture support

Lossless and optimized modes now support a PNG or JPEG image node linked directly from `Color` to Principled `Base Color`, while other material factors stay constant. Image bytes are embedded unchanged in GLB buffer views. Textured materials use a white base-color multiplier; loop UVs are included in the vertex split key and exported as `TEXCOORD_0`, with Blender V converted to glTF V. Original UV seams survive material merging.

The texture fixture applies an asymmetric four-color image to a battery label in a temporary copy of the preserved source. Its independent checks verify that the embedded PNG bytes exactly equal the saved source image, the material factor is `[1,1,1,1]`, all textured primitives have UVs, and every exported position/UV pair equals the evaluated Blender loop pair after the V conversion. The fixture is an exporter test, not part of the model's artwork.

No roughness or normal texture mapping is implemented in this pass. Unrecognized shader links fail explicitly. The earlier documented differences between Cycles and web PBR/refraction remain.

## Verification artifacts

All baseline artifacts are preserved under `output/web_optimization_baseline/`:

- `air65-ii.glb` and `model-metadata.json`: optimized model and summarized provenance.
- `optimization-metrics.json`: all 703 object costs, proposed actions, acceptance/reversion reasons, sample counts, distances and per-group bounds.
- `preview.blend`: evaluated optimized meshes with the original studio and cameras, for matched renders. It is marked as a web preview and must not replace the detailed source.
- `repeat/air65-ii.glb`: independent second optimized export; **byte-identical** to the first.
- `lossless_regression/air65-ii.glb`: the updated exporter in default mode; **byte-identical** to the original lossless asset, SHA-256 `9b48b97ebc2aceedfd66ec45654f4a34dbcfa91a3f73a3a995a977b34c94e1ec`.
- `gltf-validator.json`: Khronos glTF Validator 2.0.0-dev.3.10 result, **0 errors / 0 warnings**. Four informational messages concern 288 zero-area triangles inherited from evaluated source details.
- `texture_fixture.blend`, `texture_fixture.png` and `texture_fixture_export/`: isolated UV/image regression fixture. Its GLB also reports **0 errors / 0 warnings** in Khronos validation.
- `regression_checks.json`: byte repeatability, lossless regression and texture/UV checks.

The source `.blend` hash is checked before and after export. No source `.blend`, component specification, measurement registry, site checkout or baseline `output/web/` file was changed by this task.

## Invocation for the newly refined source

The optimized mode is selected with **`--mode optimized`**. Choose the fresh refined source path and a separate output directory:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/export_web_model.py -- \
  --source output/with_battery/air65_ii.blend \
  --mode optimized \
  --optimization-config scripts/web_optimization.json \
  --output output/web_optimized/air65-ii.glb \
  --save-preview-blend
```

Omit `--save-preview-blend` if a matched Blender review copy is unnecessary. Without an explicit `--output`, optimized mode writes to `output/web_optimized/air65-ii.glb`.

To produce a detailed export, retain the default mode or explicitly select `--mode lossless`, preferably choosing a separate output folder when preserving existing evidence:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python scripts/export_web_model.py -- \
  --source output/with_battery/air65_ii.blend \
  --mode lossless \
  --output output/web_detailed_refined/air65-ii.glb
```

Both modes write `model-metadata.json`; optimized mode additionally writes `optimization-metrics.json`. Inspect these results for the new source before publishing. The previous baseline's numeric reduction is not an acceptance result for the new geometry. The main task owns fresh independent visual review and actual browser-performance measurements.

## Refined source integration

The main renderer now supports explicitly authored shared boundary normals for separately editable canopy patches. The exporter protects meshes carrying custom normals from all retessellation, including planar dissolution, because a surface-distance threshold alone cannot establish shading equivalence. Their positions, triangles, UVs and authored normals are retained. The fresh textured-model figures and measured browser timings are reported in `reports/refinement_validation.md`; the figures above remain the preserved baseline experiment.

## Final serialization precision

The refined source exposed a process-dependent one-ULP variation in four bevel-interpolated UV coordinates (about 0.00000003 normalized units). The final exporter canonicalizes evaluated UVs to six decimal places before indexing, in both full and optimized mode. The bound is 0.0000005 normalized units, or 0.001024 pixel for a 2048-pixel image. Image bytes, source UVs and geometry remain unchanged. Thus the earlier fixture’s exact UV-byte observation describes that fixture/run, while current delivered UVs use the explicitly recorded deterministic precision. Current repeatability evidence is in `output/web_optimized/reproducibility.json`.

## Independent visual review changed the final profile

The first refined candidate passed geometric distance limits but showed visibly polygonal black lens rings in the focal close-up. The rejected image is preserved at `reports/refinement/rejected_web_lens.png`. The final `air65-bounded-web-v2` profile excludes the entire camera component from retessellation, in addition to the existing protection for authored canopy normals. This intentionally trades some triangle savings for optical silhouette quality; the fresh independent review determines closure.
