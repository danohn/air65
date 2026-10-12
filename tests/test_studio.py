"""Test physical timing, portable dry runs and stale/corrupt atlas rejection."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/studio"))
import encode_animation
import render_spinup
import render_studio
from pipeline import (MotionProfile, cache_identity, cached_phase, check_cache,
                      read_json, sha256_file, write_json)


@pytest.fixture
def motion():
    return read_json(ROOT / "specs/studio/motion.json")


def test_published_rpm_integral_and_shutter_travel(motion):
    profile = MotionProfile(motion)
    assert motion["source"]["test_rows"][-1] == {"throttle_percent": 100, "voltage_v": 3.86, "rpm": 60394}
    assert "test samples" in motion["source"]["qualification"]
    assert profile.frame_count == 250
    assert profile.total_turns == 5536
    assert profile.hold == pytest.approx(2.999884094446468)
    assert profile.rpm_at(0) == profile.rpm_at(9.96) == 0
    assert profile.rpm_at(5) == 60394
    assert profile.turns_at(-0.01) == profile.turns_at(0.01) == 0
    assert profile.turns_at(9.95) == profile.turns_at(9.97) == profile.total_turns
    assert profile.turns_at(5.01) - profile.turns_at(4.99) == pytest.approx(20.1313333333333)
    # The derivative of angle, including both nonconstant-speed ramps, must equal RPM.
    for t in (1.501, 1.7, 2.5, 3.7, 4.5, 7.1, 8.1, 9.4):
        derivative = (profile.turns_at(t + 1e-5) - profile.turns_at(t - 1e-5)) / 2e-5 * 60
        assert derivative == pytest.approx(profile.rpm_at(t), abs=0.01)


def test_corner_signs_match_numeric_pitch_not_historical_filenames(motion):
    assembly = read_json(ROOT / "specs/assembly.json")
    for instance in assembly["instances"]:
        if not instance["id"].startswith("prop_"):
            continue
        component = read_json(ROOT / assembly["components"][instance["component"]])
        hands = {node["args"]["handedness"] for node in component["nodes"] if node["op"] == "propeller_blade"}
        assert hands == {motion["motion"]["sign_by_corner"][instance["id"].removeprefix("prop_")]}
    moving = set(motion["motion"]["rotating_motor_parts"])
    assert "silver_bell" in moving and "upper_shaft" in moving
    assert not any("winding" in name or "stator" in name or "screw" in name for name in moving)


@pytest.mark.parametrize("change", [
    {"duration_s": 9.5}, {"shutter_s": 0.1}, {"atlas_period_degrees": 130},
    {"ramp_up_s": 0}, {"peak_rpm": float("nan")}, {"start_rest_s": 0},
])
def test_invalid_motion_fails_before_blender(motion, change):
    motion.update(change)
    with pytest.raises(ValueError):
        MotionProfile(motion)


def test_atlas_identity_tracks_render_inputs_and_moves_with_identical_source(tmp_path, motion):
    source = tmp_path / "source.blend"
    source.write_bytes(b"source")
    moved = tmp_path / "other-name.blend"
    shutil.copyfile(source, moved)
    code = {"renderer.py": "abc"}
    runtime = {"blender": "5.2.2", "device": "CPU"}
    identity = cache_identity(source, motion, code, runtime)
    assert cache_identity(moved, motion, code, runtime) == identity
    changed = copy.deepcopy(motion)
    changed["cycles_samples"] += 1
    assert cache_identity(source, changed, code, runtime) != identity
    assert cache_identity(source, motion, {"renderer.py": "changed"}, runtime) != identity
    assert cache_identity(source, motion, code, {**runtime, "device": "METAL"}) != identity
    assert cache_identity(source, motion, code, runtime, {"unpacked_texture": "sha"}) != identity
    source.write_bytes(b"different source")
    assert cache_identity(source, motion, code, runtime) != identity


def test_atlas_rejects_unidentified_stale_and_corrupt_phases(tmp_path):
    directory = tmp_path / "atlas"
    assert check_cache(directory, {"test": 1}) == {}
    assert not directory.exists()
    with pytest.raises(ValueError, match="no matching identity"):
        check_cache(directory, {"test": 1}, require_existing=True)
    directory.mkdir()
    phase = directory / "phase_000.exr"
    phase.write_bytes(b"rendered linear pixels")
    with pytest.raises(ValueError, match="no matching identity"):
        check_cache(directory, {"test": 1})
    write_json(directory / "identity.json", {"test": 1})
    with pytest.raises(ValueError, match="inputs/runtime changed"):
        check_cache(directory, {"test": 2})
    with pytest.raises(ValueError, match="Unverified"):
        cached_phase(phase, {})
    records = {phase.name: {"bytes": phase.stat().st_size, "sha256": sha256_file(phase)}}
    assert cached_phase(phase, records)
    phase.write_bytes(b"corrupted linear pixels")
    with pytest.raises(ValueError, match="changed atlas phase"):
        cached_phase(phase, records)


def test_dry_runs_work_from_another_cwd_without_bpy_or_writes(tmp_path, monkeypatch, capsys):
    source = tmp_path / "source.blend"
    source.write_bytes(b"source identity only; dry-run does not open Blender")
    target = tmp_path / "not-created"
    monkeypatch.chdir(tmp_path)
    render_studio.main(["--source", str(source), "--output", str(target), "--dry-run"])
    studio_plan = json.loads(capsys.readouterr().out)
    assert studio_plan["resolution"] == [3200, 2400]
    assert studio_plan["samples"] == 384
    render_spinup.main(["--source", str(source), "--output", str(target), "--dry-run"])
    spin_plan = json.loads(capsys.readouterr().out)
    assert spin_plan["peak_rpm"] == 60394 and spin_plan["frame_count"] == 250
    assert not target.exists()


def test_studio_dry_run_rejects_overwriting_source(tmp_path):
    source = tmp_path / "air65_ii_studio.blend"
    source.write_bytes(b"existing source")
    with pytest.raises(ValueError, match="overwrite the source blend"):
        render_studio.main(["--source", str(source), "--output", str(tmp_path), "--dry-run"])
    assert source.read_bytes() == b"existing source"


def make_frames(directory, count=8, fps=25):
    frames = directory / "frames"
    frames.mkdir(parents=True)
    records = []
    for index in range(count):
        color = (20, 35, 50) if index in (0, count - 1) else (20 + index * 12, 80, 110)
        Image.new("RGB", (64, 64), color).save(frames / f"frame_{index:04}.png")
        records.append({"frame": index, "time_s": index / fps, "rpm": 0 if index in (0, count - 1) else 1000})
    manifest = {"frame_count": count, "fps": fps, "duration_s": count / fps, "dimensions": [64, 64],
                "timing": {"rest_until_s": 0.04, "spinup_until_s": 0.1, "hold_until_s": 0.16,
                           "stopped_at_s": (count - 1) / fps}, "frames": records}
    write_json(directory / "animation_manifest.json", manifest)
    return manifest


def test_encoder_refuses_missing_or_noncontiguous_frames(tmp_path):
    manifest = make_frames(tmp_path)
    encode_animation.validate_frames(tmp_path, manifest)
    manifest["frames"][2]["time_s"] = 0.2
    with pytest.raises(ValueError, match="Non-contiguous"):
        encode_animation.validate_frames(tmp_path, manifest)
    manifest["frames"][2]["time_s"] = 0.08
    (tmp_path / "frames/frame_0007.png").unlink()
    with pytest.raises(ValueError, match="Missing exposure frame"):
        encode_animation.validate_frames(tmp_path, manifest)


def test_encoder_uses_manifest_fps_and_shell_free_portable_paths(tmp_path):
    manifest = make_frames(tmp_path, count=8, fps=20)
    labels = encode_animation.labels_ass(manifest)
    assert "0:00:00.35,0:00:00.40,Speed" in labels
    commands = encode_animation.encode_commands("/custom/ffmpeg", tmp_path / "with spaces", manifest, "movie", True)
    assert str(tmp_path / "with spaces/frames/frame_%04d.png") in commands[0]
    assert commands[0][commands[0].index("-framerate") + 1] == "20"
    assert commands[1][commands[1].index("-final_delay") + 1] == "5"
    assert all(command[0] == "/custom/ffmpeg" for command in commands)


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="Optional FFmpeg smoke test")
@pytest.mark.parametrize("labels", [False, True])
def test_small_encoder_roundtrip_in_temporary_directory(tmp_path, labels):
    if labels:
        filters = subprocess.check_output([shutil.which("ffmpeg"), "-hide_banner", "-filters"], text=True, stderr=subprocess.STDOUT)
        if "subtitles" not in filters:
            pytest.skip("Optional libass subtitle filter is unavailable")
    source, target = tmp_path / "input with spaces", tmp_path / "delivery with spaces"
    make_frames(source)
    encode_animation.main(["--input", str(source), "--output", str(target), *([] if labels else ["--no-labels"])])
    report = read_json(target / "delivery_validation.json")
    assert report["gif"]["duration_ms"] == 320
    assert report["gif"]["first_last_identical"]
    assert report["mp4"]["streams"][0]["nb_frames"] == "8"
    assert report["labels"] is labels
