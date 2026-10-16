# Doc2md

Convert documents and audio files to Markdown using
[MarkItDown](https://github.com/microsoft/markitdown) and
[faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Requirements

- Python 3.13 and [uv](https://docs.astral.sh/uv/)
- NVIDIA GPU (optional, for faster audio transcription)

Set up with `make setup` inside `tools/doc2md`.

## Usage

The commands below assume the tool environment is active. From the repository root,
prefix each with `uv run --project tools/doc2md`.

```bash
# Convert a single file
doc2md document.docx

# Convert multiple files
doc2md report.pdf slides.pptx notes.docx

# Convert all files in a directory
doc2md ./documents/

# Custom output directory
doc2md ./documents/ -o converted/

# Exclude patterns
doc2md ./documents/ -e "*.tmp" "*.logger"

# Verbose logging
doc2md ./documents/ -v

# Or run as a module
python -m doc2md.cli ./documents/
```

### CLI Options

| Option                  | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `paths`                 | Files or directories to process (positional)                 |
| `-o`, `--output`        | Output directory (default: `output`)                         |
| `-e`, `--exclude`       | Glob patterns to exclude                                     |
| `-v`, `--verbose`       | Enable debug logging                                         |
| `--whisper-model`       | Model name or path (default: `Systran/faster-whisper-small`) |
| `--whisper-language`    | Language code, e.g. `es` (auto-detect if omitted)            |
| `--whisper-beam-size`   | Beam size (default: `1`)                                     |
| `--whisper-device`      | `auto`, `cpu`, or `cuda` (default: `auto`)                   |
| `--whisper-cpu-threads` | CPU threads (default: `4`)                                   |

### Configuration

When `WORK_AGENTS_CONFIG` points to the repository `config.toml`, the `[doc2md]` section
is read (see `config.toml.example`); the matching `--whisper-*` option takes priority. A
malformed config file exits 1 with a message.

## Supported Formats

Documents are converted via MarkItDown; audio files are transcribed via faster-whisper.

| Category  | Extensions                                                                                 |
| --------- | ------------------------------------------------------------------------------------------ |
| Audio     | `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`                                                    |
| Images    | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.gif`, `.webp`, `.svg`                          |
| Documents | Any format supported by MarkItDown (`.docx`, `.pdf`, `.pptx`, `.xlsx`, `.html`, `.csv`, …) |

Images that produce no text content are copied as-is to the output directory. PowerPoint
files get their embedded images extracted alongside the Markdown.

## Output

The tool preserves the input directory structure inside the output folder:

```
output/
├── report_pdf.md
├── slides_pptx.md
├── slides_images/
│   ├── Picture1.png
│   └── Picture2.png
├── interview_mp3.md
└── subdir/
    └── notes_docx.md
```

## Development

Targets (`make lint`, `make code-check`, `make test`, `make all`) come from
[`tools/tool.mk`](../tool.mk); the repository gates (`make lint-doc2md`,
`make test-doc2md`) are in the root [`Makefile`](../../Makefile). `make test` enforces
an 80% coverage floor.
