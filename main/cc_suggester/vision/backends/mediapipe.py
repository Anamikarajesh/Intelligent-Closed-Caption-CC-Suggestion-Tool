"""MediaPipe backend placeholder with actionable setup guidance."""

from __future__ import annotations

from pathlib import Path

from cc_suggester.core.config import PipelineConfig
from cc_suggester.core.errors import BackendUnavailableError
from cc_suggester.core.types import AudioEventCandidate, ReactionResult, VideoMetadata
from cc_suggester.vision.backends.base import VisionBackend


class MediaPipeVisionBackend(VisionBackend):
    """Registered placeholder for future face/pose reaction analysis."""

    name = "mediapipe"
    requires_valid_media = True

    def analyze(
        self,
        video_path: Path,
        metadata: VideoMetadata,
        audio_events: list[AudioEventCandidate],
        config: PipelineConfig,
    ) -> list[ReactionResult]:
        try:
            import mediapipe  # noqa: F401
        except Exception as exc:
            raise BackendUnavailableError(
                message="The MediaPipe vision backend is not installed in this environment yet.",
                code="mediapipe_not_installed",
                suggestions=[
                    "Use --vision-backend opencv for a CPU scene-motion baseline.",
                    "Use --vision-backend mock for deterministic demos/tests.",
                    "Install MediaPipe and OpenCV before selecting this backend.",
                ],
            ) from exc
        raise BackendUnavailableError(
            message="MediaPipe is installed, but face/pose reaction scoring is not wired yet.",
            code="mediapipe_not_wired",
            suggestions=[
                "Use --vision-backend opencv for now.",
                "Implement Face Landmarker and Pose Landmarker inside this backend.",
            ],
        )
