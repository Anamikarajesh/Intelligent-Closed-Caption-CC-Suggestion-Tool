"""Video metadata inspection utilities."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from cc_suggester.core.types import VideoMetadata


def inspect_video(path: Path) -> VideoMetadata:
    """Inspect a video using ffprobe when available, with a safe fallback."""

    path = Path(path)
    exists = path.exists()
    metadata = VideoMetadata(
        path=path,
        exists=exists,
        size_bytes=path.stat().st_size if exists else None,
        container=path.suffix.lstrip(".").lower() or None,
    )
    if not exists:
        return metadata

    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        metadata.probe_error = "ffprobe not found"
        return metadata

    command = [
        ffprobe,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, check=True, text=True)
        payload = json.loads(completed.stdout or "{}")
    except Exception as exc:
        metadata.probe_error = str(exc)
        return metadata

    fmt = payload.get("format", {})
    try:
        metadata.duration = float(fmt["duration"]) if "duration" in fmt else None
    except (TypeError, ValueError):
        metadata.duration = None

    for stream in payload.get("streams", []):
        if stream.get("codec_type") == "audio":
            metadata.has_audio = True
        if stream.get("codec_type") == "video":
            metadata.width = stream.get("width")
            metadata.height = stream.get("height")
            rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate")
            metadata.fps = _parse_fraction(rate)
    if metadata.has_audio is None:
        metadata.has_audio = False
    return metadata


def _parse_fraction(value: str | None) -> float | None:
    if not value:
        return None
    try:
        numerator, denominator = value.split("/", maxsplit=1)
        denominator_float = float(denominator)
        if denominator_float == 0:
            return None
        return float(numerator) / denominator_float
    except Exception:
        try:
            return float(value)
        except Exception:
            return None
