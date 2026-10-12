"""Package public generated artifacts separately from the Git source repository."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIRS = (
    'output/final', 'output/with_battery', 'output/web', 'output/web_optimized',
    'output/prototype', 'output/refinement_inspection', 'output/frame_final',
    'output/canopy_refinement/isolated_final', 'output/browser_benchmark',
)
ARTIFACT_FILES = (
    'output/canopy_refinement/authoring_validation.json',
    'output/canopy_refinement/component_validation.json',
)


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def public_artifact(path):
    """Explicit artifact boundary; never include research photos or their composite."""
    parts = Path(path).parts
    return (
        bool(parts) and parts[0] == 'output'
        and not any(p in {'.git', '.venv', '__pycache__', 'references'} for p in parts)
        and Path(path).name not in {'.DS_Store', 'visual_comparison.png'}
        and not re.search(r'\.blend\d+$', str(path))
        and Path(path).suffix not in {'.pyc', '.log'}
    )


def collect(root, directories, extra=()):
    files = []
    for directory in directories:
        folder = root / directory
        if not folder.is_dir():
            raise ValueError(f'Missing release input directory: {directory}')
        files.extend(p for p in folder.rglob('*') if p.is_file())
    files.extend(root / name for name in extra)
    result = []
    for path in sorted(set(files)):
        if path.is_symlink():
            raise ValueError(f'Release input cannot be a symlink: {path}')
        relative = path.relative_to(root).as_posix()
        if public_artifact(relative):
            if not path.is_file():
                raise ValueError(f'Missing release input: {relative}')
            result.append(path)
    return result


def make_archive(root, destination, files, profile):
    entries = [dict(path=p.relative_to(root).as_posix(), bytes=p.stat().st_size,
                    sha256=sha256(p)) for p in files]
    manifest = dict(schema_version=1, profile=profile, files=entries,
                    note='Generated project artifacts. Downloaded reference photographs and the photo-containing comparison sheet are excluded.')
    with zipfile.ZipFile(destination, 'w') as archive:
        for path, entry in zip(files, entries):
            info = zipfile.ZipInfo(entry['path'], date_time=(2026, 10, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=6)
        info = zipfile.ZipInfo('MANIFEST.json', date_time=(2026, 10, 12, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, json.dumps(manifest, indent=2) + '\n', compresslevel=6)
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError(f'Archive integrity check failed: {destination.name}')
    return dict(name=destination.name, bytes=destination.stat().st_size,
                sha256=sha256(destination), file_count=len(entries), profile=profile)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='v0.1.0')
    parser.add_argument('--repository', default='danohn/air65')
    args = parser.parse_args()
    if not re.fullmatch(r'v\d+\.\d+\.\d+', args.version):
        parser.error('Version must use vMAJOR.MINOR.PATCH format')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repository):
        parser.error('Repository must use OWNER/NAME format')
    evidence = json.loads((ROOT / 'reports/refinement_validation.json').read_text())
    expected = evidence['assets']['refined_optimized']['sha256']
    for name in ['output/web_optimized/air65-ii.glb', 'site/dist/assets/air65-ii.glb']:
        if sha256(ROOT / name) != expected:
            raise ValueError(f'Model differs from reviewed export: {name}')
    if evidence['dry_validation'] != 'pass':
        raise ValueError('Model validation must pass')
    destination = ROOT / 'dist/releases' / args.version
    destination.mkdir(parents=True, exist_ok=True)
    archives = []
    for profile, folders, extras in [
        ('artifacts', ARTIFACT_DIRS, ARTIFACT_FILES),
        ('baseline', ('output/refinement_baseline',), ()),
    ]:
        path = destination / f'air65-ii-{profile}-{args.version}.zip'
        archives.append(make_archive(ROOT, path, collect(ROOT, folders, extras), profile))
    downloads = []
    for source, name in [
        ('output/final/air65_ii.blend', 'air65-ii.blend'),
        ('output/with_battery/air65_ii.blend', 'air65-ii-with-battery.blend'),
        ('output/web_optimized/air65-ii.glb', 'air65-ii.glb'),
        ('output/final/multiview.png', 'air65-ii-multiview.png'),
    ]:
        path = destination / name
        shutil.copyfile(ROOT / source, path)
        downloads.append(dict(name=name, bytes=path.stat().st_size, sha256=sha256(path)))
    base = f'https://github.com/{args.repository}/releases/download/{args.version}'
    for asset in archives + downloads:
        asset['url'] = base + '/' + asset['name']
    index = dict(schema_version=1, version=args.version, repository=args.repository,
                 public_glb_sha256=expected, archives=archives, downloads=downloads)
    index_dir = ROOT / 'releases'
    index_dir.mkdir(exist_ok=True)
    (index_dir / f'{args.version}.json').write_text(json.dumps(index, indent=2) + '\n')
    (destination / 'SHA256SUMS').write_text(''.join(
        f"{asset['sha256']}  {asset['name']}\n" for asset in archives + downloads))
    print(json.dumps(index, indent=2))


if __name__ == '__main__':
    main()
