# Performance

This file describes the 44 rules classified under the performance category of the
front-end practices catalogue. For each rule it states the condition to verify, how to
check it in a page, route, or build configuration, and how to correct it. The skill
loads this file as the reference for performance checks and fixes. Numeric values are
cited with their basis: either a named standard (Core Web Vitals or web.dev guidance) or
a heuristic of the rule itself, which is labelled as such. Several rules carry the
performance category for their operational effect but are chiefly concerned with
security, consent, or process; their statements say so where relevant.

## Rule index

| Rule                        | Priority | Difficulty   | Rule statement                                                                                    |
| --------------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------- |
| `largest-contentful-paint`  | critical | intermediate | The largest visible element should render within the good LCP range of 2.5 s.                     |
| `back-forward-cache`        | high     | advanced     | Pages should stay eligible for the back/forward cache and restore correctly from it.              |
| `browser-caching`           | high     | intermediate | Each resource type should send cache headers that match how often it changes.                     |
| `cdn`                       | high     | intermediate | Static assets should be served from edge locations near the user.                                 |
| `compression`               | high     | beginner     | Text resources should be transferred with gzip or Brotli encoding.                                |
| `consent-mode`              | high     | intermediate | Google Consent Mode v2 should send accurate consent states so tags respect them.                  |
| `critical-request-chains`   | high     | advanced     | Requests needed before first render should form a shallow dependency chain.                       |
| `cumulative-layout-shift`   | high     | intermediate | Content should not move unexpectedly, keeping CLS at or below 0.1.                                |
| `first-contentful-paint`    | high     | intermediate | The first text or image should paint within the good FCP range of 1.8 s.                          |
| `font-loading`              | high     | intermediate | Web fonts should be discovered early, show a fallback, and use compact formats.                   |
| `http-requests`             | high     | intermediate | The initial page should issue a modest number of requests.                                        |
| `http2`                     | high     | intermediate | Resources should be delivered over HTTP/2 or HTTP/3 along the whole path.                         |
| `import-on-interaction`     | high     | intermediate | Code needed only after a user action should load when that action occurs.                         |
| `import-on-visibility`      | high     | intermediate | Modules for offscreen sections should load shortly before those sections appear.                  |
| `interaction-to-next-paint` | high     | advanced     | Interactions should produce a visual response within the good INP threshold of 200 ms.            |
| `lazy-loading`              | high     | beginner     | Offscreen images, iframes, and heavy embeds should load only when approaching view.               |
| `list-virtualization`       | high     | intermediate | Long collections should render only the visible rows plus a small buffer.                         |
| `loading-indicators`        | high     | beginner     | Asynchronous work should show immediate, accessible feedback without layout jumps.                |
| `page-load-time`            | high     | intermediate | The full page should finish loading within the heuristic 3-second target of the rule.             |
| `page-weight`               | high     | beginner     | Transferred page weight should stay under the heuristic budget of 1,500 KB, ideally under 500 KB. |
| `resource-hints`            | high     | intermediate | Preload, prefetch, and preconnect hints should target only assets the route needs.                |
| `third-party-scripts`       | high     | intermediate | Third-party scripts should load late, conditionally, or not at all.                               |
| `video-optimization`        | high     | intermediate | Video should be encoded and sized for its real playback context.                                  |
| `animated-content`          | medium   | intermediate | Large animated GIFs should be replaced by MP4 or WebM video with a poster.                        |
| `browser-required`          | medium   | intermediate | Performance audits should run in a real browser under throttled conditions.                       |
| `css-file-size`             | medium   | intermediate | Stylesheets should be minified and free of unused rules.                                          |
| `dom-size`                  | medium   | intermediate | The DOM should stay small and shallow, mounting optional content only when needed.                |
| `duplicate-js`              | medium   | intermediate | Each JavaScript library should ship in a single version.                                          |
| `fetchpriority-attribute`   | medium   | beginner     | The LCP resource should be marked high and competing resources marked low.                        |
| `gtm-present`               | medium   | intermediate | A tag container should load asynchronously and fire only the tags it needs.                       |
| `js-file-size`              | medium   | intermediate | JavaScript should be split and tree-shaken into modest compressed bundles.                        |
| `js-libraries`              | medium   | intermediate | Dependencies should be free of known vulnerabilities and avoid unnecessary weight.                |
| `js-redirects`              | medium   | intermediate | Redirects should be issued by the server or edge, not by client scripts.                          |
| `lazy-above-fold`           | medium   | intermediate | Images in the initial viewport should not be lazy-loaded.                                         |
| `legacy-js`                 | medium   | intermediate | Modern browsers should receive modern code without legacy transpilation.                          |
| `preconnect`                | medium   | intermediate | Preconnect should be limited to third-party origins the first view needs now.                     |
| `render-blocking`           | medium   | intermediate | Only assets required for first paint should block rendering.                                      |
| `service-worker`            | medium   | intermediate | A service worker should cache static assets with versioning and cleanup.                          |
| `source-maps`               | medium   | intermediate | Source maps should reach error tooling without being publicly served.                             |
| `streaming-html`            | medium   | advanced     | Server-rendered HTML should be flushed in chunks before slow data resolves.                       |
| `ttfb`                      | medium   | intermediate | The server should send the first byte of HTML within 800 ms.                                      |
| `offline-fallback`          | low      | beginner     | Failed navigations offline should show a custom, self-contained page.                             |
| `speculation-rules`         | low      | intermediate | Likely next pages should be prefetched or prerendered with conservative scope.                    |

## Critical rendering path

### Optimize largest contentful paint

The largest visible element of a route should render within 2.5 seconds, the good range
for LCP defined by Core Web Vitals.

Check:

- Identify the LCP element in a DevTools performance trace or PageSpeed Insights.
- Confirm the element is not lazy-loaded and is discoverable in the initial HTML.
- Classify the delay as slow server response, late discovery, heavy transfer, render
  delay, or incorrect priority.

Fix:

- Preload the LCP resource on the current route and mark it high priority.
- Render the LCP candidate on the server where possible, instead of after a client
  fetch.
- Reduce time to first byte when the HTML itself arrives late.

### Optimize first contentful paint

The first text or image should paint within 1.8 seconds, the good range for FCP in
web.dev guidance.

Check:

- Measure FCP for the route in Lighthouse or from field data.
- List the stylesheets, synchronous scripts, and fonts that precede the first paint in
  the waterfall.

Fix:

- Remove or defer blocking resources and inline the CSS needed for the first screen.
- Preconnect to the origins that the first view depends on.

### Eliminate render-blocking resources

Only assets needed for first paint should block the parser or the renderer.

Check:

- Find synchronous scripts in the document head and CSS loaded through nested `@import`
  chains.
- Determine which of these assets the first screen actually uses.

Fix:

- Add `defer` or `async` to scripts that do not contribute to the first paint.
- Keep inline critical CSS minimal and load the remaining stylesheets without blocking.

```html
<script src="/app.js" defer></script>
<link rel="stylesheet" href="/rest.css" media="print" onload="this.media='all'" />
```

### Minimize critical request chains

Dependent requests needed before first render should form as shallow a chain as
possible.

Check:

- Trace the initiator chain in the network waterfall, such as HTML to CSS to font.
- Look for `@import` rules and scripts that inject other scripts before rendering.

Fix:

- Replace `@import` with HTML link elements, or inline small critical stylesheets.
- Preload deep critical resources, such as fonts, so they are discovered from the HTML.
  The rule suggests a chain depth of two or three as a heuristic.

### Use fetchpriority to hint resource loading priority

The `fetchpriority` attribute should mark the LCP resource as high and resources that
compete with it as low.

Check:

- Confirm the LCP image carries `fetchpriority="high"` and is not lazy-loaded.
- Flag pages with more than one or two high-priority resources, a heuristic of the rule,
  since the hint loses its meaning when applied broadly.

Fix:

- Set `fetchpriority="high"` on the single most important resource per route.
- Set `fetchpriority="low"` on offscreen images, prefetch links, and non-critical
  scripts.

```html
<img src="/hero.webp" alt="Product overview" fetchpriority="high" />
```

### Disable lazy loading for above-the-fold content

Images in the initial viewport should load eagerly and with high priority.

Check:

- Search for `loading="lazy"` on images at the top of the page, including hero and LCP
  candidates.
- Check mobile as well as desktop layouts, since an image may be visible on only one.

Fix:

- Remove `loading="lazy"` from above-the-fold images.
- Apply `fetchpriority="high"` to the primary image. The rule suggests not lazy-loading
  the first two or three images of a list as a heuristic.

### Implement lazy loading for offscreen content

Offscreen images, iframes, and heavy embeds should defer loading until they approach the
viewport.

Check:

- Find offscreen images, iframes, and video embeds that load eagerly without reason.
- Flag an element only when its offscreen position is clear from the markup or route
  layout; otherwise the finding is not established.

Fix:

- Add `loading="lazy"` with explicit `width` and `height` to offscreen images and
  iframes.
- Use an Intersection Observer with a modest root margin, around 200 to 400 px as a
  heuristic, for custom deferral.

### Keep page load time under 3 seconds

The full page should finish loading within 3 seconds on a standard connection. This is a
heuristic target stated by the rule, not a published standard.

Check:

- Measure load time with throttled conditions in Lighthouse or WebPageTest.
- Identify which phase, server, transfer, script execution, or render, dominates.

Fix:

- Apply the fixes for the dominant phase, such as caching, compression, or reduced
  JavaScript, from the related rules in this file.
- Add a load-time budget to continuous integration so regressions are detected.

## Resource hints and discovery

### Use resource hints for faster loading (resource-hints)

Preload, prefetch, preconnect, and dns-prefetch hints should accelerate only the assets
that the route needs.

Check:

- List the existing hints and confirm each targets an asset used on the current route or
  on the next likely navigation.
- Verify that `as` and `crossorigin` are set correctly for fonts and CORS resources.

Fix:

- Preload late-discovered critical assets of the current route, keeping the count to
  roughly three to five per route as a heuristic.
- Prefetch the likely next navigation rather than the current page, and remove hints for
  speculative third parties.

### Use preconnect for critical third-party origins

Preconnect should be declared only for third-party origins that the first view needs
immediately.

Check:

- Confirm that each preconnected origin receives a request on the initial route.
- Flag preconnects to origins used only after an interaction, since they hold
  connections without benefit.

Fix:

- Keep preconnect for two to four high-value origins, such as a font host or the hero
  media CDN; the count of two to four is a heuristic.
- Use `dns-prefetch` for origins that may be used later, and add `crossorigin` to CORS
  fetches such as fonts.

## Network delivery and caching

### Reduce Time to First Byte (TTFB)

The server should send the first byte of HTML within 800 ms, the good threshold for TTFB
in web.dev guidance.

Check:

- Measure TTFB separately for cache hits and cache misses in DevTools or WebPageTest.
- Inspect server traces for slow queries, synchronous work before the first byte, and
  repeated upstream calls.

Fix:

- Cache HTML or API responses at the edge where content permits, and reduce origin work
  for the common path.
- Select only the columns a query needs, index filtered columns, and avoid blocking
  upstream fetches before the response starts.

### Enable HTTP/2 or HTTP/3

Resources should be delivered over HTTP/2 or HTTP/3 along the whole delivery path.

Check:

- Check the Protocol column in the DevTools network panel for every origin, including
  CDN and edge hosts.
- Confirm that the origin, edge, and load balancer all negotiate the newer protocol.

Fix:

- Enable HTTP/2 on the TLS listener of the web server, since browsers require HTTPS for
  it.
- Stop sharding assets across domains, which defeats multiplexing, and do not
  concatenate files solely for HTTP/1.1 benefits.

### Minimize HTTP requests

The initial page should issue a modest number of requests. The rule uses about 50 as a
heuristic target.

Check:

- Count requests for the initial route in the network panel and list the smallest ones.
- Look for many tiny icons, duplicated scripts, and resources that are never used.

Fix:

- Combine icons into an SVG sprite and inline very small critical assets.
- Remove unused resources, and reduce request count only where it changes the waterfall,
  since multiplexing already reduces its cost.

### Use a content delivery network

Static assets should be served from edge locations close to the user.

Check:

- Check response headers of static assets for CDN indicators, such as `cf-ray` or
  `x-amz-cf-id`.
- Compare latency from distant regions with and without the CDN.

Fix:

- Place static assets and cacheable HTML behind a CDN, with correct origin cache
  headers.
- Verify the cache hit ratio in the CDN dashboard after the change.

### Enable browser caching

Each resource type should send cache headers that match how often it changes.

Check:

- Inspect `Cache-Control` and `ETag` headers on static, hashed, and HTML responses.
- Confirm that repeat visits are served from disk or memory cache in the network panel.

Fix:

- Use a long `max-age` with `immutable` for hashed assets, and `must-revalidate` for
  HTML.
- Keep personal or sensitive responses private or `no-store`.

```text
hashed assets: Cache-Control: public, max-age=31536000, immutable
HTML:          Cache-Control: public, max-age=0, must-revalidate
```

### Enable text-based compression

HTML, CSS, JavaScript, JSON, and SVG should be transferred with gzip or Brotli encoding.

Check:

- Confirm that the `Content-Encoding` header of text responses is `gzip` or `br`.
- Confirm that images and video are not compressed a second time.

Fix:

- Enable Brotli with gzip as fallback on the web server or CDN, and pre-compress static
  files during the build.
- Keep on-the-fly compression levels moderate, since high levels raise origin TTFB.

### Avoid JavaScript-based redirects

Redirects should be issued by the server or the edge with a 3xx status, not by client
scripts.

Check:

- Search for `window.location` assignments that run on page load.
- Use `curl -I` or the network panel to confirm the redirect status of the URL.

Fix:

- Replace client-side redirects with 301 or 302 responses from the server or edge.
- Use a meta refresh only as a last resort, since it still adds a round trip.

### Stream HTML to the browser before the full response is ready

Server-rendered pages should flush the application shell and above-the-fold HTML before
slow data resolves.

Check:

- Find `renderToString` calls or handlers that await every query before sending the
  first byte.
- Check whether slow, data-dependent components sit inside a Suspense boundary or an
  equivalent mechanism.

Fix:

- Use `renderToPipeableStream` with an `onShellReady` callback, or a `ReadableStream`,
  so the shell is sent early.
- Give each independently slow section its own boundary, and ensure proxies do not
  buffer the response.

## Asset weight

### Keep page weight under 1500KB

Total transferred page weight should stay under 1,500 KB and ideally under 500 KB. Both
values are heuristics of the rule.

Check:

- Sum transferred bytes by resource type in the network panel or with a Lighthouse
  budget.
- Identify images, JavaScript, and fonts as the usual largest contributors.

Fix:

- Serve modern image formats at the displayed dimensions, using responsive sources.
- Split and trim JavaScript and CSS, and add a byte budget to continuous integration.

### Optimize CSS file size

Stylesheets should be minified and free of unused rules, because CSS blocks rendering.

Check:

- Use the DevTools coverage view to measure the share of unused CSS on the route.
- Flag stylesheets that exceed about 50 KB compressed, a heuristic of the rule.

Fix:

- Remove unused selectors during the build with a tool such as PurgeCSS, and minify with
  a tool such as cssnano.
- Split stylesheets by route, and avoid loading an entire framework for a few
  components.

### Convert animated GIFs to video

Large animated GIFs should be replaced by MP4 or WebM video with a poster image.

Check:

- Find GIF assets that are larger than a few hundred pixels or longer than about one
  second, using these figures as heuristic thresholds of the rule.
- Confirm the animation has an accessible text alternative.

Fix:

- Convert the GIF to WebM and MP4, and use a video element with `autoplay`, `loop`,
  `muted`, and `playsinline`.
- Provide a `poster` and an accessible description for the animation.

```html
<video autoplay loop muted playsinline poster="anim.jpg" aria-label="Animation">
  <source src="anim.webm" type="video/webm" />
  <source src="anim.mp4" type="video/mp4" />
</video>
```

### Optimize and compress web videos

Video should be encoded and sized for its real playback context and should not download
in full before it is needed.

Check:

- Compare the delivered resolution with the rendered player size, and flag sources much
  larger than the player.
- Check audio tracks on muted background video, the `preload` attribute, and the
  presence of a poster image.

Fix:

- Re-encode to a sensible resolution and codec, ordering sources from most to least
  efficient, such as AV1 or VP9 in WebM before H.264 in MP4.
- Strip audio from silent loops, set `preload` to `metadata` or `none` below the fold,
  and add a poster.

### Optimize web font loading

Web fonts should be discovered early, render text immediately with a fallback, and use
compact formats.

Check:

- Confirm that each `@font-face` declares a `font-display` value and that text does not
  stay invisible during loading.
- Check whether the critical font is preloaded and served as WOFF2.

Fix:

- Use `font-display: swap` with fallback metrics matched to the web font, to limit
  layout shift.
- Preload the one or two critical font files, subset them to the characters used, and
  self-host them.

## JavaScript cost

### Optimize JavaScript bundle size

JavaScript should be split and tree-shaken so that each bundle stays within a modest
compressed size. The rule uses 200 KB compressed as a heuristic.

Check:

- Inspect compressed bundle sizes in the build report or a bundle analyzer.
- Flag large bundles that load on routes which do not use them.

Fix:

- Split code by route and load heavy components with dynamic `import()`.
- Import only the functions needed from large libraries, so the bundler can remove
  unused exports.

### Remove duplicate JavaScript libraries

Each library should appear in the shipped code in a single version.

Check:

- Run `npm ls` or `pnpm why` for the package and inspect the bundle for repeated
  modules.
- Look for the same library loaded both from a CDN and from the bundle.

Fix:

- Align version ranges and use overrides or deduplication to force one resolved version.
- Remove the duplicate script tag or CDN copy when the bundle already includes the
  library.

### Use secure and up-to-date JS libraries

Dependencies should be free of known vulnerabilities and should not add heavy packages
where a lighter option covers the need. The rule is mainly a security check.

Check:

- Run the package manager's audit command against the lockfile.
- Review large dependencies, such as date or utility libraries, for lighter options.

Fix:

- Upgrade or replace vulnerable packages, and run the audit in continuous integration.
- Prefer modular imports, or native APIs such as `Intl` and `fetch`, where they suffice.

### Avoid serving legacy JavaScript to modern browsers

Modern browsers should receive native syntax and only the polyfills they require.

Check:

- Inspect the build output for transpiled syntax and polyfill blocks that modern
  browsers do not need.
- Check the browserslist target and whether module and nomodule scripts are used.

Fix:

- Set the build target and browserslist to the modern browsers the project supports.
- Serve module bundles to modern browsers, and use a nomodule bundle only where legacy
  support is required.

```html
<script type="module" src="/modern.js"></script>
<script nomodule src="/legacy.js"></script>
```

### Load non-critical code on user interaction

Code used only after a click, focus, hover, or similar action should load at that
moment.

Check:

- Find heavy modules imported statically for features opened by a user action, such as
  editors, maps, or export tools.
- Verify that the initial route works without them.

Fix:

- Replace the static import with a dynamic `import()` inside the event handler.
- Show immediate feedback while the chunk loads, and reuse the module afterwards.

```javascript
button.addEventListener("click", async () => {
  const { openEditor } = await import("./editor.js");
  openEditor();
});
```

### Load non-critical code when content approaches the viewport

Modules for offscreen sections should load shortly before those sections scroll into
view.

Check:

- Find offscreen components, such as charts or review lists, that are bundled into the
  first load.
- Confirm that the section reserves its height, so late loading does not shift layout.

Fix:

- Observe a placeholder with an Intersection Observer and import the module when it
  intersects, using a root margin of roughly 300 to 1000 px as a heuristic.
- Disconnect the observer after the first load, and keep the placeholder at a stable
  height.

## Third-party and tag management

### Optimize third-party script loading

Third-party scripts should load late, conditionally, or not at all, so that they do not
compete with critical content.

Check:

- List the third-party scripts on the route and mark those needed before first paint.
- Look for parser-blocking vendor tags in the head and for long tasks attributed to
  vendor code.

Fix:

- Use `async` or `defer` for independent vendors, and load chat, review, and video
  widgets on idle, visibility, or interaction.
- Replace heavy embeds with a lightweight facade that loads the real player on click.

### Optimize Google Tag Manager implementation

The container should load asynchronously and fire only the tags each page needs.

Check:

- Confirm that the container snippet loads its script asynchronously.
- Review triggers, particularly All Pages triggers that fire many tags on every load.

Fix:

- Remove unused tags, and move non-critical tags to later triggers such as Window Loaded
  or a custom event.
- Consider server-side tagging for tags that do not need to run in the browser.

### Implement Google Consent Mode v2

Consent states should default to denied where regulation requires it and update once the
visitor decides, so that tags respect the choice. The rule is primarily a privacy
compliance check.

Check:

- Confirm that a default consent command runs before the tag container loads.
- Verify with a tag debugger that consent parameters in outgoing requests change after
  an update.

Fix:

- Set defaults to denied in regulated regions before any tag loads, with a short
  `wait_for_update` grace period.
- Send the update as soon as the consent management platform records a choice, and never
  hard-code granted consent.

## Rendering and interactivity

### Minimize cumulative layout shift

Layout should remain stable, keeping the CLS score at or below 0.1 as defined by Core
Web Vitals.

Check:

- Measure CLS in Lighthouse or from field data, and locate the shifting elements in the
  performance panel.
- Look for images and embeds without dimensions, banners injected above content, and web
  fonts that change text metrics.

Fix:

- Set `width` and `height` or an aspect ratio on images and embeds, and reserve space
  for ads and dynamic blocks.
- Animate `transform` and `opacity` rather than layout properties, and insert new
  content below existing content.

### Optimize interaction to next paint

Interactions should produce a visible response within 200 ms, the good threshold for INP
defined by Core Web Vitals.

Check:

- Identify slow interactions with the INP attribution in DevTools or in field reports.
- Look for long tasks above 50 ms, a heuristic threshold of the rule, in event handlers
  and for forced layout reads interleaved with writes.

Fix:

- Split long work into smaller chunks that yield to the main thread, or move heavy
  computation to a Web Worker.
- Batch DOM reads before writes, and mark non-urgent state updates as transitions.

### Reduce DOM size and complexity

The DOM should stay small and shallow, with hidden or repeated content mounted only when
needed.

Check:

- Count nodes with `document.querySelectorAll('*').length` and measure the maximum
  depth.
- Compare against the rule's heuristics of about 1,500 nodes and a depth of 32.

Fix:

- Remove wrapper elements that carry no meaning, while keeping headings, lists, and
  table structure intact.
- Mount drawers, tabs, and modals only when shown, and paginate or virtualize large
  collections.

### Virtualize long lists and tables

Large collections should render only the visible rows plus a small overscan buffer.

Check:

- Review views that render more than roughly 100 to 200 repeated items at once, a
  heuristic of the rule.
- Confirm scrolling jank or a large node count in a trace before adopting
  virtualization.

Fix:

- Use a windowing library such as react-window, with fixed or measured row sizes.
- Keep keyboard navigation, focus, selection, and table semantics working inside the
  virtualized list.

### Show loading indicators

Asynchronous work should show immediate, accessible feedback without causing layout
jumps.

Check:

- Trigger each asynchronous action and confirm that a loading state appears at once.
- Verify that status regions announce progress and that busy regions expose `aria-busy`
  or an equivalent attribute.

Fix:

- Use skeletons for content areas and spinners or disabled states for actions, with
  `role="status"` and a text label.
- Reserve the final content height so that the indicator does not cause a layout shift.

## Navigation and offline

### Optimize pages for back/forward cache

Pages should remain eligible for the back/forward cache and restore correctly from it.

Check:

- Search for `unload` listeners and for `beforeunload` listeners that are attached
  unconditionally.
- Check whether `pageshow` handling refreshes state only when `event.persisted` is true.

Fix:

- Replace `unload` with `pagehide` for teardown work, and use `pageshow` for resume
  work.
- Attach `beforeunload` only while a form has unsaved changes, and verify eligibility in
  DevTools.

### Register a service worker for caching and offline support

A service worker should cache static assets under versioned caches and remove old caches
on activation, without storing personal responses.

Check:

- Confirm that the worker is active and that install and activate handlers exist.
- Confirm that caching is limited to idempotent GET requests and excludes user-specific
  data.

Fix:

- Pre-cache a small set of critical assets during install, and bump the cache version
  when cached assets change in incompatible ways.
- Use cache-first for hashed assets, network-first for navigations, and
  stale-while-revalidate for other data, or delegate these to Workbox.

### Provide an offline fallback page

When a navigation fails offline, the user should see a custom, self-contained page
instead of the browser's generic error.

Check:

- Disconnect the network in DevTools and navigate to an uncached route.
- Verify that the offline page has no external dependencies.

Fix:

- Pre-cache the offline page during install, and return it only for failed navigation
  requests.
- Inline its styles and images so that it renders entirely from the cache.

### Use the Speculation Rules API to prefetch and prerender navigations

Likely next pages should be prefetched or prerendered through declarative rules whose
scope excludes sensitive or side-effecting URLs.

Check:

- Confirm that the rules exclude logout, authenticated mutation pages, and API routes.
- Check the speculative loads panel in DevTools for the status of each candidate.

Fix:

- Start with prefetch and moderate eagerness, and use prerender only for one
  high-confidence next step.
- Confirm that analytics does not count prerendered views that the user never sees.

## Measurement and tooling

### Perform browser-based performance audits

Performance audits should run in a real browser with throttled network and CPU, so that
rendering metrics are captured.

Check:

- Confirm that the audit pipeline executes a browser engine, not only static analysis of
  the source.
- Confirm that the audit profile includes mobile emulation and throttling.

Fix:

- Add a Lighthouse or Playwright audit for key routes to continuous integration, with
  throttling enabled.
- Compare results from several device profiles or regions before drawing conclusions.

### Provide source maps for production debugging

Production builds should generate source maps that error tooling can read without
publishing them on the public site.

Check:

- Confirm that the build produces source maps and that the public path does not serve
  them.
- Confirm that the error tracker applies the maps to a test error.

Fix:

- Generate hidden source maps and upload them to the error tracking service during
  deployment.
- Remove the map files from the public output after the upload.
