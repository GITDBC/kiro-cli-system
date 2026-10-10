# Finding Calibration Reference

Load this file when writing a findings table, and always when the review is one section
of a parallel multi-reviewer run. Its purpose is that two reviewers in isolated contexts
assign the same severity and effort to the same defect. In a large-scale multi-section
parallel review they did not: identical "silent numeric corruption reaches a downstream
consumer" defects were rated `High` in one section and `Medium` in three others, and
four different effort vocabularies appeared across eight comparable notes.

## Severity anchors

Severity describes **consequence if the defect executes in production**, never the
reviewer's confidence or the category of the code involved.

| Severity   | Anchor                                                                                                                                       | Real example                                                                                                 |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `Critical` | Data loss, security vulnerability, credential exposure, or a crash on the normal path                                                        | Unclosed handle corrupting a written parquet partition; secret logged at debug level                         |
| `High`     | **Silent incorrect output reaching a production consumer** — `inf`, `NaN`, a wrong value, or dropped rows, with no exception and no log line | Unguarded division feeding a capacity-planning multiplier; `inner` join silently dropping rows on a KPI path |
| `Medium`   | Robustness gap needing an unusual or edge-case input to trigger; or a documented-behaviour mismatch with real confusion risk                 | Missing validation on an optional parameter that is always set today                                         |
| `Low`      | Style, naming, or a documentation nit with no behavioural ambiguity                                                                          | Non-descriptive local variable name; a docstring missing an `Examples` section                               |

The `High` anchor is the one that drifts. Apply this test: **can the wrong value reach a
consumer without anything in the logs saying so?** If yes, it is `High`, whether the
reviewer frames it as a "bug" or a "robustness gap", and whether the fix is one line or
fifty. Category instinct (`Bug` > `Robustness` > `Docs`) is not a severity input.

## Effort anchors

Effort is the size of the **corrective diff**, not the difficulty of understanding the
code.

| Effort | Diff size          | Shape                                                      |
| ------ | ------------------ | ---------------------------------------------------------- |
| `XS`   | ≤ 3 changed lines  | Add a guard, fix a log level, rename a variable            |
| `S`    | ≤ 15 changed lines | Add a validation block, wrap a call in `try/except`        |
| `M`    | ≤ 40 changed lines | Extract a helper, add row-count telemetry to a merge class |
| `L`    | > 40 changed lines | Restructure a class, introduce a new module                |

Forbidden effort values: literal line counts (`"~15 lines"`), and the words
`Low`/`Medium`/`High` — those belong to the severity column and reusing them there made
one real note unsortable against its siblings.

## Value vocabulary (frozen)

| Column      | Allowed values                                                                             |
| ----------- | ------------------------------------------------------------------------------------------ |
| `ID`        | `F1`, `F2`, … contiguous, no gaps                                                          |
| `File:Line` | `path/to/file.py:142` or `path/to/file.py:142-158` — mandatory, no exceptions              |
| `Category`  | `Bug`, `Robustness`, `Security`, `Performance`, `Standards`, `Simplify`, `Docs`, `Clarity` |
| `Severity`  | `Critical`, `High`, `Medium`, `Low` — Title Case only                                      |
| `Effort`    | `XS`, `S`, `M`, `L` — upper case only                                                      |

Lower-case severity values (`high`, `medium`) appeared in two of eight real notes and
break programmatic merging of parallel sections. They are invalid.

Append a provenance tag to the `Category` cell so a consolidator can separate enforced
rules from taste without reading the detail section:

- `Standards [code-standards: logging]` — violates a documented rule, name the section
- `Clarity [preference]` — reviewer opinion with no rule behind it

A `[preference]` finding may never be rated above `Low`.

## Calibration anchors for parallel runs

When a review fans out to two or more reviewers, the orchestrator MUST paste this block
verbatim into every reviewer's `relevant_context`. Shared anchors, not a shared prose
rubric, are what stopped the drift described above.

```text
Calibration anchors (apply verbatim):
- Unguarded division producing inf/NaN in a value written to output = High, XS
- Inner join dropping rows on a KPI path with no row-count log = High, S
- Missing module docstring = Low, XS
- Method name that reads ambiguously, no rule cited = Low [preference], XS
```

## Self-retraction test

Before emitting a row, answer: _is this worth someone's time to fix?_ If the detail
paragraph would end in "not a defect", "no functional issue found", "optional", or "can
be skipped", **delete the row**. Two independent reviewers in the real run each emitted
a numbered finding and then argued against it in its own detail section, so the mistake
is a template gap rather than one reviewer's lapse. A retracted finding costs every
downstream reader the same attention as a real one and costs the consolidator more,
because it has to be re-read to be dismissed.
