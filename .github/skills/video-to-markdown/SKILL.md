---
name: video-to-markdown
description: |
  Converts video files (mp4, mkv, webm, avi) to Markdown documents using speech recognition.
  Extracts audio with ffmpeg, transcribes with OpenAI Whisper, and generates structured Markdown
  with timestamps. Use when user wants to transcribe video, convert video to text, generate
  video transcript, or create documentation from video content.
compatibility: Requires ffmpeg, Python 3.12+, CUDA GPU recommended for faster processing
metadata:
  author: video2doc
  version: "1.0"
---

# Video to Markdown Conversion

Convert video files to structured Markdown documents with timestamps using speech recognition.

## When to Use

- User wants to transcribe a video file
- User needs to convert video content to text documentation
- User wants to create meeting notes from recorded video
- User asks to extract speech/dialogue from video

## Workflow

```
Video (mp4/mkv/webm/avi)
    ↓ [ffmpeg - audio extraction]
Audio (16kHz mono WAV)
    ↓ [Whisper - speech recognition]
Transcription with timestamps
    ↓ [formatting]
Markdown document
```

## Prerequisites

1. **ffmpeg** - For audio extraction
2. **Python 3.12+** with uv package manager
3. **CUDA GPU** (recommended) - For faster transcription
4. **openai-whisper** package

## Step-by-Step Instructions

### 1. Check Environment

```bash
# Verify ffmpeg
ffmpeg -version

# Verify GPU (if available)
nvidia-smi --query-gpu=name,memory.total --format=csv
```

### 2. Setup Project

```bash
# Initialize uv project
uv init --python 3.12

# Install whisper with CUDA support
# Configure pyproject.toml with pytorch-cu126 index
uv add openai-whisper torch
```

See [pyproject.toml template](references/pyproject-template.toml) for CUDA configuration.

### 3. Run Conversion

```bash
uv run python main.py "video.mp4" -l zh -m large-v3
```

### 4. Output Format

The generated Markdown includes:
- Document header with metadata (generation time, duration, language)
- Transcribed content with timestamps `[HH:MM:SS → HH:MM:SS]`
- Timeline table appendix

## Model Selection Guide

| Model | VRAM | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|-----------------|
| tiny | ~1GB | ★★★★★ | ★ | Quick previews |
| base | ~1GB | ★★★★ | ★★ | Draft transcripts |
| small | ~2GB | ★★★ | ★★★ | General use |
| medium | ~5GB | ★★ | ★★★★ | Good quality |
| large-v3 | ~10GB | ★ | ★★★★★ | Best accuracy |

## Language Codes

Common codes for `-l` parameter:
- `zh` - Chinese
- `en` - English
- `ja` - Japanese
- `ko` - Korean
- `auto` - Auto-detect (default)

## Troubleshooting

### CUDA Not Available

If PyTorch shows `CUDA available: False`:

1. Check CUDA installation: `echo $env:CUDA_PATH`
2. Reinstall torch with CUDA index in pyproject.toml
3. Delete `uv.lock` and run `uv sync`

### Triton Warning on Windows

```
UserWarning: Failed to launch Triton kernels...
```

This is expected on Windows. Triton only supports Linux. The warning does not affect transcription quality.

### Model Download Fails

If SHA256 checksum fails:
1. Delete corrupted model: `~/.cache/whisper/<model>.pt`
2. Retry with stable network connection
3. Consider using smaller model first

## Example Output

See [example output](references/example-output.md) for sample Markdown structure.

## CLI Reference

```
usage: main.py [-h] [-o OUTPUT] [-m MODEL] [-l LANGUAGE] video

positional arguments:
  video                 Input video file path

options:
  -o, --output          Output Markdown file path (default: same as video)
  -m, --model           Whisper model (tiny/base/small/medium/large-v3)
  -l, --language        Language code (zh/en/ja/ko or auto)
```
