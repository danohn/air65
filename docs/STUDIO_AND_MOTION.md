# Studio media and interactive motors

The [3D Explorer](https://air65-ii-explorer.danohn.chatgpt.site/) has an RPM slider and the [Studio page](https://air65-ii-explorer.danohn.chatgpt.site/studio.html) presents the photograph and ten-second animation. The [v0.2.0 release](https://github.com/danohn/air65/releases/tag/v0.2.0) contains the editable projects and full-resolution downloads.

## Publication choices

| Destination | Contents | Reason |
| --- | --- | --- |
| Git source | `scripts/studio/`, `specs/studio/`, media/release helpers, exporter changes, viewer controls, focused tests and validation | Preserve the decisions and reproducible process. |
| Tracked website assets | One motion-aware GLB, a 1600px WebP photograph, full JPEG, MP4 and video poster | A fresh clone runs the site without Blender. The compact media add about 1.1 MB; the video loads on demand. |
| GitHub release | Studio and animated `.blend` files, full-resolution PNG/JPEG, GIF, MP4, updated GLB, curated ZIP and checksums | Make the finished work downloadable without accumulating large render files in Git history. |
| Ignored local files | EXR phase atlas, 250 PNG frames, alternate encodes, preview/debug outputs, logs, caches, downloaded reference photographs and Blender backups | Rebuildable working data and third-party research material do not belong in the public source tree. |

The site links to the GIF on GitHub instead of loading a 3.8 MB GIF automatically. It serves the 209 KB MP4 with native video controls and `preload="none"`. Nothing starts moving on page load. The full PNG remains a release download; the 3200 × 2400 JPEG is small enough to offer directly from the site.

## Interactive behavior and accuracy

- The slider covers **0–60,394 RPM**, with stop, 120 RPM inspection, 30,000 RPM and maximum presets. Pause preserves the selected RPM; reset restores the authored pose and stops the motors.
- Slow motion advances time at **1/500 speed**, and displays the resulting visual RPM separately. It does not relabel the selected physical speed.
- All four propellers and motor bells rotate about their original axes. Stators, copper windings, mounts, screws and wiring remain stationary. Adjacent corners rotate in opposite directions, following the actual numeric blade pitch.
- The exporter retains the 13 component anchors. It partitions motor geometry by moving/stationary role and prop geometry by blade/hub surface before material batching. The motion export preserves the prior asset's 262,810 triangles, normals, UVs, materials, textures and component anchors exactly; only mesh organization changes.
- Browser angular increments use RPM × elapsed time, independent of frame rate. Tab hiding suspends the animation; reopening resumes without a time jump. Component visibility, exploded positions and camera motion remain independent.
- At speed, blades fade into a circular transparency estimate derived from their actual projected triangle coverage. The same 1/50-second nominal exposure guides the transition. This is a lightweight real-time approximation, not the studio renderer's full radiance integration. The circular proxy never participates in object picking. Wireframe pauses motion and shows the real geometry.
- The airframe stays in a display pose. Neither the browser animation nor the movie simulates lift, flight control, vibration or battery discharge. The existing unplugged battery display pose remains documented.

The upper reference is BETAFPV's **60,394 RPM at 3.86 V** bench-test sample for the Racing 0702 30000KV motor and GF1207-3P propeller. The manufacturer labels the data as test samples; they are not telemetry from a particular aircraft. `specs/studio/motion.json` records the source, all transcribed rows, confidence and qualifications. The published movie's spin-up/down timing is an authored presentation curve.

Sources: [manufacturer motor page](https://betafpv.com/products/0702-brushless-motors-2026), [manufacturer load-test table](https://cdn.shopify.com/s/files/1/1778/6615/files/0702_Brushless_Motors_2026_load_performance.jpg?v=1769068827). The downloaded chart is neither required at runtime nor redistributed.

## Restore or regenerate

Restore the original project and the studio additions into ignored `output/`:

```sh
uv sync --python 3.14 --frozen
uv run scripts/restore_release.py --index releases/v0.1.0.json
uv run scripts/restore_release.py --index releases/v0.2.0.json
```

The restore helper verifies archive and file checksums, rejects unsafe paths and refuses to replace differing local files. The studio archive excludes the large intermediate atlas and individual animation frames. Restoring both releases provides the source scene as well as the finished studio outputs.

Blender runs its own Python and NumPy. External scripts run through uv; the encoder also requires FFmpeg and ffprobe on PATH (or explicit flags). The tested Blender build is 5.2.2 LTS, `d13f752e3b9c`. On this Mac:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python scripts/studio/render_studio.py -- --output output/studio_rebuild
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python scripts/studio/render_spinup.py -- --source output/studio_rebuild/air65_ii_studio.blend --output output/spinup_rebuild --stage all
uv run scripts/studio/encode_animation.py --input output/spinup_rebuild --output output/spinup_web_rebuild --labels-position top
```

Use your installed Blender path on other systems; append `--cpu` if a supported GPU is unavailable. The default studio is 3200 × 2400 at 384 samples; the animation is 960 × 720, 25 fps, ten seconds, with 72 Cycles phases at 96 samples. The renderer integrates scene-linear EXR samples over each exposure, then applies the saved AgX view transform.

Use fresh regeneration directories: the promoted renderer deliberately rejects the old exploratory atlas identity. New caches bind the source blend, configuration, code, Blender/device and external assets, with checksums for individual EXRs. See [source validation](../reports/studio_source_validation.md) for dry runs, stage controls and smoke-test results. Exact pixels across Blender versions/devices are not promised.

The published GIF/MP4 use captions in an upper safe area so native player controls cannot cover the RPM counter. They are encoded from the same integrated frames; the original bottom-caption exploratory copies remain local. To rebuild that presentation from the original local frame sequence, use `uv run scripts/studio/encode_animation.py --input output/prop_spinup --output output/prop_spinup_web --labels-position top`. The release restores these finished files under `output/prop_spinup_web/` without the intermediate frames.

Prepare the tracked web media from the restored published outputs:

```sh
uv run scripts/prepare_studio_media.py
uv run scripts/package_studio_release.py
```

The second command creates the curated archive and `releases/v0.2.0.json`; it does not upload anything. To regenerate the browser GLB with semantic motion groups, use the exporter with `--mode optimized --motion-spec specs/studio/motion.json`; see [the motion export report](../reports/web_motion_export.md) for its full command and exact validation.

## Checks

```sh
uv run pytest -q
npm --prefix site run check
npm --prefix site test
```

The browser tests use the actual shipped GLB hierarchy and check time integration, directions, stationary transforms, pause/reset and exploded offsets. The independent export validation compares geometry/material/texture multisets to the prior static asset. The studio source tests check the actual saved scene settings, motion constraints, cache boundaries and GIF/MP4 encoding. Browser interaction and publication results are recorded in `reports/site/studio_motion_validation.md`.
