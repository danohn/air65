"""Portable, Blender-independent validation and timing for the studio pipeline."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def repo_path(value: str | Path) -> Path:
    """CLI/config relative paths always start at the repository, not the caller cwd."""
    return (ROOT / Path(value).expanduser()).resolve()


def portable_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def json_hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def require_number(value, name: str, minimum: float = 0, maximum: float = math.inf,
                   integer: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if not minimum <= value <= maximum or (integer and int(value) != value):
        kind = "integer" if integer else "number"
        raise ValueError(f"{name} must be a {kind} in [{minimum}, {maximum}]")


def validate_studio(spec: dict) -> None:
    if spec.get("schema_version") != 1:
        raise ValueError("Unsupported studio schema_version")
    require_number(spec["width"], "width", 64, 8192, True)
    require_number(spec["height_ratio"], "height_ratio", 0.1, 10)
    require_number(spec["cycles_samples"], "cycles_samples", 1, 4096, True)
    if not spec.get("lights"):
        raise ValueError("Studio needs at least one light")
    for axis in ("margin_x", "margin_y"):
        require_number(spec["camera"][axis], f"camera.{axis}", 0, 0.49)


def scalar_clip(value, lower, upper):
    return min(max(value, lower), upper)


class MotionProfile:
    """Smooth RPM and its analytic integral; optional clip supports NumPy arrays."""

    def __init__(self, spec: dict):
        if spec.get("schema_version") != 1:
            raise ValueError("Unsupported motion schema_version")
        limits = {
            "duration_s": (0.04, 3600, False), "fps": (1, 100, True),
            "width": (64, 8192, True), "height": (64, 8192, True),
            "shutter_s": (0.000001, 1, False), "atlas_phases": (3, 4096, True),
            "atlas_period_degrees": (0.001, 360, False),
            "cycles_samples": (1, 4096, True), "start_rest_s": (0, 3600, False),
            "ramp_up_s": (0.000001, 3600, False), "ramp_down_s": (0.000001, 3600, False),
            "nominal_hold_s": (0, 3600, False), "peak_rpm": (1, 1000000, False),
        }
        for key, (low, high, integer) in limits.items():
            require_number(spec[key], key, low, high, integer)
        self.spec = spec
        self.duration = spec["duration_s"]
        self.fps = spec["fps"]
        self.frame_count = round(self.duration * self.fps)
        if not math.isclose(self.frame_count, self.duration * self.fps, abs_tol=1e-8):
            raise ValueError("duration_s * fps must be an integer number of frames")
        if spec["shutter_s"] > 1 / self.fps:
            raise ValueError("shutter_s must not exceed the frame interval")
        self.rest, self.up, self.down = spec["start_rest_s"], spec["ramp_up_s"], spec["ramp_down_s"]
        self.peak_rpm = spec["peak_rpm"]
        self.peak_rps = self.peak_rpm / 60
        self.total_turns = round(self.peak_rps * (self.up / 2 + spec["nominal_hold_s"] + self.down / 2))
        self.hold = self.total_turns / self.peak_rps - (self.up + self.down) / 2
        self.up_end = self.rest + self.up
        self.hold_end = self.up_end + self.hold
        self.stop = self.hold_end + self.down
        self.period_turns = spec["atlas_period_degrees"] / 360
        if self.hold < 0:
            raise ValueError("Loop closure produces a negative hold; increase nominal_hold_s")
        half_shutter = spec["shutter_s"] / 2
        if self.rest < half_shutter or self.stop > (self.frame_count - 1) / self.fps - half_shutter:
            raise ValueError("Both first and last complete camera exposures must lie in the rest intervals")
        if not math.isclose(1 / self.period_turns, round(1 / self.period_turns), abs_tol=1e-8):
            raise ValueError("Atlas period must divide a full revolution for the closed loop")
        require_number(spec["exposure_integration"]["quadrature_samples_per_frame"],
                       "quadrature_samples_per_frame", 1, 10000000, True)
        signs = spec["motion"]["sign_by_corner"]
        if set(signs) != {"FL", "FR", "RL", "RR"} or any(type(v) is not int or v not in (-1, 1) for v in signs.values()):
            raise ValueError("sign_by_corner must provide integer +/-1 for FL, FR, RL and RR")
        parts = spec["motion"]["rotating_motor_parts"]
        if not parts or len(set(parts)) != len(parts):
            raise ValueError("rotating_motor_parts must be a nonempty unique list")

    def rpm_at(self, t, clip=scalar_clip):
        u = clip((t - self.rest) / self.up, 0, 1)
        v = clip((t - self.hold_end) / self.down, 0, 1)
        return self.peak_rpm * u * u * (3 - 2 * u) * (1 - v * v * (3 - 2 * v))

    def turns_at(self, t, clip=scalar_clip):
        u = clip((t - self.rest) / self.up, 0, 1)
        v = clip((t - self.hold_end) / self.down, 0, 1)
        ramp_in = self.peak_rps * self.up * (u**3 - 0.5 * u**4)
        constant = self.peak_rps * clip(t - self.up_end, 0, self.hold)
        ramp_out = self.peak_rps * self.down * (v - v**3 + 0.5 * v**4)
        return ramp_in + constant + ramp_out

    def timing(self):
        return {"rest_until_s": self.rest, "spinup_until_s": self.up_end,
                "hold_until_s": self.hold_end, "stopped_at_s": self.stop,
                "total_rotor_revolutions": self.total_turns}


def source_code_hashes(*names: str) -> dict:
    directory = Path(__file__).resolve().parent
    return {name: sha256_file(directory / name) for name in sorted(names)}


def cache_identity(source: Path, spec: dict, code_hashes: dict, runtime: dict,
                   dependencies: dict | None = None) -> dict:
    """No absolute source path in identity: moving an identical checkout is safe."""
    return {"cache_version": 1, "source_sha256": sha256_file(source),
            "effective_spec_sha256": json_hash(spec), "source_code_sha256": code_hashes,
            "runtime": runtime, "external_assets_sha256": dependencies or {}}


def check_cache(directory: Path, identity: dict, require_existing: bool = False) -> dict:
    """Read-only check: never silently adopt old or unidentifiable phase files."""
    identity_file = directory / "identity.json"
    if not identity_file.exists():
        if require_existing or any(directory.glob("phase_*.exr")):
            raise ValueError("Atlas has no matching identity; render into a fresh output directory")
        return {}
    if read_json(identity_file) != identity:
        raise ValueError("Atlas inputs/runtime changed; choose a fresh output directory")
    return read_json(directory / "files.json") if (directory / "files.json").exists() else {}


def cached_phase(path: Path, records: dict) -> bool:
    if not path.exists():
        return False
    recorded = records.get(path.name)
    if not recorded or recorded != {"bytes": path.stat().st_size, "sha256": sha256_file(path)}:
        raise ValueError(f"Unverified or changed atlas phase: {path.name}; choose a fresh output directory")
    return True
