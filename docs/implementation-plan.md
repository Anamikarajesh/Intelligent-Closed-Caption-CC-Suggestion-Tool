# Complete Implementation Plan

This document describes how to take the current runnable scaffold to a complete open-source Intelligent Closed Caption Suggestion Tool.

The implementation should continue to follow one rule: the core pipeline owns the product logic, while CLI, Web UI, and future VLC/API integrations remain clients of the same reusable modules.

## Current State

The first scaffold is implemented under `main/`.

Completed:

- Python package structure: `cc_suggester`
- CLI entrypoint: `python -m cc_suggester`
- Shared data models for metadata, diagnostics, audio events, reaction results, caption suggestions, and full pipeline results
- Pipeline configuration and device mode handling
- Environment diagnostics with CPU/GPU reporting
- Friendly CLI errors for wrong commands, missing input files, unavailable CUDA, and unavailable backends
- Mock audio backend for deterministic non-speech event candidates
- DSP audio backend for offline CPU candidate detection from WAV/extracted audio
- Registered placeholder backends with actionable errors for YAMNet, PANNs, AST, BEATs, and CLAP
- Mock visual backend for deterministic reaction scores
- OpenCV visual backend for frame-difference scene reaction scoring
- Registered MediaPipe placeholder with actionable setup guidance
- Event smoothing
- Decision engine with event importance priors and ambient penalties
- Multilingual caption label glossary for English, Hindi, Tamil, Telugu, Bengali, Marathi, and Malayalam
- SRT, JSON, CSV, diagnostics, and config exports
- Streamlit Web UI client that calls the same core pipeline
- CLI commands for full analysis, audio-only detection, metadata inspection, diagnostics, export, label listing, and Web UI launch guidance
- JSON config loading and CLI override merging
- Basic tests for SRT formatting, label lookup, config merging, CLI behavior, and DSP detection
- Interactive HTML Web UI mockup
- Architecture diagrams and CLI examples

The current implementation is still intentionally model-light. It includes a real DSP baseline and OpenCV vision path, but heavyweight pretrained models still need their optional dependencies and model-loading code.

## Target Final Outcome

The final project should:

- Accept raw video files through CLI and Web UI.
- Extract audio reliably.
- Detect non-speech sound events with timestamps and confidence scores.
- Analyze event-aligned video frames for speaker or scene reactions.
- Combine audio and visual evidence to decide CC/no-CC.
- Avoid over-captioning routine ambient sounds.
- Generate multilingual non-speech caption labels.
- Export accepted captions to SRT.
- Export JSON/CSV debug reports for all candidates.
- Provide editor review, edit, accept, reject, and export workflows in the Web UI.
- Run on CPU by default and use GPU when available.
- Provide clear diagnostics and recovery suggestions.
- Remain modular enough to add better audio/vision backends later.

## Phase 1: Real Media Handling

Goal: make video ingestion robust enough for real sample files.

Status: partially implemented.

Tasks:

- Add stricter video validation in `core/media.py`. Done.
- Require valid video input for real backends unless `--allow-demo-input` is explicitly passed. Done.
- Use `ffprobe` metadata for duration, FPS, resolution, codecs, and audio stream checks. Done when ffprobe is available.
- Use `audio/extractor.py` to extract mono 16 kHz WAV files into the run directory. Done for the DSP backend when input is a video.
- Add clear errors for missing audio streams, unsupported files, and ffmpeg failures. Done.
- Save extracted audio path in debug output. Done for DSP events/artifacts.
- Add small test fixtures or generated synthetic media for integration tests. Done with `scripts/generate_sample_video.py`; tests skip when ffmpeg is unavailable.

Acceptance checks:

- `ccs inspect sample.mp4` reports metadata.
- `ccs analyze sample.mp4 --audio-backend mock --vision-backend mock` writes outputs.
- Missing audio produces a friendly actionable error.
- Invalid file type does not silently proceed as a video.

Verification commands:

```bash
python -m cc_suggester inspect sample.mp4
python -m cc_suggester analyze sample.mp4 --lang hi --device auto --out outputs/
python -m pytest tests
```

## Phase 2: Goal 1 Audio Event Detection

Goal: replace the mock audio detector with a real sound event detection backend.

Recommended first semantic backend: YAMNet.

Status: DSP baseline implemented; YAMNet optional backend implemented and requires TensorFlow/TensorFlow Hub; PANNs/AST/BEATs remain future optional backends.

Tasks:

- Add CPU DSP candidate detection backend. Done.
- Add optional audio dependencies in `requirements-audio.txt`.
- Implement `audio/backends/yamnet.py` behind the existing `AudioBackend` interface. Done.
- Convert video audio to the sample rate expected by the backend. Done through extraction/WAV loading.
- Run frame-level sound classification. Done when TensorFlow Hub dependencies/model are available.
- Map model class names to internal event IDs. Done.
- Add confidence thresholding. Done.
- Add event smoothing and merge adjacent detections. Done through shared post-processing.
- Add ambient event suppression rules. Done through decision penalties.
- Keep raw model class names and scores in debug output. Done.
- Add backend selection through CLI: `--audio-backend yamnet`. Done.

Later audio backends:

- PANNs for stronger pretrained audio tagging and event detection.
- AST or BEATs for transformer-based experiments.
- CLAP for open-vocabulary matching of custom labels.

Acceptance checks:

- Real audio events are detected from a video file.
- Each event has `event_id`, `start_time`, `end_time`, `audio_confidence`, and `raw_class_name`.
- Low-confidence events are filtered.
- Adjacent same-label events are merged.
- JSON output includes raw backend debug details.

Verification commands:

```bash
python -m cc_suggester analyze sample.mp4 --audio-backend yamnet --vision-backend mock --lang en
python -m cc_suggester export outputs/sample/results.json --format srt --lang hi
python -m pytest tests
```

## Phase 3: Goal 2 Visual Reaction Detection

Goal: replace the mock visual backend with a real event-aligned reaction analysis module.

Recommended first backend: OpenCV + MediaPipe.

Status: OpenCV scene-motion baseline implemented; MediaPipe face/pose scoring remains future work.

Tasks:

- Add optional vision dependencies in `requirements-vision.txt`.
- Implement frame extraction in `vision/frame_sampler.py`.
- Sample frames before, during, and after each detected audio event. Done in OpenCV backend.
- Implement OpenCV optical-flow motion spike features. Partially done with frame-difference motion scoring.
- Implement MediaPipe face and pose analysis.
- Estimate reaction signals:
  - head turn
  - body/posture shift
  - facial expression change
  - mouth/eye/brow movement
  - scene-level motion spike
- Convert signals into a normalized `reaction_confidence`.
- Save frame count and signal breakdown in JSON debug output.
- Add backend selection through CLI: `--vision-backend mediapipe`.

Later visual backends:

- MMPose for stronger pose estimation.
- MMAction2 for action recognition.
- Video-language models for optional scene reasoning.

Acceptance checks:

- For each audio event, frames are sampled around the timestamp.
- Each event receives a reaction score.
- JSON includes signal-level explanation.
- Videos with no visible person still produce scene-level motion signals or a graceful low-reaction score.

Verification commands:

```bash
python -m cc_suggester analyze sample.mp4 --audio-backend yamnet --vision-backend mediapipe --lang en
python -m pytest tests
```

## Phase 4: Decision Engine Hardening

Goal: improve CC/no-CC decisions so the tool avoids over-captioning.

Tasks:

- Tune scoring weights using editor feedback.
- Add event-specific thresholds.
- Add duration-based penalties for continuous ambient sounds.
- Add scene-impact bonuses for visible reaction, speech pause, or sudden attention shift.
- Add review-band decisions for borderline events.
- Add explainable reasons for accepted, rejected, and review-needed captions.
- Add unit tests for high-impact, ambient, and borderline event decisions.

Acceptance checks:

- High-impact events such as alarms, sirens, glass breaking, and explosions are usually accepted at high audio confidence.
- Ambient events such as fan noise, continuous traffic, and background chatter are rejected unless there is strong scene impact.
- Borderline cases are marked as review instead of being silently accepted.

Verification commands:

```bash
python -m pytest tests
python -m cc_suggester analyze sample.mp4 --lang hi
```

## Phase 5: Web Editor Review UI

Goal: build a real Web UI that uses the same backend modules as the CLI.

Recommended first implementation: Streamlit.

Status: first Streamlit client implemented; advanced timeline editing is still future work.

Tasks:

- Add `cc_suggester/ui/streamlit_app.py`. Done.
- Add video upload or local video selection. Upload done.
- Add controls for language, device, audio backend, vision backend, and thresholds. Done.
- Add Start Caption button. Done.
- Display generated video preview. Done.
- Show event timeline markers.
- Show review panel with editable caption text. Done.
- Add accept/reject/edit state. Basic state done in UI; exporting edited state still needs hardening.
- Add export buttons for SRT, JSON, and CSV. Done for generated files.
- Add error popups and diagnostics panel. Basic error display done.
- Reuse `core/pipeline.py`; do not duplicate logic in UI. Done.

Acceptance checks:

- A user can select a video, run analysis, review suggestions, edit labels, accept/reject events, and export SRT.
- UI state matches the exported output.
- GPU failure offers retry on CPU.

Verification commands:

```bash
streamlit run cc_suggester/ui/streamlit_app.py
python -m pytest tests
```

## Phase 6: CLI Productization

Goal: make the CLI reliable for contributors, batch processing, and debugging.

Status: partially implemented.

Tasks:

- Add `ccs audio` for audio-only detection. Done.
- Add `ccs vision` for visual scoring from existing audio events.
- Add `ccs labels` to list supported event labels and languages. Done.
- Add config file loading. Done for JSON config.
- Add shell completion if Typer is adopted later.
- Improve command suggestions and examples.
- Add structured exit codes.
- Add more tests around CLI errors and outputs. Partially done.

Acceptance checks:

- Common errors explain what happened and what to run next.
- CLI supports batch-friendly JSON outputs.
- All commands are documented.

Verification commands:

```bash
python -m cc_suggester --help
python -m cc_suggester doctor
python -m cc_suggester analize
python -m pytest tests
```

## Phase 7: Multilingual Label Expansion

Goal: support consistent, editor-friendly labels across Indian languages.

Tasks:

- Move glossary to JSON files under `label_maps/`.
- Add glossary validation tests.
- Add missing common event labels.
- Review initial translations with native speakers or editors.
- Add optional IndicTrans2 fallback for labels not in the curated glossary.
- Add language selection in CLI and Web UI.

Initial languages:

- English
- Hindi
- Tamil
- Telugu
- Bengali
- Marathi
- Malayalam

Later expansion:

- all 22 scheduled Indian languages

Acceptance checks:

- Same event ID exports correct labels in supported languages.
- Unknown labels gracefully fall back to English or normalized event text.
- Glossary changes are testable.

Verification commands:

```bash
python -m cc_suggester export outputs/sample/results.json --format srt --lang ml
python -m pytest tests
```

## Phase 8: Evaluation and Editor Feedback

Goal: measure whether the tool actually reduces editor effort.

Tasks:

- Collect sample Hindi and regional-language videos.
- Create editor review CSV format.
- Collect accepted/rejected/corrected labels from editors.
- Track precision, recall, over-captioning, missed-important-event rate, timestamp quality, and editor correction time.
- Tune thresholds and rules from feedback.
- Add evaluation scripts and reports.

Acceptance checks:

- Evaluation report exists for the sample set.
- Editor acceptance rate is tracked.
- Known false-positive/false-negative patterns are documented.

Verification commands:

```bash
python -m cc_suggester analyze sample.mp4 --out evaluation/runs
```

## Phase 9: Packaging and Distribution

Goal: make the project easy to install and reproduce.

Tasks:

- Finalize `pyproject.toml`.
- Add proper optional dependency groups.
- Add Dockerfile for CPU.
- Add optional GPU Docker notes.
- Add GitHub Actions for tests.
- Add release checklist.
- Add contribution guide and issue templates.

Acceptance checks:

- Fresh clone can run tests.
- Fresh clone can run mock pipeline.
- Optional ML backends are documented separately.
- Docker build works for CPU pipeline.

Verification commands:

```bash
python -m pip install -e .[dev]
python -m pytest tests
python -m cc_suggester doctor
```

## Phase 10: Future Integrations

Goal: extend the tool beyond CLI and Web UI once the core is stable.

Possible extensions:

- Local FastAPI service around `core/pipeline.py`
- VLC plugin that calls the local API or CLI
- Batch processing dashboard
- Editor feedback active-learning loop
- Optional dialogue subtitle integration
- Optional same-language subtitle review workflow
- Model comparison benchmark page

These should remain separate from the core pipeline so the project stays maintainable.

## Suggested Immediate Next Steps

The next implementation sprint should be:

1. Run YAMNet against a real cached/local TensorFlow Hub model and tune label mapping thresholds.
2. Implement MediaPipe face/pose reaction scoring.
3. Add `ccs vision` for visual scoring from existing audio event JSON.
4. Add tests for backend registry errors and decision rules.
5. Add CLI tests for `doctor`, missing input, and backend dependency failures.
6. Harden the Streamlit review/export workflow.

This sequence keeps risk low because the existing mock pipeline continues to work while real media and model backends are added incrementally.

## Definition of Done

The project should be considered complete when:

- Goal 1 works with at least one real audio event detection backend.
- Goal 2 works with at least one real visual reaction backend.
- Goal 3 exports accepted non-speech captions to SRT.
- JSON and CSV reports include all accepted/rejected candidates.
- CLI and Web UI both use the same backend pipeline.
- CPU mode works reliably.
- GPU mode is supported where available and fails clearly where unavailable.
- Initial multilingual label export works.
- Editor feedback has been collected on a sample Hindi/regional-language set.
- README and docs explain installation, usage, troubleshooting, evaluation, and extension points.
