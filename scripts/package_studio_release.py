"""Package the curated studio deliverables, excluding render caches and references."""
import argparse
import json
from pathlib import Path
import re
import shutil

from package_release import collect, make_archive, sha256

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    'output/studio_portrait/air65_ii_studio.blend',
    'output/studio_portrait/air65_ii_studio.jpg',
    'output/studio_portrait/air65_ii_studio.png',
    'output/studio_portrait/air65_ii_studio_manifest.json',
    'output/prop_spinup/air65_ii_spinup.blend',
    'output/prop_spinup_web/air65_ii_spinup_10s.gif',
    'output/prop_spinup_web/air65_ii_spinup_10s.mp4',
    'output/prop_spinup/animation_manifest.json',
    'output/prop_spinup_web/delivery_validation.json',
    'output/prop_spinup/motion_spec.json',
    'output/prop_spinup/visual_review.json',
    'output/prop_spinup/still.png',
    'output/prop_spinup/full_speed.png',
    'output/prop_spinup/delivery_still.png',
    'output/web_motion/air65-ii.glb',
    'output/web_motion/model-metadata.json',
    'output/web_motion/motion-validation.json',
    'output/web_motion/regression-checks.json',
    'output/web_motion/gltf-validator.json',
)
DOWNLOADS = (
    ('output/studio_portrait/air65_ii_studio.blend', 'air65-ii-studio.blend'),
    ('output/studio_portrait/air65_ii_studio.jpg', 'air65-ii-studio.jpg'),
    ('output/studio_portrait/air65_ii_studio.png', 'air65-ii-studio.png'),
    ('output/prop_spinup/air65_ii_spinup.blend', 'air65-ii-spinup.blend'),
    ('output/prop_spinup_web/air65_ii_spinup_10s.gif', 'air65-ii-spinup-10s.gif'),
    ('output/prop_spinup_web/air65_ii_spinup_10s.mp4', 'air65-ii-spinup-10s.mp4'),
    ('output/web_motion/air65-ii.glb', 'air65-ii.glb'),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='v0.2.0')
    args = parser.parse_args()
    if not re.fullmatch(r'v\d+\.\d+\.\d+', args.version):
        parser.error('Version must use vMAJOR.MINOR.PATCH format')
    delivery = json.loads((ROOT / 'output/prop_spinup_web/delivery_validation.json').read_text())
    if delivery['gif']['duration_ms'] != 10000 or not delivery['gif']['first_last_identical']:
        raise ValueError('A validated ten-second seamless GIF is required')
    for filename, facts in delivery['outputs'].items():
        if sha256(ROOT / 'output/prop_spinup_web' / filename) != facts['sha256']:
            raise ValueError(f'Animation no longer matches validation: {filename}')
    model = ROOT / 'output/web_motion/air65-ii.glb'
    if sha256(model) != sha256(ROOT / 'site/dist/assets/air65-ii.glb'):
        raise ValueError('Site GLB differs from the release model')
    destination = ROOT / 'dist/releases' / args.version
    destination.mkdir(parents=True, exist_ok=True)
    archive = make_archive(ROOT, destination / f'air65-ii-studio-{args.version}.zip', collect(ROOT, (), ARTIFACTS), 'artifacts')
    downloads = []
    for source, filename in DOWNLOADS:
        target = destination / filename
        shutil.copyfile(ROOT / source, target)
        downloads.append({'name':filename, 'bytes':target.stat().st_size, 'sha256':sha256(target)})
    for asset in [archive, *downloads]:
        asset['url'] = f"https://github.com/danohn/air65/releases/download/{args.version}/{asset['name']}"
    index = {
        'schema_version':1, 'version':args.version, 'repository':'danohn/air65',
        'description':'Studio additions and the motion-aware web export. The original model and historical baseline remain in v0.1.0.',
        'base_release':'v0.1.0', 'public_glb_sha256':sha256(model),
        'archives':[archive], 'downloads':downloads,
    }
    (ROOT / 'releases' / f'{args.version}.json').write_text(json.dumps(index, indent=2) + '\n')
    (destination / 'SHA256SUMS').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in [archive, *downloads]))
    print(json.dumps(index, indent=2))


if __name__ == '__main__':
    main()
