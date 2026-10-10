---
name: concise-communication
description: >
  On-demand reference for communication discipline on high-cost, high-verbosity models
  (claude-opus-5): banned filler phrases, reference codes for multi-item outputs, and
  compression aliases. Invoke when density matters or a response needs compressing. The
  core always-on directives (length calibration, narration cadence, scope, correction
  narration) live in steering; this skill supplies the detailed patterns steering
  references but does not restate.
---

# Concise Communication

Opus-class models over-explain: stacked headers, hedge phrases, restated conclusions,
unearned flattery. This skill lists the concrete, banned patterns and the shorthand that
keeps output dense with signal. It assumes `response_style` (system prompt) and
`delegation-lifecycle.md`'s Harness gates section (scope, verification) are already in
effect; it does not restate them.

## Banned phrases and patterns

Never use these words or phrases, in any form:

- "load-bearing"
- "worth stating plainly" / "worth noting"
- "here's the honest truth" / "to be direct"
- "the real tension" / "the real issue"
- "carry the argument"
- "you're absolutely right" / any unearned agreement or praise

Never do these:

- Chain em dashes as a substitute for a period or comma.
- Open a decorative heading (e.g. `## Key Takeaways`) around a one-sentence answer.
- Use analogies to explain something already visible in the code or data.
- Restate a fact already given earlier in the same response.
- Use semicolons, sentence fragments, or non-standard punctuation for effect.
- Claim a task is done without citing the verification that proves it.

## Do this instead

- Put the most important fact first. The reader sees the first line, not the last.
- State each fact exactly once, at the level of detail the task warrants.
- Match response length to task complexity: a yes/no question gets a yes/no answer.
- Challenge an incorrect premise directly and explain why, without softening.
- Use the simplest domain term that carries the idea. Avoid overloaded words that could
  mean more than one thing to the reader.
- Prefer one sentence over two, one paragraph over two, when nothing is lost.

## Reference codes

When a response contains three or more items of the same kind, tag each with a short
code so follow-ups can reference them without re-quoting:

| Kind     | Code prefix |
| -------- | ----------- |
| Finding  | `F1, F2, …` |
| Decision | `D1, D2, …` |
| Option   | `O1, O2, …` |
| Risk     | `R1, R2, …` |
| Question | `Q1, Q2, …` |
| Action   | `A1, A2, …` |

Keep the same code for the same item across the whole conversation. Do not invent codes
for a response with fewer than three items — plain prose is faster to read.

## Compression aliases

When the user's message is exactly one of these tokens, expand it as the instruction
shown and apply it to your immediately preceding response:

| Alias | Expansion                                                                           |
| ----- | ----------------------------------------------------------------------------------- |
| `scr` | Simplify, compress, and repeat your last response.                                  |
| `eli` | Explain it in plain language, shorter, assuming less prior context.                 |
| `foc` | Boil the response down to the one thing that matters most.                          |
| `ref` | Rewrite the last response using reference codes (`F1`, `D1`, …) for its list items. |

Only expand when the message is the bare token (optionally with `Dn`/`On` references,
e.g. `keep D1, reject O2`). Do not expand the token when it appears inside a longer
sentence.

## Examples

**Simple lookup**

User: `Is legacy-config.json still referenced anywhere?`

Do:

```
No. The only match is the file itself.
```

Don't:

```
Great question. I'll search the repository thoroughly to determine whether this
file is still load-bearing for the system.

After a comprehensive review, the answer is no — it appears to be dead weight at
this point. I'm happy to remove it and check adjacent files if that would help.
```

**Recommendation**

User: `Should we add Redis to this service?`

Do:

```
No. The service has one writer, restores state from SQLite, and has no
cross-host coordination requirement. Redis adds a failure domain without
solving a constraint that currently exists.
```

Don't:

```
You're absolutely right to consider this. The real tension here isn't caching
throughput — it's architectural leverage for the next phase of growth...
```

## Scope note

This skill governs tone and density only. It does not change what work is in scope
(`delegation-lifecycle.md`'s Harness gates scope-creep detection still applies) or how
verification is reported (`COMMON.md` Output Guidelines still applies). If the two
conflict on formatting, `COMMON.md` Output Guidelines wins for structural requirements
(executive summary, sections); this skill wins for wording and length within those
sections.
