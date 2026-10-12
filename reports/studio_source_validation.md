# Studio and motor-animation source promotion

Validated on 2026-10-12 with Blender 5.2.2 LTS (`d13f752e3b9c`), its bundled Python/NumPy, uv-managed Python 3.14, Pillow and locally available FFmpeg/ffprobe. The promoted pipeline preserves the published studio setup and RPM demonstration. This work did not render a new full-resolution photograph or full movie, or replace existing delivery artifacts.

## Tracked production files

| File | Purpose |
|---|---|
| `scripts/studio/render_studio.py` | Build an editable photographic studio from the existing with-battery `.blend`; render PNG/JPEG. |
| `scripts/studio/render_spinup.py` | Articulate the rotor components, render a phase atlas, compose shutter-integrated frames and save an editable animated `.blend`. |
| `scripts/studio/encode_animation.py` | Encode GIF/MP4, preserving the published captions by default, and verify decoded deliveries. |
| `scripts/studio/pipeline.py` | Blender-independent path handling, configuration checks, physical timing and cache-integrity helpers. |
| `specs/studio/studio.json` | Published studio camera, lights, backdrop, optical overrides and render defaults. |
| `specs/studio/motion.json` | Timing, shutter, numerical integration, rotor membership/signs and manufacturer RPM provenance. |
| `tests/test_studio.py` | Focused tests for timing, source/cache safeguards, portable entry points and encoding. |

The original implementation sources were read from `output/studio_portrait/render_studio.py`, `output/prop_spinup/render_spinup.py` and `output/prop_spinup/encode_animation.py`, alongside their specifications, manifests and animation README. Debug/check scripts were not promoted. Existing output files, project dependency files and unrelated source directories were not modified.

## Reproduction

First build or restore `output/with_battery/air65_ii.blend` using the existing project workflow. It is an input artifact, not something these studio scripts silently download. Install the repository's existing Python dependencies with `uv sync` if necessary. Blender supplies `bpy` and NumPy; the external encoder uses the project's Pillow dependency. FFmpeg must provide H.264 encoding, and the default captioned presentation requires its libass `subtitles` filter. Arial is the published font; systems without it may use a different font fallback.

Run from any working directory using an absolute script path, or use these commands from the repository root. `blender` below denotes a Blender executable on PATH; on the validated macOS installation it is `/Applications/Blender.app/Contents/MacOS/Blender`.

```sh
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/studio/render_studio.py -- \
  --output output/studio_rebuild

blender --background --factory-startup --python-exit-code 1 \
  --python scripts/studio/render_spinup.py -- \
  --source output/studio_rebuild/air65_ii_studio.blend \
  --output output/prop_spinup_rebuild

uv run python scripts/studio/encode_animation.py \
  --input output/prop_spinup_rebuild
```

Using fresh output directories avoids changing restored/publication artifacts and avoids mixing atlas generations. Defaults without output overrides remain `output/studio_portrait` and `output/prop_spinup`. All CLI/config relative paths are interpreted against the repository root, not the caller's working directory. The encoder finds FFmpeg/ffprobe through PATH; explicit executable arguments or `FFMPEG_BIN`/`FFPROBE_BIN` are supported. No user-specific executable path is embedded in the scripts.

Useful controls:

- Studio: `--config`, `--source`, `--output`, `--width`, `--samples`, `--preview`, `--cpu`, `--no-render`, `--dry-run`. Published defaults are 3200 × 2400 and 384 samples. A preview uses preview sampling thresholds; use explicit width/sample overrides for a faster small image.
- Animation: `--config`, `--source`, `--output`, `--width`, `--height`, `--samples`, `--cpu`, `--dry-run`, and `--stage all|atlas|compose|rig|validate`. `--phase-limit N` is allowed only with `--stage atlas`. Defaults are 960 × 720, 72 atlas phases and 96 Cycles samples. `--stage validate` checks articulation without writing output. `--stage rig` saves keyframes without rendering or replacing the exposure-frame manifest.
- Encoding: `--input`, `--output`, `--stem`, `--ffmpeg`, `--ffprobe`, `--no-labels`, `--dry-run`. Output defaults to the input directory. GIF timing requires an integer frame rate dividing 100; the published 25 fps uses exact 40 ms frame delays. H.264 output requires even dimensions.

Examples of checks that need no Blender rendering:

```sh
uv run python scripts/studio/render_studio.py --dry-run
uv run python scripts/studio/render_spinup.py --dry-run
uv run python scripts/studio/encode_animation.py --dry-run

blender --background --factory-startup --python-exit-code 1 \
  --python scripts/studio/render_spinup.py -- --stage validate

uv run pytest -q tests/test_studio.py
```

Atlas and composition may be run separately. Keep the source, effective config, code, Blender build and selected rendering device consistent across those stages. Pass `--cpu` consistently if forcing CPU. A default 960 × 720 × 72 RGBA float32 atlas occupies about 796 MB before additional image/composition memory.

## Preserved appearance and motion

The photographic setup retains the four original rectangular lights and their powers/colors/positions, charcoal satin floor, dark world, 85 mm perspective camera, focus point, f/64 depth of field, AgX transform and 0.2 exposure. The presentation-only clear-prop overrides remain transmission 0.98 and roughness 0.065. No aircraft geometry was substituted or regenerated by the studio renderer.

The authoritative motion configuration retains all nine transcribed Racing 0702 30000KV/GF1207-3P benchmark rows. Its peak is **60,394 RPM at 3.86 V**, from the manufacturer's full-throttle bench sample. Both the original qualification and authored-transient caveat remain attached. The [motor product page](https://betafpv.com/products/0702-brushless-motors-2026) and [load-performance table](https://cdn.shopify.com/s/files/1/1778/6615/files/0702_Brushless_Motors_2026_load_performance.jpg?v=1769068827) are recorded in the config. The locally inspected table's hash is included for provenance; the image is neither included nor required to run the pipeline.

The 10-second timeline still rests for 1.5 seconds, accelerates for 2.5 seconds, holds for 2.999884094446468 seconds, decelerates for 2.5 seconds, and rests until the end. Its analytic integral closes at 5,536 complete rotations. The 250 frames are generated at 25 fps with 1/50-second exposures and 32,768 time quadrature samples per frame. Scene-linear phase radiance is integrated before the saved AgX view transform.

`motion.sign_by_corner` is `FL:+1, FR:-1, RL:-1, RR:+1`, where positive means CCW viewed from above. The signs match the geometry's numeric pitch. Historical component filenames have the opposite top-view naming convention. Only the complete propellers and the listed motor bells/crowns/shafts rotate; stators, windings, wires, mounts, screws and bushings remain fixed.

## Source and cache integrity

Output project paths are checked against the input project to avoid overwriting a source `.blend`. Every build records the source checksum and verifies that it remains unchanged. Atlas identity includes the source `.blend` checksum, the effective config (including CLI render overrides), renderer/helper code hashes, Blender version/build, selected device names, architecture and any unpacked image/linked-library file checksums. Each completed EXR also has its own size/checksum record.

An atlas with no matching identity, changed inputs/runtime, a missing phase record or changed phase bytes is rejected. The promoted renderer intentionally does **not** silently adopt the earlier prototype atlas: its format/code identity differs. Generate a fresh atlas in a new output directory. This is conservative cache invalidation; even a source-code edit that does not affect imagery may require a new cache.

Per-stage manifests avoid erasing useful earlier results: atlas-only writes `atlas_manifest.json`, rig-only writes `rig_manifest.json`, and composition/all writes `animation_manifest.json`. The encoder requires a complete contiguous frame manifest and validates GIF dimensions/duration/infinite looping/endpoint equality/motion, plus MP4 dimensions, duration, frame rate and frame count. It uses a global GIF palette with ordered dithering, preserving the published approach to color stability.

## Validation performed

- `uv run --no-sync pytest -q tests/test_studio.py`: **16 passed**. Coverage includes the benchmark transcription, analytic derivative through both ramps, shutter travel, loop endpoints, pitch/sign agreement, invalid timing, cache-source/config/code/device/dependency changes, corrupt phase detection, source-overwrite rejection, cwd-independent dry runs and missing/noncontiguous input frames.
- Two short synthetic encoder round trips, with captions and without captions: eight 64 × 64 frames, 320 ms GIF/MP4, run in temporary paths containing spaces. Both decoded loops and MP4 metadata passed. This tests the production encoder without rendering a movie.
- Headless Blender `--no-render` studio rebuild in a temporary directory: the new manifest exactly matched the existing published manifest for camera, four lights, optical overrides, 942 model-geometry objects, source hash, 3200 × 2400 resolution and 384-sample setting. Validation selected CPU while the published final render used Metal; no pixels were rendered in this check.
- Headless `--stage validate` on the temporary studio: **68 moving objects, 875 stationary objects**, unchanged starting transforms and stationary transforms after a trial phase. No output directory was created by the validation stage.
- Headless `--stage rig` saved an editable animated project in a temporary directory, with 5,536 total rotations. It did not create an atlas or overwrite an exposure-frame manifest.
- One real **64 × 64, one-sample CPU atlas phase** was rendered in a temporary directory. A second identical invocation reused its verified checksum cache; changing the sample count rejected the old identity. No full sequence was rendered.
- SHA-256 checks confirmed the existing with-battery project, studio project, studio manifest, animation manifest and legacy atlas identity were unchanged after the Blender validation. Temporary validation artifacts were removed automatically.

## Remaining limits

The production scripts have been promoted and tested without regenerating the large published deliveries. The regenerated scene setup matches the recorded original; byte-identical `.blend` files or pixel-identical renders across Blender versions, devices, denoisers and font installations are not promised. The animation remains a synchronized stationary studio demonstration, not flight telemetry, a motor transient measurement or thrust simulation.

The 72-phase/120-degree interpolation approximation is unchanged. Finite 64/128-sided round meshes are only approximately axisymmetric, and angular interpolation limits fine detail. Native viewport playback of the very high-speed keyframed rig may strobe; the exposure-integrated pipeline is the intended movie-rendering path.
