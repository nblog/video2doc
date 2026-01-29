"""
video2doc - 视频转 Markdown 文档工具

工作流程:
1. 使用 ffmpeg 从视频提取音频
2. 使用 Whisper 进行语音识别
3. 格式化输出为 Markdown 文档
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import whisper


def extract_audio(video_path: Path, audio_path: Path) -> bool:
    """使用 ffmpeg 从视频中提取音频 (16kHz mono WAV)"""
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",                    # 不要视频
        "-acodec", "pcm_s16le",   # 16-bit PCM
        "-ar", "16000",           # 16kHz (Whisper 要求)
        "-ac", "1",               # mono
        "-y",                     # 覆盖已存在的文件
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[错误] ffmpeg 提取音频失败:\n{result.stderr}", file=sys.stderr)
        return False
    return True


def format_timestamp(seconds: float) -> str:
    """将秒数格式化为 HH:MM:SS"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_duration(seconds: float) -> str:
    """格式化时长为人类可读格式"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    if m > 0:
        return f"{m}分{s}秒"
    return f"{s}秒"


def transcribe_audio(
    audio_path: Path,
    model_name: str = "large-v3",
    language: str | None = None,
) -> dict:
    """使用 Whisper 转录音频"""
    print(f"[信息] 加载 Whisper 模型: {model_name}")
    model = whisper.load_model(model_name)

    print("[信息] 开始转录...")
    result = model.transcribe(
        str(audio_path),
        language=language,
        verbose=False,
        word_timestamps=True,  # 获取词级时间戳
    )
    return result


def generate_markdown(
    result: dict,
    video_path: Path,
    video_duration: float,
) -> str:
    """将转录结果格式化为 Markdown"""
    title = video_path.stem
    detected_language = result.get("language", "unknown")
    segments = result.get("segments", [])

    lines = [
        f"# {title}",
        "",
        f"> 📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 🎬 视频时长: {format_duration(video_duration)}",
        f"> 🌐 检测语言: {detected_language}",
        f"> 🤖 转录模型: Whisper",
        "",
        "---",
        "",
        "## 转录内容",
        "",
    ]

    # 按段落输出，带时间戳
    for seg in segments:
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        lines.append(f"**[{start} → {end}]**")
        lines.append(f"{text}")
        lines.append("")

    # 附录：完整时间轴表格
    lines.extend([
        "---",
        "",
        "## 附录：完整时间轴",
        "",
        "| 时间 | 内容 |",
        "|------|------|",
    ])

    for seg in segments:
        start = format_timestamp(seg["start"])
        text = seg["text"].strip().replace("|", "\\|")  # 转义表格分隔符
        # 截断过长的文本
        if len(text) > 80:
            text = text[:77] + "..."
        lines.append(f"| {start} | {text} |")

    lines.append("")
    return "\n".join(lines)


def get_video_duration(video_path: Path) -> float:
    """获取视频时长（秒）"""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        print(
            f"[警告] 无法解析视频时长，返回 0.0 作为默认值。视频文件: {video_path}",
            file=sys.stderr,
        )
        if result.stdout.strip():
            print(
                f"[警告] ffprobe 标准输出: {result.stdout.strip()}",
                file=sys.stderr,
            )
        if result.stderr.strip():
            print(
                f"[警告] ffprobe 错误输出: {result.stderr.strip()}",
                file=sys.stderr,
            )
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="视频转 Markdown 文档工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "video",
        type=Path,
        help="输入视频文件路径",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="输出 Markdown 文件路径 (默认: 视频同目录同名.md)",
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="large-v3",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help="Whisper 模型 (默认: large-v3)",
    )
    parser.add_argument(
        "-l", "--language",
        type=str,
        default=None,
        help="指定语言代码，如 zh, en (默认: 自动检测)",
    )

    args = parser.parse_args()

    video_path = args.video.resolve()
    if not video_path.exists():
        print(f"[错误] 视频文件不存在: {video_path}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if output_path is None:
        output_path = video_path.with_suffix(".md")
    else:
        output_path = output_path.resolve()

    print(f"[信息] 输入视频: {video_path}")
    print(f"[信息] 输出文档: {output_path}")

    # 获取视频时长
    video_duration = get_video_duration(video_path)
    print(f"[信息] 视频时长: {format_duration(video_duration)}")

    # 提取音频到临时文件
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = Path(tmp.name)

    try:
        print("[步骤 1/3] 提取音频...")
        if not extract_audio(video_path, audio_path):
            sys.exit(1)
        print(f"[信息] 音频已提取: {audio_path}")

        print("[步骤 2/3] 语音转文字...")
        result = transcribe_audio(
            audio_path,
            model_name=args.model,
            language=args.language,
        )

        print("[步骤 3/3] 生成 Markdown...")
        markdown = generate_markdown(result, video_path, video_duration)

        output_path.write_text(markdown, encoding="utf-8")
        print(f"[完成] 文档已保存: {output_path}")

    finally:
        # 清理临时音频文件
        if audio_path.exists():
            audio_path.unlink()


if __name__ == "__main__":
    main()
