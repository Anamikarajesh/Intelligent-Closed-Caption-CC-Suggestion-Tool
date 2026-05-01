"""Audio backend registry."""

from cc_suggester.audio.backends.base import AudioBackend
from cc_suggester.audio.backends.mock import MockAudioBackend


def get_audio_backend(name: str) -> AudioBackend:
    """Return an audio backend by name."""

    normalized = name.lower().strip()
    if normalized in {"mock", "demo"}:
        return MockAudioBackend()
    raise ValueError(
        f"Unknown audio backend '{name}'. Available in this scaffold: mock. "
        "Planned backends: yamnet, panns, ast, beats."
    )
