#!/usr/bin/env bash
# yt2md — Download YouTube audio and transcribe to Markdown via doc2md (Whisper).
#
# Dependencies (all pip-installable):
#   pip install yt-dlp imageio-ffmpeg
#   + doc2md venv at tools/doc2md/
#
# Usage:
#   ./tools/yt2md.sh <youtube-url> [output-dir]
#
# Example:
#   ./tools/yt2md.sh "https://www.youtube.com/watch?v=VIDEO_ID" tmp/
#
# Note: CPU transcription can take several minutes for long videos.

set -euo pipefail
trap 'echo "[ERROR] Script failed at line $LINENO" >&2' ERR

URL="${1:?Usage: yt2md.sh <youtube-url> [output-dir]}"
OUTDIR="${2:-tmp}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOC2MD_VENV="$PROJECT_ROOT/tools/doc2md/.venv/bin"

# --- Dependency checks ---
command -v yt-dlp >/dev/null 2>&1 || { echo "[ERROR] yt-dlp not found. Install: pip install yt-dlp" >&2; exit 1; }

# --- Input validation ---
[[ "$URL" =~ ^https://(www\.)?(youtube\.com|youtu\.be)/ ]] || { echo "[ERROR] URL must be a YouTube URL (youtube.com or youtu.be)." >&2; exit 1; }
[ -x "$DOC2MD_VENV/python3" ] || { echo "[ERROR] doc2md venv not found at $DOC2MD_VENV." >&2; exit 1; }

# Ensure ffmpeg from imageio-ffmpeg is on PATH
FFMPEG_DIR=$(python3 -c "import imageio_ffmpeg, os; print(os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe()))" 2>/dev/null || true)
[ -n "$FFMPEG_DIR" ] && export PATH="$FFMPEG_DIR:$PATH"

mkdir -p "$OUTDIR"

AUDIO_BASE="$OUTDIR/yt2md_audio_$$"
trap 'rm -f "$AUDIO_BASE".* 2>/dev/null' EXIT

echo "[INFO] Downloading audio from: $URL"
yt-dlp \
  --extract-audio \
  --audio-format mp3 \
  --audio-quality 5 \
  --output "$AUDIO_BASE.%(ext)s" \
  --no-playlist \
  --quiet --progress \
  -- "$URL"

AUDIO_FILE="$AUDIO_BASE.mp3"
if [ ! -f "$AUDIO_FILE" ]; then
  echo "[ERROR] No audio file found after download." >&2
  exit 1
fi
echo "[INFO] Audio saved: $AUDIO_FILE"

echo "[INFO] Transcribing with Whisper via doc2md..."
"$DOC2MD_VENV/python3" -c "
from doc2md.converter import convert_files
from doc2md.types import DEFAULT_WHISPER_ARGS
import sys, pathlib

audio = pathlib.Path(sys.argv[1])
outdir = pathlib.Path(sys.argv[2])
args = dict(DEFAULT_WHISPER_ARGS)
args['device'] = 'cpu'

count = convert_files([audio], outdir, whisper_args=args)
if count == 0:
    print('[ERROR] Transcription produced no output.', file=sys.stderr)
    sys.exit(1)
print(f'[INFO] Transcribed {count} file(s) to {outdir}/')
" "$AUDIO_FILE" "$OUTDIR"

# Show the generated markdown file
MD_FILE=$(find "$OUTDIR" -maxdepth 1 -name '*.md' -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
if [ -n "$MD_FILE" ]; then
  echo "[INFO] Transcript: $MD_FILE"
  echo "[INFO] Size: $(wc -l < "$MD_FILE") lines, $(wc -c < "$MD_FILE") bytes"
fi
