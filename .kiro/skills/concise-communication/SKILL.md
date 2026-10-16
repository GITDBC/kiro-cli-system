---
name: concise-communication
description: >
  On-demand communication patterns for models prone to long replies (claude-opus-5.5):
  banned filler phrases, reference codes for multi-item outputs, and worked do/don't
  examples. Invoke when density matters or a response needs compressing. Not for the
  always-on directives, which live in COMMON.md.
---

# Concise Communication

Opus-class models can over-explain: stacked headers, hedge phrases, restated
conclusions, unearned flattery. Anthropic documents longer default replies, heavier
narration, and longer written documents for Opus 5; the Opus 5.5 guide defers to those
patterns and reports no change, so the premise carries over unmeasured. This skill lists
the concrete banned patterns and the shorthand that keeps output dense. Length,
narration, scope, and correction rules are in the `Communication` section of `COMMON.md`
and are not restated here.

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

## Do this instead

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

This skill governs wording and density only. Structural requirements (executive summary,
sections) follow `COMMON.md` Output Guidelines, which win on any conflict.
