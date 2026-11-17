# Images and Media

This file defines the image and media rules of the front-end practices skill. It covers
the accessibility of image markup, dimensions and loading behaviour, responsive
delivery, format and compression choices, vector and sprite assets, and fallback
handling for images that fail. It is the reference that the skill loads when it checks
these rules in a codebase and when it proposes fixes for them.

## Rule index

| Rule               | Priority | Difficulty   | Rule statement                                                                              |
| ------------------ | -------- | ------------ | ------------------------------------------------------------------------------------------- |
| alt-text           | critical | beginner     | Informative images carry meaningful alt text, and decorative images use an empty alt value. |
| broken-images      | high     | beginner     | Image sources resolve to existing files, and build or runtime failures are caught.          |
| critical-images    | high     | beginner     | The LCP image is loaded with high fetch priority and is never lazy-loaded.                  |
| dimensions         | high     | beginner     | Every img element declares width and height that match its intrinsic aspect ratio.          |
| image-cdn          | high     | intermediate | Images are delivered through a CDN that transforms and caches them at the edge.             |
| image-compression  | high     | beginner     | Raster images are compressed to a quality that removes bytes without visible artefacts.     |
| image-file-size    | high     | intermediate | Image files stay within documented size budgets appropriate to their role.                  |
| image-optimization | high     | intermediate | The image pipeline combines format, compression, sizing, and metadata handling.             |
| modern-format      | high     | intermediate | Modern formats are served where supported, with a universally supported fallback.           |
| offscreen-lazy     | high     | beginner     | Images below the fold defer loading with native lazy loading, except critical images.       |
| optimized          | high     | intermediate | Served images carry no unnecessary metadata and use efficient encoder settings.             |
| picture-element    | high     | beginner     | Each picture element ends with an img fallback that carries the image attributes.           |
| responsive-images  | high     | intermediate | Images rendered at several sizes offer srcset candidates and a matching sizes value.        |
| responsive-size    | high     | intermediate | Images are delivered at a pixel size close to the size at which they are rendered.          |
| srcset             | high     | intermediate | Images wider than about 100 pixels offer srcset width candidates.                           |
| webp-format        | high     | beginner     | Raster images are delivered as WebP with a JPEG or PNG fallback.                            |
| avif-format        | medium   | intermediate | AVIF is offered as the most efficient source, with WebP and JPEG as fallbacks.              |
| figure-figcaption  | medium   | beginner     | Images with visible captions are grouped with figure and figcaption elements.               |
| retina-display     | medium   | intermediate | Fixed-size raster images provide 2x variants for high-density screens.                      |
| svg-inline         | medium   | intermediate | Inline SVG is kept small and used only where interactivity requires it.                     |
| svg-optimization   | medium   | beginner     | SVG files are cleaned of editor metadata while keeping viewBox and accessibility data.      |
| error-images       | low      | beginner     | Images that fail at runtime show a meaningful fallback instead of a broken icon.            |
| filename-quality   | low      | beginner     | Image filenames are descriptive, lowercase, and separated by hyphens.                       |
| progressive-jpeg   | low      | beginner     | JPEG files that remain in use are encoded progressively.                                    |
| sprite-generation  | low      | intermediate | Small icons are combined into sprites or symbol sets where that reduces requests.           |

## Accessibility and semantics

### Alt text for images

Every informative image needs an alt attribute that conveys the purpose of the image in
its context, while decorative images carry an empty alt value so that assistive
technology skips them.

Check:

- Every img element has an alt attribute; a missing attribute is a defect.
- Alt values are not file names or generic words such as "image" or "photo".
- Linked images describe the destination, and images of text repeat that text.

Fix:

- Describe the information the image conveys, not its appearance alone.
- Set alt="" on decorative images instead of omitting the attribute.
- For charts, pair a short alt with a longer description linked from the page.

```html
<img src="sales.png" alt="Bar chart: Q3 sales rose 40% year over year" />
<img src="divider.svg" alt="" />
```

### Figure and figcaption captions

A visible caption that belongs to an image is marked up with figure and figcaption, so
that the association is exposed to assistive technology and to search engines.

Check:

- Captions placed beside an img element are plain paragraphs or spans outside a figure.
- A figcaption is placed between other children of its figure element.
- The alt text repeats the caption word for word instead of complementing it.

Fix:

- Wrap the img and its caption in a figure, with figcaption as first or last child.
- Keep the alt text short, because the caption already supplies visible context.
- Reserve figure for content that has a caption or is self-contained.

```html
<figure>
  <img src="harbour.jpg" alt="Fishing boats at a harbour wall at dusk" />
  <figcaption>Harbour at Ribeira, autumn 2024</figcaption>
</figure>
```

## Dimensions and loading

### Explicit width and height

Every img element declares width and height attributes that match its intrinsic aspect
ratio, which lets the browser reserve space before the file arrives and keeps layout
shift low.

Check:

- Templates and components render img elements without width or height attributes.
- Attribute values do not match the aspect ratio of the file.
- Tiny decorative SVGs and containers that already reserve stable space are exempt.

Fix:

- Add the intrinsic pixel dimensions as attributes and keep CSS max-width at 100 percent
  with height set to auto.
- When the size is unknown at authoring time, reserve space with aspect-ratio on a
  wrapper element.
- Confirm the result with layout shift regions in the DevTools Rendering panel.

```html
<img src="team.jpg" alt="Team at a whiteboard" width="800" height="450" />
```

### Offscreen lazy loading

Images positioned below the initial viewport defer their download with the native lazy
attribute, while images visible on first load do not.

Check:

- Below-the-fold img elements lack loading="lazy". Report this only when the position
  can be inferred from the markup or the surrounding component.
- Header logos, heroes, or first visible items carry loading="lazy".
- Images with loading="eager" sit far below the fold without a stated reason.

Fix:

- Add loading="lazy" to below-the-fold images, keeping their width and height.
- Remove loading="lazy" from the hero, the logo, and the first visible item.
- Pair the first visible large image with fetchpriority="high" rather than deferral.

```html
<img src="hero.jpg" alt="Hero" width="1200" height="600" fetchpriority="high" />
<img src="gallery-2.jpg" alt="Gallery" width="400" height="300" loading="lazy" />
```

### Critical image priority

The image that forms the Largest Contentful Paint, typically a hero or the first product
image, is loaded with high fetch priority and is never deferred.

Check:

- The first-viewport image lacks fetchpriority or carries loading="lazy".
- A hero provided only as a CSS background is not announced to the browser early.
- More than one or two images are marked as high priority, which dilutes the signal.

Fix:

- Set fetchpriority="high" and eager loading on the LCP image.
- Preload a known hero URL in the document head with rel="preload" and as="image".
- Confirm the LCP element in the DevTools Performance panel or in Lighthouse.

```html
<link rel="preload" as="image" href="/img/hero.webp" fetchpriority="high" />
```

## Responsive delivery

### Responsive srcset candidates

Images that render at several sizes provide a srcset with width descriptors, so that the
browser selects a candidate that matches the viewport and the pixel density.

Check:

- Images wider than about 100 CSS pixels have no srcset attribute.
- A srcset lists a single candidate and therefore offers no benefit.
- Density descriptors are used on images whose layout width changes with the viewport.

Fix:

- Generate variants at several widths, for example 400, 800, 1200, and 1600 pixels, and
  list them with w descriptors.
- Keep src pointing at a mid-range variant as the fallback.
- Use x descriptors only for fixed-size images such as avatars and logos.

```html
<img
  src="photo-800.jpg"
  alt="Harbour at dusk"
  width="1200"
  height="800"
  srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1200.jpg 1200w"
  sizes="(max-width: 600px) 100vw, 50vw"
/>
```

### Responsive sizes attribute

The sizes attribute states the rendered width of the image at each breakpoint, which
allows the browser to choose the right candidate from the srcset.

Check:

- A srcset is present without sizes, so the browser assumes 100vw.
- The sizes values differ from the real layout set by grid, columns, or max-width.
- The breakpoints in sizes differ from the breakpoints in the stylesheet.

Fix:

- Derive sizes from the actual layout, with one media condition per breakpoint and a
  final fallback width.
- Update sizes in the same change as any CSS layout change.
- Inspect the candidate that loads at a mobile width and at a desktop width.

### Responsive display size

Image files are delivered at a pixel size close to the size at which they are rendered,
so that a large source file is never sent to a small container.

Check:

- The intrinsic width is more than about twice the rendered width at common viewports.
- One large source file serves thumbnails, cards, and avatars alike.
- The Lighthouse "properly size images" audit reports savings for the same images.

Fix:

- Produce smaller variants and point srcset at them, rather than relying on CSS scaling.
- Set sizes to the rendered width so that the smaller candidates are chosen.
- Re-run the audit and compare transfer sizes before and after the change.

### Retina and high-DPI assets

Raster images shown at fixed sizes supply a 2x variant, and optionally a 3x variant, so
that they remain sharp on high-density displays.

Check:

- Fixed-size raster images such as logos and avatars provide only a 1x source.
- CSS background images on high-density screens have no image-set or resolution query.
- 3x variants are shipped where 2x is visually sufficient.

Fix:

- Add x descriptors to srcset for fixed-size images, listing 1x and 2x candidates.
- Use image-set() or a min-resolution media query for CSS backgrounds.
- Prefer SVG for logos and icons, because it scales to any pixel density.

```html
<img
  src="logo.png"
  srcset="logo.png 1x, logo@2x.png 2x"
  alt="Acme"
  width="200"
  height="50"
/>
```

### Picture element fallback

Every picture element ends with an img child that carries the alt text, the dimensions,
and a universally supported source, and the source elements precede it.

Check:

- A picture element has no img child, or the img is not its last child.
- Alt, width, height, or loading attributes sit on source elements, where they are
  ignored.
- Source elements lack a type or media attribute where format or art direction is
  intended.

Fix:

- Add an img as the last child, with a JPEG or PNG src and the required attributes.
- Move image attributes from source to img, which is the only element that renders.
- Order sources from most to least efficient, for example AVIF, then WebP, then img.

```html
<picture>
  <source type="image/avif" srcset="photo.avif" />
  <source type="image/webp" srcset="photo.webp" />
  <img src="photo.jpg" alt="Mountain lake at dawn" width="800" height="600" />
</picture>
```

## Formats and compression

### WebP format

Photographic and graphic raster images are delivered as WebP with a JPEG or PNG
fallback, which typically yields smaller files at comparable visual quality.

Check:

- JPEG or PNG photographs are served with no WebP alternative.
- Picture elements offer no WebP source.
- CSS background images are served only as JPEG or PNG without negotiation.

Fix:

- Convert sources to WebP at a quality setting in the mid-70s to mid-80s and keep the
  original files as fallbacks.
- Wrap the img in a picture element with a WebP source.
- Confirm the served Content-Type in the Network panel.

### AVIF format

AVIF gives a further size reduction over WebP for photographic content, and it is
offered ahead of WebP when the browser supports it.

Check:

- Large photographs are delivered only as WebP or JPEG although the build can encode
  AVIF.
- An AVIF source is placed after the WebP or JPEG source.
- AVIF is applied to small icons or logos, where it gives little benefit.

Fix:

- Add an AVIF source first in the picture element, followed by WebP and the img.
- Generate AVIF at build time, because encoding is slower than for WebP or JPEG.
- Keep simple graphics and logos in SVG or PNG.

### Modern format negotiation

Raster images use modern formats where the browser supports them, either through picture
sources in the markup or through a CDN that selects the format from the Accept header.

Check:

- Raster images are shipped only as JPEG or PNG, with no source alternatives.
- CDN image URLs lack a format negotiation parameter when a CDN is in use.
- Format choices differ between components without a documented policy.

Fix:

- Enable the CDN auto-format option or generate WebP and AVIF variants in the build.
- Keep a fallback format in the img element so that every browser receives an image.
- Verify the delivered format in the Network panel in a current and an older browser.

### Image compression

Raster images are compressed to a quality setting that removes unnecessary bytes while
keeping visual artefacts out of view.

Check:

- Photographs are saved at maximum quality or with unnecessary precision.
- Screenshots or graphics show lossy artefacts when viewed at 100 percent zoom.
- No compression step exists in the build or in the upload pipeline.

Fix:

- Compress JPEG and WebP photographs in the 70 to 85 quality range and review the
  output.
- Use lossless or palette-based compression for PNG graphics.
- Run compression in the build or in CI so that new assets pass through it.

### Image file size budgets

Image files stay within documented size budgets, with the largest allowance reserved for
hero images, so that page weight remains predictable.

Check:

- Photographs above about 200 KB, hero images above about 400 KB, or thumbnails above
  about 30 KB.
- Oversized files in public directories or in CMS uploads.
- Regressions in the largest images on the most visited pages.

Fix:

- Reduce dimensions and quality, convert to WebP or AVIF, and measure the result again.
- Record an exception when an image legitimately exceeds its budget.
- Enforce the budget in CI by checking the size of newly added assets.

### Image optimisation pipeline

Images are optimised as a whole, combining format choice, compression, responsive
variants, and metadata removal, rather than through isolated manual steps.

Check:

- Camera exports or unprocessed editor files are shipped to production.
- Responsive variants and modern formats are missing from the build output.
- The pipeline has no single source of truth, so variants drift apart over time.

Fix:

- Generate every width and format from one source file in a single build step.
- Store originals outside the served directory and commit only the generated outputs or
  run generation during deployment.
- Confirm the output with a Lighthouse image audit after each change.

### Metadata and encoder settings

Served images carry no unnecessary metadata and are encoded with settings that favour a
small file without visible loss.

Check:

- JPEG files served to users still contain EXIF data with camera or location details.
- JPEG files are encoded with default settings where an optimised encoder is available.
- PNG files are served without lossless optimisation.

Fix:

- Strip metadata explicitly during encoding rather than relying on defaults.
- Use an optimised JPEG encoder and lossless optimisation for PNG files.
- Inspect a served file with an EXIF tool before deployment.

### Progressive JPEG

JPEG files that remain in use are encoded progressively, so that a low-resolution pass
renders before the complete file has arrived.

Check:

- Baseline JPEG files are used for large above-the-fold images.
- The encoder configuration of the build does not enable progressive output.
- Progressive output is applied to tiny thumbnails, where it gives no measurable gain.

Fix:

- Enable progressive output in the JPEG encoder settings.
- Compare file sizes afterwards, which are usually similar or smaller.
- Treat progressive JPEG as a fallback measure, since WebP and AVIF already cover most
  delivery.

## Vector and sprite assets

### SVG optimisation

SVG files are cleaned of editor metadata, comments, and redundant markup, while the
viewBox and any accessibility elements the file needs are kept.

Check:

- Editor comments, generator metadata, and unused definitions remain in SVG files.
- A standalone SVG lacks a viewBox, or its title and desc elements were removed.
- Empty groups or hidden elements remain in the markup.

Fix:

- Run the files through SVGO with a configuration that keeps viewBox and title.
- Preserve animation definitions when a file is animated, and check the result visually.
- Record the byte size before and after the optimisation.

### Inline SVG size

Inline SVG markup is kept small and used only where the page needs to style or script
individual paths, so that the HTML document stays light and cacheable.

Check:

- Inline SVG blocks larger than about 1 KB, particularly illustrations.
- The same icon is inlined in several places.
- Static inline SVG could be an external file referenced from an img element.

Fix:

- Move static illustrations to external files and reference them through an img.
- Use a symbol sprite or a component for repeated icons, with SVGR in React projects.
- Mark decorative inline SVG with aria-hidden, and keep inline markup only where styling
  or scripting depends on it.

```html
<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24">
  <use href="/icons.svg#icon-search"></use>
</svg>
```

### CSS and symbol sprites

Small icons that appear together are combined into one sprite, and symbol sets are the
preferred form for new icon work.

Check:

- Many small raster icons are requested separately on the same page.
- Sprite sheets contain photographs or large images.
- Icons that must change colour are provided as raster sprites.

Fix:

- Use an SVG symbol sprite or icon components for new icon sets.
- Where a raster sprite already exists, keep its offsets in step with the stylesheet.
- Do not combine photographs into sprites; use lazy loading for them instead.

## Delivery and failure handling

### Image CDN

Images are served from an image CDN or transformation service that resizes, converts,
and caches them at the edge.

Check:

- Images are served directly from the application origin without transformation.
- Image URLs hard-code one size and one format for every device.
- Image responses lack cache headers.

Fix:

- Route image URLs through the CDN with width, format, and quality parameters.
- Build srcset candidates from the same URL pattern so that each size is cached.
- Verify cache status and cache headers in the Network panel.

```html
<img
  src="https://images.example.com/hero.jpg?w=800&fm=auto&q=80"
  alt="Hero"
  width="800"
  height="450"
/>
```

### Broken image handling

Image sources resolve to existing files, and any failure at runtime is caught by a
handler that swaps in a placeholder, so that users do not see a broken icon.

Check:

- img src values point to missing files, which a build-time script can detect.
- Dynamic image paths are built from data without an existence check.
- External images have no error handler.

Fix:

- Correct or add the missing asset, and add a build step that verifies local paths.
- Swap in a placeholder once and clear the handler, so that a missing placeholder does
  not trigger an endless loop.
- Test by blocking the request in DevTools and confirming that the placeholder appears.

```html
<img
  src="/img/product.jpg"
  alt="Blue running shoe"
  onerror="this.onerror=null; this.src='/img/placeholder.png';"
/>
```

### Image load error fallback

Images that fail to load are replaced with a meaningful placeholder, such as an initials
avatar or a neutral panel, and the failure is recorded for diagnosis.

Check:

- Components that render user-supplied images have no fallback state.
- Error handlers do not guard against repeated error events.
- Load failures are not reported to monitoring.

Fix:

- Use a stateful component that switches to a placeholder on the first error.
- Keep the alt text meaningful in the fallback state.
- Log the failing source with rate limiting, so that a broken CDN does not flood logs.

### Filename quality

Image filenames are descriptive, lowercase, and separated by hyphens, which aids
maintenance and provides a relevance signal in image search.

Check:

- Camera defaults such as IMG_ or DSC_ prefixes, or generic names such as image1.jpg.
- Spaces, underscores used as separators, or mixed case in source asset names.
- Hashed build outputs are not defects; only source assets are checked.

Fix:

- Rename source assets with three to five lowercase words joined by hyphens.
- Update every reference in HTML, CSS, and scripts in the same change.
- Sanitise uploaded filenames on the server at upload time.
