"""YAMNet backend placeholder with actionable dependency guidance."""

from __future__ import annotations

from pathlib import Path

from cc_suggester.audio.backends.base import AudioBackend
from cc_suggester.core.config import PipelineConfig
from cc_suggester.core.errors import BackendUnavailableError
from cc_suggester.core.types import AudioEventCandidate, VideoMetadata


class YamnetAudioBackend(AudioBackend):
    """YAMNet backend stub.

    The class is registered so users get a precise error message instead of an
    unknown-backend failure. The real implementation should load TensorFlow Hub
    YAMNet or an offline exported model.
    """

    name = "yamnet"
    requires_audio_file = True
    requires_valid_media = True

    def detect(
        self,
        video_path: Path,
        metadata: VideoMetadata,
        config: PipelineConfig,
    ) -> list[AudioEventCandidate]:
        raise BackendUnavailableError(
            message="The YAMNet backend is not installed in this environment yet.",
            code="yamnet_not_installed",
            suggestions=[
                "Use --audio-backend dsp for an offline CPU baseline.",
                "Use --audio-backend mock for deterministic demos/tests.",
                "Install TensorFlow/TensorFlow Hub and add an offline YAMNet model path.",
            ],
        )
