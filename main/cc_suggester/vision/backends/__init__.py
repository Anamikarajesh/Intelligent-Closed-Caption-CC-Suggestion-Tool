"""Vision backend registry."""

from cc_suggester.vision.backends.base import VisionBackend
from cc_suggester.vision.backends.mock import MockVisionBackend


def get_vision_backend(name: str) -> VisionBackend:
    """Return a visual reaction backend by name."""

    normalized = name.lower().strip()
    if normalized in {"mock", "demo"}:
        return MockVisionBackend()
    raise ValueError(
        f"Unknown vision backend '{name}'. Available in this scaffold: mock. "
        "Planned backends: mediapipe, opencv, mmpose, mmaction."
    )
