"""CLI entrypoint for the Intelligent CC Suggestion Tool."""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path
from typing import Sequence

from cc_suggester import __version__
from cc_suggester.core.config import SUPPORTED_DEVICES, SUPPORTED_LANGUAGES, PipelineConfig
from cc_suggester.core.diagnostics import run_diagnostics
from cc_suggester.core.errors import CCSuggesterError
from cc_suggester.core.media import inspect_video
from cc_suggester.core.pipeline import analyze_video, export_from_report


COMMANDS = ("analyze", "inspect", "doctor", "export", "web")


class FriendlyParser(argparse.ArgumentParser):
    """ArgumentParser that raises instead of exiting mid-flow."""

    def error(self, message: str) -> None:
        raise ValueError(message)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI."""

    args = list(sys.argv[1:] if argv is None else argv)
    if args and not args[0].startswith("-") and args[0] not in COMMANDS:
        return _unknown_command(args[0])

    parser = _build_parser()
    try:
        namespace = parser.parse_args(args)
        if not hasattr(namespace, "handler"):
            parser.print_help()
            return 0
        return int(namespace.handler(namespace))
    except CCSuggesterError as exc:
        _print_friendly_error(exc)
        return 2
    except ValueError as exc:
        print(f"Command error: {exc}", file=sys.stderr)
        print("\nTry:", file=sys.stderr)
        print("  ccs --help", file=sys.stderr)
        return 2


def _build_parser() -> FriendlyParser:
    parser = FriendlyParser(
        prog="ccs",
        description="Generate meaningful non-speech closed caption suggestions from video.",
    )
    parser.add_argument("--version", action="version", version=f"ccs {__version__}")
    subparsers = parser.add_subparsers(dest="command", parser_class=FriendlyParser)

    analyze = subparsers.add_parser("analyze", help="Run the full CC suggestion pipeline.")
    analyze.add_argument("input", type=Path, help="Input video path.")
    analyze.add_argument("--lang", default="en", choices=SUPPORTED_LANGUAGES, help="Caption label language.")
    analyze.add_argument("--device", default="auto", choices=SUPPORTED_DEVICES, help="Device mode.")
    analyze.add_argument("--audio-backend", default="mock", help="Audio backend name.")
    analyze.add_argument("--vision-backend", default="mock", help="Vision backend name.")
    analyze.add_argument("--out", default=Path("outputs"), type=Path, help="Output root directory.")
    analyze.add_argument("--decision-threshold", default=0.65, type=float, help="Accept threshold.")
    analyze.add_argument("--review-threshold", default=0.50, type=float, help="Review threshold.")
    analyze.set_defaults(handler=_handle_analyze)

    inspect = subparsers.add_parser("inspect", help="Inspect video metadata.")
    inspect.add_argument("input", type=Path, help="Input video path.")
    inspect.set_defaults(handler=_handle_inspect)

    doctor = subparsers.add_parser("doctor", help="Check ffmpeg, Python, and CPU/GPU status.")
    doctor.add_argument("--device", default="auto", choices=SUPPORTED_DEVICES, help="Device mode to validate.")
    doctor.set_defaults(handler=_handle_doctor)

    export = subparsers.add_parser("export", help="Export SRT from a JSON result report.")
    export.add_argument("report", type=Path, help="Pipeline results.json file.")
    export.add_argument("--format", default="srt", choices=("srt",), help="Export format.")
    export.add_argument("--lang", default="en", choices=SUPPORTED_LANGUAGES, help="Caption label language.")
    export.add_argument("--out", type=Path, default=None, help="Output SRT path.")
    export.set_defaults(handler=_handle_export)

    web = subparsers.add_parser("web", help="Show how to launch the planned Web UI.")
    web.set_defaults(handler=_handle_web)
    return parser


def _handle_analyze(args: argparse.Namespace) -> int:
    config = PipelineConfig(
        language=args.lang,
        device=args.device,
        audio_backend=args.audio_backend,
        vision_backend=args.vision_backend,
        output_dir=args.out,
        decision_threshold=args.decision_threshold,
        review_threshold=args.review_threshold,
    )
    result = analyze_video(args.input, config)
    accepted = sum(1 for item in result.suggestions if item.accepted)
    review = sum(1 for item in result.suggestions if item.requires_review)
    rejected = len(result.suggestions) - accepted - review

    print("Analysis complete.")
    print(f"Input: {result.input_path}")
    print(f"Output directory: {result.output_dir}")
    print(f"Device used: {result.diagnostics.actual_device}")
    print(f"Events: {len(result.audio_events)} detected, {accepted} accepted, {review} review, {rejected} rejected")
    for name, path in result.files.items():
        print(f"{name}: {path}")
    return 0


def _handle_inspect(args: argparse.Namespace) -> int:
    metadata = inspect_video(args.input)
    print(f"Path: {metadata.path}")
    print(f"Exists: {metadata.exists}")
    print(f"Size: {metadata.size_bytes}")
    print(f"Container: {metadata.container}")
    print(f"Duration: {metadata.duration}")
    print(f"FPS: {metadata.fps}")
    print(f"Resolution: {_format_resolution(metadata.width, metadata.height)}")
    print(f"Has audio: {metadata.has_audio}")
    if metadata.probe_error:
        print(f"Probe warning: {metadata.probe_error}")
    return 0


def _handle_doctor(args: argparse.Namespace) -> int:
    config = PipelineConfig(device=args.device)
    diagnostics = run_diagnostics(config)
    print("Environment diagnostics")
    print(f"Python: {diagnostics.python_version}")
    print(f"ffmpeg: {diagnostics.ffmpeg_path or 'not found'}")
    print(f"ffprobe: {diagnostics.ffprobe_path or 'not found'}")
    print(f"Torch available: {diagnostics.torch_available}")
    print(f"CUDA available: {diagnostics.cuda_available}")
    print(f"Selected device: {diagnostics.selected_device}")
    print(f"Actual device: {diagnostics.actual_device}")
    print(f"GPU: {diagnostics.gpu_name or 'none'}")
    if diagnostics.fallback_reason:
        print(f"Fallback: {diagnostics.fallback_reason}")
    for warning in diagnostics.warnings:
        print(f"Warning: {warning}")
    return 0


def _handle_export(args: argparse.Namespace) -> int:
    output_path = args.out or args.report.with_name(f"captions.{args.lang}.srt")
    written = export_from_report(args.report, output_path, args.lang)
    print(f"Exported {args.format.upper()}: {written}")
    return 0


def _handle_web(args: argparse.Namespace) -> int:
    mockup_path = Path(__file__).resolve().parents[3] / "mockups" / "web-ui.html"
    print("The planned Web UI will use the same core pipeline modules as the CLI.")
    print("Current interactive mockup:")
    print(f"  {mockup_path}")
    print("\nFuture command:")
    print("  streamlit run cc_suggester/ui/streamlit_app.py")
    return 0


def _unknown_command(command: str) -> int:
    suggestion = difflib.get_close_matches(command, COMMANDS, n=1)
    print(f"No such command: {command}", file=sys.stderr)
    if suggestion:
        print(f"Did you mean: {suggestion[0]}?", file=sys.stderr)
    print("\nTry:", file=sys.stderr)
    print("  ccs analyze input.mp4 --device auto --lang hi", file=sys.stderr)
    print("  ccs doctor", file=sys.stderr)
    return 2


def _print_friendly_error(error: CCSuggesterError) -> None:
    print(error.message, file=sys.stderr)
    if error.suggestions:
        print("\nSuggestions:", file=sys.stderr)
        for index, suggestion in enumerate(error.suggestions, start=1):
            print(f"{index}. {suggestion}", file=sys.stderr)
    if error.details:
        print("\nDetails:", file=sys.stderr)
        for key, value in error.details.items():
            print(f"- {key}: {value}", file=sys.stderr)


def _format_resolution(width: int | None, height: int | None) -> str:
    if width is None or height is None:
        return "unknown"
    return f"{width} x {height}"


if __name__ == "__main__":
    raise SystemExit(main())
