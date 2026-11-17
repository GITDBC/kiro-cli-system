# HTML

This file describes the HTML rules of the front-end-practices skill. It lists each rule
with its priority, difficulty, and a statement of the requirement, followed by the
checks that verify the requirement and the fixes that resolve a violation. The skill
loads this file as the reference for HTML checks and fixes; the CSS rules are held in
the companion file `css.md`.

## Rule index

| Rule                           | Priority | Difficulty   | Rule statement                                                                        |
| ------------------------------ | -------- | ------------ | ------------------------------------------------------------------------------------- |
| `charset`                      | critical | beginner     | Declare UTF-8 in a meta charset element near the top of the head.                     |
| `doctype`                      | critical | beginner     | Start every document with the HTML5 doctype to force standards mode.                  |
| `viewport`                     | critical | beginner     | Include a viewport meta tag that sets the layout width to device width.               |
| `accessible-notifications`     | high     | intermediate | Announce status messages and alerts through live regions.                             |
| `defer-async`                  | high     | beginner     | Load scripts with defer, async, or type module so parsing is not blocked.             |
| `form-validation`              | high     | intermediate | Attach validation errors to their fields and expose them to assistive technology.     |
| `html5-semantic-elements`      | high     | beginner     | Describe page structure with semantic elements instead of generic containers.         |
| `input-types`                  | high     | beginner     | Use the input type and autocomplete values that match the data collected.             |
| `lang-attribute`               | high     | beginner     | Declare a valid BCP 47 language on the html element.                                  |
| `navigation-landmark`          | high     | beginner     | Wrap navigation in labelled nav elements and provide a skip link.                     |
| `subresource-integrity`        | high     | intermediate | Protect external scripts and stylesheets with integrity hashes.                       |
| `unique-id`                    | high     | beginner     | Ensure every id value occurs only once in the document.                               |
| `video-accessibility`          | high     | intermediate | Provide captions, audio descriptions, and transcripts, and never autoplay with sound. |
| `w3c-compliant`                | high     | beginner     | Validate the markup against the W3C HTML validator and fix errors first.              |
| `webpagetest`                  | high     | intermediate | Measure loading performance from real locations and act on waterfall findings.        |
| `404-page`                     | medium   | beginner     | Serve a helpful custom page with a real 404 status for missing URLs.                  |
| `accessible-tooltips`          | medium   | intermediate | Make tooltips focusable, linked to their trigger, and dismissible with Escape.        |
| `accordion-accessibility`      | medium   | intermediate | Build accordion triggers as buttons that expose expanded state and controls.          |
| `breadcrumb-navigation`        | medium   | beginner     | Mark breadcrumbs as an ordered list in a labelled nav with aria-current.              |
| `carousel-accessibility`       | medium   | advanced     | Give carousels pause controls, keyboard operation, and reduced-motion support.        |
| `clean-up-comments`            | medium   | beginner     | Remove development comments and debug markup before production.                       |
| `custom-element-accessibility` | medium   | advanced     | Expose roles, states, and form participation of custom elements to browsers.          |
| `direction-attribute`          | medium   | intermediate | Set dir for right-to-left content and isolate mixed-direction text.                   |
| `draggable-accessibility`      | medium   | advanced     | Provide keyboard and single-pointer alternatives to every drag operation.             |
| `favicons`                     | medium   | intermediate | Declare the icon formats and sizes that browsers and devices request.                 |
| `file-upload-accessibility`    | medium   | intermediate | Label file inputs, state accepted types, and announce upload feedback.                |
| `link-checker`                 | medium   | beginner     | Verify internal, external, and anchor links with an automated checker.                |
| `noscript-tag`                 | medium   | beginner     | Keep core content in the initial HTML and provide a noscript fallback.                |
| `pagination-accessibility`     | medium   | beginner     | Label pagination as a nav and mark the current page with aria-current.                |
| `search-input`                 | medium   | intermediate | Use a search input inside a search landmark with a visible or programmatic label.     |
| `tabs-accessibility`           | medium   | intermediate | Implement tabs with the tablist, tab, and tabpanel roles and arrow-key movement.      |
| `video-thumbnail`              | medium   | beginner     | Give each video element a poster image and reserved dimensions.                       |
| `web-app-manifest`             | medium   | beginner     | Link a web app manifest that describes name, icons, start URL, and display.           |
| `pwa-installability`           | low      | intermediate | Meet the browser criteria for installing the site as a progressive web app.           |

## Document structure

### Declare the UTF-8 character encoding

The document declares UTF-8 in a meta charset element that appears within the first 1024
bytes, so that all characters are decoded correctly.

Check:

- The charset declaration is present in the head and precedes any non-ASCII text.
- The declared value is UTF-8, and no conflicting charset is set by the server.

Fix:

- Add `<meta charset="UTF-8">` as the first element inside the head.
- Remove or align any charset value sent in the HTTP Content-Type header.

### Use the HTML5 doctype

Every document begins with `<!DOCTYPE html>`, which selects standards mode and prevents
the layout differences of quirks mode.

Check:

- Inspect the raw response rather than the DOM; the first bytes must be the doctype.
- Flag a missing doctype, an HTML 4 or XHTML doctype containing a DTD URL, and any
  whitespace, comment, or byte-order mark placed before the doctype.

Fix:

- Place `<!DOCTYPE html>` on the first line, before the html element.
- In framework projects, edit the root template and confirm the rendered output, because
  the framework may emit its own document wrapper.

### Set a responsive viewport

The head contains a viewport meta tag so that mobile browsers lay out the page at the
device width instead of a desktop width.

Check:

- A viewport meta tag with `width=device-width` is present in the head.
- The content value does not contain `maximum-scale=1` or `user-scalable=no`, which
  block pinch zoom.

Fix:

- Add `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Remove zoom-blocking values so that users can enlarge the page.

### Declare the page language

The html element carries a non-empty lang attribute with a valid BCP 47 tag, which
allows screen readers, translation tools, and hyphenation to select the correct
language.

Check:

- The lang attribute is present on the html element and its value is not empty.
- The value is a language code such as `en`, `en-US`, or `zh-Hant`, not a language name
  such as `english`, and it matches the main content language.
- Passages in another language carry their own lang on the containing element.

Fix:

- Set the code on the html element, for example `<html lang="fr">`.
- Add lang to the block element that contains each passage in a different language.
- Check codes against the IANA Language Subtag Registry.

### Set text direction for right-to-left content

The dir attribute states the reading direction of the page or of a fragment, and bidi
isolation keeps mixed-direction text from reordering neighbouring content.

Check:

- Pages in Arabic, Hebrew, Persian, or Urdu declare dir="rtl" on the html element or on
  the containing element.
- Inline user-generated text that can mix directions is isolated or marked with
  dir="auto".

Fix:

- Set dir on the html element for a page written in a right-to-left language.
- Wrap inline names or snippets that mix directions in a bdi element.

```html
<p>Author: <bdi>محمد</bdi> wrote this.</p>
```

### Keep IDs unique

Each id value occurs once in the document, because labels, ARIA references, and script
lookups resolve to a single element only.

Check:

- Search the rendered HTML for duplicate id values, including those generated by
  component libraries or repeated partials.
- Confirm that every reference in label for, aria-describedby, aria-controls, and
  aria-labelledby resolves to exactly one element.

Fix:

- Rename or remove duplicate ids and update each reference to the intended element.
- Use classes for styling and reserve ids for anchors and references.

### Validate markup against W3C standards

The markup passes the W3C HTML validator, and errors are resolved before warnings
because errors commonly cause rendering and accessibility faults.

Check:

- Run the W3C Nu HTML Checker on the rendered page and record every error.
- Look for unclosed tags, invalid nesting, and missing required attributes.

Fix:

- Resolve errors first, beginning with the earliest one, since later errors often follow
  from it.
- Run an HTML linter such as html-validate in the continuous integration pipeline so
  that regressions fail the build.

### Remove development comments and debug markup

Development notes, debug markup, and temporary placeholders are removed before the
production build, while comments that serve accessibility or legal purposes remain.

Check:

- Search the rendered HTML for TODO, FIXME, and DEBUG notes, commented-out markup, and
  hidden debug elements.
- Review comments for internal hostnames, endpoints, or credentials.

Fix:

- Delete the temporary comments and markup from the templates.
- Configure the build to strip comments and keep only those approved as required.

## Semantic elements and navigation

### Use semantic HTML elements

Page structure is expressed with header, main, nav, section, article, aside, and footer
where these elements describe the content, instead of generic containers.

Check:

- Identify div wrappers that stand in for a landmark or a self-contained article.
- Confirm that the page has one main element.

Fix:

- Replace generic wrappers with the element whose meaning matches the content.
- Keep div for purely presentational grouping where no semantic element fits.

```html
<main>
  <article>
    <h1>Article title</h1>
  </article>
</main>
```

### Mark navigation with landmark regions

Each navigation block is a nav element with an accessible name, so that assistive
technology users can list and distinguish the navigation regions of the page.

Check:

- Each group of navigation links is wrapped in a nav element.
- When several nav elements exist, each has a distinct aria-label or aria-labelledby.

Fix:

- Wrap primary, secondary, and footer link groups in separate nav elements.
- Label each nav, for example "Main" or "Footer", and place a skip link to the main
  content before the other focusable elements.

### Build accessible breadcrumbs

Breadcrumbs form an ordered list inside a labelled nav element, and the current page is
identified with aria-current.

Check:

- The trail is wrapped in a nav with aria-label="Breadcrumb" and built from ol and li
  elements.
- The final item carries aria-current="page".
- Any structured data describes the same trail as the visible breadcrumbs.

Fix:

- Rebuild the trail with the nav, ol, and li structure and add aria-current.
- Generate the structured data from the same source that renders the trail.

### Make pagination accessible

Pagination is a labelled nav, the current page is indicated programmatically, and each
control has an accessible name that includes its visible text.

Check:

- The container is a nav with aria-label="Pagination".
- The current page has aria-current="page", and every control is a link or button that a
  keyboard can reach.
- Accessible names contain the visible text, such as "Next", so that speech input users
  can activate the control by saying the label.

Fix:

- Wrap the controls in a nav element with aria-label="Pagination".
- Mark the current page with aria-current="page" and keep the visible text as part of
  each accessible name.

### Provide a helpful custom 404 page

Requests for missing URLs receive a real 404 status and a page that offers search and
routes back into the site.

Check:

- A request for an unknown URL returns HTTP status 404, not 200.
- The page has a clear heading, a search form, a home link, and links to the main
  sections.

Fix:

- Configure the server or framework to send status 404 for unmatched routes.
- Add a branded error template with search and navigation, and set a noindex robots
  directive on it when the page must not be indexed.

### Find and repair broken links

Internal, external, anchor, and mailto links resolve to their intended targets, and a
checker verifies them automatically.

Check:

- Run a link checker against the built site and review 404 responses, redirects, and
  missing fragment targets.
- Confirm that every anchor href points to an existing id.

Fix:

- Replace redirected links with their final destinations and remove or replace dead
  links.
- Run a checker such as lychee or linkchecker in continuous integration, and schedule
  checks of external links because they change over time.

## Forms

### Use semantic input types

Each input element uses the type and autocomplete values that describe the data it
collects, which selects the right mobile keyboard and enables autofill.

Check:

- Email, telephone, URL, and date fields use type email, tel, url, and date rather than
  text.
- Personal data fields carry an autocomplete token from the standard list.

Fix:

- Change the type attribute to the most specific value that fits the data.
- Add autocomplete tokens, for example autocomplete="email".

```html
<label for="email">Email</label>
<input id="email" type="email" name="email" autocomplete="email" />
```

### Validate forms accessibly

Validation errors are attached to their fields, announced to assistive technology, and
not conveyed through color alone.

Check:

- Required fields are marked with required or aria-required and their label says so.
- Error text is linked with aria-describedby, and aria-invalid is true on fields that
  fail validation.
- Do not flag client-rendered forms for lacking method or action when a script handles
  submission.

Fix:

- Render each error next to its field and reference it with aria-describedby.
- Group related choices in a fieldset with a legend, and announce a summary of the
  errors when the form is submitted.

### Make search inputs accessible

The search input has a label and a search role, and suggestions can be used from the
keyboard.

Check:

- The input has type="search" and a visible label or an aria-label.
- The form containing the input has role="search".
- Autocomplete suggestions are reachable from the keyboard, and result counts are
  announced.

Fix:

- Use type="search" and wrap the input in a form with role="search".
- Support arrow-key navigation through suggestions and announce the result count in a
  live region.

### Make file uploads accessible

File inputs have visible labels, declared accepted types, and feedback that assistive
technology can perceive.

Check:

- Each file input has a label, and its instructions are linked with aria-describedby.
- The accept attribute lists the permitted types, and the size limit is stated in text.
- Progress and error messages are announced through a live region.

Fix:

- Pair each input with a visible label and a hint that states the types and maximum
  size.
- Provide a button that opens the file picker for every drag-and-drop zone.

## Interactive components

### Announce notifications to assistive technology

Status messages and alerts are placed in live regions, so that screen readers announce
them without moving focus.

Check:

- Routine messages use role="status" with aria-live="polite", and urgent failures use
  role="alert".
- The live region exists before its content changes, and the message remains on screen
  long enough to be read.
- Each notification offers a visible dismiss control.

Fix:

- Use role="status" for confirmations and role="alert" for failures that need immediate
  attention.
- Render the live region container at page load and insert the text into it later.

```html
<div role="status" aria-live="polite"></div>
<!-- Script later inserts: "Changes saved." -->
```

### Make tooltips accessible

Tooltips are reachable from the keyboard, linked to their trigger, and dismissible
without moving focus.

Check:

- The trigger is a focusable button or link, and the tooltip is referenced by
  aria-describedby.
- The tooltip appears on focus as well as on hover, can be dismissed with Escape, and
  stays visible while the pointer is over it (WCAG 1.4.13).
- Essential information is not placed only inside a tooltip.

Fix:

- Give the tooltip role="tooltip" and reference it from the trigger.
- Implement Escape dismissal and keep the tooltip open while it is hovered.

### Make accordions keyboard operable

Accordion triggers are buttons that expose their expanded state and control a labelled
panel.

Check:

- Each trigger is a button inside a heading, with aria-expanded and aria-controls.
- Enter and Space toggle the panel, and collapsed panels are removed from the focus
  order.

Fix:

- Update aria-expanded on each toggle and point aria-controls at the panel.
- Apply hidden to collapsed panels and label each panel with aria-labelledby. Arrow-key
  movement between headers is optional in the WAI-ARIA accordion pattern.

### Implement tabs with the tab pattern

Tabs follow the WAI-ARIA tabs pattern, with roles, selected state, and arrow-key
movement between tabs.

Check:

- The container has role="tablist", each control has role="tab" with aria-selected and
  aria-controls, and each panel has role="tabpanel" with aria-labelledby.
- Only the selected tab is in the tab sequence, and the arrow keys move between tabs.

Fix:

- Apply a roving tabindex: 0 on the selected tab, -1 on the others, updated on each
  selection.
- Keep Tab moving from the tab list into the active panel.

### Make carousels controllable

Carousels that rotate automatically provide pause control, keyboard operation, and
announcements, and they respect the reduced-motion preference.

Check:

- Automatic rotation has a visible pause control and does not start when
  prefers-reduced-motion is set.
- Slides can be reached with buttons, and slide changes are exposed through a polite
  live region.

Fix:

- Add previous, next, and pause controls with accessible names.
- Check matchMedia for prefers-reduced-motion and keep rotation paused for those users.

### Make drag and drop operable without a pointer

Each drag operation has a keyboard alternative and a single-pointer alternative, and the
outcome is announced.

Check:

- Each draggable item can be moved with the keyboard, for example with Space to pick up
  and arrow keys to move (WCAG 2.5.7 requires a single-pointer alternative).
- The outcome of each move is announced through a live region.

Fix:

- Add keyboard handlers and move-up and move-down buttons as alternatives.

### Make custom elements accessible

Custom elements expose their role, states, keyboard behaviour, and form participation to
assistive technology and to forms.

Check:

- Confirm that the widget cannot be built from a native control with styling.
- Verify that the element sets its role and states through ElementInternals and that
  custom inputs are form-associated.
- Verify that the keyboard interaction matches the ARIA pattern for the widget.

Fix:

- Attach ElementInternals and set the role and state properties on it.
- Declare static formAssociated for custom inputs, and replace the component with a
  native element when one supports the interaction.

```js
class AppCheckbox extends HTMLElement {
  static formAssociated = true;
  #internals = this.attachInternals();
  connectedCallback() {
    this.#internals.role = "checkbox";
  }
}
```

## Media

### Provide captions, descriptions, and transcripts for video

Videos carry accurate captions, audio descriptions, and a transcript, and players do not
autoplay with sound.

Check:

- Each video has track elements of kind captions that are accurate, not automatically
  generated, and of kind descriptions where visual content needs narration.
- The video has controls, does not autoplay with sound, and its pause control works from
  the keyboard.
- A transcript is linked close to the player.

Fix:

- Add track elements with srclang and label, and mark the default track.
- Provide a transcript and remove autoplay; add a global pause control for any motion
  that starts without user action.

```html
<video controls preload="metadata" poster="poster.jpg">
  <source src="talk.mp4" type="video/mp4" />
  <track kind="captions" src="talk-en.vtt" srclang="en" label="English" default />
</video>
```

### Add a poster image to video elements

Each video element names a representative poster image and reserves its dimensions, so
that a blank frame and layout shift are avoided.

Check:

- Each video element has a poster attribute that resolves to an image.
- The width and height attributes, or equivalent CSS, reserve space for the player.
- The poster image depicts the actual content of the video.

Fix:

- Add a poster attribute that points to a 16:9 image, at least 1280 by 720 pixels for HD
  content.
- Set width and height on the video element.

## Head and resource loading

### Load scripts with defer, async, or module type

Scripts do not block HTML parsing, because they use defer, async, or type module.

Check:

- Each classic script in the head has defer or async, unless it must run before the
  parser continues.
- Scripts at the end of the body that could run after parsing are candidates for defer.

Fix:

- Use defer for scripts that depend on the DOM or on each other, since deferred scripts
  keep their order.
- Use async only for independent scripts such as analytics; module scripts defer by
  default.

### Protect external scripts and stylesheets with SRI

External scripts and stylesheets carry an integrity hash, so that the browser refuses
content that differs from the expected file.

Check:

- List every script and stylesheet whose origin differs from the page origin.
- Confirm that each one has an integrity attribute and crossorigin="anonymous".

Fix:

- Add integrity with the SHA-384 hash that the provider publishes, or generate one with
  openssl.
- Keep crossorigin="anonymous", which the browser requires for cross-origin integrity
  checks, and regenerate the hash whenever the file version changes.

```html
<script
  src="https://cdn.example.com/lib.min.js"
  integrity="sha384-BASE64_HASH"
  crossorigin="anonymous"
></script>
```

### Provide noscript fallbacks and initial content

Pages that depend on scripts present meaningful content, and they offer a usable path
when scripting is unavailable.

Check:

- Important content and pagination links appear in the initial HTML, not only after
  hydration.
- Each noscript element offers alternative content or a route forward, not only an
  instruction to enable JavaScript.

Fix:

- Render core content on the server and enhance it progressively with scripts.
- Replace user-agent sniffing with feature detection.

### Provide favicons for each platform

The site supplies the icon formats that browsers, devices, and home screens request.

Check:

- A favicon in ICO or PNG at 32 by 32 pixels is declared, and an SVG icon is declared
  for modern browsers.
- An apple-touch-icon of 180 by 180 pixels is declared, and icons listed in the manifest
  exist at their stated sizes.

Fix:

- Generate the set with an icon generator and place the files at the site root or
  declare them in the head.
- Declare each format with a link element.

```html
<link rel="icon" href="/favicon.ico" sizes="32x32" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
```

### Link a web app manifest

The head links a manifest file that describes the application name, icons, start URL,
and display mode.

Check:

- A link element with rel="manifest" points to a JSON file that returns status 200.
- The manifest defines name or short_name, start_url, display, and icons of at least 192
  and 512 pixels.

Fix:

- Add the manifest link to the head, together with a theme-color meta element for the
  browser interface.
- Set display to standalone and theme_color to the brand color.

```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#2563eb" />
```

### Meet PWA installability criteria

The site meets the browser criteria for installation: HTTPS, a valid manifest, a service
worker with a fetch handler, and suitable icons.

Check:

- The site is served over HTTPS, and the manifest provides name, start_url, display, and
  icons of 192 and 512 pixels.
- A service worker is registered and handles fetch events, and a maskable icon is
  provided.

Fix:

- Repair the manifest and register a service worker that answers fetch requests,
  returning cached content when the network is unavailable.
- Add an icon with purpose "maskable" for adaptive Android icons.

### Analyze loading performance with WebPageTest

Loading behaviour is measured from real locations and browsers, and waterfall charts and
filmstrips identify the requests that block rendering.

Check:

- Run at least three tests from locations close to the users, covering the first view
  and the repeat view.
- Inspect the waterfall for render-blocking requests and slow third-party requests.

Fix:

- Act on the findings by compressing and caching resources, reducing render-blocking
  requests, and shortening the critical path.
- Repeat the test after each change and compare the runs, because single runs vary.
