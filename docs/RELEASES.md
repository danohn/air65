# Reproducing the published delivery

The first GitHub release is [v0.1.0](https://github.com/danohn/air65/releases/tag/v0.1.0). The interactive model remains at https://air65-ii-explorer.danohn.chatgpt.site.

The [v0.2.0 studio release](https://github.com/danohn/air65/releases/tag/v0.2.0) adds the studio portrait, ten-second propeller animation, both editable Blender scenes, and the motion-aware browser GLB. Its curated `air65-ii-studio-v0.2.0.zip` restores 19 finished outputs and validation files, without the EXR atlas, 250 source frames, logs or reference photographs. Individual JPEG, full PNG, GIF, MP4, Blender and GLB downloads are also available. The original model and baseline archives remain in v0.1.0.

After restoring the original artifacts below, add the studio delivery with:

```sh
uv run scripts/restore_release.py --index releases/v0.2.0.json
```

`releases/v0.2.0.json` pins the new checksums. The source and rebuild commands are described in [Studio and motion](STUDIO_AND_MOTION.md). `scripts/package_studio_release.py` recreates the v0.2.0 packages from an explicit allowlist; the older `scripts/package_release.py` retains its frozen v0.1.0 validation boundary.

The Git repository contains the modelling source and ready-to-run website. Large generated results are release assets:

- `air65-ii-artifacts-v0.1.0.zip`: final dry/optional Blender projects, source renders, full and optimized exports, inspection views, prototype and validation evidence.
- `air65-ii-baseline-v0.1.0.zip`: original model, its source snapshot, renders, export and reports for historical comparison. The old sheet containing a third-party photograph is excluded.
- `air65-ii.blend`, `air65-ii-with-battery.blend`, `air65-ii.glb` and `air65-ii-multiview.png`: convenient individual downloads.
- `SHA256SUMS`: checksums for the release assets. Each ZIP also has a file-level `MANIFEST.json`.

Restore both artifact ZIPs into the ignored `output/` directory:

```sh
uv sync --python 3.14 --frozen
uv run scripts/restore_release.py
```

The restorer uses the exact URLs, byte sizes and SHA-256 values in `releases/v0.1.0.json`. It verifies the archive and every file before writing, rejects unsafe paths/symlinks and refuses to replace differing local files. Identical existing files are left in place. Downloaded packages are cached under ignored `dist/downloads/`.

Use `--baseline-only` or `--artifacts-only` for a partial restore. For files already downloaded from the release, pass `--from-dir /path/to/downloads`. Use `--overwrite` only when intentionally replacing locally modified generated outputs. The restorer never writes model source or reference photographs.

After a full restore, the original browser benchmark and before/after generators have their expected inputs. The source build itself does not require the baseline or downloaded reference photographs:

```sh
uv run pytest -q
uv run scripts/build.py --validate-only
uv run scripts/build.py --resolution 1400 --samples 64
```

Blender runs its own Python; use the recorded Blender 5.2.2 LTS build for the documented repeatability comparison. New renders on another runtime are not promised to be pixel-identical.

The old local `dist/air65_ii_project.zip` is a research archive containing downloaded references. It is not the public release package. `scripts/package_release.py` creates the public packages and release index; `scripts/package.py` retains the original local research-packaging workflow.

The optional diagnostic `scripts/audit_canopy_normals.py` runs inside Blender with a saved canopy project loaded. Its `--resolved` argument selects the matching resolved JSON; the default points to the final isolated canopy artifact.
