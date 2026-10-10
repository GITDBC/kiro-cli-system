---
name: mermaid-diagrams
description: >
  Mermaid diagram syntax reference. Use when generating architecture diagrams, sequence
  diagrams, ER diagrams, flowcharts, state machines, or any Mermaid code block. Provides
  correct syntax rules, common pitfalls, and patterns for each diagram type. Triggers:
  'mermaid', 'diagram', 'flowchart', 'sequence diagram', 'ER diagram', 'architecture
  diagram', 'state machine'. Not for rendering diagrams to images.
---

# Mermaid Diagram Reference

All diagrams must render correctly in MkDocs Material and GitHub Markdown.

## Critical Syntax Rules

- **Node IDs**: alphanumeric + underscores only. No `@`, `/`, `-`, or leading numbers.
- **Labels**: no `()`, `[]`, `"`, or `/` inside label text. Plain descriptive text only.
- **Edges**: spaces around arrows — `A --> B` not `A-->B`.
- **No custom styling**: no `style`, `classDef`, or CSS. MkDocs Material handles
  theming.
- **Subgraphs**: only when 3+ components need visual clustering.
- **Direction**: declare explicitly — `flowchart TD` or `LR`.

```
❌ DnD[@dnd-kit/core]         → invalid ID (@)
❌ UI[KanbanBoard(React)]     → invalid label (parentheses)
❌ Auth[Auth/Login Service]   → invalid label (slash)
✅ DndKit[dnd-kit core]
✅ Auth[Auth Login Service]
```

## Diagram Type Selection

| Need                                     | Diagram   | Directive              |
| ---------------------------------------- | --------- | ---------------------- |
| Component relationships, system overview | Flowchart | `flowchart TD` or `LR` |
| Multi-step interactions, API calls       | Sequence  | `sequenceDiagram`      |
| Data model, database schema              | ER        | `erDiagram`            |
| Object model, class hierarchy            | Class     | `classDiagram`         |
| State machines, lifecycle                | State     | `stateDiagram-v2`      |

Skip diagrams for trivial changes (single-component, no interactions).

## Per-Type Legends

- **Flowchart** shapes: `[text]` rect · `([text])` rounded · `[(text)]` cylinder/DB ·
  `{text}` diamond · `[[text]]` subroutine. Edges: `-->` solid · `-.->` dotted · `==>`
  thick · `-->|label|` labeled.
- **Sequence**: `->>` request · `-->>` response · `alt`/`else`/`end` conditionals ·
  `loop`/`end` repetition · `activate`/`deactivate` lifelines.
- **ER**: `||` exactly one · `o{` zero or more · `|{` one or more · `o|` zero or one.

A renderable worked example of each of the five types is in
`references/mermaid-examples.md` — load the entry for the type being written.

## Guidelines

- Keep diagrams under 15 nodes — split if larger.
- Use semantic IDs (`AuthSvc` not `A`).
- `TD` for hierarchies, `LR` for pipelines/flows.
- One diagram per concern — don't mix data flow with deployment topology.
- Validate mentally before output: valid IDs? plain label text? edges spaced?
