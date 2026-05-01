"""Audio backend registry."""

from cc_suggester.audio.backends.base import AudioBackend
from cc_suggester.audio.backends.dsp import DspAudioBackend
from cc_suggester.audio.backends.mock import MockAudioBackend
from cc_suggester.audio.backends.yamnet import YamnetAudioBackend


def get_audio_backend(name: str) -> AudioBackend:
    """Return an audio backend by name."""

    normalized = name.lower().strip()
    if normalized in {"mock", "demo"}:
        return MockAudioBackend()
    if normalized in {"dsp", "energy"}:
        return DspAudioBackend()
    if normalized == "yamnet":
        return YamnetAudioBackend()
    raise ValueError(
        f"Unknown audio backend '{name}'. Available: mock, dsp, yamnet. "
        "Planned advanced backends: panns, ast, beats."
    )
