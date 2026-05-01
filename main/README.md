# cc-suggester

Python implementation for the Intelligent Closed Caption Suggestion Tool.

This package generates meaningful non-speech closed caption suggestions from video. The current implementation is a runnable foundation: it proves the modular pipeline, CLI, diagnostics, decision engine, multilingual labels, and SRT/JSON/CSV export flow before heavy ML backends are added.

## Current Implementation Status

Implemented now:

- `cc_suggester.core`: pipeline orchestration, config, shared data models, diagnostics, media inspection, friendly errors
- `cc_suggester.audio`: audio backend interface, deterministic mock backend, event smoothing, ffmpeg extraction helper
- `cc_suggester.vision`: vision backend interface, deterministic mock backend, frame-sampling and reaction helper placeholders
- `cc_suggester.decision`: scoring rules, ambient penalties, multilingual caption glossary
- `cc_suggester.output`: SRT, JSON, and CSV writers
- `cc_suggester.cli`: `analyze`, `inspect`, `doctor`, `export`, and `web` commands
- `tests`: basic tests for SRT output and label lookup

Not implemented yet:

- Real YAMNet/PANNs/AST/BEATs audio backend
- Real OpenCV/MediaPipe visual reaction backend
- Streamlit Web UI connected to the pipeline
- Real evaluation dataset and editor feedback loop
- Docker and VLC integration

The full roadmap is documented in [`../docs/implementation-plan.md`](../docs/implementation-plan.md).

## Setup

The current scaffold uses only the Python standard library for the core pipeline.

```bash
cd main
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For development tests:

```bash
pip install -r requirements-dev.txt
```

For the future Web UI:

```bash
pip install -r requirements-ui.txt
```

## CLI Usage

Run diagnostics:

```bash
python -m cc_suggester doctor
```

Inspect a video:

```bash
python -m cc_suggester inspect path/to/video.mp4
```

Run the current mock pipeline:

```bash
python -m cc_suggester analyze path/to/video.mp4 --lang hi --device auto --out outputs/
```

Export another language from an existing JSON report:

```bash
python -m cc_suggester export outputs/video/results.json --format srt --lang ml
```

Show Web UI guidance:

```bash
python -m cc_suggester web
```

The installed package will expose the same CLI as `ccs`:

```bash
ccs analyze path/to/video.mp4 --lang hi --device auto
```

## Output Files

Each analysis run creates a directory under `outputs/`:

```text
outputs/
  video-name/
    captions.<lang>.srt
    results.json
    events.csv
    diagnostics.json
    config.json
```

`captions.<lang>.srt` contains only accepted captions. `results.json` and `events.csv` include accepted, rejected, and review-needed candidates for debugging and editor review.

## Backend Strategy

Backends are intentionally pluggable.

Audio backends implement:

```text
detect(video_path, metadata, config) -> list[AudioEventCandidate]
```

Vision backends implement:

```text
analyze(video_path, metadata, audio_events, config) -> list[ReactionResult]
```

The first real audio backend should be YAMNet. The first real visual backend should be OpenCV + MediaPipe. The mock backends should remain available for tests and demos.

## Verification

Run syntax checks:

```bash
python -m compileall cc_suggester
```

Run tests:

```bash
python -m pytest tests
```

Run CLI smoke checks:

```bash
python -m cc_suggester doctor
python -m cc_suggester analize
python -m cc_suggester analyze README.md --lang hi --device auto --out outputs
python -m cc_suggester export outputs/README/results.json --format srt --lang ml --out outputs/README/captions.ml.srt
```

The `analize` command is intentionally useful as a smoke check for friendly typo suggestions.

## Immediate Next Sprint

1. Add strict real-video validation.
2. Extract mono 16 kHz WAV audio into each run directory.
3. Add `requirements-audio.txt`.
4. Implement `audio/backends/yamnet.py`.
5. Add decision-rule and CLI tests.
6. Add a small synthetic/sample video fixture for integration tests.

After that, implement the MediaPipe visual backend and connect the Streamlit Web UI to `core/pipeline.py`.
