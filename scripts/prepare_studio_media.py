"""Prepare the small, authored studio assets intentionally tracked with the site."""
from pathlib import Path
import hashlib
import json
import shutil

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "site/dist/assets"


def main():
    inputs = {
        "studio.jpg": ROOT / "output/studio_portrait/air65_ii_studio.jpg",
        "spinup.mp4": ROOT / "output/prop_spinup_web/air65_ii_spinup_10s.mp4",
    }
    poster = ROOT / "output/prop_spinup/still.png"
    for path in [*inputs.values(), poster, ROOT / "specs/studio/motion.json"]:
        if not path.is_file():
            raise SystemExit(f"Missing {path.relative_to(ROOT)}. Restore the studio release or generate the studio outputs first; see docs/STUDIO_AND_MOTION.md.")
    DEST.mkdir(parents=True, exist_ok=True)
    for name, source in inputs.items():
        shutil.copyfile(source, DEST / name)
    for source, name, size in [
        (inputs["studio.jpg"], "studio.webp", (1600, 1200)),
        (poster, "spinup-poster.webp", (960, 720)),
    ]:
        with Image.open(source) as image:
            image = image.convert("RGB")
            image.thumbnail(size, Image.Resampling.LANCZOS)
            image.save(DEST / name, quality=90, method=6)
    shutil.copyfile(ROOT / "specs/studio/motion.json", DEST / "motion.json")
    names = [*inputs, "studio.webp", "spinup-poster.webp", "motion.json"]
    manifest = {
        "schema_version": 1,
        "description": "Authored studio media. GIF, full PNG and editable Blender projects are GitHub release downloads; no reference photographs are distributed.",
        "source_files": {name: str(path.relative_to(ROOT)) for name, path in inputs.items()},
        "files": {name: {"bytes": (DEST / name).stat().st_size, "sha256": hashlib.sha256((DEST / name).read_bytes()).hexdigest()} for name in names},
    }
    (DEST / "studio-media.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
