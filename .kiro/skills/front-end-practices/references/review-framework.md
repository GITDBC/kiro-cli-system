# Review Framework

This file is the reference for how to prioritise and structure a front-end review
against the rule corpus held in this skill. It gives the category inventory with rule
counts, the meaning of the priority and difficulty metadata, an ordered review workflow,
and the limits of the checklist. Each rule group is held in a category file under
`references/`, as listed in the table below.

## Categories

Counts are the number of rule sections in each category file. They sum to 386, and each
file's count equals its number of index rows and `###` rule sections.

The total is 386, equal to the upstream published catalogue, and the three authoring
skills (`improve-rule`, `frontend-checklist-global` and `find-npm-packages`) were
excluded.

The upstream README's generated category list also disagrees with its own catalogue for
HTML (25 in the README, 34 in the catalogue) and CSS (32 in the README, 31 in the
catalogue). That disagreement is in the upstream project and was not reconciled here.

| Category                    | Rule count | Reference file      |
| --------------------------- | ---------: | ------------------- |
| Accessibility               |         89 | accessibility.md    |
| SEO                         |         93 | seo-and-metadata.md |
| Performance                 |         43 | performance.md      |
| Images                      |         25 | images-and-media.md |
| Privacy                     |          5 | privacy-and-i18n.md |
| Internationalisation (i18n) |          5 | privacy-and-i18n.md |
| HTML                        |         34 | html.md             |
| CSS                         |         31 | css.md              |
| JavaScript                  |         26 | javascript.md       |
| Security                    |         22 | security.md         |
| Testing                     |         13 | testing.md          |
| Total                       |        386 |                     |

The `meta`, `global` and `content` category values appear only on the three non-rule
skills excluded above and therefore add no rule count.

## Priority and difficulty

Priority has four levels. The upstream legend defines them as follows, paraphrased:
critical marks site-breaking, compliance-sensitive, or security-sensitive issues that
must be fixed first; high marks issues with major impact on user experience,
accessibility, performance, or discoverability; medium marks strong best practices that
belong in normal front-end quality review; low marks useful improvements that are
situational or of lower urgency. In the corpus, 19 rules are critical, 134 high, 208
medium and 25 low.

Difficulty has three levels: beginner, intermediate and advanced. The material read for
this framework does not define them, so their meaning here is an inference: the label
indicates the expertise needed to apply the fix. The corpus holds 134 beginner, 236
intermediate and 16 advanced rules. The priority and difficulty totals above were
checked against the columns of the reference index tables.

The following order is a recommendation of this framework and not a rule of the upstream
checklist. Work the findings by priority first, so that critical items are always
addressed before high items, and by difficulty second, so that beginner items are closed
before intermediate and advanced items within the same priority. A critical advanced
finding therefore takes precedence over a high beginner finding. Beginner items are
placed first within each level because they close quickly and reduce the open list.

## Review workflow

- Scope the change: identify the templates, stylesheets, scripts, media and data access
  that it touches, and whether the review targets a component, a page or a public URL.
- Select categories according to what the change touches. Templates touch HTML and
  accessibility; stylesheets touch CSS and performance; scripts touch JavaScript and
  security; data fetching touches performance and security; images and media touch the
  images category. This mapping is a proposal of this framework.
- Order the selected rules by the priority and difficulty sequence described above.
- For each rule, run the check described in its check prompt and in the automated and
  manual checks of its Verification section.
- Before recording a finding, consult the Exceptions section of the rule, where one
  exists, to exclude valid exceptions and common false positives.
- Apply the fix described in the rule's fix prompt and its code example, adapted to the
  codebase in use.
- Re-run the Verification checks on the changed code and repeat the check that first
  revealed the finding before closing it.

## Scope and limits

The checklist is a set of rules with checks and remediation guidance. It is not a test
suite, and it does not execute the application. A review that finds no issues does not
establish that the application works correctly, and the checks should be complemented by
the project's own automated tests.

Several rules are judgement calls. Their Verification sections include manual checks
that require a browser, assistive technology or visual inspection, and their findings
depend on context. Compatibility notes depend on the browser policy of the repository,
so a rule may be satisfied in one target environment and not in another.

The checklist does not cover back-end logic, infrastructure, product design or the
choice of user interface pattern. Those concerns fall outside its scope and must be
assessed separately.
