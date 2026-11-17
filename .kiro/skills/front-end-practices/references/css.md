# CSS

This file describes the CSS rules of the front-end-practices skill. It lists each rule
with its priority, difficulty, and a statement of the requirement, followed by the
checks that verify the requirement and the fixes that resolve a violation. The skill
loads this file as the reference for CSS checks and fixes; the HTML rules are held in
the companion file `html.md`.

## Rule index

| Rule                     | Priority | Difficulty   | Rule statement                                                                     |
| ------------------------ | -------- | ------------ | ---------------------------------------------------------------------------------- |
| `animation-performance`  | high     | intermediate | Animate only transform and opacity so the browser can composite the motion.        |
| `css-critical`           | high     | advanced     | Inline the styles needed for the first viewport and load the rest afterwards.      |
| `css-custom-properties`  | high     | beginner     | Store repeated colors, spacing, and type values as custom properties on :root.     |
| `css-minification`       | high     | beginner     | Serve production stylesheets minified and compressed.                              |
| `css-non-blocking`       | high     | intermediate | Load non-critical stylesheets without blocking the first render.                   |
| `embedded-or-inline-css` | high     | beginner     | Keep styles in external files, with inline blocks limited to justified cases.      |
| `focus-styles`           | high     | beginner     | Keep a visible focus indicator for keyboard users at all times.                    |
| `responsive-units`       | high     | beginner     | Size text and spacing with relative units that respect user preferences.           |
| `specificity-management` | high     | intermediate | Keep selectors low in specificity and shallow in nesting.                          |
| `unused-css`             | high     | intermediate | Remove selectors that no rendered page uses from the shipped stylesheet.           |
| `container-queries`      | medium   | intermediate | Make components respond to their container size instead of the viewport.           |
| `css-containment`        | medium   | advanced     | Use contain and content-visibility to limit the scope of layout and paint work.    |
| `css-grid`               | medium   | intermediate | Use CSS Grid for layouts that control both rows and columns.                       |
| `css-order`              | medium   | beginner     | Place stylesheets before synchronous scripts in the document head.                 |
| `css-print`              | medium   | intermediate | Provide a print stylesheet that hides interactive elements and sets print type.    |
| `dark-mode-css`          | medium   | intermediate | Support dark mode by redefining semantic color tokens.                             |
| `flexbox-patterns`       | medium   | intermediate | Apply flexbox sizing rules correctly and use gap for spacing.                      |
| `font-size`              | medium   | intermediate | Keep body text at 1rem or larger with relative units that scale with zoom.         |
| `horizontal-scroll`      | medium   | intermediate | Lay out content so no page scrolls horizontally at 320 CSS pixels.                 |
| `interstitials`          | medium   | intermediate | Avoid pop-ups that cover content, and manage focus in any dialog that is required. |
| `logical-properties`     | medium   | intermediate | Use logical properties so spacing follows the writing direction.                   |
| `naming-conventions`     | medium   | beginner     | Name classes with one consistent methodology, such as BEM.                         |
| `reset-css`              | medium   | beginner     | Start the cascade from a reset or normalize stylesheet.                            |
| `styles-lint`            | medium   | beginner     | Lint all CSS and SCSS with Stylelint in editors, hooks, and pipelines.             |
| `webfont-format`         | medium   | intermediate | Serve web fonts as WOFF2 with a WOFF fallback and control their loading.           |
| `cascade-layers`         | low      | intermediate | Declare an explicit layer order with @layer for the cascade.                       |
| `color-oklch`            | low      | intermediate | Define color palettes in oklch so equal lightness steps look equal.                |
| `css-at-property`        | low      | advanced     | Register custom properties with @property when they need a type or animation.      |
| `has-selector`           | low      | intermediate | Style a parent from its descendants with :has() instead of script toggling.        |
| `subgrid`                | low      | intermediate | Use subgrid so nested items align to the tracks of their parent grid.              |
| `view-transitions`       | low      | intermediate | Animate page and state changes with the View Transitions API.                      |

## Loading and delivery

### Inline critical CSS for the first viewport

The styles needed to render the first viewport are inlined in the head, and the
remaining stylesheet loads without delaying the first paint.

Check:

- Identify the stylesheets that block the first render and the styles that the
  above-the-fold content actually uses.
- Confirm that the inlined block is small, about 14 KB, and generated by a tool rather
  than maintained by hand.

Fix:

- Extract the above-the-fold rules with a tool such as critical, critters, or
  Lighthouse, and inline the result in the head.
- Load the remaining stylesheet without blocking the render, and regenerate the inlined
  block as part of the build.

### Load non-critical stylesheets without blocking the render

Non-critical stylesheets do not delay the first render, because they are loaded
asynchronously or only when a media condition applies.

Check:

- Plain link elements with rel="stylesheet" for non-critical CSS appear in the head.
- Stylesheets needed only in some contexts lack a media attribute or a media query.

Fix:

- Preload the stylesheet with as="style" and switch it to rel="stylesheet" in its onload
  handler, with a noscript fallback.
- Split the CSS by media query so that browsers do not block on sheets they do not need.

```html
<link rel="preload" href="/css/site.css" as="style" onload="this.rel='stylesheet'" />
<noscript><link rel="stylesheet" href="/css/site.css" /></noscript>
```

### Minify and compress production stylesheets

Production stylesheets contain no comments or redundant whitespace and are sent in a
compressed form.

Check:

- Production bundles contain no comments or unnecessary whitespace.
- The server or CDN returns the stylesheet with Brotli or gzip compression.

Fix:

- Enable minification with cssnano, lightningcss, or the default minifier of the
  framework.
- Enable Brotli or gzip compression at the server or the CDN.

### Order stylesheets before synchronous scripts

Stylesheets appear before synchronous scripts in the head, so that scripts never read
unstyled values and the cascade is complete when the first script runs.

Check:

- Stylesheets are listed in the head before any synchronous script.
- Scripts that read layout or computed styles run after the stylesheets they need.

Fix:

- Reorder the head so that reset, base, and component stylesheets precede synchronous
  scripts.
- Mark non-critical scripts with defer or async so that they do not block parsing.

### Keep styles out of inline and embedded blocks

Styles live in external stylesheets, and inline style attributes and style elements are
limited to critical CSS and to values that are computed at runtime.

Check:

- Search the markup for style attributes and style elements, and classify each as
  critical, dynamic, or removable.
- A declaration repeated across elements in style attributes indicates a missing class.

Fix:

- Move repeated declarations into classes in an external stylesheet.
- Keep inline style only for runtime values, such as a custom property assignment.

```html
<!-- Dynamic value supplied by the server or by a script -->
<div style="--progress: 62%"></div>
```

### Serve web fonts as WOFF2 with fallback and controlled loading

Fonts are delivered in WOFF2 with a WOFF fallback, and their loading does not hide text
for longer than necessary.

Check:

- Each @font-face rule lists WOFF2 first and WOFF second, and legacy formats such as TTF
  or EOT are absent unless a target requires them.
- font-display is declared, and the primary font is preloaded.

Fix:

- Convert fonts to WOFF2, subset them to the characters the site uses, and keep a WOFF
  source as the fallback.
- Set font-display to swap or optional, and preload the primary font with crossorigin.

```css
@font-face {
  font-family: "Inter";
  src:
    url("/fonts/inter.woff2") format("woff2"),
    url("/fonts/inter.woff") format("woff");
  font-display: swap;
}
```

## Architecture and cascade

### Declare an explicit cascade with layers

The layer order is declared once, so that the winning rule depends on the layer and not
on selector specificity or the order of imports.

Check:

- The main stylesheet declares its layer order near the top, for example reset, base,
  components, and utilities.
- Overrides rely on !important or deeply nested selectors, which layers would make
  unnecessary.
- Unlayered styles are identified, because they outrank every declared layer.

Fix:

- Declare the layer list at the top of the main stylesheet and place each style in the
  matching layer.
- Move third-party and reset styles into the earliest layers.

```css
@layer reset, base, components, utilities;
@layer components {
  .button {
    padding: 0.5rem 1rem;
  }
}
```

### Keep selector specificity low and flat

Selectors stay at the lowest specificity that works, so that overrides do not require
more specific selectors or !important.

Check:

- Find ID selectors used for styling, selectors nested deeper than three levels, and
  declarations marked !important.
- Find overrides that repeat a selector only to win the cascade.

Fix:

- Replace ID selectors with classes, and flatten nested selectors.
- Use :where() for base styles that must remain easy to override, and remove !important
  except for deliberate utility overrides.

### Name classes with one consistent convention

Class names follow a single methodology, so that the purpose of a class is clear from
its name and style collisions are avoided.

Check:

- Class names follow one pattern across the codebase, such as block, block__element, and
  block--modifier.
- Utility classes and JavaScript hooks are distinguishable from component classes, and
  ambiguous names such as active are qualified.

Fix:

- Rename classes to the chosen pattern and update the markup and the selectors together.
- Give JavaScript hooks their own prefix, such as js-, and keep state names explicit,
  such as card--selected.

### Start the cascade from a reset or normalize layer

A reset or normalize stylesheet loads before the project styles, so that browsers share
the same defaults.

Check:

- A reset or normalize stylesheet is loaded before the project styles.
- The framework's built-in reset is not duplicated by a second reset.

Fix:

- Import normalize.css or a modern reset such as CSS Remedy before the custom styles, or
  rely on the framework reset.
- Remove duplicate resets that apply the same defaults twice.

### Define design tokens as custom properties

Repeated colors, spacing values, and type sizes are stored as custom properties on
:root, so that a change in one place propagates to every use.

Check:

- Hard-coded colors, spacing values, and font sizes repeat across the stylesheet.
- Theme values are repeated inside component rules instead of referenced.

Fix:

- Declare repeated values as --name properties on :root and replace the literals with
  var(--name).
- Add a fallback to var() only where the property may be undefined, such as in
  third-party components.

### Register typed custom properties with @property

Custom properties that need a type, an initial value, or animation are registered, so
that the browser can interpolate them and validate their values.

Check:

- Custom properties used in transitions or animations are not registered, so the browser
  cannot interpolate them.
- Typed tokens lack a declared syntax, and tokens meant to be scoped inherit by default.

Fix:

- Add an @property block with syntax, initial-value, and inherits for each animated or
  typed token.
- Set inherits to false for tokens that must not leak into child elements.

```css
@property --accent {
  syntax: "<color>";
  inherits: false;
  initial-value: #2563eb;
}
```

### Remove unused selectors from the shipped stylesheet

The stylesheet delivered to users contains only the selectors that rendered pages use.

Check:

- Run browser coverage analysis on representative pages and measure the share of rules
  that never match.
- Check framework and library bundles for components that the project does not use.

Fix:

- Add PurgeCSS or a comparable tool to the build, with a safelist for classes that are
  generated at runtime.
- Import only the components in use, and repeat the coverage analysis after each
  release.

### Lint stylesheets with Stylelint

Stylesheets are checked by Stylelint in the editor, in the pre-commit hook, and in the
continuous integration pipeline.

Check:

- A Stylelint configuration exists and covers the syntax in use, CSS or SCSS.
- The lint step runs in continuous integration and fails the build on errors.

Fix:

- Install stylelint with stylelint-config-standard, and add
  stylelint-config-standard-scss for SCSS sources.
- Enable auto-fix in the editor and run the linter in the pre-commit hook and in the
  pipeline.

```bash
npm install --save-dev stylelint stylelint-config-standard
npx stylelint "**/*.css"
```

### Replace script-driven class toggling with :has()

A parent is styled from the state of its descendants in CSS, so that the class toggling
logic is removed from JavaScript.

Check:

- JavaScript toggles a class on a parent according to the state or content of a child.
- The selector is supported by the browser targets, which is the case for the Baseline
  since late 2023.

Fix:

- Replace the class toggle with a :has() selector on the parent.
- Keep :has() selectors simple, because complex selectors over large subtrees can be
  costly to evaluate.

```css
.card:has(img) {
  grid-template-columns: 200px 1fr;
}
.form-group:has(input:invalid) label {
  color: #b91c1c;
}
```

## Layout

### Use CSS Grid for two-dimensional layouts

Layouts that control both rows and columns use CSS Grid, which aligns items on both axes
without width hacks.

Check:

- Float or flexbox layouts that fix widths to align rows and columns are candidates for
  grid.
- Named regions could be described with grid-template-areas.

Fix:

- Convert the container to display grid with grid-template-columns and
  grid-template-rows, or grid-template-areas for named regions.
- Use repeat(auto-fill, minmax()) for responsive card grids without media queries.

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  gap: 1.5rem;
}
```

### Apply flexbox sizing rules and gap spacing

One-dimensional layouts use flexbox with explicit sizing, so that items shrink and wrap
predictably and spacing does not depend on margins.

Check:

- Text-containing flex children lack min-width: 0, so long content overflows.
- Spacing between items is created with margins instead of gap.
- Flex shorthand values are used without a clear intent for grow, shrink, and basis.

Fix:

- Add min-width: 0 to flex children that must truncate or wrap.
- Replace inter-item margins with gap, and set flex with explicit grow, shrink, and
  basis values.

### Align nested items with subgrid

Nested grid items use subgrid so that they share the tracks of the parent grid, which
aligns titles, bodies, and footers across cards.

Check:

- Cards in a grid show misaligned titles, bodies, or footers when content lengths
  differ.
- Alignment is currently produced by JavaScript height measurement.

Fix:

- Define the rows of the parent grid, make each card span the tracks it needs, and set
  grid-template-rows to subgrid on the card.

```css
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: auto 1fr auto;
}
.card {
  display: grid;
  grid-row: span 3;
  grid-template-rows: subgrid;
}
```

### Contain layout and paint in self-contained components

Self-contained components declare containment, and long lists skip off-screen rendering,
so that the browser limits the scope of layout and paint work.

Check:

- Independent widgets that do not overflow or affect outside layout are candidates for
  containment.
- Long lists below the fold render without content-visibility.
- Components with contain: paint are checked for clipped focus rings and popovers.

Fix:

- Add contain: layout style paint to independent widgets, and use contain: strict only
  where the size is fixed.
- Apply content-visibility: auto with contain-intrinsic-size to repeated items.

```css
.feed-item {
  content-visibility: auto;
  contain-intrinsic-size: auto 400px;
}
```

### Use logical properties for direction-neutral spacing

Spacing and positioning follow the writing direction, so that one stylesheet serves
left-to-right and right-to-left languages.

Check:

- Physical properties such as margin-left, padding-right, and border-left appear in
  components used in several languages.
- Left and right positioning is used where the layout must mirror in right-to-left
  content.

Fix:

- Replace physical properties with their logical equivalents, such as
  margin-inline-start and padding-block.
- Use a [dir="rtl"] override only for a property that has no logical equivalent.

## Responsive design

### Size text and spacing with relative units

Text and spacing are sized with relative units, so that the layout follows the user font
size and the viewport.

Check:

- Font sizes and padding values in px ignore user font size changes.
- Fixed widths in px prevent components from fitting smaller viewports.

Fix:

- Convert font sizes to rem, and use em for spacing that belongs to a component.
- Use percentages, flex, grid, or clamp() for widths and fluid type, and do not fix the
  root font size.

```css
body {
  font-size: 1rem;
}
h1 {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
}
```

### Respond to container size with container queries

Components adapt to the width of their container, so that they remain correct in
sidebars, grids, and full-width areas.

Check:

- Components with viewport media queries break when placed in a narrow column.
- The container element lacks container-type, so container queries cannot apply.

Fix:

- Set container-type to inline-size on the parent, and name it when several containers
  are nested.
- Replace viewport breakpoints inside the component with @container rules.

```css
.card-wrap {
  container-type: inline-size;
}
@container (min-width: 30rem) {
  .card {
    display: grid;
    grid-template-columns: 1fr 2fr;
  }
}
```

### Prevent horizontal scrolling at 320 CSS pixels

Content reflows within a 320 CSS pixel viewport, so that no page requires horizontal
scrolling at 400 percent zoom (WCAG 1.4.10).

Check:

- Test the page at a 320-pixel viewport width and look for horizontal overflow.
- Look for fixed px widths, width: 100vw on full-width elements, white-space: nowrap,
  and long unbreakable strings.
- Check that images and video have max-width: 100%.

Fix:

- Replace fixed widths with max-width, and set max-width: 100% with height: auto on
  images and video.
- Add overflow-wrap: break-word to text containers and replace 100vw with 100%. Confine
  wide data tables to a container with overflow-x: auto.

```css
img,
video {
  max-width: 100%;
  height: auto;
}
.table-wrap {
  overflow-x: auto;
}
```

## Typography and color

### Keep body text at a readable size with relative units

Body text on mobile is 1rem or larger, and sizes are relative, so that text scales with
the user preference and with zoom (WCAG 1.4.4).

Check:

- Body or paragraph text is below 1rem on mobile.
- Any font size is below 0.75rem, except for captions and footnotes that are
  deliberately small.
- The html or body element sets a fixed px font size that overrides the browser default,
  or the layout breaks at 200 percent zoom.

Fix:

- Convert pixel sizes to rem by dividing by 16, for example 14px becomes 0.875rem.
- Keep the root font size at 100 percent, so that the user default is respected.

```css
html {
  font-size: 100%;
}
body {
  font-size: 1rem;
  line-height: 1.5;
}
```

### Define color palettes in oklch

Palettes are defined in oklch, so that a fixed change in lightness produces a similar
perceived change across hues and states.

Check:

- Color tokens use hex or hsl values, and equal lightness steps look different across
  hues.
- Hover and active states are derived with ad hoc adjustments.

Fix:

- Convert the tokens to oklch(L C H) and keep the L steps consistent across hues.
- Add wide-gamut variants behind @media (color-gamut: p3) where they add value, and
  recheck contrast after the conversion.

```css
:root {
  --brand-500: oklch(60% 0.19 255);
  --brand-600: oklch(52% 0.19 255);
}
```

### Support dark mode with semantic color tokens

Dark mode is produced by redefining semantic tokens, so that components do not change
and the user preference is respected.

Check:

- The stylesheet uses prefers-color-scheme or a data-theme pattern.
- Hard-coded colors in components remain and do not adapt to the dark theme.
- Contrast meets the WCAG thresholds in both themes.

Fix:

- Define semantic tokens such as --color-surface on :root, and redefine them in an
  @media (prefers-color-scheme: dark) block.
- Support a manual choice with a data-theme attribute, store the preference, and test
  contrast in both themes.

```css
:root {
  --color-surface: #ffffff;
  --color-text: #111827;
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-surface: #111827;
    --color-text: #f9fafb;
  }
}
```

## Motion and transitions

### Animate only transform and opacity

Motion uses transform and opacity, which the browser can composite without recalculating
layout, so that animations stay smooth while the main thread is busy.

Check:

- Animations or transitions target top, left, width, height, margin, or padding.
- Animated elements are disabled or reduced under prefers-reduced-motion.

Fix:

- Replace position changes with translate() and size changes with scale().
- Use will-change sparingly, and wrap motion in a prefers-reduced-motion check.

```css
.panel {
  transition:
    transform 200ms ease-out,
    opacity 200ms;
}
.panel.is-open {
  transform: translateY(0);
  opacity: 1;
}
```

### Animate page and state changes with view transitions

Changes between page states are animated by the View Transitions API, which removes the
need for a JavaScript animation library for these effects.

Check:

- A JavaScript animation library is used only to cross-fade between states or pages.
- Transition animations are disabled for users who prefer reduced motion.

Fix:

- Wrap DOM updates in document.startViewTransition() for same-page changes.
- Use @view-transition { navigation: auto } for cross-document navigation, and
  view-transition-name on elements that should animate individually.

```css
@view-transition {
  navigation: auto;
}
.hero-image {
  view-transition-name: hero;
}
```

## Accessibility and output

### Keep a visible focus indicator

Keyboard users can always see which element has focus, because the default outline is
never removed without a visible replacement (WCAG 2.4.7).

Check:

- Find outline: none or outline: 0 on interactive elements, and confirm that each has a
  visible replacement on :focus-visible.
- Replacement rings meet a 3:1 contrast ratio against adjacent colors (WCAG 1.4.11), and
  they are not clipped by overflow: hidden or misplaced by missing positioning.

Fix:

- Use :focus-visible with an outline of at least 2px and a positive outline-offset.
- Anchor pseudo-element rings to the interactive element, and remove overflow clipping
  from ancestors that contain the ring.

```css
:focus-visible {
  outline: 2px solid #1d4ed8;
  outline-offset: 2px;
}
```

### Avoid interstitials that cover the content

Pop-ups and overlays do not hide the main content on load, and required dialogs manage
focus and can be dismissed from the keyboard.

Check:

- Fixed or absolutely positioned overlays with a high z-index appear on load and cover
  most of the content on small screens.
- Each dialog has a labelled close control, can be dismissed with Escape, moves focus
  inside when opened, and returns focus to the trigger when closed.

Fix:

- Replace load-time overlays with banners or inline panels, and show pop-ups only after
  a user action.
- Implement the dialog pattern with role="dialog", aria-modal="true", a focus trap, and
  focus restoration. Keep legally required notices small.

### Provide a print stylesheet

Printed pages contain the content without interactive chrome, and their type and page
breaks suit paper.

Check:

- A print stylesheet is linked with media="print" or applied inside an @media print
  block.
- Navigation, ads, and controls are hidden, and page breaks do not separate headings
  from their text.
- External link destinations are visible in the printed output.

Fix:

- Hide navigation and controls in @media print, set body text in a serif face with pt
  units, and avoid breaks after headings.
- Print external URLs after links whose text does not contain them.

```css
@media print {
  .no-print,
  nav,
  aside {
    display: none;
  }
  a[href^="http"]::after {
    content: " (" attr(href) ")";
  }
}
```
