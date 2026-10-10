# Technical Writer — Documentation Patterns

Reference patterns for the technical-writer agent. Load when creating README files,
setting up MkDocs, or scaffolding documentation structure.

## README Template

```markdown
# Project Name

> One-sentence description of what this does and why it matters.

## Objective

<!-- 2-3 sentences: the problem this solves. -->

## Quick Start

<!-- Shortest possible path to working. -->

## Installation

### Prerequisites

- Python 3.11+
- pip / uv

### Instructions

The package is installed via pip:

    pip install project-name

## Usage

### Basic example

### Configuration

| Setting   | Type  | Default | Description                          |
| --------- | ----- | ------- | ------------------------------------ |
| `timeout` | `int` | `5000`  | Request timeout in milliseconds.     |
| `retries` | `int` | `3`     | Number of retry attempts on failure. |

## API Reference

Full API reference is available at [docs link].

## Development

### Tests

    pytest --cov=src --cov-report=xml:coverage.xml

### Linting

    ruff check src/

## License

MIT © [Author]
```

## MkDocs Configuration

```yaml
# mkdocs.yml
site_name: Project Documentation
theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - API Reference: api/
  - Configuration: configuration.md
  - Contributing: contributing.md

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - toc:
      permalink: true
```
