# Ousterhout Principles — Red-Flag Checklists

Full red-flag checklists from 'A Philosophy of Software Design' (Ousterhout), used by
Track 1 (structural design) and Track 2 (code-level red flags) of the
`software-design-review` skill. Load when running either track's evaluation.

## Track 1 — Structural design checklist

Evaluate against:

- **Module depth**: deep (simple interface, significant functionality) vs shallow?
  Pass-through methods that add interface complexity without functionality?
- **Information hiding**: each design decision encapsulated in one module? Information
  leakage across modules? Temporal decomposition (structured by execution order rather
  than knowledge domain)?
- **Abstraction quality**: right level (not too general, not too specific)?
  Specialization cleanly separated from general-purpose code?

Output: findings table `| Location | Principle violated | Severity | Suggestion |`

## Track 2 — Code-level red flags

Scan for (Ousterhout red flags):

- **Information Leakage**: design decision reflected in multiple modules.
- **Pass-Through Method**: does almost nothing except pass arguments to another method
  with similar signature.
- **Repetition**: nontrivial code repeated.
- **Special-Purpose Code in General-Purpose Mechanism**: general mechanism contains
  case-specific code.
- **Conjoined Methods**: understanding one requires understanding the other.
- **Vague Name**: name doesn't convey useful information.
- **Hard to Pick Name**: difficulty naming an entity (suggests poor design).
- **Hard to Describe**: documentation must be long to be complete (design too complex).
- **Nonobvious Code**: behavior can't be understood with a quick reading.

Also evaluate: Can any exceptions be eliminated by redesigning the interface? Are
comments compensating for poor design rather than capturing intent?

Output: findings table `| Location | Red flag | Severity | Suggestion |`

## Dependency taxonomy for testing deepened modules

When Track 1 recommends deepening a shallow module cluster, classify each dependency
crossing the new module's boundary to decide how the seam is tested. Adapted from
mattpocock/skills (MIT).

| Category            | Description                                                                               | Testing approach                                                                                                                                                           |
| ------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| In-process          | Pure computation, in-memory state, no I/O                                                 | Always deepenable: merge the modules and test through the new interface directly, no adapter needed                                                                        |
| Local-substitutable | Dependency has a local test stand-in (e.g. an in-memory filesystem, an embedded database) | Deepenable if the stand-in exists; test with the stand-in in the suite, seam stays internal                                                                                |
| Ports-and-adapters  | Own services across a network boundary (internal microservices, internal APIs)            | Define a port at the seam; the deep module owns the logic, the transport is an injected adapter — an in-memory adapter for tests, an HTTP/gRPC/queue adapter in production |
| True external       | Third-party services outside the team's control (payment processors, messaging providers) | Inject the dependency as a port; tests provide a mock adapter                                                                                                              |

A port is only justified once at least two adapters exist (typically production and
test) — a single-adapter seam is indirection, not a real boundary.
