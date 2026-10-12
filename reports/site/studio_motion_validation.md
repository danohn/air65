# Studio and interactive motion validation

Checked 12 October 2026. This report covers the new studio media, motion-aware export and interactive motor controls. The earlier static model benchmark in `site/VALIDATION.md` remains historical evidence for its exact asset; it is not a performance measurement of this new motion mode.

## Source and geometry

- `uv run pytest -q`: **50 passed**. These include the studio configuration/cache/encoding tests and the motion partition checks.
- `npm --prefix site run check`: passed.
- `npm --prefix site test`: **4 passed**. Node tests load the actual shipped GLB hierarchy and verify elapsed-time RPM integration, blur thresholds, eight rotor transforms, stationary components, pause/reset/slow motion and independent exploded positions. They do not render pixels or replace browser inspection.
- `git diff --check`: passed before publication.
- Shipped GLB: **10,441,784 bytes**, SHA-256 `4721b58072d8f5cacca84b873e626163061e4317ec158477046d85d49a332b2d`.
- The export preserves all 262,810 triangles, positions, normals, UVs, winding, material definitions, embedded images and 13 component anchors of the preceding static asset. Two independent exports match byte for byte. Khronos validation reports zero errors and zero warnings. See [the export report](../web_motion_export.md).
- The renderer uses the shared motion JSON. Adjacent rotor pairs have opposite signs; only propellers and motor bells rotate. Source Blender files were preserved. See [studio source validation](../studio_source_validation.md).

## Actual browser observations

The local static site was inspected in the Codex in-app Chromium browser at **1365 × 900** and **390 × 844**, using real UI interactions. Browser emulation is not a physical phone test.

- The model loads without warning/error console messages. Default speed is zero; the optional battery is hidden. Animation does not start automatically.
- Maximum selects **60,394 RPM** and shows the high-speed blur explanation. Slow motion retains that selected RPM and explicitly shows **120.8 RPM** at 1/500 playback speed. The 120 RPM preset exposes blade movement. Keyboard Home/ArrowRight on the slider changes the value to 0 then 1 RPM.
- Pause retains the selected speed. Resume restarts it. Reset restores zero speed, the authored pose, normal playback, the assembled perspective view and default component visibility.
- Explode reaches 100% with the illustrative-spacing label. Enabling wireframe pauses motion; starting motion turns wireframe off. The same component anchors preserve explode and visibility behavior.
- Returning from Studio to the viewer loads a working model and controls. This observation does not establish which browser history-cache path was used.
- The initial phone panel covered the model. The corrected layout places the viewer above a bounded, scrolling inspector. The revised capture shows the model and RPM controls together without horizontal overflow.
- Studio loads the photograph and poster independently of the GLB. Its native Play button starts the MP4: observed `paused=false`, `duration=10`, `readyState=4`, advancing `currentTime`, and no media error. The video is user initiated with `preload="none"`.
- Desktop and phone Studio layouts were inspected. Download links target the full JPEG, compact MP4 and versioned GitHub release. Release publication and Site deployment are recorded separately.

Evidence: [desktop slow motion](motion-desktop.png), [desktop normal-speed blur](motion-blur-desktop.png), [phone controls](motion-mobile.png), [desktop Studio](studio-desktop.png), [phone Studio](studio-mobile.png), and [independent review](studio_motion_review.md).

## Packaging and publication boundary

The tracked WebP/JPEG/MP4/poster plus motion JSON total about **1.1 MB**. The GIF is a release download. `scripts/package_studio_release.py` creates a 19-file archive that excludes third-party research images, the phase atlas, individual animation frames, caches, logs and alternate encodes.

The release ZIP was restored using `scripts/restore_release.py --index releases/v0.2.0.json --from-dir dist/releases/v0.2.0 --destination <temporary-directory>`. All **19 files** passed archive and per-file checksum validation. The temporary directory was removed after validation. The selected GIF is ten seconds with a seamless first/last decoded frame; the MP4 is 960 × 720 at 25 fps. The exact delivered media hashes are pinned in the release index and delivery validation. Independent review found that bottom captions overlapped native video controls. The final GIF/MP4 were re-encoded from the same integrated frames with upper-right RPM/stage captions; all timing and loop checks passed again. Original exploratory encodes remain local.

The public [Site version 3](https://air65-ii-explorer.danohn.chatgpt.site/) deployed successfully at 04:36 UTC on 12 October 2026. Its live maximum/slow-motion controls were exercised and the console remained free of warnings/errors. The [published screenshot](published-studio-motion.png) captures that state. [GitHub v0.2.0](https://github.com/danohn/air65/releases/tag/v0.2.0) is published with all nine assets uploaded. Exact source and deployment identities are recorded in [studio_motion_deployment.json](studio_motion_deployment.json). The older `deployment.json`, `public_asset_validation.json` and refinement screenshots retain Site version 2 evidence.

## Limits

The browser's radial coverage blur is an approximation. It does not integrate scene radiance, reflections or shadows over time. Propellers do not cast shadows in the existing viewer setup; cached high-speed motor-bell shadows are not temporally integrated. The studio video uses the documented Cycles phase integration instead. No new FPS or GPU benchmark is claimed.

The 60,394 RPM endpoint is a [manufacturer bench sample](https://betafpv.com/products/0702-brushless-motors-2026), not measured flight telemetry. The movie ramp is authored. None of these checks establishes aerodynamic performance, physical rotor dynamics or dimensional metrology. The estimated model geometry and unplugged battery display pose retain the earlier fidelity qualifications.
