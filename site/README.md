# Air65 II — 3D Explorer

A static, public Three.js viewer for the Air65 II Racing reference reconstruction. All runtime code and assets are hosted with the site. No API keys, accounts, external APIs or OpenAI API calls are required by the application.

## Run locally

From this directory:

```sh
uv run python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8765. There is no build step. JavaScript syntax check: `npm run check`.

## Controls

- Drag to rotate, scroll to zoom, right-drag to pan. Touch: one finger rotates; two fingers zoom and pan.
- The camera bar offers perspective, top, front, right and bottom views.
- Click geometry or a component name to inspect it. Notes appear directly beneath the selected row, and the inspector scrolls them into view. Click the name again to close its notes; switches control visibility.
- The slider separates component groups with illustrative spacing, and wireframe shows mesh topology.
- Reset restores the assembled configuration with the optional battery hidden.
- The motor slider covers 0–60,394 RPM. Presets offer stop, a readable 120 RPM inspection speed, 30,000 RPM and the manufacturer bench-test maximum. Nothing spins automatically on page load.
- Pause preserves the selected RPM. Slow motion runs at 1/500 time and labels the displayed speed. Reset stops motors and restores their authored phase; wireframe pauses motion for inspection.
- High-speed props use a lightweight blur derived from the actual blade outlines. The Studio page provides the Cycles photo/video and release download links.
- With the canvas focused, arrow keys rotate, plus/minus zoom and 0/Home resets.
- The parts inspector becomes a collapsible sheet on narrow screens. Its close button stays visible while scrolling, and opening/closing it preserves keyboard access to the controls.

## Assets and accuracy

`dist/assets/air65-ii.glb` is the separately optimized export of `../output/with_battery/air65_ii.blend`, created with `../scripts/export_web_model.py --mode optimized --motion-spec specs/studio/motion.json` from the project root. It retains 13 component anchors, separates rotor/stator and blade/hub geometry, and embeds five authored texture images. The detailed editable Blender source and a full evaluated GLB remain in the parent project. The battery is hidden by default. Coordinates are metres, Y up, X right and -Z forward; the viewer scales the scene into millimetres internally.

`dist/assets/model-metadata.json` records the current asset hash, source hashes, counts, component bounds, motion roles and sampled optimization limits. The source-to-web validation is in `../reports/web_motion_export.md`. Earlier static-model performance measurements remain historical in `../reports/refinement_validation.md`; current feature checks are in `../reports/site/studio_motion_validation.md`. Geometry is evaluated on export; rotor angles are supplied at runtime.

Published measurements anchor the source model, but estimated surfaces remain estimates. The viewer exposes this distinction through component notes and its accuracy dialog. Exploded spacing is illustrative and browser lighting/transmission differ from Cycles rendering. The optional battery is shown with its power lead unplugged.

Three.js 0.186.1 and the required addons are vendored under `dist/vendor/three`, including their MIT license. The original project render supplies the loading image; the new studio portrait supplies the social preview. No third-party reference photographs are distributed on this site. `studio.html` does not load Three.js or the GLB. The MP4 uses `preload="none"`; the GIF and large Blender/PNG files are GitHub release links.

Run `npm test` for the motion integration checks against the shipped GLB hierarchy. Full media/source reproduction instructions are in `../docs/STUDIO_AND_MOTION.md`.

## Deployment

The registered ChatGPT Site is `appgprj_6acc1dd67ef48191a83f2578cef3428e`. `.openai/hosting.json` declares the static output directory. Publish updates through the native Sites source synchronization and deployment workflow; do not create another Site for updates. Repository credentials stay outside the source tree and are passed to the helper through hidden stdin only.
