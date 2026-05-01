"""Configuration for pipeline runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SUPPORTED_LANGUAGES = ("en", "hi", "ta", "te", "bn", "mr", "ml")
SUPPORTED_DEVICES = ("auto", "cpu", "cuda")


@dataclass(slots=True)
class PipelineConfig:
    """Runtime configuration shared by CLI, UI, and future integrations."""

    language: str = "en"
    device: str = "auto"
    audio_backend: str = "mock"
    vision_backend: str = "mock"
    output_dir: Path = Path("outputs")
    audio_threshold: float = 0.45
    reaction_threshold: float = 0.35
    decision_threshold: float = 0.65
    review_threshold: float = 0.50
    min_event_duration: float = 0.25
    merge_gap: float = 0.40
    sample_window_before: float = 1.0
    sample_window_after: float = 1.0
    write_rejected_to_reports: bool = True

    def __post_init__(self) -> None:
        if self.language not in SUPPORTED_LANGUAGES:
            supported = ", ".join(SUPPORTED_LANGUAGES)
            raise ValueError(f"Unsupported language '{self.language}'. Supported: {supported}")
        if self.device not in SUPPORTED_DEVICES:
            supported = ", ".join(SUPPORTED_DEVICES)
            raise ValueError(f"Unsupported device '{self.device}'. Supported: {supported}")
        self.output_dir = Path(self.output_dir)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["output_dir"] = str(self.output_dir)
        return data
