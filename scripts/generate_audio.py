#!/usr/bin/env python3
"""
generate_audio.py

Converts a finished Hugo markdown post into a spoken-word MP3 using Piper
(self-hosted, offline neural TTS). Strips markdown syntax down to clean
speakable text, synthesizes with Piper, and drops the MP3 into static/audio/.
Also patches the post's front matter with an `audio:` field pointing at it.

Usage:
    python3 generate_audio.py --post content/blog/2026-07-15-cybernews.md \
        --static-dir static/audio \
        --voice-model /opt/piper-voices/en_US-lessac-medium.onnx

Requires:
    pip install piper-tts
    ffmpeg (for wav -> mp3 conversion)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def strip_markdown_to_speech_text(markdown_text: str) -> str:
    """Turn a Hugo markdown post body into clean, speakable plain text."""
    text = markdown_text

    # Drop the front matter block entirely
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)

    # Convert markdown links [text](url) -> just the text, spoken naturally
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # Drop italic source markers like "— *Help Net Security*" -> ", from Help Net Security"
    text = re.sub(r"—\s*\*(.+?)\*", r", from \1.", text)

    # Strip remaining markdown formatting characters
    text = re.sub(r"[*_`#>]", "", text)

    # Collapse horizontal rules and excess whitespace
    text = re.sub(r"^-{3,}$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"^- ", "", text, flags=re.MULTILINE)

    return text.strip()


def synthesize(text: str, voice_model: Path, out_wav: Path) -> None:
    proc = subprocess.run(
        ["/opt/piper-venv/bin/piper", "--model", str(voice_model), "--output_file", str(out_wav)],
        input=text,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        print(f"Piper failed:\n{proc.stderr}", file=sys.stderr)
        sys.exit(1)


def convert_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    proc = subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
        capture_output=True,
    )
    if proc.returncode != 0:
        print(f"ffmpeg conversion failed:\n{proc.stderr.decode()}", file=sys.stderr)
        sys.exit(1)
    wav_path.unlink()

def patch_front_matter(post_path: Path, audio_relpath: str) -> None:
    """Add a `post_audio:` field to the post's front matter if not already present."""
    text = post_path.read_text(encoding="utf-8")
    if re.search(r"^post_audio:", text, re.MULTILINE):
        text = re.sub(r"^post_audio:.*$", f"post_audio: \"{audio_relpath}\"", text, flags=re.MULTILINE)
    else:
        text = re.sub(r"^(---\n)", f"\\1post_audio: \"{audio_relpath}\"\n", text, count=1)
    post_path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--post", required=True, type=Path, help="Path to the Hugo markdown post")
    parser.add_argument("--static-dir", required=True, type=Path, help="e.g. static/audio")
    parser.add_argument("--voice-model", required=True, type=Path)
    args = parser.parse_args()

    if not args.post.exists():
        print(f"ERROR: {args.post} not found.", file=sys.stderr)
        sys.exit(1)

    args.static_dir.mkdir(parents=True, exist_ok=True)

    slug = args.post.stem  # e.g. "2026-07-15-cybernews"
    wav_path = args.static_dir / f"{slug}.wav"
    mp3_path = args.static_dir / f"{slug}.mp3"

    markdown_text = args.post.read_text(encoding="utf-8")
    speech_text = strip_markdown_to_speech_text(markdown_text)

    synthesize(speech_text, args.voice_model, wav_path)
    convert_to_mp3(wav_path, mp3_path)

    # Hugo serves static/ at site root, so static/audio/x.mp3 -> /audio/x.mp3
    audio_relpath = f"/audio/{slug}.mp3"
    patch_front_matter(args.post, audio_relpath)

    print(f"Wrote {mp3_path}, patched {args.post} with audio field.")


if __name__ == "__main__":
    main()
