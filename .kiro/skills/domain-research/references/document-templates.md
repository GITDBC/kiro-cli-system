# Document Type Templates

Section outlines for the four recurring document types, plus the diagram conventions
that apply to them. Load the entry for the document type being written. The README and
MkDocs templates live in `technical-writer-patterns.md` alongside the report-structure
and citation guidance.

## Pipeline Documentation

1. **Objective** — What the pipeline does and why it exists
2. **Inputs** — Table: File, Origin, Description, Used in Steps
3. **User Settings** — Configurable parameters
4. **Outputs** — Table: File, Origin, Description, Used in Steps
5. **Steps** — Each step: Purpose, Inputs, Outputs, Main Classes, Functionality,
   Considerations
6. **Dependencies** — Grouped by purpose (core, dev, testing)

## Test Documentation

1. **Overview** — What is being tested and why
2. **Test Data** — Data sources and preparation
3. **Configuration** — Test environment setup
4. **Test Classes** — Grouped by category; format: `test_method_name()`: description
5. **Considerations** — Execution times, data strategy, known limitations

## Configuration Documentation

- Table: Setting, Type, Default Value, Comment
- Descriptions grouped by category; include validation rules and parameter interactions

## Dependency Documentation

- Group by purpose (core, dev, testing); table: Library, Version; include install
  instructions

## Diagrams in These Documents

- Vertical nodes in execution order
- Show execution flow, step dependencies, classes and outputs

Mermaid syntax rules and per-type legends are in the `mermaid-diagrams` skill.
