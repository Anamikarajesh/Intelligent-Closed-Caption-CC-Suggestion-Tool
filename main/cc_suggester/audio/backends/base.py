"""Audio backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from cc_suggester.core.config import PipelineConfig
from cc_suggester.core.types import AudioEventCandidate, VideoMetadata


class AudioBackend(ABC):
    """Interface implemented by sound event detection backends."""

    name: str

    @abstractmethod
    def detect(
        self,
        video_path: Path,
        metadata: VideoMetadata,
        config: PipelineConfig,
    ) -> list[AudioEventCandidate]:
        """Detect non-speech audio event candidates."""
