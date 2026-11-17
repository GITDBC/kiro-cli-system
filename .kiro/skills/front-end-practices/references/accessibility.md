# Accessibility

This file describes the accessibility rules of the front-end practices skill. It covers
89 rules grouped by topic. For each rule it gives the priority, the implementation
difficulty, a statement of the requirement, the checks that establish conformance, and
the corrective actions. It is the reference that the skill loads when it performs
accessibility checks and proposes fixes, and each rule is written so that it can be
applied without consulting external sources.

## Rule index

| Rule                           | Priority | Difficulty   | Rule statement                                                                                                       |
| ------------------------------ | -------- | ------------ | -------------------------------------------------------------------------------------------------------------------- |
| `aria-hidden-body`             | critical | intermediate | The body element must never carry `aria-hidden="true"`, because that hides the whole page from assistive technology. |
| `aria-input-field-name`        | critical | beginner     | Every input, textarea, and select must expose a name that matches its visible label.                                 |
| `button-name`                  | critical | beginner     | Every button must have a non-empty accessible name that describes its action.                                        |
| `flashing-content`             | critical | beginner     | Content must not flash more than three times per second or in areas that exceed the photosensitivity thresholds.     |
| `form-labels`                  | critical | beginner     | Every form control must have a visible label that is programmatically associated with it.                            |
| `heading-hierarchy`            | critical | beginner     | A page must have one h1, and headings must descend one level at a time.                                              |
| `input-image-alt`              | critical | beginner     | An image input must carry alternative text that names the action it performs.                                        |
| `keyboard-navigation`          | critical | intermediate | All interactive content must be operable with the keyboard, without traps outside modals.                            |
| `zoom-reflow`                  | critical | intermediate | Content must reflow into a single column at 400% zoom without horizontal scrolling.                                  |
| `accessible-authentication`    | high     | advanced     | Sign-in and recovery flows must offer a path that does not require a cognitive function test.                        |
| `aria-labels`                  | high     | intermediate | Interactive elements must have concise, descriptive names rather than generic ones.                                  |
| `aria-live-regions`            | high     | intermediate | Dynamic updates must be announced through live regions that exist before the content changes.                        |
| `aria-required-children`       | high     | intermediate | Composite ARIA roles must own the child roles that the specification requires.                                       |
| `aria-valid-attr`              | high     | beginner     | Only valid, standard ARIA attribute names may be used.                                                               |
| `autoplay-media`               | high     | beginner     | Audio must not start automatically, and video that does must start muted with immediate controls.                    |
| `color-contrast`               | high     | intermediate | Text and essential interface components must meet the WCAG minimum contrast ratios.                                  |
| `content-without-css`          | high     | intermediate | Meaning, reading order, and required actions must survive when author styles are disabled.                           |
| `duplicate-id-active`          | high     | intermediate | Focusable and interactive elements must have unique identifiers.                                                     |
| `duplicate-id-aria`            | high     | intermediate | Every identifier referenced by an ARIA attribute must be unique.                                                     |
| `focus-management`             | high     | intermediate | Focus must move deliberately when content opens, closes, or changes.                                                 |
| `focus-not-obscured`           | high     | intermediate | A focused element must remain visible and must not be hidden by sticky interface layers.                             |
| `focus-order`                  | high     | intermediate | The focus sequence must follow the visual and reading order.                                                         |
| `link-text`                    | high     | beginner     | Link text must describe the destination so that it makes sense out of context.                                       |
| `modal-accessibility`          | high     | intermediate | A modal dialog must trap focus, close with Escape, and return focus to its trigger.                                  |
| `orientation`                  | high     | intermediate | Content must remain usable in portrait and landscape unless one orientation is essential.                            |
| `reduced-motion`               | high     | beginner     | Non-essential motion must be disabled or replaced when the user requests reduced motion.                             |
| `redundant-entry`              | high     | intermediate | Information already provided in a process must be reused rather than requested again.                                |
| `screen-reader-testing`        | high     | intermediate | Key journeys must be verified with at least two screen reader and browser combinations.                              |
| `sensory-instructions`         | high     | beginner     | Instructions must not rely solely on color, shape, position, or sound.                                               |
| `session-timeout-recovery`     | high     | advanced     | Users must be warned before a timeout discards their work and must be able to recover it.                            |
| `skip-navigation`              | high     | beginner     | Pages with repeated navigation must offer a skip link to the main content.                                           |
| `text-resizing`                | high     | intermediate | Text must scale to 200% without clipping, overlap, or loss of functionality.                                         |
| `video-captions`               | high     | intermediate | Video with audio must provide synchronized captions that include relevant sounds.                                    |
| `viewport-zoom`                | high     | beginner     | The viewport definition must not disable or restrict user zoom.                                                      |
| `accessible-tables`            | medium   | intermediate | Data tables must use header cells, a caption or name, and must not be used for layout.                               |
| `accesskeys`                   | medium   | intermediate | Each access key value must be unique within the document.                                                            |
| `aria-allowed-attr`            | medium   | intermediate | Each ARIA attribute must be supported by the role of the element that carries it.                                    |
| `aria-command-name`            | medium   | intermediate | Command roles such as button, link, and menuitem must have an accessible name.                                       |
| `aria-deprecated-role`         | medium   | intermediate | Deprecated ARIA roles must be replaced by current roles or native elements.                                          |
| `aria-dialog-name`             | medium   | intermediate | Dialog and alertdialog elements must have an accessible name.                                                        |
| `aria-hidden-focus`            | medium   | intermediate | An element with `aria-hidden="true"` must not contain focusable descendants.                                         |
| `aria-meter-name`              | medium   | intermediate | A meter must have a label that identifies the quantity it measures.                                                  |
| `aria-progressbar-name`        | medium   | intermediate | A progress bar must have a name and, when known, its current value and range.                                        |
| `aria-required-attr`           | medium   | intermediate | Roles that define required states or properties must include those attributes.                                       |
| `aria-required-parent`         | medium   | intermediate | Child roles must be placed inside the parent roles that they require.                                                |
| `aria-roles`                   | medium   | intermediate | Role values must be standard, correctly spelled, and preferably replaced by native elements.                         |
| `aria-text`                    | medium   | intermediate | An element with `role="text"` must not contain interactive descendants.                                              |
| `aria-toggle-field-name`       | medium   | intermediate | Checkboxes, radio buttons, and switches must have a name that states what they control.                              |
| `aria-tooltip-name`            | medium   | intermediate | A tooltip must be referenced from its trigger so that its content is announced.                                      |
| `aria-treeitem-name`           | medium   | intermediate | Each treeitem must have a non-empty name, and expandable items must expose their state.                              |
| `aria-valid-attr-value`        | medium   | intermediate | Each ARIA attribute must carry a value of the type it allows, including existing ID references.                      |
| `audio-descriptions`           | medium   | intermediate | Information shown only visually in a video must also be available as an audio description.                           |
| `consistent-help`              | medium   | beginner     | Help mechanisms that recur across related pages must appear in the same relative order.                              |
| `decorative-elements`          | medium   | beginner     | Purely decorative images and icons must be hidden from assistive technology.                                         |
| `definition-list`              | medium   | intermediate | A dl element may contain only dt and dd elements, optionally grouped in div elements.                                |
| `dlitem`                       | medium   | beginner     | Every dt and dd element must belong to a dl element, directly or through a div group.                                |
| `empty-heading`                | medium   | beginner     | Heading elements must contain perceivable text.                                                                      |
| `empty-links`                  | medium   | beginner     | Every link must expose text that describes its destination, including icon-only links.                               |
| `form-field-multiple-labels`   | medium   | beginner     | A form control should have one label element, combining further text with aria-labelledby.                           |
| `frame-title`                  | medium   | beginner     | Every iframe and frame must have a title that identifies its content.                                                |
| `heading-order`                | medium   | beginner     | Heading levels must not skip, so that each heading is at most one level deeper than its predecessor.                 |
| `html-xml-lang-mismatch`       | medium   | beginner     | When both lang and xml:lang are present on the html element, their values must be identical.                         |
| `identical-links-same-purpose` | medium   | intermediate | Links with identical text must lead to the same destination.                                                         |
| `inclusive-language`           | medium   | beginner     | Content must avoid ableist, gendered, and culturally specific terms.                                                 |
| `label-content-name-mismatch`  | medium   | intermediate | The visible label of a control must appear at the start of its accessible name.                                      |
| `landmark-one-main`            | medium   | beginner     | A page must contain exactly one main landmark.                                                                       |
| `landmark-regions`             | medium   | intermediate | Page sections must use HTML5 landmarks, and repeated landmark types must be labelled.                                |
| `link-in-text-block`           | medium   | intermediate | Links within running text must be distinguishable from the surrounding text by more than color.                      |
| `list-structure`               | medium   | intermediate | The direct children of ul and ol elements must be li elements.                                                       |
| `listitem`                     | medium   | beginner     | Every li element must sit directly inside a ul, ol, or menu element.                                                 |
| `meta-refresh`                 | medium   | intermediate | Pages must not redirect or reload automatically through a meta refresh.                                              |
| `object-alt`                   | medium   | intermediate | An object element must contain fallback content that conveys the same information.                                   |
| `parallax-effects`             | medium   | intermediate | Parallax motion must be disabled for reduced-motion users and must not gate content.                                 |
| `paste-inputs`                 | medium   | intermediate | Form fields must accept pasted input.                                                                                |
| `plain-language`               | medium   | beginner     | Content must use short sentences, common words, active voice, and an accessible reading level.                       |
| `scrolljacking`                | medium   | beginner     | Scripts must not override native scroll speed, direction, or paging.                                                 |
| `select-name`                  | medium   | intermediate | Every select element must have an associated label or equivalent accessible name.                                    |
| `semantic-lists`               | medium   | beginner     | Groups of related items must use ul, ol, or dl elements rather than styled divs.                                     |
| `skip-link`                    | medium   | intermediate | A skip link should be the first focusable element and must target the main content.                                  |
| `tabindex`                     | medium   | intermediate | The tabindex attribute must use 0 or -1 only, and positive values must not be used.                                  |
| `table-duplicate-name`         | medium   | intermediate | Each data table must have a caption or aria-label that is unique on the page.                                        |
| `table-headers`                | medium   | intermediate | Header cells must be th elements with a scope attribute of col or row.                                               |
| `td-headers-attr`              | medium   | intermediate | Headers attributes on td elements must reference existing th identifiers.                                            |
| `th-has-data-cells`            | medium   | intermediate | Every th element must be associated with at least one data cell.                                                     |
| `touch-targets`                | medium   | intermediate | Interactive targets must meet the minimum size or spacing for pointer and touch input.                               |
| `anchor-smooth-scroll`         | low      | beginner     | Smooth scrolling to anchors must be disabled for reduced-motion users, and focus must reach the target.              |
| `autofocus-avoidance`          | low      | beginner     | Form fields should not receive focus automatically on page load.                                                     |
| `image-redundant-alt`          | low      | beginner     | Alternative text must not repeat phrases such as "image of" or adjacent text.                                        |
| `text-in-images`               | low      | beginner     | Text should be delivered as real HTML text rather than rendered inside images.                                       |

## Images, objects and frames

### Provide alternative text for image buttons

An image input must expose a text alternative that names the action it performs.

Check:

- Confirm that every `input[type="image"]` has a non-empty `alt` attribute.
- Confirm that the text names the action, not the file name or appearance of the image.

Fix:

- Give the `alt` attribute a value such as "Search" or "Submit".
- Where a text button fits better, replace the image input with a native button.

```html
<input type="image" src="magnifier.png" alt="Search" />
```

### Avoid redundant image alternative text

Alternative text should convey the meaning of an image without repeating phrases that
assistive technology already announces or text that appears beside the image.

Check:

- Search `alt` values for prefixes such as "image of" or "photo of".
- Compare each `alt` value with the adjacent caption or link text for duplication.

Fix:

- Remove the prefix and keep only the informative content.
- Use `alt=""` when the adjacent text already conveys the same information.

### Hide decorative elements from assistive technology

Purely decorative images, icons, and SVG graphics should be excluded from the
accessibility tree so that screen readers do not announce them.

Check:

- Confirm that decorative `img` elements use an empty `alt` attribute.
- Confirm that decorative SVGs and icon fonts carry `aria-hidden="true"`.
- Do not report decorative assets as performance defects unless they cause layout
  shifts.

Fix:

- Use `alt=""` on decorative `img` elements instead of omitting `alt`.
- Move purely visual artwork to a CSS `background-image` where that is practical.

### Avoid images of text

Text should be delivered as real HTML text rather than as part of an image, because
images cannot be resized, translated, or reflowed reliably.

Check:

- Identify images whose content is words that could be real text.
- Exclude logos and decorative typography from the finding.

Fix:

- Replace the image with HTML text styled through CSS and web fonts.
- If an image of text is unavoidable, provide the same words in its `alt` text.

### Provide alternative text for objects

An object element must contain fallback content that conveys the same information when
the embedded resource cannot be rendered.

Check:

- Confirm that every `object` element contains non-empty fallback content.
- Confirm that the fallback provides the function or meaning of the resource.

Fix:

- Add descriptive text or a semantic equivalent inside the element.
- Use an `img` or a link instead when the resource is only an image or a document.

```html
<object data="chart.svg" type="image/svg+xml">
  <p>Sales rose 12% between Q1 and Q2 2024.</p>
</object>
```

### Provide titles for iframes and frames

Every frame must carry a title that identifies its content, so that users can decide
whether to enter it before they navigate into it.

Check:

- Confirm that every `iframe` and `frame` element has a non-empty `title`.
- Confirm that the title describes the content, not a generic label.

Fix:

- Add a `title` attribute that names the embedded content, such as the video title.
- Remove frames that duplicate content available elsewhere on the page.

## Audio, video and motion

### Provide audio descriptions for video

Information conveyed only visually in a video must also be available through an audio
description track or an equivalent narration.

Check:

- Identify visual-only content such as actions, on-screen text, and scene changes.
- Verify that an audio description track or spoken equivalent is available.

Fix:

- Add a `track` element with `kind="descriptions"` for a separate description track.
- Use an extended description with pauses when dialogue leaves too little time.

```html
<video controls>
  <track
    kind="descriptions"
    src="described.vtt"
    srclang="en"
    label="Audio description"
  />
</video>
```

### Provide captions for video content

Prerecorded and live video with audio must provide synchronized captions that include
speech, speaker changes, and relevant non-speech sounds.

Check:

- Confirm that each video with audio has a captions track with a valid WebVTT file.
- Confirm that the caption control of each embedded player is accessible.

Fix:

- Create a WebVTT file with complete dialogue and descriptions of relevant sounds.
- Add `<track kind="captions" default>` to the video and review auto-generated captions.

### Avoid autoplaying media

Audio must not start automatically. Video that autoplays must start muted and must offer
controls to pause or stop it immediately.

Check:

- Confirm that no audio or video starts on page load.
- If autoplay is essential, confirm that the media is muted and that its controls are
  reachable early in the tab order.

Fix:

- Remove the `autoplay` attribute from media elements.
- If autoplay is required, add `muted` and a visible, keyboard-accessible pause control.

### Avoid seizure-triggering flashing content

Content must not flash more than three times per second, and any flashing area must stay
below the photosensitivity thresholds.

Check:

- Test animated GIFs, videos, and CSS animations for rapid flashing.
- Confirm that no flash exceeds three per second and that the flashing area is below 25%
  of the viewport.

Fix:

- Slow the animation or remove the flashing effect entirely.
- Replace the effect with a fade or a static cue that conveys the same information.

### Respect reduced motion preferences

Non-essential animation must be disabled, or replaced by gentle opacity or color
transitions, when the user has requested reduced motion.

Check:

- Confirm that animations are wrapped in a `prefers-reduced-motion` condition.
- Confirm that no content flashes and that motion warnings precede immersive pages.

Fix:

- Disable non-essential animation inside `@media (prefers-reduced-motion: reduce)`.
- Provide a user control that pauses or disables animation.

```css
.hero-banner {
  animation: slide-in 600ms ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .hero-banner {
    animation: fade-in 300ms linear;
  }
}
```

### Provide alternatives to parallax effects

Parallax motion, in which background and foreground move at different speeds, must be
disabled for users who request reduced motion and must never be required to reach
content.

Check:

- Identify layered scroll effects and confirm whether they run under reduced motion.
- Confirm that the essential content is available without the effect.

Fix:

- Enable the effect only inside a `prefers-reduced-motion: no-preference` condition.
- Provide a static fallback that conveys the same content.

### Avoid scrolljacking and custom scroll behavior

Scripts must not override native scroll speed, direction, or paging, because such
changes break assistive technology and the expectations of most users.

Check:

- Test scrolling and confirm that it feels native.
- Look for wheel or scroll listeners that change speed, direction, or page position.

Fix:

- Remove the code that overrides default scroll behavior.
- If custom scrolling is essential, respect reduced motion and offer a way to disable
  it.

### Provide instant anchor scroll option

Smooth scrolling to same-page anchors should apply only when the user has not requested
reduced motion, and keyboard focus must land on the target of the link.

Check:

- Activate same-page anchor links with reduced motion enabled.
- Confirm that focus moves to the target element after navigation.

Fix:

- Apply `scroll-behavior: smooth` only inside a `no-preference` condition.
- Make the target focusable with `tabindex="-1"` and call `focus()` on it.

```css
@media (prefers-reduced-motion: no-preference) {
  html {
    scroll-behavior: smooth;
  }
}
```

## Forms and input fields

### Associate labels with form controls

Every input, select, and textarea must have a visible label that is programmatically
associated with it, and placeholder text cannot replace that label.

Check:

- Confirm that each control is associated with a label through `for` and `id`, or
  through an ARIA labelling attribute.
- Flag controls that rely on placeholder text, and grouped controls without a legend.

Fix:

- Add a `label` element whose `for` value matches the control `id`.
- Wrap related radio buttons or checkboxes in a `fieldset` with a `legend`.

```html
<label for="email">Email address</label>
<input id="email" name="email" type="email" autocomplete="email" />
```

### Ensure all input fields have accessible names

Every input, textarea, and select, including custom widgets that use textbox or combobox
roles, must expose a name that matches its visible label.

Check:

- Find controls that lack a label, `aria-label`, or `aria-labelledby`.
- Check custom widgets with textbox or combobox roles for the same requirement.

Fix:

- Prefer a `label` element associated through `for` and `id`.
- Use `aria-label` for controls such as search fields, and keep placeholder text as a
  format hint only.

### Provide accessible names for select elements

Each select element must have an associated label, and its first option must not serve
as a substitute for that label.

Check:

- Confirm that every `select` has a valid `label` association or ARIA name.
- Confirm that the first option is not used as the only description of the control.

Fix:

- Add a `label` whose `for` attribute matches the `id` of the select.
- Use `aria-label` or `aria-labelledby` only when a visible label is not possible.

### Provide accessible names for toggle fields

Checkboxes, radio buttons, and switches must have a name that states what the control
turns on, off, or selects.

Check:

- Confirm that every checkbox, radio button, and element with `role="switch"` has a
  name.
- Confirm that the name describes the choice rather than a generic state.

Fix:

- Add a `label` element, `aria-label`, or `aria-labelledby` to each toggle.

### Use a single label for each form field

A form control should be associated with one label element. Where several text fragments
name the control, they should be combined through `aria-labelledby`.

Check:

- Count the label elements associated with each form control.
- Note controls that have several labels that produce redundant announcements.

Fix:

- Consolidate the labels into a single `label` element.
- Use `aria-labelledby` with a space-separated list of identifiers when several text
  fragments must name one control.

### Align visible labels with accessible names

The visible text of a control should appear at the start of its accessible name, so that
voice control users can activate the control by speaking its label.

Check:

- Compare the visible text of buttons and links with their `aria-label` values.
- Confirm that the visible text appears in the accessible name.

Fix:

- Place the exact visible text at the beginning of the `aria-label` value.

### Allow pasting into form inputs

Form fields must accept pasted input, so that password managers and copied values can be
used without errors.

Check:

- Search for handlers that cancel the paste event, such as `onpaste="return false"`.
- Check password and card number fields for the same restriction.

Fix:

- Remove paste-blocking attributes and event handlers from all inputs.

### Avoid autofocus on form fields

Form fields should not receive focus automatically on page load, particularly when
meaningful content appears before them.

Check:

- Search for the `autofocus` attribute on form elements.
- Confirm that page load does not move focus away from the top of the page.

Fix:

- Remove the `autofocus` attribute.
- If focus is needed, move it in response to a user action. Login and search-only pages
  are the usual exceptions.

### Provide accessible authentication methods

Sign-in, multi-factor, and recovery flows must offer at least one path that does not
require the user to memorize, transcribe, or solve a cognitive function test.

Check:

- Review login and recovery flows for blocked paste, password manager hostility, and
  transcription requirements.
- Flag CAPTCHA or knowledge checks that have no alternative.

Fix:

- Support paste and password managers, and support one-time code autofill.
- Offer a passkey, magic link, or device approval path alongside the password path.

```html
<input id="otp" name="otp" inputmode="numeric" autocomplete="one-time-code" />
```

## Accessible names of controls

### Provide accessible names for buttons

Every button must have a non-empty accessible name that describes its action, and a
control that navigates to another page should be a link.

Check:

- Find buttons that have no text, `aria-label`, or `aria-labelledby`.
- Find buttons whose only effect is navigation to a URL.

Fix:

- Add visible text, an `aria-label`, or an `aria-labelledby` reference.
- Replace navigation buttons with `a` elements.

```html
<button type="button" aria-label="Close dialog">
  <svg aria-hidden="true" focusable="false">…</svg>
</button>
```

### Provide accessible names for ARIA command elements

Elements with command roles, such as button, link, or menuitem, must have a name derived
from their text content or from an ARIA labelling attribute.

Check:

- Identify elements with command roles that lack a clear accessible name.

Fix:

- Add inner text, an `aria-label`, or an `aria-labelledby` reference.

### Provide accessible names for all interactive elements

Buttons, links, and other interactive widgets must have a discernible and concise name
that describes the action or the destination.

Check:

- Audit buttons, links, and widgets for missing or unhelpful names.
- Flag generic names such as "More" or "Click here".

Fix:

- Add descriptive text content.
- Use `aria-label` where the visual design restricts the amount of visible text.

### Use descriptive link text

Link text must make sense when read out of context, because screen reader users often
navigate by a list of all links on the page.

Check:

- Flag generic phrases such as "click here", "read more", or "learn more".
- Confirm that download links state the file type and size.

Fix:

- Rewrite the link text so that it names the destination or the outcome.
- Use `aria-label` when the design requires short visible text.

### Provide accessible text for empty and icon-only links

Every link must expose text that describes its destination, and links without visible
text need an accessible name.

Check:

- Find anchor elements that contain no text and icon-only links without a label.
- Check the destinations for broken links.

Fix:

- Add `aria-label` or visually hidden text that names the destination.
- Repair or remove broken links.

### Keep identical link text consistent in destination

Links that share the same text must lead to the same destination. Otherwise, their text
must be made distinct.

Check:

- Identify links with identical text that point to different URLs.

Fix:

- Change the link text so that it names each destination.
- Confirm that identical text always leads to the same resource where it is repeated.

### Provide accessible names for tooltips

A tooltip must be referenced from its trigger through `aria-describedby`, so that its
content reaches assistive technology.

Check:

- Confirm that each element with `role="tooltip"` is referenced by its trigger.

Fix:

- Add `aria-describedby` on the trigger that points to the tooltip identifier.

### Ensure dialogs have an accessible name

Elements with the dialog or alertdialog role must have an accessible name, so that users
hear the purpose of the dialog when focus moves into it.

Check:

- Find elements with `role="dialog"` or `role="alertdialog"` that have no name.

Fix:

- Add `aria-labelledby` that references the dialog heading.
- Use `aria-label` when no visible heading exists.

### Provide accessible names for meter elements

A meter must carry a label that identifies the quantity it measures, so that its value
is meaningful to the user.

Check:

- Find `meter` elements and `role="meter"` elements without a name.

Fix:

- Add `aria-label` or `aria-labelledby` that names the measurement.

### Provide accessible names for progress bars

A progress bar must have a name that identifies the task it reports. When its value is
known, it should expose the current, minimum, and maximum values.

Check:

- Confirm that each `role="progressbar"` has a name.
- Confirm that the value attributes are present when the progress is known.

Fix:

- Add `aria-label` or `aria-labelledby` that names the task, without repeating the word
  "progress".
- Add `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` when the value is known.

### Provide accessible names for tree items

Each treeitem must have a non-empty name, and each item with children must expose its
expanded or collapsed state.

Check:

- Compute the name of each treeitem from `aria-labelledby`, `aria-label`, and text.
- Confirm that parent items carry `aria-expanded` with the value `true` or `false`.

Fix:

- Use descriptive visible text, or add `aria-label` when an icon has no text.
- Toggle `aria-expanded` each time that the item expands or collapses.

## Keyboard, focus and interaction

### Enable keyboard navigation for all elements

All interactive content must be operable with the keyboard, the focus order must follow
the reading order, and keyboard traps must exist only inside modal dialogs that offer an
escape route.

Check:

- Tab through the page and confirm that every interactive element is reachable.
- Confirm that hidden content cannot receive focus.

Fix:

- Arrange the DOM in the order of the visual layout.
- Remove hidden content from the tab sequence, and avoid positive `tabindex` values.

### Ensure logical focus order

The sequence in which focus moves must match the visual and reading order, and focus
must return to a sensible place when a dialog closes.

Check:

- Tab through the page and confirm that the order matches the visual layout.
- Confirm that focus returns to the triggering element when a dialog closes.

Fix:

- Reorder the DOM so that it matches the layout, and use CSS for visual positioning.
- Use `tabindex="0"` for custom controls and `tabindex="-1"` for script-managed focus.

### Manage focus during dynamic interactions

Focus must move deliberately when content opens, closes, or changes, so that keyboard
users are not left in an unexpected location.

Check:

- Confirm focus behavior when modals open and close, and when views change.
- Confirm that new content receives focus or is announced after a dynamic update.

Fix:

- Move focus to the new content, or to a heading inside it, when it appears.
- Return focus to the trigger element when the content is dismissed.

### Keep focused elements unobscured

A focused element must remain visible and must not be hidden behind sticky headers,
footers, cookie banners, or chat launchers.

Check:

- Tab through the page with all sticky interface layers active.
- Repeat the check at high zoom and on mobile layouts.

Fix:

- Add `scroll-padding` that equals the height of the sticky region.
- Reduce the height of overlays that cover the page.

```css
html {
  scroll-padding-top: 5rem; /* height of the sticky header */
}
```

### Use appropriate tabindex values

The tabindex attribute should carry the value 0 on custom interactive elements and the
value -1 on elements that receive focus only from script. Positive values must not be
used.

Check:

- Search for positive `tabindex` values.
- Confirm that custom interactive elements are focusable.

Fix:

- Remove positive values from the markup.
- Use `tabindex="0"` or `tabindex="-1"` according to the purpose of the element.

### Assign unique access keys

Each accesskey value must appear only once in the document, so that a shortcut triggers
exactly one element.

Check:

- Search for duplicate `accesskey` attributes across the document.

Fix:

- Assign a unique value to each `accesskey` attribute.
- Remove access keys that duplicate others.

### Make modal dialogs keyboard accessible

A modal dialog must trap focus while it is open, close with the Escape key, and return
focus to the element that opened it.

Check:

- Confirm that the dialog has the dialog role and `aria-modal="true"`.
- Confirm that Tab cycles within the dialog, that Escape closes it, and that focus
  returns on close.

Fix:

- Prefer the native `dialog` element opened with `showModal()`, which provides the focus
  containment and Escape handling.
- Make the background inert while the dialog is open.

### Hide focusable descendants of aria-hidden containers

An element with `aria-hidden="true"` must not contain focusable descendants, because a
focused element inside it is silent for screen reader users.

Check:

- Scan each `aria-hidden="true"` container for links, buttons, and inputs.

Fix:

- Set `tabindex="-1"` on focusable children of the container.
- Apply the `inert` attribute to the container instead when it is appropriate.

### Provide sufficient touch target size

Interactive targets should measure at least 24 by 24 CSS pixels, or be spaced so that
they satisfy the spacing exception. A size of 44 by 44 pixels is the stronger
recommendation for touch input.

Check:

- Measure the rendered bounding box of buttons, links, and inputs, including padding.
- Inline text links are exempt from the minimum size requirement.

Fix:

- Add padding to enlarge the hit area without changing the visual size.
- For icon-only buttons, extend the hit area with a positioned pseudo-element.

```css
.icon-btn {
  position: relative;
  min-width: 44px;
  min-height: 44px;
}
.icon-btn::before {
  content: "";
  position: absolute;
  inset: -12px;
}
```

### Use unique IDs for active elements

Focusable and interactive elements must have unique id values, because duplicate
identifiers can misdirect focus and actions.

Check:

- Search for duplicate `id` attributes on focusable or interactive elements.

Fix:

- Assign a unique `id` to each affected element and update its references.

## ARIA usage

### Use only allowed ARIA attributes for each role

Each ARIA attribute used on an element must be supported by the role of that element.

Check:

- Compare the attributes on each element with the attributes that its role supports.

Fix:

- Remove attributes that the role does not support.
- Change the role if the attribute reflects the intended role of the element.

### Avoid using deprecated ARIA roles

Deprecated roles, such as `directory`, and abstract roles must not be used in HTML.

Check:

- Search the markup for deprecated or abstract role values.

Fix:

- Replace each role with its current equivalent or with a native HTML element.

### Do not use aria-hidden on the document body

The body element must never carry `aria-hidden="true"`, because that setting silences
the entire page for screen reader users.

Check:

- Confirm that the body never receives `aria-hidden` during its lifecycle, including
  modal open and close code.

Fix:

- Remove `aria-hidden` from the body.
- Hide only the background container while a modal is open, and restore it on close.

```html
<!-- Incorrect: silences the whole page -->
<body aria-hidden="true">
  <!-- Correct: hide only the background while a modal is open -->
  <main inert>…</main>
</body>
```

### Include required ARIA attributes for roles

Roles that define required states or properties, such as slider, must include those
attributes so that assistive technology can report the state of the element.

Check:

- Verify each role against the required properties in the WAI-ARIA specification.

Fix:

- Add the missing attributes, for example `aria-valuenow` on a slider.

### Ensure ARIA roles contain required child roles

Composite roles such as tablist, list, menu, and tree must own the child roles that the
specification requires, so that assistive technology can enumerate their items.

Check:

- Confirm that each composite container owns the required child roles.
- Flag containers whose children are plain elements without roles.

Fix:

- Add the required role to each child, for example `role="tab"` inside a tablist.
- Apply `role="none"` to layout wrappers, or prefer native elements such as ul and li.

### Ensure ARIA roles are contained by required parent roles

Child roles such as listitem, tab, and menuitem must be placed inside the parent roles
that they require.

Check:

- Verify that elements with roles such as listitem, tab, and menuitem are nested
  correctly.

Fix:

- Wrap the child in the required parent role.
- Prefer the equivalent native structure where one exists.

### Use valid ARIA role values

Role values must be standard ARIA roles spelled correctly, and native elements should be
preferred to custom widgets built with ARIA.

Check:

- Search for role attributes with misspelled or non-standard values.

Fix:

- Correct the spelling or replace the role with the standard value.
- Replace custom ARIA widgets with native controls where that is possible.

### Avoid focusable descendants in role="text" elements

An element with `role="text"` flattens its content into one string, so interactive
descendants become invisible to assistive technology.

Check:

- Find `role="text"` elements that contain links, buttons, or inputs.

Fix:

- Remove the `role="text"` attribute from the container.
- Move the interactive children outside the container.

### Ensure ARIA attributes are valid

Attribute names must be valid, standard ARIA properties, and misspelled names must be
corrected because browsers ignore unknown names.

Check:

- Identify misspelled or non-existent `aria-*` attribute names.

Fix:

- Replace each name with the correct attribute name from the specification.

### Use valid values for ARIA attributes

Each ARIA attribute must carry a value of the type it allows, such as `true` or `false`,
an integer, or an identifier that exists in the document.

Check:

- Validate the values against the allowed types.
- Confirm that each identifier referenced by `aria-labelledby` or `aria-owns` exists.

Fix:

- Correct the value to the format defined by the specification, for example `true`
  instead of `yes`.

### Announce dynamic content with ARIA live regions

Dynamic updates, such as status messages, cart counts, and form errors, must be
announced through live regions that already exist in the DOM when the content changes.

Check:

- Verify that notifications, errors, and loading states are announced.

Fix:

- Add `aria-live="polite"` for non-urgent updates and `aria-live="assertive"` only for
  critical alerts.
- Use `role="status"` or `role="alert"` where the semantics fit.

### Ensure duplicate IDs do not break ARIA references

Every identifier referenced by an ARIA attribute must be unique, so that each reference
resolves to the intended element.

Check:

- Find ARIA references whose target identifier appears more than once in the DOM.

Fix:

- Make the identifiers unique and update the references that point to them.

## Color and visual cues

### Meet minimum color contrast ratios

Text must meet a contrast ratio of at least 4.5:1 for normal text and 3:1 for large
text, and interface components must meet 3:1 against adjacent colors.

Check:

- Compute the contrast of text against its background for each state, including hover,
  focus, active, and visited.
- Check borders, icons, and focus indicators against adjacent colors at 3:1.

Fix:

- Darken the foreground or lighten the background until the ratio meets the minimum.
- Do not reduce contrast through `opacity`. Compute the blended color instead.

### Make links in text blocks visually distinguishable

Links within running text must be distinguishable from the surrounding text by more than
color alone, normally through an underline.

Check:

- Identify links in body copy whose underline has been removed.
- If the underline is removed, confirm a 3:1 contrast against the body text and a
  non-color change on hover and focus.

Fix:

- Restore the underline on inline links within body copy.
- If the design excludes the underline, meet the contrast requirement and add a visible
  hover and focus treatment.

### Avoid sensory-only instructions

Instructions must not depend solely on color, shape, position, or sound. Text labels
must accompany each such reference.

Check:

- Review instructions for references such as "the red button" or "the menu on the
  right".
- Check that audio cues have a visual equivalent.

Fix:

- Name the control in text, for example "Submit (green)".
- Combine cues so that a user who cannot perceive one of them can still follow the
  instruction.

## Headings, landmarks and navigation

### Use logical heading hierarchy

Each page must have exactly one h1, and headings must descend one level at a time so
that they reflect the structure of the content rather than its styling.

Check:

- Confirm that the page has exactly one h1 and that no level is skipped.
- Generate the heading outline with an accessibility tool and review its text.

Fix:

- Assign h1 to the page title, h2 to major sections, and h3 to subsections.
- Use CSS for visual styling, not heading elements.

### Maintain logical heading order

Heading levels must follow sequential order, so that no level is skipped on the way down
the document. This rule overlaps with the heading hierarchy rule, and both are checked
together.

Check:

- Confirm that each heading follows a heading of the same or the preceding level.

Fix:

- Change the level of a heading that skips a step, for example an h3 after an h1 becomes
  an h2.

### Ensure headings contain text

Heading elements must contain perceivable text, because empty headings create empty
entries in the document outline.

Check:

- Find h1 to h6 elements that are empty or contain only whitespace.

Fix:

- Add descriptive text to the heading.
- Remove the element when it serves no purpose.

### Use exactly one main landmark

A page must contain exactly one main landmark, either a main element or an element with
`role="main"`, so that users can jump directly to the primary content.

Check:

- Count the main elements and the elements with `role="main"`.

Fix:

- Merge multiple main regions into one main element.
- Remove `role="main"` from the extra containers.

### Use landmark regions correctly

Page sections should be expressed as HTML5 landmarks such as header, nav, main, and
footer. Where several landmarks of one type exist, each must carry a distinguishing
label.

Check:

- Find generic div containers that represent a header, navigation, or footer.
- Confirm that repeated landmark types have labels.

Fix:

- Replace the generic containers with the matching HTML5 elements.
- Add `aria-label` to each navigation landmark when several are present.

### Implement "Skip to Content" links

A skip link should be the first focusable element on the page, and it should target the
main content container.

Check:

- Confirm that the skip link exists, is the first focusable element, and targets an
  element that exists.
- Confirm that the link becomes visible when it receives focus.

Fix:

- Add the link at the top of the body, with its target set to the main element's
  identifier.
- Keep the link off-screen rather than `display: none`, because hidden content cannot
  receive focus.

```css
.skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  left: 1rem;
  top: 1rem;
}
```

### Include a skip navigation link

A page with repeated navigation must offer a skip link to the main content, and the link
must become visible when it receives focus. This rule and the skip link rule are checked
together.

Check:

- Press Tab once after page load and confirm that a "Skip to main content" link appears.
- Confirm that the link targets the main content identifier.

Fix:

- Add the link as the first focusable element.
- Hide it visually until it receives focus.

### Keep repeated help mechanisms in a consistent location

Help options that recur across related pages must appear in the same relative order and
at the same location, so that users can find them while they are struggling.

Check:

- Compare the order of contact, chat, help, and phone entries across related pages.

Fix:

- Move the help mechanisms to a consistent position.
- Keep their relative order stable across the flow at the same breakpoint.

### Ensure content remains usable without CSS

Meaning, reading order, and required actions must survive when author styles are
disabled or replaced by user styles.

Check:

- Disable author styles and confirm the reading order, labels, errors, and primary
  actions.
- Look for meaning carried only by CSS generated content.

Fix:

- Use semantic HTML and a DOM order that matches the task sequence.
- Do not place essential labels or required markers in CSS generated content.

## Lists and definition lists

### Use correct list structure

The direct children of ul and ol elements must be li elements, and nested lists must be
placed inside an li element.

Check:

- Find children of ul and ol elements that are not li elements.

Fix:

- Move or wrap the non-li children so that each one is an li element.

### Place list items within list containers

Every li element must sit directly inside a ul, ol, or menu element, and an element with
`role="listitem"` must be owned by an element with `role="list"`.

Check:

- Find li elements whose parent is not ul, ol, or menu.
- Find `role="listitem"` elements without a list ancestor.

Fix:

- Wrap the items in a ul or ol element.
- Replace a list item that exists only for styling with a div or p element.

### Use semantic list elements

Groups of related items, such as navigation entries, features, and steps, must use ul,
ol, or dl elements rather than styled divs or spans.

Check:

- Identify groups of related items built from divs or spans that look like lists.

Fix:

- Use ul for unordered groups, ol for sequences, and dl for term and definition pairs.

### Use correct definition list structure

A dl element may contain only dt and dd elements, optionally grouped in div elements,
and script or template elements.

Check:

- Confirm that each dl element contains only permitted children.
- Flag other elements placed directly inside the dl element.

Fix:

- Remove the invalid children or move them outside the dl element.
- Wrap each dt and dd group in a div when a group is needed.

### Wrap definition items in a definition list

Every dt and dd element must belong to a dl element, either directly or through a div
group that is itself a child of the dl element.

Check:

- Locate dt and dd elements whose parent is not a dl or a permitted div group.

Fix:

- Wrap each orphaned dt or dd element in a dl element.

## Tables

### Use semantic table markup for screen readers

Data tables must provide header cells with a scope, a caption or accessible name, and
must not be used for layout.

Check:

- Confirm that header cells are th elements with a scope and that a caption exists.
- Flag tables used only to position content on the page.

Fix:

- Convert the header cells to th elements and add `scope`.
- Add a caption and use CSS Grid or Flexbox for layout.

### Ensure tables have unique accessible names

Each data table on a page must have a caption or aria-label that is distinct from the
names of the other tables.

Check:

- Confirm that every data table has a caption or aria-label.
- Flag generic names such as "Table 1".

Fix:

- Add a caption or aria-label that describes the data in the table.

### Define proper table headers

Header cells must be th elements with a scope attribute of col or row, so that each data
cell is associated with its headers.

Check:

- Confirm that the header cells are th elements with a valid scope value.

Fix:

- Convert header cells from td to th.
- Add `scope="col"` to column headers and `scope="row"` to row headers.

### Link table cells to headers using IDs

In complex tables where scope is not sufficient, the headers attribute of each td
element must reference existing th identifiers.

Check:

- Confirm that every value in a headers attribute matches an existing th identifier.

Fix:

- Correct the headers attribute so that it lists the identifiers of the relevant th
  elements, separated by spaces.

### Ensure table headers associate with data cells

Every th element must be associated with at least one data cell, so that no header
describes nothing.

Check:

- Find th elements that have no associated data cells.

Fix:

- Remove the empty headers, or map them to the data cells they describe.

## Responsive layout, zoom and orientation

### Support content reflow at 400% zoom

Content must reflow into a single column at 400% zoom, which corresponds to a viewport
of 320 CSS pixels, without horizontal scrolling. All functions must remain usable.

Check:

- Zoom the browser to 400% and confirm that the content forms one column.
- Confirm that no content is truncated or overlapped.

Fix:

- Use relative units such as rem, em, and percentages instead of fixed pixels.
- Use fluid layouts and media queries that adapt to the viewport width.

### Support text resizing to 200%

Text must scale to 200% without clipping, overlap, or loss of functionality.

Check:

- Apply the browser text size setting at 200% and confirm that no text is clipped.

Fix:

- Use rem or em units for font sizes.
- Avoid fixed-height containers that clip overflowing text.

### Do not disable pinch zoom

The viewport definition must not disable or restrict user zoom, because low-vision users
depend on zoom to read the content.

Check:

- Inspect the viewport meta element for `user-scalable=no`, `user-scalable=0`, and
  restrictive `maximum-scale` values.

Fix:

- Remove the restrictive values.
- If the page zooms on input focus in iOS, set the font size of the input to 16 pixels
  or larger instead.

```html
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

### Support both portrait and landscape orientation

Content and controls must remain available and usable in both orientations, unless one
orientation is essential to the task.

Check:

- Rotate the device or the emulated viewport and confirm that all content remains
  usable.
- Flag orientation locks and rotate-device overlays that block content.

Fix:

- Remove the orientation lock and use layouts that adapt to both orientations.
- Keep an orientation requirement only when the task is genuinely dependent on it.

## Cognition, language and timing

### Prevent data loss from session timeouts

Users must be warned before an inactivity timeout discards their work. They must be able
to extend the session, and they must recover entered data after re-authentication.

Check:

- Confirm that the timeout duration is disclosed and that a warning precedes expiry.
- Confirm that entered data is preserved across expiry and re-authentication.

Fix:

- Add an accessible timeout warning that offers extension.
- Save drafts and restore the user to the same step after re-authentication.

### Avoid meta refresh redirects

Pages must not redirect or reload automatically through a meta refresh element.

Check:

- Search the HTML for `http-equiv="refresh"`.

Fix:

- Replace the element with a server-side 301 or 302 redirect.
- Offer a user-initiated link where the user must choose the next step.

### Avoid redundant entry in the same process

Information already supplied in a process must be reused rather than requested again,
except where re-entry is a security measure such as password confirmation.

Check:

- Review multi-step flows for fields that ask for the same information more than once.

Fix:

- Auto-populate repeated fields and offer a "same as" choice where it applies.
- Preserve entered data between steps.

### Write in plain language

Content must use short sentences, common words, and active voice, and it must be written
at a reading level that suits the broadest intended audience.

Check:

- Identify jargon, complex sentences, and passive constructions.
- Confirm that the instructions and actions are clear.

Fix:

- Simplify the sentences and define each technical term at its first use.
- Use short paragraphs and lists where they aid comprehension.

### Use inclusive language

Content must avoid ableist, gendered, and culturally specific terms, and error messages
must guide the user rather than blame.

Check:

- Search for ableist terms, gendered defaults, and idioms that do not translate.
- Review error messages for tone.

Fix:

- Replace ableist terms with neutral alternatives.
- Use gender-neutral forms such as "they" and "users", and write messages that guide.

### Match lang and xml:lang attributes

When the html element carries both lang and xml:lang, the two values must be identical
and must be valid BCP 47 language tags.

Check:

- Compare the lang and xml:lang values on the html element, including subtags.

Fix:

- Make both values identical, using the primary language of the content.
- Remove xml:lang from HTML documents served as text/html, where it is unnecessary.

### Test with screen readers

Key user journeys must be verified with at least two screen reader and browser
combinations, because automated scans do not detect incorrect announcements, reading
order, or focus traps.

Check:

- Test with NVDA and Chrome on Windows, or VoiceOver and Safari on macOS.
- Confirm that interactive elements are announced with name, role, and state.

Fix:

- Add accessible names where they are missing.
- Correct the reading order, focus return, and live region announcements that fail.
