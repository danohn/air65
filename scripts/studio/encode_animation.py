"""Encode integrated studio frames with a stable GIF palette and H.264 MP4.

Run with uv run python scripts/studio/encode_animation.py. FFmpeg/ffprobe must
be on PATH or supplied with flags/environment variables; no Blender is needed.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess

from pipeline import portable_path, read_json, repo_path, sha256_file, write_json


def executable(value: str | None, name: str) -> str:
    found = shutil.which(value or name)
    if not found:
        raise ValueError(f"{name} not found; pass --{name}, set {name.upper()}_BIN, or add it to PATH")
    return found


def validate_frames(directory: Path, manifest: dict) -> None:
    frames = manifest.get("frames", [])
    count, fps, duration = manifest["frame_count"], manifest["fps"], manifest["duration_s"]
    if not isinstance(count, int) or count < 2 or len(frames) != count:
        raise ValueError("Manifest has no complete exposure-frame sequence; run --stage compose first")
    if not isinstance(fps, int) or fps < 1 or 100 % fps:
        raise ValueError("GIF delivery requires integer fps dividing 100, such as 20, 25 or 50")
    if not math.isclose(count / fps, duration, abs_tol=1e-8):
        raise ValueError("Frame count, fps and duration disagree")
    if len(manifest["dimensions"]) != 2 or any(v % 2 for v in manifest["dimensions"]):
        raise ValueError("MP4 yuv420p delivery requires even image width and height")
    for index, frame in enumerate(frames):
        if frame["frame"] != index or not math.isclose(frame["time_s"], index / fps, abs_tol=1e-7):
            raise ValueError(f"Non-contiguous frame manifest at index {index}")
        path = directory / "frames" / f"frame_{index:04}.png"
        if not path.is_file():
            raise ValueError(f"Missing exposure frame: {path}")


def stamp(seconds: float) -> str:
    centiseconds = round(seconds * 100)
    return f"{centiseconds//360000}:{centiseconds//6000%60:02}:{centiseconds//100%60:02}.{centiseconds%100:02}"


def labels_ass(manifest: dict, label_position: str = "bottom") -> str:
    """Use a 960x720 canvas, with an optional safe area above native video controls."""
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 960
PlayResY: 720
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Arial,29,&H00F2F2F4,&H00F2F2F4,&H501E1920,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,32,32,24,1
Style: Small,Arial,12,&H00D1CAD1,&H00D1CAD1,&H501E1920,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,32,32,24,1
Style: Speed,Arial,25,&H00F2F2F4,&H00F2F2F4,&H401E1920,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,32,32,24,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    end = stamp(manifest["duration_s"])
    events = [
        f"Dialogue: 0,0:00:00.00,{end},Title,,0,0,0,," + r"{\pos(32,26)}Air65 II",
        f"Dialogue: 0,0:00:00.00,{end},Small,,0,0,0,," + r"{\pos(33,65)}RACING  /  MOTOR SPIN-UP",
        f"Dialogue: 0,0:00:00.00,{end},Small,,0,0,0,," + r"{\an9\pos(928,32)\fs10}MANUFACTURER BENCH RPM REFERENCE",
    ]
    timing, fps = manifest["timing"], manifest["fps"]
    for frame in manifest["frames"]:
        index, t, rpm = frame["frame"], frame["time_s"], round(frame["rpm"])
        if t < timing["rest_until_s"] or t >= timing["stopped_at_s"]:
            label = "STILL"
        elif t < timing["spinup_until_s"]:
            label = "SPINNING UP"
        elif t < timing["hold_until_s"]:
            label = "AT SPEED"
        else:
            label = "WINDING DOWN"
        start, stop = stamp(index / fps), stamp((index + 1) / fps)
        speed_position = r"\an9\pos(928,51)" if label_position == "top" else r"\pos(32,641)"
        stage_position = r"\an9\pos(928,85)" if label_position == "top" else r"\pos(33,676)"
        events.extend([
            f"Dialogue: 1,{start},{stop},Speed,,0,0,0,,{{{speed_position}}}{rpm:,} rpm",
            f"Dialogue: 1,{start},{stop},Small,,0,0,0,,{{{stage_position}}}{label}",
        ])
    return header + "\n".join(events) + "\n"


def encode_commands(ffmpeg: str, directory: Path, manifest: dict, stem: str, labels: bool) -> list[list[str]]:
    fps, count = str(manifest["fps"]), str(manifest["frame_count"])
    inputs = ["-framerate", fps, "-start_number", "0", "-t", str(manifest["duration_s"]),
              "-i", str(directory / "frames" / "frame_%04d.png")]
    presentation = "subtitles=labels.ass," if labels else ""
    prefix = [ffmpeg, "-hide_banner", "-loglevel", "warning", "-y"]
    return [
        [*prefix, *inputs, "-vf", presentation + "palettegen=max_colors=256:stats_mode=full:reserve_transparent=1",
         "-frames:v", "1", "-update", "1", "palette.png"],
        [*prefix, *inputs, "-i", "palette.png", "-filter_complex",
         f"[0:v]{presentation}null[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=none[out]",
         "-map", "[out]", "-frames:v", count, "-loop", "0", "-final_delay", str(100 // manifest["fps"]),
         "-fps_mode", "passthrough", stem + ".gif"],
        [*prefix, *inputs, "-vf", presentation + "null", "-frames:v", count,
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", stem + ".mp4"],
    ]


def validate_deliveries(output: Path, stem: str, manifest: dict, ffprobe: str) -> dict:
    from PIL import Image

    with Image.open(output / (stem + ".gif")) as gif:
        duration, hashes = 0, []
        loop = gif.info.get("loop")
        for index in range(gif.n_frames):
            gif.seek(index)
            duration += gif.info.get("duration", 0)
            hashes.append(hashlib.sha256(gif.convert("RGB").tobytes()).hexdigest())
        gif_info = {"size": list(gif.size), "encoded_frames": gif.n_frames, "duration_ms": duration,
                    "loop": loop, "distinct_decoded_frames": len(set(hashes)),
                    "first_last_identical": hashes[0] == hashes[-1]}
    if gif_info["size"] != manifest["dimensions"] or duration != round(manifest["duration_s"] * 1000):
        raise ValueError(f"Encoded GIF size/duration mismatch: {gif_info}")
    if loop != 0 or not gif_info["first_last_identical"] or gif_info["distinct_decoded_frames"] < 2:
        raise ValueError(f"Encoded GIF lacks motion or a seamless infinite loop: {gif_info}")
    probe = json.loads(subprocess.check_output([
        ffprobe, "-v", "error", "-show_entries",
        "format=duration:stream=width,height,nb_frames,r_frame_rate", "-of", "json",
        str(output / (stem + ".mp4")),
    ], text=True))
    stream = probe["streams"][0]
    if (abs(float(probe["format"]["duration"]) - manifest["duration_s"]) >= 0.001
            or [stream["width"], stream["height"]] != manifest["dimensions"]
            or Fraction(stream["r_frame_rate"]) != manifest["fps"]
            or int(stream["nb_frames"]) != manifest["frame_count"]):
        raise ValueError(f"Encoded MP4 metadata mismatch: {probe}")
    return {"gif": gif_info, "mp4": probe,
            "outputs": {name: {"bytes": (output / name).stat().st_size,
                               "sha256": sha256_file(output / name)}
                        for name in (stem + ".gif", stem + ".mp4")}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="output/prop_spinup", help="Directory with animation_manifest.json and frames/")
    parser.add_argument("--output", help="Delivery directory; defaults to --input")
    parser.add_argument("--stem", help="Output filename stem; default air65_ii_spinup_<duration>s")
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG_BIN"))
    parser.add_argument("--ffprobe", default=os.environ.get("FFPROBE_BIN"))
    parser.add_argument("--no-labels", action="store_true", help="Encode the clean studio presentation without captions")
    parser.add_argument("--labels-position", choices=("bottom", "top"), default="bottom",
                        help="Use top for embedded web playback; bottom preserves the original standalone layout")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print commands without writing files")
    args = parser.parse_args(argv)
    directory = repo_path(args.input)
    output = repo_path(args.output) if args.output else directory
    manifest = read_json(directory / "animation_manifest.json")
    validate_frames(directory, manifest)
    stem = args.stem or f"air65_ii_spinup_{manifest['duration_s']:g}s"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", stem):
        parser.error("--stem must be a plain filename stem with letters, numbers, dots, underscores or hyphens")
    ffmpeg, ffprobe = executable(args.ffmpeg, "ffmpeg"), executable(args.ffprobe, "ffprobe")
    commands = encode_commands(ffmpeg, directory, manifest, stem, not args.no_labels)
    if args.dry_run:
        print(json.dumps({"input": portable_path(directory), "output": portable_path(output),
                          "frame_count": manifest["frame_count"], "commands": commands}, indent=2))
        return
    if not args.no_labels:
        filters = subprocess.check_output([ffmpeg, "-hide_banner", "-filters"], text=True, stderr=subprocess.STDOUT)
        if "subtitles" not in filters:
            raise ValueError("FFmpeg needs the libass subtitles filter; use a build with libass or pass --no-labels")
    output.mkdir(parents=True, exist_ok=True)
    if not args.no_labels:
        (output / "labels.ass").write_text(labels_ass(manifest, args.labels_position), encoding="utf-8")
    for command in commands:
        print("ENCODE", command[-1], flush=True)
        subprocess.run(command, cwd=output, check=True)
    report = validate_deliveries(output, stem, manifest, ffprobe)
    report.update({"source_manifest_sha256": sha256_file(directory / "animation_manifest.json"),
                   "encoder_sha256": sha256_file(Path(__file__)), "labels": not args.no_labels,
                   "labels_position": args.labels_position if not args.no_labels else None})
    write_json(output / "delivery_validation.json", report)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"encode: {exc}") from exc
