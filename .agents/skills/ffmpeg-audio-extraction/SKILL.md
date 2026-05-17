---
name: ffmpeg-audio-extraction
description: |
  Extracts audio tracks from video files using ffmpeg with optimal settings.
  Supports format conversion, resampling, and channel mixing.
  Use when extracting audio from video, converting audio formats,
  preparing audio for speech recognition, or processing media files.
compatibility: Requires ffmpeg command-line tool
metadata:
  author: video2doc
  version: "1.0"
---

# FFmpeg Audio Extraction

Extract and convert audio from video files using ffmpeg.

## When to Use

- Extracting audio track from video files
- Converting audio to specific format/sample rate
- Preparing audio for speech recognition (Whisper)
- Processing media files for further analysis

## Prerequisites

Verify ffmpeg installation:

```powershell
ffmpeg -version
```

> **Tip: Getting FFmpeg**
> - **macOS**: `brew install ffmpeg`
> - **Linux**: `apt install ffmpeg` or `dnf install ffmpeg`
> - **Windows**: Download from [BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds/releases), e.g. `ffmpeg-n7.1-latest-win64-gpl-shared-7.1.zip`, extract and add `bin/` to `PATH`
>
> Alternatively, set `FFMPEG_PATH` environment variable to the ffmpeg executable path.

## Common Operations

### Extract Audio (Keep Original Format)

```bash
ffmpeg -i video.mp4 -vn -acodec copy audio.aac
```

Parameters:
- `-vn` - No video
- `-acodec copy` - Copy audio without re-encoding

### Extract for Whisper (Recommended)

Whisper expects 16kHz mono audio:

```bash
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

Parameters:
- `-acodec pcm_s16le` - 16-bit PCM (uncompressed)
- `-ar 16000` - 16kHz sample rate
- `-ac 1` - Mono channel

### Extract to MP3

```bash
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

Parameters:
- `-q:a 2` - Quality level (0-9, lower is better)

### Extract to FLAC (Lossless)

```bash
ffmpeg -i video.mp4 -vn -acodec flac audio.flac
```

## Python Integration

```python
import subprocess
from pathlib import Path

def extract_audio(
    video_path: Path,
    audio_path: Path,
    sample_rate: int = 16000,
    mono: bool = True,
) -> bool:
    """Extract audio from video using ffmpeg."""
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",                      # No video
        "-acodec", "pcm_s16le",     # 16-bit PCM
        "-ar", str(sample_rate),    # Sample rate
        "-ac", "1" if mono else "2", # Channels
        "-y",                       # Overwrite
        str(audio_path),
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    
    return result.returncode == 0
```

## Get Media Information

### Duration

```powershell
ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4
```

### Full Metadata (JSON)

```powershell
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4
```

### Python Helper

```python
import subprocess
import json

def get_video_info(video_path: str) -> dict:
    """Get video metadata using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def get_duration(video_path: str) -> float:
    """Get video duration in seconds."""
    info = get_video_info(video_path)
    return float(info["format"]["duration"])
```

## Batch Processing

### PowerShell - All Videos in Directory

```powershell
Get-ChildItem *.mp4 | ForEach-Object {
    $output = $_.BaseName + ".wav"
    ffmpeg -i $_.FullName -vn -ar 16000 -ac 1 $output
}
```

### Python Batch

```python
from pathlib import Path
import subprocess

def batch_extract(input_dir: Path, output_dir: Path):
    """Extract audio from all videos in directory."""
    output_dir.mkdir(exist_ok=True)
    
    for video in input_dir.glob("*.mp4"):
        audio = output_dir / f"{video.stem}.wav"
        subprocess.run([
            "ffmpeg", "-i", str(video),
            "-vn", "-ar", "16000", "-ac", "1",
            "-y", str(audio)
        ])
```

## Audio Quality Settings

### Sample Rates

| Rate | Use Case |
|------|----------|
| 8000 | Telephone quality |
| 16000 | Speech recognition (Whisper) |
| 22050 | Low-quality music |
| 44100 | CD quality |
| 48000 | Professional audio |

### Bit Depth

| Format | Bits | Use Case |
|--------|------|----------|
| pcm_s16le | 16 | Standard, Whisper compatible |
| pcm_s24le | 24 | High quality |
| pcm_f32le | 32 | Maximum precision |

## Troubleshooting

### No Audio Stream

```
Stream map '0:a' matches no streams
```

Video may not have audio. Check with:
```bash
ffprobe -v error -select_streams a -show_entries stream=codec_type video.mp4
```

### Encoding Errors

If specific codec fails, try:
```bash
ffmpeg -i video.mp4 -vn -acodec aac audio.m4a
```

### Long Videos

For very long videos, consider streaming to temp file:
```python
import tempfile

with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    audio_path = f.name
    extract_audio(video_path, Path(audio_path))
```

## Advanced: Extract Specific Time Range

```bash
# Extract 30 seconds starting at 1:00
ffmpeg -i video.mp4 -ss 00:01:00 -t 30 -vn -ar 16000 -ac 1 clip.wav
```

## Advanced: Multiple Audio Tracks

List tracks:
```bash
ffprobe -v error -select_streams a -show_entries stream=index,codec_name video.mkv
```

Extract specific track:
```bash
ffmpeg -i video.mkv -map 0:a:1 -vn audio_track2.wav
```
