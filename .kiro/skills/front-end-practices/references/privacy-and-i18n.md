# Privacy and Internationalization

This file defines the privacy and internationalisation rules of the front-end practices
skill. It covers consent for non-essential cookies, the visibility of the privacy
policy, data minimisation and erasure, cross-site cookies, locale-aware formatting of
numbers, currencies, and plurals, text expansion in layouts, culturally neutral imagery,
and hreflang annotations for multilingual sites. It is the reference that the skill
loads when it checks these rules in a codebase and when it proposes fixes for them.

## Rule index

| Rule                | Priority | Difficulty   | Rule statement                                                                      |
| ------------------- | -------- | ------------ | ----------------------------------------------------------------------------------- |
| cookie-consent      | high     | intermediate | Non-essential cookies and trackers wait for a recorded and revocable opt-in.        |
| privacy-policy      | high     | beginner     | A privacy policy is reachable from every page through a clearly labelled link.      |
| currency-formatting | medium   | beginner     | Numbers, currencies, and dates are formatted with Intl APIs and an explicit locale. |
| data-minimisation   | medium   | intermediate | Personal data is collected and stored only where a documented feature consumes it.  |
| hreflang            | medium   | intermediate | Multilingual pages declare reciprocal hreflang alternates with a self-reference.    |
| pluralization       | medium   | intermediate | Count-dependent text uses the plural categories defined for each target locale.     |
| right-to-erasure    | medium   | intermediate | Users can request deletion, which clears local data and triggers server deletion.   |
| text-expansion      | medium   | intermediate | Components holding translated text tolerate longer strings without clipping.        |
| third-party-cookies | medium   | intermediate | Cross-site cookies from external domains are avoided or gated behind consent.       |
| locale-images       | low      | beginner     | Culturally specific imagery has neutral defaults and locale overrides where needed. |

## Consent and privacy notices

### Cookie consent notice

Non-essential cookies and trackers are set only after the user has given specific,
informed, and freely given consent, and the user can withdraw that consent later.

Check:

- Analytics, advertising, or social scripts execute before a consent choice is recorded.
- The banner offers only an acceptance control, or categories are pre-selected.
- No persistent settings entry point remains after the banner has been dismissed.

Fix:

- Block each non-essential tag until its category is granted, and initialise it only
  after the grant is recorded.
- Present accept and reject controls with equal prominence, plus a granular view.
- Add a persistent "Cookie settings" link in the footer, and store the decision with a
  version identifier so that a changed purpose triggers a new prompt.

```javascript
function applyConsent(choice) {
  // Load analytics only after an explicit grant for that category.
  if (choice.analytics === true) {
    loadTag("analytics");
  }
}
```

### Privacy policy link

A published privacy policy is reachable from every page through a clearly labelled link,
usually in the footer, and the document describes the data practices actually in use.

Check:

- A page template, including error pages, lacks a privacy policy link in the footer.
- The link text is vague, such as "Legal", or it is hidden behind a menu.
- The policy omits retention periods, recipients of data, or contact details.

Fix:

- Add a footer link in the shared layout, labelled with the localised equivalent of
  "Privacy Policy".
- Cover the collected fields, the purposes, the recipients, the retention periods, and
  the rights available to users.
- Compare the policy with the analytics, logging, and monitoring setup in production.

### Third-party cookies

Cross-site cookies set by external domains are avoided where a first-party or
privacy-preserving alternative exists, and any that remain are gated behind consent.

Check:

- Set-Cookie responses from other domains appear in the Network panel for page loads.
- Embedded videos, maps, or social widgets set tracking cookies by default.
- Tracking pixels or advertising tags load without a consent gate.

Fix:

- Replace third-party analytics with first-party or privacy-preserving analytics, or
  load remaining tags only through a consent-aware container.
- Use the privacy-enhanced variant of an embed where the provider offers one.
- Set Secure, HttpOnly, and SameSite attributes on first-party cookies.

```http
Set-Cookie: session=<opaque>; Secure; HttpOnly; SameSite=Lax
```

## Data handling

### Data minimisation

Each personal data field, storage key, analytics property, and API payload is collected
only when a documented feature consumes it.

Check:

- Form fields are submitted to the API but never read by a handler.
- Client storage holds a whole user object where an identifier would suffice.
- Analytics or log payloads contain raw email addresses, names, or full query strings.

Fix:

- Remove unused fields from the form and from the request body.
- Store an opaque identifier on the client and fetch details from the server when
  needed.
- Replace personal identifiers in analytics and logs with pseudonymous identifiers, and
  record the retention period for each stream.

### Right to erasure

Users can request deletion of their personal data from an account or privacy area, and
the request clears client-side data and starts a server-side deletion workflow.

Check:

- Account or privacy settings contain no deletion path.
- The deletion action clears the server record but leaves local storage, IndexedDB, or
  cookies populated.
- The user receives no confirmation or no statement of the timeline.

Fix:

- Place the deletion action behind a confirmation dialog that is keyboard accessible.
- Clear local storage, IndexedDB databases, and application cookies alongside the server
  request.
- Queue the server-side deletion, including downstream processors, and state the
  timeline. Article 12(3) of the GDPR generally requires a response within one month,
  unless the period is extended.

```javascript
localStorage.clear();
sessionStorage.clear();
await fetch("/api/account/erasure", { method: "POST" });
```

## Localised formatting

### Currency and number formatting

Numbers, currency amounts, percentages, and dates are rendered through the Intl APIs
with an explicit locale, rather than through hard-coded symbols, separators, or the
runtime default locale.

Check:

- Currency symbols, comma-insertion regular expressions, or toFixed output reach users.
- Intl.NumberFormat or Intl.DateTimeFormat is called without a locale argument, which
  can produce a mismatch between server and client rendering.
- Localised strings are sorted with plain comparison instead of Intl.Collator.

Fix:

- Replace manual formatting with Intl.NumberFormat using the currency style, and with
  Intl.DateTimeFormat, passing the user locale in every call.
- Cache formatter instances per locale and currency for list views.
- Use Intl.Collator for locale-aware ordering, with a defined fallback locale.

```javascript
const fmt = new Intl.NumberFormat(locale, { style: "currency", currency });
const label = fmt.format(1234.5);
```

### Pluralization

Text that depends on a count is selected from plural variants defined for the target
locale, using the CLDR plural categories rather than a binary singular and plural
choice.

Check:

- A count is concatenated with a noun in a string built in code.
- A ternary chooses only between a singular and a plural form.
- Locale files lack plural categories that the target language requires.

Fix:

- Select the variant with ICU MessageFormat plural syntax or with Intl.PluralRules.
- Define every category the locale needs; Arabic, for example, uses six.
- Add a CI check that compares plural keys across all locale files.

```text
{count, plural, one {# item} other {# items}}
```

## Localised content and layout

### Text expansion tolerance

Components that render translated text grow with longer strings, so that translated
labels do not overflow, clip, or truncate in ways that hide their meaning.

Check:

- Buttons, labels, navigation items, or headings with translated text declare a fixed
  inline-size or width.
- Elements with translated text use overflow hidden, nowrap, or ellipsis on content that
  must stay readable.
- No pseudo-locale or long-string test runs in review or in CI.

Fix:

- Replace fixed widths with min-inline-size and allow wrapping where the design permits.
- Use logical properties, so that layouts also hold in right-to-left locales.
- Add a pseudo-locale snapshot test that lengthens strings by roughly 30 to 40 percent.

```css
.button {
  min-inline-size: 7.5rem;
  padding-inline: 1rem;
}
```

### Locale-neutral imagery

Illustrations, icons, and gestures that carry different meanings across cultures use
neutral alternatives by default, and locale-specific variants are added only where the
meaning genuinely differs.

Check:

- Hand gestures, animal or religious imagery, or colour-coded status symbols appear in
  shared assets.
- Flags are used to represent languages in a language switcher.
- Text is baked into raster images, where it cannot be translated or resized.

Fix:

- Replace culture-specific icons with abstract or widely understood symbols.
- Use a locale-keyed lookup with a neutral default for images that must vary.
- Render text as HTML, or as SVG text supplied by the caller, and label language
  switchers with language names written in their own script.

## Multilingual discovery

### Hreflang annotations

Multilingual pages declare their language and regional alternates with hreflang
annotations that are reciprocal, include a self-reference, and provide an x-default.

Check:

- Multilingual pages carry no alternate links, or their links are not reciprocal.
- A page omits its own hreflang entry, or a language selector page omits x-default.
- Codes are invalid, such as a language name in place of an ISO 639-1 code.

Fix:

- Emit alternates for every language variant, including the page itself, in the head or
  in an XML sitemap.
- Use ISO 639-1 language codes with an optional ISO 3166-1 region code, and point
  x-default at the fallback page.
- Verify the rendered HTML or sitemap and the HTTP response, not only the source
  template.

```html
<link rel="alternate" hreflang="en-GB" href="https://example.com/en-gb/about" />
<link rel="alternate" hreflang="x-default" href="https://example.com/about" />
```
