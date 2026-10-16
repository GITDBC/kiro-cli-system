# Jirafetcher

Fetch, transition, and comment on Jira tickets and their subtasks. Exports grouped
Markdown files ready for LLM processing.

## Requirements

- Python 3.13 and [uv](https://docs.astral.sh/uv/)
- A Jira instance with REST API v2 access
- A Personal Access Token (PAT) or API token

Set up with `make setup` inside `tools/jirafetcher`.

## Configuration

Create a `config.json` file in the project root (already in `.gitignore`):

```json
{
  "token": "your-jira-personal-access-token",
  "statuses": ["In Review", "On Hold", "In Progress"],
  "title_filter": "[MyProject]"
}
```

`token` is required (Jira PAT or API token, sent as a Bearer token). `statuses` defaults
to `In Review` and `On Hold`; `title_filter` is an optional case-insensitive substring
of the issue summary.

When `config.json` does not exist, the `[jirafetcher]` section of the TOML file that
`WORK_AGENTS_CONFIG` points to supplies the same fields (see `config.toml.example`). The
JSON file wins when both are present. A malformed TOML file exits 1 with a message.

## Usage

The CLI uses subcommands: `fetch`, `transition`, and `comment`. The commands below
assume the tool environment is active; from the repository root, prefix each with
`uv run --project tools/jirafetcher`.

### Fetch subtasks to Markdown

```bash
# Basic usage — uses config.json defaults
jirafetcher fetch "https://jira.example.com/browse/PROJ-123"

# Override statuses from CLI
jirafetcher fetch "https://jira.example.com/browse/PROJ-123" -s "In Review" "In Progress"

# Override title filter
jirafetcher fetch "https://jira.example.com/browse/PROJ-123" -t "[MyProject]"

# Custom output directory and config file
jirafetcher fetch "https://jira.example.com/browse/PROJ-123" -o my_output/ -c my_config.json

# Preview without writing files
jirafetcher fetch "https://jira.example.com/browse/PROJ-123" --dry-run

# Fetch the ticket itself (not subtasks)
jirafetcher fetch "https://jira.example.com/browse/PROJ-123" --self
```

### Transition subtasks to a new status

```bash
# Move "In Review" subtasks to "Done"
jirafetcher transition "https://jira.example.com/browse/PROJ-123" "Done" -s "In Review"

# Transition with a comment
jirafetcher transition "https://jira.example.com/browse/PROJ-123" "Done" \
  -s "In Review" -m "Reviewed and approved"

# Dry-run to preview changes
jirafetcher transition "https://jira.example.com/browse/PROJ-123" "Done" --dry-run

# Transition the ticket itself
jirafetcher transition "https://jira.example.com/browse/PROJ-123" "Done" --self
```

### Add comments to tickets

```bash
# Comment on all "On Hold" subtasks
jirafetcher comment "https://jira.example.com/browse/PROJ-123" \
  "Waiting for external dependency" -s "On Hold"

# Dry-run
jirafetcher comment "https://jira.example.com/browse/PROJ-123" "Update" --dry-run

# Comment directly on the ticket (not its subtasks)
jirafetcher comment "https://jira.example.com/browse/PROJ-123" "Status update" --self

# Read comment from a file
jirafetcher comment "https://jira.example.com/browse/PROJ-123" -f comment.txt --self

# Read comment from stdin
echo "Automated comment" | jirafetcher comment "https://jira.example.com/browse/PROJ-123" --self

# Comment on subtasks AND the parent ticket
jirafetcher comment "https://jira.example.com/browse/PROJ-123" "Update for all" --include-parent
```

### Common options (all subcommands)

| Option                 | Description                                |
| ---------------------- | ------------------------------------------ |
| `url`                  | Jira story URL (positional, required)      |
| `-s`, `--statuses`     | Filter subtasks by status                  |
| `-t`, `--title-filter` | Filter subtasks by title substring         |
| `-c`, `--config`       | Config file path (default: `config.json`)  |
| `-v`, `--verbose`      | Enable debug logging                       |
| `-n`, `--dry-run`      | Preview without applying changes           |
| `--self`               | Operate on the ticket itself, not subtasks |
| `--include-parent`     | Include parent ticket with subtasks        |

### Fetch-specific options

| Option               | Description                           |
| -------------------- | ------------------------------------- |
| `-o`, `--output-dir` | Output directory (default: `output/`) |

### Transition-specific options

| Option            | Description                                  |
| ----------------- | -------------------------------------------- |
| `target_status`   | Target status name (positional, e.g. `Done`) |
| `-m`, `--comment` | Add a comment when transitioning             |

### Comment-specific options

| Option         | Description                                                    |
| -------------- | -------------------------------------------------------------- |
| `body`         | Comment text (optional; reads `--file` or piped stdin instead) |
| `-f`, `--file` | Read comment body from a UTF-8 text file                       |

If `body` is omitted and `--file` is not provided, the body is read from stdin. When
stdin is a TTY and no source is given, the command exits with an error.

## Output

The `fetch` subcommand generates one Markdown file per status inside the output
directory:

```
output/
├── in_review.md
├── on_hold.md
└── in_progress.md
```

Each file contains all matching subtasks with their metadata, description, and comments.

## Retry behaviour

The Jira client automatically retries on rate-limiting (HTTP 429) and transient server
errors (502, 503, 504) with exponential backoff, up to 3 attempts.

## Development

Targets (`make lint`, `make code-check`, `make test`, `make all`) come from
[`tools/tool.mk`](../tool.mk); the repository gates (`make lint-jirafetcher`,
`make test-jirafetcher`) are in the root [`Makefile`](../../Makefile). `make test`
enforces an 80% coverage floor.
