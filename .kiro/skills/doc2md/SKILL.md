---
name: doc2md
description: >
  Convert documents (docx, pdf, pptx, xlsx, html, images) and audio recordings to
  Markdown with the doc2md CLI. Triggers: 'convert to markdown', 'docx to md', 'pdf to
  markdown', 'transcribe audio', 'extract text from document', 'doc2md'. Not for writing
  or editing documentation (use technical-writer) or for fetching Jira content (use
  jira).
---

# Document to Markdown

Wraps the `references/doc2md` CLI: documents go through MarkItDown, audio through
faster-whisper. Input directory structure is preserved under the output directory.

## Usage

```bash
export WORK_AGENTS_CONFIG="<repo>/config.toml"
uv run --project <repo>/.kiro/skills/doc2md/references/doc2md doc2md \
  <abs-input-file-or-dir> -o <repo>/tmp/converted
```

- Use absolute paths; relative ones break if the working directory has changed.
- `-e "<glob>"` excludes patterns; `-v` enables debug logging.
- Audio needs a GPU or patience: on CPU it is 10-50x slower. For long recordings warn
  the user, or pass `--whisper-device cpu --whisper-beam-size 1` (faster, lower
  quality). `--whisper-language <code>` skips language auto-detection.
- Images with no extractable text are copied as-is; PowerPoint images are extracted next
  to the Markdown.
- Report the output paths and any file the tool skipped or failed on; if the environment
  is missing or broken, say so and stop rather than installing anything.

Full options and supported formats: `references/doc2md/README.md` or `--help`.
