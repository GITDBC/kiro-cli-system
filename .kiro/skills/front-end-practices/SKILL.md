---
name: front-end-practices
description: >
  Front-end design and engineering practices: checks and fixes for HTML, CSS,
  JavaScript, accessibility, SEO and metadata, performance, images and media, privacy,
  internationalization, security and testing. Use when writing, reviewing or refactoring
  front-end code, templates, styles or client-side scripts, or when a front-end review
  needs prioritised checks. Triggers: 'front-end review', 'accessibility check',
  'performance review', 'SEO check', 'HTML review', 'CSS review', 'frontend checklist'.
  Not for Python code (use code-standards) or for backend security audits (use
  security-audit).
---

# Front-End Practices

A checklist-based skill for front-end work, distilled into one reference per category.
Each rule states what to check and how to fix it; priorities and difficulty levels let a
reviewer order the work.

Start with [review-framework.md](references/review-framework.md) to select the
categories a change touches, then load only the matching category references. Load a
category file only when the change touches it.

## Reference Index

| Reference                                             | Covers                                                          |
| ----------------------------------------------------- | --------------------------------------------------------------- |
| [review-framework.md](references/review-framework.md) | Categories, priorities, difficulty, review workflow, limits     |
| [accessibility.md](references/accessibility.md)       | Alternative text, forms, keyboard, ARIA, contrast, structure    |
| [seo-and-metadata.md](references/seo-and-metadata.md) | Titles, descriptions, canonical URLs, structured data, sitemaps |
| [performance.md](references/performance.md)           | Loading, resource hints, JavaScript cost, rendering, caching    |
| [images-and-media.md](references/images-and-media.md) | Formats, sizing, lazy loading, responsive images, video, audio  |
| [privacy-and-i18n.md](references/privacy-and-i18n.md) | Consent, cookies, data minimisation, locales, plurals, dates    |
| [html.md](references/html.md)                         | Document structure, semantics, forms, links, lists, tables      |
| [css.md](references/css.md)                           | Layout, responsive design, typography, motion, theming          |
| [javascript.md](references/javascript.md)             | Modules, language features, runtime errors, events, linting     |
| [security.md](references/security.md)                 | Transport, headers, cookies, third-party resources, inputs      |
| [testing.md](references/testing.md)                   | Unit, end-to-end and visual regression testing                  |

## Usage

1. Identify the categories the change touches.
2. Load those reference files and apply each rule's Check steps.
3. Fix the findings in priority order (critical first), then re-run the Check steps to
   confirm the fix.
4. Report findings by rule slug, so each one can be traced to its reference section.

## Notes

- Thresholds that a rule presents as heuristics are not published standards. Confirm the
  threshold the project actually enforces before failing a build on it.
- Provenance and the licence of the derived content are in
  [PROVENANCE.md](PROVENANCE.md).
