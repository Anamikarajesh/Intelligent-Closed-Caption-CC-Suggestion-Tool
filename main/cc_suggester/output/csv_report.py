"""CSV review report export."""

from __future__ import annotations

import csv
from pathlib import Path

from cc_suggester.core.types import CaptionSuggestion


def write_csv_report(suggestions: list[CaptionSuggestion], output_path: Path) -> Path:
    """Write a reviewer-friendly CSV report."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=[
                "event_id",
                "start_time",
                "end_time",
                "caption_text",
                "language",
                "audio_confidence",
                "reaction_confidence",
                "decision_score",
                "accepted",
                "requires_review",
                "reason",
            ],
        )
        writer.writeheader()
        for suggestion in suggestions:
            writer.writerow(
                {
                    "event_id": suggestion.event_id,
                    "start_time": suggestion.start_time,
                    "end_time": suggestion.end_time,
                    "caption_text": suggestion.caption_text,
                    "language": suggestion.language,
                    "audio_confidence": suggestion.audio_confidence,
                    "reaction_confidence": suggestion.reaction_confidence,
                    "decision_score": suggestion.decision_score,
                    "accepted": suggestion.accepted,
                    "requires_review": suggestion.requires_review,
                    "reason": suggestion.reason,
                }
            )
    return output_path
