---
name: whisper-transcription
description: |
  Uses OpenAI Whisper for speech-to-text transcription with GPU acceleration.
  Handles model selection, language detection, and timestamp extraction.
  Includes post-processing for hotword correction (fixing misrecognized terms,
  proper nouns, abbreviations, and technical jargon from ASR output).
  Use when transcribing audio/video files, extracting speech from media,
  or performing speech recognition tasks.
compatibility: Requires Python 3.8+, ffmpeg, GPU recommended
metadata:
  author: video2doc
  version: "1.1"
---

# Whisper Transcription

Transcribe audio and video files using OpenAI Whisper with optimal settings.

## When to Use

- User wants to transcribe audio or video files
- Speech-to-text conversion needed
- Extracting dialogue or narration from media
- Creating subtitles or captions

## Installation

```bash
# Via uv (recommended)
uv add openai-whisper

# Via pip
pip install -U openai-whisper
```

**Note**: Ensure CUDA-enabled PyTorch is installed for GPU acceleration.
See [uv-cuda-setup](../uv-cuda-setup/SKILL.md) skill if needed.

## Basic Usage

### Python API

```python
import whisper

# Load model (downloads on first use)
model = whisper.load_model("large-v3", device="cuda")

# Transcribe
result = model.transcribe(
    "audio.wav",
    language="zh",           # or None for auto-detect
    word_timestamps=True,    # enable word-level timing
    verbose=False,
)

# Access results
print(result["text"])           # full transcript
print(result["language"])       # detected language
print(result["segments"])       # timestamped segments
```

### CLI Usage

```bash
whisper audio.mp3 --model large-v3 --language zh --output_format txt
```

## Model Selection

| Model | Parameters | VRAM | Relative Speed | Best For |
|-------|-----------|------|----------------|----------|
| tiny | 39M | ~1GB | ~10x | Testing, quick drafts |
| base | 74M | ~1GB | ~7x | Fast transcription |
| small | 244M | ~2GB | ~4x | Balanced quality/speed |
| medium | 769M | ~5GB | ~2x | Good accuracy |
| large-v3 | 1550M | ~10GB | 1x | Best accuracy |

### Selection Logic

```python
def select_model(vram_gb: float, priority: str = "accuracy") -> str:
    """Select optimal Whisper model based on available VRAM."""
    if priority == "speed":
        if vram_gb >= 2:
            return "small"
        return "tiny"
    
    # Priority: accuracy
    if vram_gb >= 10:
        return "large-v3"
    elif vram_gb >= 5:
        return "medium"
    elif vram_gb >= 2:
        return "small"
    elif vram_gb >= 1:
        return "base"
    return "tiny"
```

## Language Handling

### Supported Languages

Whisper supports 99 languages. Common codes:

| Language | Code | Language | Code |
|----------|------|----------|------|
| Chinese | zh | Japanese | ja |
| English | en | Korean | ko |
| Spanish | es | French | fr |
| German | de | Russian | ru |

### Mixed Language Content

For content with mixed languages (e.g., Chinese with English terms):

```python
# Let Whisper auto-detect - it handles code-switching well
result = model.transcribe("mixed.wav", language=None)
```

Or specify primary language:

```python
# Specify primary language, Whisper still recognizes foreign terms
result = model.transcribe("mixed.wav", language="zh")
```

## Timestamp Options

### Segment-Level (Default)

```python
result = model.transcribe("audio.wav")
for seg in result["segments"]:
    print(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}")
```

### Word-Level

```python
result = model.transcribe("audio.wav", word_timestamps=True)
for seg in result["segments"]:
    for word in seg.get("words", []):
        print(f"[{word['start']:.2f}] {word['word']}")
```

## Audio Preprocessing

Whisper expects:
- Sample rate: 16kHz
- Channels: Mono
- Format: WAV, MP3, FLAC, or any ffmpeg-supported format

### Extract Audio from Video

```bash
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

### Python Audio Loading

```python
import whisper

# Whisper handles format conversion internally via ffmpeg
audio = whisper.load_audio("video.mp4")
```

## GPU Optimization

### Explicit Device Selection

```python
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("large-v3", device=device)
```

### Memory Management

For large files on limited VRAM:

```python
# Use fp16 for memory efficiency (default on CUDA)
result = model.transcribe("long_audio.wav", fp16=True)

# Or process in chunks (handled automatically by Whisper)
```

## Windows-Specific Notes

### Triton Warning

```
UserWarning: Failed to launch Triton kernels...
```

- **Cause**: Triton only supports Linux
- **Impact**: Slightly slower word timestamp alignment
- **Solution**: None needed, transcription quality unaffected

### Model Cache Location

Models are cached at: `~/.cache/whisper/`

To clear corrupted downloads:
```powershell
Remove-Item "$env:USERPROFILE\.cache\whisper\*.pt" -Force
```

## Error Handling

```python
def safe_transcribe(audio_path: str, model_name: str = "medium"):
    """Transcribe with fallback for memory errors."""
    import torch
    import whisper
    
    models = ["large-v3", "medium", "small", "base", "tiny"]
    start_idx = models.index(model_name) if model_name in models else 1
    
    for model_name in models[start_idx:]:
        try:
            model = whisper.load_model(model_name, device="cuda")
            return model.transcribe(audio_path)
        except torch.cuda.OutOfMemoryError:
            print(f"VRAM insufficient for {model_name}, trying smaller...")
            torch.cuda.empty_cache()
    
    # Final fallback: CPU
    model = whisper.load_model("tiny", device="cpu")
    return model.transcribe(audio_path)
```

## Output Formats

Whisper CLI supports multiple output formats:

```bash
whisper audio.mp3 --output_format all
```

Generates:
- `.txt` - Plain text
- `.vtt` - WebVTT subtitles
- `.srt` - SRT subtitles
- `.tsv` - Tab-separated with timestamps
- `.json` - Full result with all metadata

## Post-Processing: Hotword Correction

Whisper transcriptions often contain misrecognized terms, especially for:
- Technical terminology and jargon
- Proper nouns (names, brands, products)
- Abbreviations and acronyms
- Foreign words and loanwords

After transcription, apply hotword correction to fix these errors while preserving the original meaning, tone, and structure.

**When to apply**: After obtaining raw Whisper output, before final document generation.

See [Hotword Correction Reference](references/HOTWORD-CORRECTION.md) for detailed correction guidelines and prompts.
