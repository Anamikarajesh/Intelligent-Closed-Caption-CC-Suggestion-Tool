# CLI Command Examples

These examples show the planned CLI experience for the Intelligent Closed Caption Suggestion Tool.

## Full Analysis

```bash
ccs analyze input.mp4 --lang hi --device auto --out outputs/
```

Runs the complete pipeline: audio event detection, visual reaction scoring, caption decision, and SRT/JSON/CSV export.

## Force CPU

```bash
ccs analyze input.mp4 --lang en --device cpu --audio-backend yamnet --vision-backend mediapipe
```

Useful for systems without GPU support or for reproducible CPU-only runs.

## Require GPU

```bash
ccs analyze input.mp4 --lang ta --device cuda
```

Fails with a clear diagnostic if CUDA/GPU is not available, then suggests retrying with CPU.

## Inspect a Video

```bash
ccs inspect input.mp4
```

Shows metadata such as duration, FPS, resolution, codec, audio stream availability, and estimated processing requirements.

## Run Environment Diagnostics

```bash
ccs doctor
```

Checks ffmpeg, Python dependencies, model availability, CPU/GPU status, CUDA availability, and common setup issues.

## Export Another Language

```bash
ccs export outputs/input/results.json --format srt --lang ml
```

Creates a Malayalam SRT from an existing JSON result using the caption label glossary.

## Launch Web UI

```bash
ccs web
```

Starts the editor review interface for selecting a video, running analysis, reviewing suggestions, and exporting SRT files.

## Example Friendly Error

```text
No such command: analize
Did you mean: analyze?

Try:
  ccs analyze input.mp4 --device auto --lang hi
```

## Example GPU Diagnostic

```text
CUDA was requested, but no usable GPU was detected.

Detected:
- torch.cuda.is_available(): false
- CUDA runtime: not found
- NVIDIA driver: not found

Suggestions:
1. Retry on CPU:
   ccs analyze input.mp4 --device cpu

2. Check environment:
   ccs doctor
```
