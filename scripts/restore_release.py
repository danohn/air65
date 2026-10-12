"""Restore checksum-pinned release artifacts into the ignored output directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_download(path, asset):
    if path.stat().st_size != asset['bytes'] or sha256(path) != asset['sha256']:
        raise ValueError(f"Checksum/size mismatch: {asset['name']}")


def fetch(asset, directory):
    name = asset['name']
    if Path(name).name != name or '\\' in name:
        raise ValueError('Invalid release asset filename')
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / name
    if target.exists():
        verify_download(target, asset)
        return target
    if not asset['url'].startswith('https://github.com/'):
        raise ValueError('Release downloads must use HTTPS GitHub URLs')
    with tempfile.NamedTemporaryFile(dir=directory, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            request = Request(asset['url'], headers={'User-Agent': 'air65-release-restore/0.1'})
            with urlopen(request, timeout=60) as response:
                count = 0
                while chunk := response.read(1024 * 1024):
                    count += len(chunk)
                    if count > asset['bytes']:
                        raise ValueError('Download exceeds the pinned asset size')
                    stream.write(chunk)
            stream.flush()
            verify_download(temporary, asset)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    return target


def plan_archive(archive_path, destination, overwrite=False):
    """Validate every archive member and all overwrite conflicts before writing."""
    destination = destination.resolve()
    output = destination / 'output'
    if output.is_symlink():
        raise ValueError('The output directory cannot be a symlink')
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(n.casefold() for n in names)):
            raise ValueError('Duplicate archive member')
        manifest = json.loads(archive.read('MANIFEST.json'))
        entries = manifest['files']
        if set(names) != {'MANIFEST.json'} | {e['path'] for e in entries}:
            raise ValueError('Manifest does not cover the archive')
        if len(entries) + 1 != len(names):
            raise ValueError('Duplicate manifest entry')
        plan = []
        for entry in entries:
            name = entry['path']
            relative = PurePosixPath(name)
            if (relative.is_absolute() or '..' in relative.parts or '\\' in name
                    or not relative.parts or relative.parts[0] != 'output'):
                raise ValueError(f'Unsafe artifact path: {name}')
            info = archive.getinfo(name)
            if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f'Unexpected directory or symlink: {name}')
            target = destination.joinpath(*relative.parts)
            if not target.resolve().is_relative_to(output):
                raise ValueError(f'Artifact escapes output: {name}')
            if info.file_size != entry['bytes']:
                raise ValueError(f'File size mismatch: {name}')
            with archive.open(info) as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != entry['sha256']:
                    raise ValueError(f'File checksum mismatch: {name}')
            if target.exists():
                if not target.is_file():
                    raise ValueError(f'Destination is not a file: {name}')
                if sha256(target) == entry['sha256']:
                    continue
                if not overwrite:
                    raise ValueError(f'Local file differs: {name}; use --overwrite deliberately')
            plan.append((name, target))
    return plan


def apply_plan(archive_path, plan):
    with zipfile.ZipFile(archive_path) as archive:
        for name, target in plan:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
                temporary = Path(stream.name)
                try:
                    with archive.open(name) as source:
                        shutil.copyfileobj(source, stream)
                    stream.flush()
                    os.chmod(temporary, 0o644)
                    temporary.replace(target)
                finally:
                    temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, default=ROOT / 'releases/v0.1.0.json')
    parser.add_argument('--from-dir', type=Path, help='Use existing release downloads without network access')
    parser.add_argument('--destination', type=Path, default=ROOT)
    parser.add_argument('--overwrite', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--baseline-only', action='store_true')
    group.add_argument('--artifacts-only', action='store_true')
    args = parser.parse_args()
    try:
        index = json.loads(args.index.read_text())
        assets = [a for a in index['archives'] if
                  (not args.baseline_only or a['profile'] == 'baseline') and
                  (not args.artifacts_only or a['profile'] == 'artifacts')]
        plans = []
        for asset in assets:
            if Path(asset['name']).name != asset['name'] or '\\' in asset['name']:
                raise ValueError('Invalid release asset filename')
            path = (args.from_dir / asset['name']) if args.from_dir else fetch(
                asset, args.destination / 'dist/downloads')
            verify_download(path, asset)
            plans.append((path, plan_archive(path, args.destination, args.overwrite)))
        for path, plan in plans:
            apply_plan(path, plan)
            print(f'{path.name}: restored {len(plan)} files; identical existing files retained')
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f'air65 restore: {error}\n')


if __name__ == '__main__':
    main()
