# Viewer validation — refined delivery

Checked 12 October 2026 in the real Codex in-app Chromium browser. The final local viewer was checked at 1365 × 900 and 390 × 844.

## Observed results

- Buildless JavaScript syntax check passes. Loopback root and GLB return HTTP 200.
- The site asset is byte-identical to the independently repeated, validated optimized export: `8ddbc0195e22c59bc8dcf6de34885021e5cc099aea5b33a08817a11a7b6395a7` (10,417,808 bytes).
- Model loads with all default components; optional battery starts hidden. No warning or error appeared in the final local browser console.
- Zoom controls and keyboard orbit respond; reset restores the assembled view and default visibility. Top, bottom and perspective presets were rechecked with the revised asset; front/right and pointer gestures were also exercised in the original viewer validation before the asset refinement.
- Canopy/camera visibility switches expose the printed PCB. The battery toggle shows the corrected wrapper and plain underside cap. Component selection displays the updated Matrix II evidence note.
- Explode reaches 100% with its illustrative-spacing note; wireframe toggles and reset restores shaded materials and assembly state.
- The accuracy dialog shows 35 published, 39 derived and 48 estimated parameters, explains the optimized representation and links to its metadata.
- Phone parts panel opens/closes and scrolls. Resize originally retained too-close desktop framing; the final code preserves orbit and relative zoom against the new aspect ratio, with a larger fitting radius. Independent review then caught the vertical toolbar covering a duct. On phones the final toolbar is a horizontal row above the aircraft; the refreshed 390 × 844 capture shows all ducts with clear margins and no toolbar occlusion.
- A farther camera exposed depth flicker between the PCB substrate and 0.012 mm printed mask. The final renderer uses logarithmic depth precision; the corrected browser underside is visually stable. The benchmark uses the same depth mode.
- Final screenshots are in the parent project's `reports/site/refined_*.jpg`. Published-site verification and deployment identity are recorded separately after publication.

## Measurement and limits

The actual browser benchmark is `../output/browser_benchmark/`, with raw results in `../reports/browser_performance.json` and interpretation in `../reports/refinement_validation.md`. It measures three interleaved rounds per asset at a fixed 960 × 720 drawing buffer and DPR 1, after all Blender jobs finish. It records CPU submission, requestAnimationFrame cadence and optional GPU timing. It does not measure internet delivery or predict every device.

The completed Chrome 155 / ANGLE Metal Apple M1 Pro run measured 94.83 mean FPS and 7.892 ms median GPU time for the refined full asset, versus 119.54 FPS and 6.344 ms for the optimized asset. The original asset measured 93.46 FPS and 8.015 ms. The optimized cadence approaches the observed 120 Hz ceiling; all nine runs remained visible with no GPU-disjoint invalidation. These are local measurements using the exact exported asset hashes, not performance inferred from triangle counts.

Model validation includes 13 serialized group/bounds checks, 27 important optimized-dimension checks, sampled surface/bounds gates, exact repeat export and Khronos validation with zero errors and warnings. The fresh independent visual review rejects the first reduced lens candidate and evaluates the final preserved-camera version. Those checks establish export quality, not physical dimensional metrology.

WebGL 2 is required. Touch controls are supplied by OrbitControls; physical iOS/Android devices and every GPU/browser combination were not tested. The static poster and download link remain available on initialization failure. Rendering pauses while idle/hidden, and device pixel density is capped. Three.js lighting/transmission differs from Cycles.
