"""Check the publication boundary and restore corruption/overwrite safeguards."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from package_release import public_artifact
from restore_release import apply_plan, plan_archive


def make_zip(path, name='output/final/example.txt', content=b'valid', digest=None):
    manifest = {'files': [{'path': name, 'bytes': len(content),
                          'sha256': digest or hashlib.sha256(content).hexdigest()}]}
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr(name, content)
        archive.writestr('MANIFEST.json', json.dumps(manifest))


def test_public_boundary_excludes_reference_content_and_backups():
    for path in ['references/photo.jpg', 'output/refinement_baseline/reports/visual_comparison.png',
                 'output/example/references/photo.jpg', 'output/final/air65_ii.blend1',
                 'output/final/build.log']:
        assert not public_artifact(path)
    assert public_artifact('output/final/air65_ii.blend')
    assert public_artifact('output/refinement_baseline/specs/assembly.json')


def test_restore_is_idempotent_and_refuses_to_overwrite_edits(tmp_path):
    archive = tmp_path / 'artifacts.zip'
    destination = tmp_path / 'checkout'
    make_zip(archive)
    apply_plan(archive, plan_archive(archive, destination))
    assert plan_archive(archive, destination) == []
    target = destination / 'output/final/example.txt'
    target.write_bytes(b'local edit')
    with pytest.raises(ValueError, match='Local file differs'):
        plan_archive(archive, destination)
    assert target.read_bytes() == b'local edit'


@pytest.mark.parametrize('name', ['output/../../escape.txt', '/output/absolute.txt', 'specs/source.json'])
def test_restore_rejects_unsafe_or_source_paths(tmp_path, name):
    archive = tmp_path / 'bad.zip'
    make_zip(archive, name=name)
    with pytest.raises(ValueError, match='Unsafe artifact path'):
        plan_archive(archive, tmp_path / 'checkout')
    assert not (tmp_path / 'checkout').exists()


def test_restore_validates_content_before_writing(tmp_path):
    archive = tmp_path / 'corrupt.zip'
    make_zip(archive, digest='0' * 64)
    with pytest.raises(ValueError, match='checksum mismatch'):
        plan_archive(archive, tmp_path / 'checkout')
    assert not (tmp_path / 'checkout').exists()
