# SEO and Metadata

This file covers the 93 rules of the front-end-practices skill that concern search
engine optimization, page metadata, crawlability, indexing directives, structured data,
sitemaps, links, content quality, and editorial trust. It is the reference that the
skill loads when a search-engine or metadata check or fix is requested. Each rule states
its intent, lists the checks that establish compliance, and describes the corrective
actions. The index below gives every rule its category, priority, and difficulty, and
the sections that follow group the rules by topic.

## Rule index

| Rule                      | Category | Priority | Difficulty   | Rule statement                                                                  |
| ------------------------- | -------- | -------- | ------------ | ------------------------------------------------------------------------------- |
| `article`                 | seo      | high     | intermediate | Article markup must use valid Schema.org properties.                            |
| `broken-links`            | seo      | high     | beginner     | Internal links must not resolve to 404 or 5xx responses.                        |
| `canonical-url`           | seo      | high     | beginner     | Every page must declare one absolute canonical URL.                             |
| `meta-description`        | seo      | high     | beginner     | Every indexable page must carry a unique, well-sized meta description.          |
| `meta-in-body`            | seo      | high     | beginner     | Meta tags must appear only inside the document head.                            |
| `meta-title`              | seo      | high     | beginner     | Every HTML page must have a descriptive, appropriately sized title.             |
| `noindex-in-sitemap`      | seo      | high     | intermediate | Sitemaps must not list URLs that carry a noindex directive.                     |
| `quality`                 | seo      | high     | intermediate | Pages targeting search traffic must contain substantive, original content.      |
| `redirect-chain`          | seo      | high     | intermediate | Redirects must reach their destination in a single hop.                         |
| `robots-meta`             | seo      | high     | beginner     | Robots meta directives must be valid, unique, and intentional per page.         |
| `robots-meta-conflict`    | seo      | high     | intermediate | A page must not combine a robots.txt block with a noindex tag.                  |
| `robots-txt`              | seo      | high     | beginner     | A valid robots.txt must be served from the site root.                           |
| `schema-noindex-conflict` | seo      | high     | intermediate | Pages with rich-result markup must be indexable.                                |
| `sitemap`                 | seo      | high     | beginner     | An XML sitemap must exist and list the site's important pages.                  |
| `sitemap-4xx`             | seo      | high     | intermediate | Sitemaps must not list URLs that return 4xx responses.                          |
| `sitemap-valid`           | seo      | high     | beginner     | Sitemap XML must conform to the sitemaps.org protocol.                          |
| `structured-data`         | seo      | high     | intermediate | Relevant Schema.org JSON-LD must be present for rich results.                   |
| `title-unique`            | seo      | high     | beginner     | Each page must have a title that no other page shares.                          |
| `ymyl-detection`          | seo      | high     | intermediate | YMYL pages must be identified and held to elevated trust standards.             |
| `share-buttons`           | seo      | low      | beginner     | Long-form content should expose sharing controls.                               |
| `social-profiles`         | seo      | low      | beginner     | The site should link to its active social profiles.                             |
| `stop-words`              | seo      | low      | beginner     | URL slugs should omit stop words that add length without meaning.               |
| `website-search`          | seo      | low      | beginner     | Sites with internal search should expose WebSite SearchAction markup.           |
| `about-page`              | seo      | medium   | intermediate | A dedicated About page must describe who publishes the content.                 |
| `affiliate-disclosure`    | seo      | medium   | intermediate | Affiliate relationships must be disclosed clearly on the page.                  |
| `ai-content`              | seo      | medium   | intermediate | AI-assisted content must be reviewed for accuracy and originality.              |
| `all-noindex-pages`       | seo      | medium   | intermediate | Every noindex page must be reviewed and justified.                              |
| `anchor-text`             | seo      | medium   | beginner     | Link text must describe the destination.                                        |
| `article-links`           | seo      | medium   | intermediate | Articles must balance internal and external links against their length.         |
| `author-byline`           | seo      | medium   | beginner     | Content pages must show a visible author name.                                  |
| `author-expertise`        | seo      | medium   | intermediate | Author bios must state credentials relevant to the topic.                       |
| `author-info`             | seo      | medium   | intermediate | Authors must be described with machine-readable Person markup.                  |
| `breadcrumb`              | seo      | medium   | intermediate | Breadcrumb navigation must be marked up as valid BreadcrumbList data.           |
| `broken-external-links`   | seo      | medium   | intermediate | Outbound links must not point to dead or erroring destinations.                 |
| `broken-html`             | seo      | medium   | intermediate | HTML must be well formed, with tags closed and nested correctly.                |
| `canonical-chain`         | seo      | medium   | intermediate | A canonical URL must not itself redirect elsewhere.                             |
| `canonical-header`        | seo      | medium   | intermediate | HTTP Link canonical headers and HTML canonical tags must agree.                 |
| `citations`               | seo      | medium   | beginner     | Factual claims should cite reputable external sources.                          |
| `contact-page`            | seo      | medium   | beginner     | A dedicated Contact page must offer several ways to reach the site owner.       |
| `content-dates`           | seo      | medium   | intermediate | Published and updated dates must be visible and machine-readable.               |
| `dead-end-pages`          | seo      | medium   | intermediate | Content pages must link onward to related pages.                                |
| `disclaimers`             | seo      | medium   | intermediate | Sensitive content must carry an appropriate disclaimer.                         |
| `duplicate-description`   | seo      | medium   | intermediate | Meta descriptions must not repeat across pages.                                 |
| `editorial-policy`        | seo      | medium   | intermediate | The site should publish a page describing its editorial standards.              |
| `external-links`          | seo      | medium   | intermediate | Factual claims should link to verifiable sources, with safe link attributes.    |
| `faq`                     | seo      | medium   | intermediate | FAQ content must carry valid FAQPage markup that matches the visible text.      |
| `favicon`                 | seo      | medium   | intermediate | Every page must declare a favicon through a link element.                       |
| `freshness`               | seo      | medium   | intermediate | Content must expose freshness signals through dates and headers.                |
| `geo-meta`                | seo      | medium   | intermediate | Regional targeting tags must use valid ISO codes and formats.                   |
| `h1`                      | seo      | medium   | intermediate | Each page must have exactly one descriptive H1.                                 |
| `html-size`               | seo      | medium   | intermediate | HTML documents must stay below the crawler's size limit.                        |
| `https-downgrade`         | seo      | medium   | intermediate | HTTPS pages must not link to HTTP resources.                                    |
| `hyphens`                 | seo      | medium   | intermediate | URL slugs must separate words with hyphens.                                     |
| `indexability`            | seo      | medium   | intermediate | Important pages must not be blocked from indexing by accident.                  |
| `indexability-conflicts`  | seo      | medium   | intermediate | Robots.txt, meta robots, headers, and canonicals must agree.                    |
| `internal-links`          | seo      | medium   | intermediate | Key pages must receive contextual internal links from other pages.              |
| `invalid-links`           | seo      | medium   | intermediate | Links must be real anchors with valid, crawlable href values.                   |
| `json-ld-valid`           | seo      | medium   | intermediate | JSON-LD blocks must be syntactically valid and include required properties.     |
| `keyword-stuffing`        | seo      | medium   | intermediate | Content, titles, and alt text must not repeat keywords unnaturally.             |
| `length`                  | seo      | medium   | intermediate | URLs must stay short and free of unnecessary path depth.                        |
| `llm-parsability`         | seo      | medium   | intermediate | Content must be structured so that language models can extract it.              |
| `llms-txt`                | seo      | medium   | intermediate | Documentation-heavy sites may publish a curated llms.txt index.                 |
| `local-business`          | seo      | medium   | intermediate | Local businesses must provide valid LocalBusiness markup.                       |
| `lowercase`               | seo      | medium   | beginner     | URLs must use lowercase paths consistently.                                     |
| `mime-type`               | seo      | medium   | intermediate | Content-Type headers must match each resource's actual format.                  |
| `nap-consistency`         | seo      | medium   | intermediate | Name, address, and phone details must match across the site.                    |
| `nofollow-internal`       | seo      | medium   | intermediate | Internal links must not carry rel nofollow.                                     |
| `nosnippet`               | seo      | medium   | intermediate | Important pages must not suppress search snippets.                              |
| `og-image-size`           | seo      | medium   | beginner     | Open Graph images must be absolute URLs sized about 1200 by 630 pixels.         |
| `og-tags`                 | seo      | medium   | intermediate | Pages must provide the core Open Graph tags with absolute URLs.                 |
| `og-url-match`            | seo      | medium   | beginner     | The og:url value must equal the canonical URL.                                  |
| `organization`            | seo      | medium   | intermediate | The homepage should carry valid Organization markup.                            |
| `orphan-pages`            | seo      | medium   | intermediate | Every page must receive at least one internal link.                             |
| `pagination`              | seo      | medium   | intermediate | Each paginated page must canonicalize to itself.                                |
| `parameters`              | seo      | medium   | intermediate | Tracking, sort, and filter parameters must not create duplicate indexable URLs. |
| `pdf-size`                | seo      | medium   | intermediate | Linked PDFs must stay under the crawler's size limit.                           |
| `physical-address`        | seo      | medium   | beginner     | Businesses must display a physical postal address.                              |
| `product`                 | seo      | medium   | intermediate | Product pages must carry valid Product markup with offers.                      |
| `reading-level`           | seo      | medium   | intermediate | Prose must be written at a clear, readable level.                               |
| `redirect-chains`         | seo      | medium   | intermediate | Internal links must point directly to final destination URLs.                   |
| `review`                  | seo      | medium   | intermediate | Review and AggregateRating markup must be valid and based on real reviews.      |
| `service-area`            | seo      | medium   | intermediate | Multi-region service businesses must use well-structured area pages.            |
| `sitemap-coverage`        | seo      | medium   | intermediate | Every indexable canonical page must appear in the sitemap.                      |
| `sitemap-domain`          | seo      | medium   | beginner     | Sitemap URLs must use the same domain and protocol as the site.                 |
| `slug-keywords`           | seo      | medium   | beginner     | URL slugs must describe the page topic in words.                                |
| `special-chars`           | seo      | medium   | beginner     | URL paths must avoid spaces, reserved characters, and non-ASCII letters.        |
| `tel-mailto`              | seo      | medium   | beginner     | Phone numbers and email addresses must use tel: and mailto: links.              |
| `trailing-slash`          | seo      | medium   | beginner     | Trailing-slash usage must be consistent across all URLs.                        |
| `trust-signals`           | seo      | medium   | intermediate | Key conversion pages must show verifiable trust evidence.                       |
| `twitter-cards`           | seo      | medium   | beginner     | Shareable pages must declare valid Twitter (X) Card tags.                       |
| `video`                   | seo      | medium   | intermediate | Pages with video must carry valid VideoObject markup.                           |
| `weak-internal-links`     | seo      | medium   | intermediate | Important pages must receive several followable internal links.                 |
| `word-count`              | seo      | medium   | beginner     | Key pages must contain enough substance to answer their query.                  |

## Crawling and indexing

### Publish a robots.txt file

Robots.txt must exist at the site root, return HTTP 200, and contain only valid
directives that do not block essential content.

Check:

- Request the file at the root and confirm a 200 status and text content.
- Confirm that no Disallow rule blocks CSS, JavaScript, or important content paths.
- Confirm that a Sitemap line points to the absolute sitemap URL.

Fix:

- Serve the file from the root of the production host.
- Remove broad rules such as `Disallow: /` unless the host is intentionally private.
- Restrict Disallow entries to admin, cart, or other utility paths.

```text
User-agent: *
Disallow: /admin/
Disallow: /cart/
Sitemap: https://example.com/sitemap.xml
```

### Set robots meta directives correctly

Robots meta tags should carry valid, non-contradictory directives, and each page should
state the indexing intent it actually has.

Check:

- Inspect the head for one robots meta tag per page and confirm the values are valid.
- Confirm that public content pages use index, follow or omit the tag.
- Confirm that staging noindex tags have not reached production.

Fix:

- Remove duplicate or contradictory robots tags from templates.
- Use noindex, follow only on pages that should stay out of results.
- Add a deployment check that rejects noindex on the production domain.

### Resolve robots meta conflicts with robots.txt

A page blocked by robots.txt cannot have its noindex tag read, so the two signals must
not be combined for the same URL.

Check:

- List URLs that match Disallow rules and also carry a noindex tag.
- Determine whether each such URL is already indexed and should be removed.
- Check whether the robots.txt block was added after the noindex tag.

Fix:

- For pages to deindex, remove the Disallow rule and keep the noindex tag.
- For pages that must not be fetched, remove the noindex reliance and keep the block.
- Verify the outcome with a live fetch after the change.

### Make important pages indexable

Pages that matter for search must not carry noindex directives or other blocking signals
by accident.

Check:

- Fetch each important URL and inspect both the meta robots tag and the X-Robots-Tag
  header.
- Check whether a framework-level robots option sets index to false for a whole route
  group.
- Confirm that the page appears in Search Console's indexing report.

Fix:

- Remove noindex from route-level metadata that applies to content pages.
- Restrict noindex to draft, preview, and utility pages.
- Set index and follow explicitly where a template previously omitted them.

```tsx
// Only preview pages are excluded; published content stays indexable.
export const metadata = post.published
  ? { robots: { index: true, follow: true } }
  : { robots: { index: false, follow: false } };
```

### Avoid conflicting indexability signals

Robots.txt, meta robots, X-Robots-Tag headers, and canonical tags must send the same
message about each URL.

Check:

- Compare the robots.txt rule, the meta robots value, and the response header for sample
  URLs.
- Check that a canonical target is not marked noindex.
- Check that a noindex page is not also the target of a canonical from other pages.

Fix:

- Choose one primary signal per URL and remove the others that contradict it.
- Point canonical tags only at indexable URLs.
- Prefer a noindex tag over a robots.txt block when the page should drop out of results.

### Audit all noindex pages

Every noindex directive on the site should be listed, reviewed, and justified, because
accidental exclusion removes pages from search without visible errors.

Check:

- Crawl the site and list each URL with a noindex meta tag or X-Robots-Tag header.
- Classify each URL as utility, duplicate, staging, or content that should rank.
- Flag any content page found in the list.

Fix:

- Remove noindex from content pages and resubmit them.
- Keep noindex on login, cart, internal search, and staging pages.
- Repeat the audit on a schedule or in the release pipeline.

### Avoid nosnippet on important pages

The nosnippet directive and max-snippet:0 remove the description that search results
display, so they should be kept off pages that need a visible summary.

Check:

- Search robots meta values for nosnippet or max-snippet:0 on landing and article pages.
- Confirm whether the directive was copied from a template or staging setup.

Fix:

- Remove nosnippet from content templates.
- If length must be limited, use max-snippet with a numeric limit instead.

```html
<meta name="robots" content="index, follow, max-snippet:150" />
```

### Keep HTML documents under crawl limits

Very large HTML documents may be truncated by crawlers, so the content that matters must
appear early in a compact document.

Check:

- Measure the uncompressed and compressed size of key pages with curl.
- Look for large embedded JSON payloads, such as serialized application state.
- Look for inline SVG or base64 images that could be external resources.

Fix:

- Pass only the data a page renders into server-side props.
- Load further records through client requests or pagination.
- Reference large graphics as external files instead of inlining them.

### Keep linked PDFs under the crawl size limit

Linked PDF files that exceed the crawler's size limit may be indexed only in part, so
large documents should be split or compressed.

Check:

- Read the Content-Length header of each linked PDF.
- Identify PDFs that exceed the limit named in the rule.
- Check whether an HTML landing page exists for each large document.

Fix:

- Compress images inside the PDF or split it into chapters.
- Publish an HTML summary page that links to the PDF.
- Re-measure the file after the change.

### Serve correct MIME types

Each resource must be served with a Content-Type that matches its format, so that
crawlers and browsers interpret it correctly.

Check:

- Request representative HTML, CSS, JavaScript, image, and font URLs with curl -I.
- Confirm that CSS is text/css and that JavaScript is text/javascript.
- Confirm that HTML carries a UTF-8 charset.

Fix:

- Correct the server mime.types mapping or the framework headers configuration.
- Add X-Content-Type-Options: nosniff to responses.
- Redeploy and re-check the headers.

### Use schema noindex conflict checks for rich results

Structured data cannot produce rich results on a page that is excluded from the index,
so the two must be resolved together.

Check:

- Find pages that carry rich-result JSON-LD and also a noindex tag or robots.txt block.
- Check whether the page is a canonical duplicate of another URL.
- Check that the page content visibly supports the markup.

Fix:

- Remove noindex from pages that should produce rich results.
- Make the page self-canonical, or move the markup to the canonical URL.
- Validate with the rich-results testing tool after the change.

## Canonical URLs, redirects, and pagination

### Set canonical URLs for all pages

Every page should declare one absolute canonical URL that names the preferred version of
its content.

Check:

- Confirm that each HTML page has exactly one rel canonical link in the head.
- Confirm that the href is absolute, uses HTTPS, and has no tracking parameters.
- Confirm that the canonical target returns a 200 status.

Fix:

- Generate the canonical URL from the route, not from the incoming request.
- Strip query parameters that do not change the content.
- Use a self-referencing canonical on unique pages.

```html
<link rel="canonical" href="https://example.com/products/widget" />
```

### Avoid redirect chains on canonical URLs

A canonical tag should point to the final destination, not to a URL that redirects.

Check:

- Fetch each canonical target and confirm it returns 200 without a redirect.
- Check that the target does not redirect to another URL.

Fix:

- Replace the canonical href with the final destination URL.
- Update the route or redirect map so the old URL points directly to the new one.

### Sync HTML canonical tags and Link headers

When a canonical signal is sent both as an HTTP Link header and as an HTML tag, both
must name the same URL.

Check:

- Compare the Link rel canonical response header with the head link element.
- Check non-HTML resources such as PDFs for a Link header.

Fix:

- Generate both signals from one shared function.
- Remove a stale header added by a CDN or proxy rule.

```text
Link: <https://example.com/target-page>; rel="canonical"
```

### Avoid multi-hop redirect chains

A redirect should reach its destination in a single hop, because each extra hop wastes
crawl budget and slows users.

Check:

- Trace each redirect with curl -L -I and count the 3xx responses.
- Flag any sequence that requires more than one redirect before the final 200.

Fix:

- Update the earlier rule so it points to the final URL.
- Remove intermediate rules that were added after later migrations.

### Link directly to final destination URLs

Internal links and sitemap entries should name the final URL, not a URL that redirects.

Check:

- Crawl the site and list internal links whose targets return 3xx responses.
- Check sitemap entries for the same redirect pattern.

Fix:

- Rewrite internal links, navigation templates, and sitemap entries to the final URL.
- Keep the redirect in place for external links that still use the old URL.

### Use canonicals on paginated pages

Each page in a paginated series should canonicalize to itself, because pointing all
pages at page one hides the content on later pages.

Check:

- Read the canonical tag on pages 2 and later of a listing.
- Confirm that the pagination scheme is consistent across the site.

Fix:

- Make each paginated page self-canonical, including its page parameter.
- Use one pattern, either query parameters or path segments, consistently.
- Provide crawlable page links in a visible pagination navigation.

### Limit unnecessary URL parameters

Tracking, sort, and filter parameters must not produce duplicate indexable URLs.

Check:

- List URLs that differ only in parameters such as utm_source or sort order.
- Check that each variant declares a canonical to the preferred URL.
- Check that internal search result pages are noindexed.

Fix:

- Strip tracking parameters before building the canonical URL.
- Point filtered and sorted variants to the base listing.
- Noindex internal search results.

```ts
const TRACKING = ["utm_source", "utm_medium", "utm_campaign", "fbclid", "gclid"];
```

### Keep HTTPS consistent across links

Links on HTTPS pages must not point to HTTP addresses, which trigger mixed-content
warnings and redirects.

Check:

- Search templates and rendered HTML for href and src values beginning with http://.
- Check that canonical tags and sitemap URLs use HTTPS.

Fix:

- Change hard-coded HTTP URLs to HTTPS or to relative paths.
- Avoid protocol-relative URLs in new code.

### Use trailing slashes consistently

Every URL should have one preferred form, with or without a trailing slash, so that
variants do not create duplicate pages.

Check:

- Request a URL with and without the trailing slash and compare the responses.
- Confirm that the canonical tag and internal links use the chosen form.

Fix:

- Configure the framework so that the preferred form is served directly.
- Redirect the alternate form with a single 301.
- Align canonical tags and internal links with the same form.

```js
// next.config.js
module.exports = { trailingSlash: false };
```

## URL structure

### Use lowercase URLs

URL paths should be lowercase, because case-sensitive servers treat variants as
different pages.

Check:

- Request a sample of URLs with uppercase letters and compare the responses.
- Check that internal links and canonical tags use lowercase paths.

Fix:

- Redirect uppercase paths to their lowercase equivalents with a 301.
- Rename routes and file names to lowercase.

### Use hyphens in URLs

Hyphens should separate words in URL slugs, because underscores and spaces are not read
as word boundaries by search engines.

Check:

- List slugs that contain underscores, spaces, or encoded spaces.
- Check that the slug generator converts underscores to hyphens.

Fix:

- Generate slugs with a function that replaces whitespace and underscores with hyphens.
- Redirect old underscore URLs to the hyphenated versions.

### Keep URLs concise

URLs should be short and shallow, so they remain readable in results and shares.

Check:

- Flag URLs that are very long or contain several redundant path levels.
- Check whether dates or categories appear in the path without adding meaning.

Fix:

- Prefer flat routes such as one slug segment for articles.
- Remove redundant date segments and shorten the slug to its core terms.

### Include keywords in URL slugs

Slugs should name the topic of the page in plain words rather than in IDs or codes.

Check:

- Flag slugs that are numeric IDs, sequential numbers, or internal SKUs alone.
- Check that the slug reflects the page's title.

Fix:

- Derive slugs from the title or product name at creation time.
- Keep a short redirect from any old ID-based URL.

### Use safe URL characters

URL paths should contain only letters, digits, hyphens, underscores, periods, and
tildes, with non-ASCII letters transliterated.

Check:

- List URLs with spaces, fragments, query characters inside paths, or accented letters.
- Check that user-generated slugs are normalized before storage.

Fix:

- Normalize accents with Unicode decomposition and strip non-ASCII characters.
- Replace spaces with hyphens and remove reserved characters.

```js
const slug = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
```

### Remove stop words from URL slugs

Common words such as articles and prepositions add length to slugs without improving
topical signals, so they can be omitted from new slugs.

Check:

- Flag slugs that begin or contain several stop words.
- Check whether the slug generator already filters them.

Fix:

- Filter stop words in the slug generator for new content.
- Do not rewrite the slugs of already indexed pages without a redirect plan.

## Page titles and descriptions

### Write a descriptive page title

Each HTML page needs a title that describes its content and is short enough to display
fully in results.

Check:

- Confirm that each page has one title element with non-empty text.
- Flag titles that are generic, such as "Page", or longer than about 60 characters.

Fix:

- Build the title from the page's own name, followed by the brand.
- Set a default title template in the root layout.

```tsx
export const metadata = { title: { template: "%s | Brand", default: "Brand" } };
```

### Keep page titles unique

Each page should have a title that no other page shares, so that search engines can
distinguish the pages.

Check:

- Crawl the site and group pages by identical title.
- Confirm that category and listing pages include their own name in the title.

Fix:

- Include the entity name, such as the category or product, in the template.
- Rewrite generic titles that repeat across many pages.

### Write a meta description for each page

Each indexable page should have one meta description that summarizes its content in a
sentence or two.

Check:

- Confirm that each page has a meta description with a non-empty content attribute.
- Flag descriptions that are missing, empty, or contain HTML markup.

Fix:

- Derive the description from the page excerpt, truncated near 155 characters.
- Provide a site-wide fallback for pages that lack their own description.

```html
<meta name="description" content="Step-by-step sourdough recipes for home bakers." />
```

### Avoid duplicate meta descriptions

Meta descriptions should differ between pages, because repeated text gives search
engines no reason to prefer one page over another.

Check:

- Crawl the site and group pages by identical description text.
- Check whether a global layout injects the same description on every route.

Fix:

- Set page-specific descriptions in each route's metadata function.
- Use the site-wide description only as a fallback.

## Headings and HTML integrity

### Use a single descriptive H1

Each page should have exactly one H1 that states the subject of that page.

Check:

- Count H1 elements on each page; the count should be exactly one.
- Flag H1 text that is only a brand name or is empty.

Fix:

- Make the page title or lead heading the single H1.
- Demote secondary headings to H2 or lower.

### Fix malformed HTML structure

Tags must be closed and nested correctly, because broken markup can change how crawlers
read the page.

Check:

- Run the page through an HTML validator or parser.
- Look for unclosed elements and misnested inline and block tags.

Fix:

- Correct the template so that every element closes in the right order.
- Add the validator to the continuous integration pipeline.

### Meta tags in body

Meta tags placed in the body are not reliably honored, so all metadata must live in the
head.

Check:

- Search the rendered HTML for meta elements that appear after the closing head tag.
- Check whether plugins or scripts inject tags into the body.

Fix:

- Move the injection to the head, for example with a head-management API.
- Disable the plugin or widget that writes meta tags into the body.

### Favicon on every page

Each page should declare its favicon explicitly, rather than relying on the browser to
request a default file.

Check:

- Confirm that each page's head contains a link rel icon element.
- Confirm that the referenced file returns 200 with an image content type.

Fix:

- Provide an ICO fallback and an SVG icon, and reference both in the head.
- Add the same link elements to the shared layout.

```html
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
```

## Internal and external links

### Add internal links to key pages

Important pages should receive contextual links from related content, so that they are
discovered and understood through the site's structure.

Check:

- Count inbound internal links for each key page.
- Check whether anchor text names the target topic.

Fix:

- Add in-body links from related articles, using descriptive anchor text.
- Add a related-content module to templates where it is missing.

### Weak internal links

Important pages should receive several followable internal links from pages that carry
authority, not only from footers.

Check:

- Identify the key pages with the fewest followable inbound links.
- Check whether the links come from body text or only from footer and menus.

Fix:

- Link to cornerstone pages from the homepage, category pages, and high-traffic
  articles.
- Build a hub page that links to the supporting articles around one topic.

### Add internal links to orphan pages

Every page should be reachable through at least one internal link, because pages without
inbound links are hard to discover and rank.

Check:

- Compare the sitemap and crawl output and list pages with zero inbound links.
- Check whether the orphan appears in any category listing.

Fix:

- Add the page to its category or archive listing.
- Add a contextual link from a related article.

### Add outgoing links to dead-end pages

Content pages should link onward to related pages, so that readers and crawlers do not
stop at a page with no way forward.

Check:

- List content pages with no outgoing internal links in the body or related block.
- Check whether the template produces link-free pages.

Fix:

- Add an inline link where a related topic is mentioned.
- Add a "See also" section to templates that produce standalone pages.

### Use descriptive anchor text

Link text should describe the destination, because it is read by users, screen readers,
and search engines.

Check:

- Flag anchor text such as "click here", "read more", or bare URLs.
- Check that the anchor text names the topic of the target page.

Fix:

- Rewrite the link text to name the destination topic.
- Keep the surrounding sentence so that the link has context.

### Fix internal broken links

Internal links must resolve to live pages, because 404 and 5xx responses waste crawl
effort and harm the user experience.

Check:

- Crawl the site and list internal links that return 4xx or 5xx status codes.
- Check whether the broken target was renamed or removed.

Fix:

- Update the link to the current URL.
- Add a 301 redirect for any removed page that still receives links.

### Fix or remove broken external links

Outbound links should point to live destinations, because dead links suggest that the
content is out of date.

Check:

- Crawl the page and list external links that return errors or time out.
- Check whether an archived or replacement source exists.

Fix:

- Replace the link with a live or archived source that supports the same claim.
- Remove the link when no suitable replacement exists.

### Fix invalid links

Links must be real anchor elements with an href that crawlers can follow. Click handlers
on other elements are not followed.

Check:

- Search for anchors with empty href values or with javascript: URLs.
- Search for clickable div or span elements that navigate through scripts.

Fix:

- Use an anchor element with a real href for navigation, and enhance it with script.
- Use the framework's link component so that it renders a standard anchor.

```html
<a href="/products">Products</a>
```

### Avoid nofollow on internal links

Internal links should not carry rel nofollow, because the attribute withholds ranking
signals from pages within the site.

Check:

- Search rendered HTML for internal anchors that include rel="nofollow".
- Check whether a template adds nofollow to all links.

Fix:

- Remove nofollow from internal link templates.
- Reserve nofollow for untrusted user content or paid links to other domains.

### Add relevant external links

Factual claims should link to the source that supports them, so that readers can verify
the statement.

Check:

- Identify factual claims that cite a statistic or study without a link.
- Check that external links include rel noopener when they open a new tab.

Fix:

- Link the claim to the primary source.
- Add rel="noopener noreferrer" to external links that open in a new tab.

### Optimize article link density

Articles should contain a balanced number of internal and external links relative to
their length.

Check:

- Count internal and external links per article and compare them with the word count.
- Flag articles with no outbound links to sources or related content.

Fix:

- Add links where claims or related topics are introduced.
- Remove links that repeat the same destination without adding context.

## Structured data

### Use valid JSON-LD structured data

JSON-LD blocks must parse as JSON and include the properties that their Schema.org type
requires.

Check:

- Validate each script block with a JSON parser and a structured-data validator.
- Confirm that required properties such as headline and author are present.

Fix:

- Generate the object in code and serialize it with JSON.stringify.
- Add the missing required properties from the page's own data.

### Add structured data markup

Pages that qualify for rich results should carry the matching Schema.org JSON-LD, and
the markup must describe what the page visibly shows.

Check:

- Identify the page type and the rich result it may qualify for.
- Confirm that each value in the markup appears in the visible content.

Fix:

- Add a typed JSON-LD block through a reusable component.
- Validate the output with the rich-results testing tool.

### Implement valid Article structured data

Article pages should declare Article or NewsArticle markup with the properties that
describe the headline, dates, author, and image.

Check:

- Confirm that headline, image, author, and date properties are present.
- Confirm that the headline matches the visible title.

Fix:

- Generate Article markup from the same record that renders the page.
- Set image and author properties to absolute URLs and real names.

### Implement valid BreadcrumbList schema

Breadcrumb navigation should be marked up with a BreadcrumbList whose positions are
sequential and whose items are absolute URLs.

Check:

- Confirm that positions start at 1 and increase by one.
- Confirm that each item URL resolves and matches the visible breadcrumb.

Fix:

- Build the list from the same path segments that render the breadcrumb.
- Omit the final item when it is the current page, if the template does so.

### Validate FAQPage markup

FAQ markup must match questions and answers that are visible on the page, and it must
not be used for content that is hidden.

Check:

- Compare each Question name and Answer text with the visible FAQ section.
- Confirm that the FAQ section is not hidden behind an interaction that crawlers cannot
  trigger.

Fix:

- Generate FAQPage JSON-LD from the same question list that renders the section.
- Remove markup for questions that are not on the page.

### Add Product schema markup

Product pages should declare Product markup with name, image, description, and an Offer
that reflects the current price and availability.

Check:

- Confirm that name, image, description, and offers are present.
- Confirm that the price and availability match the visible values.

Fix:

- Generate Product markup from the product record.
- Use the Schema.org availability URLs, such as InStock or OutOfStock.

### Add Review schema markup

Review and AggregateRating markup must describe reviews that are real, visible, and
attributed to a reviewer.

Check:

- Confirm that the rating values fall within the declared best and worst values.
- Confirm that the reviews displayed on the page match the markup.

Fix:

- Include the review count and rating only when real reviews exist.
- Attribute each review to a named author with a date.

### Add VideoObject schema to video pages

Pages that embed video should declare VideoObject markup with a name, description,
thumbnail, upload date, and content URL or embed URL.

Check:

- Confirm that each video has a name, description, thumbnail, and upload date.
- Confirm that the content or embed URL resolves.

Fix:

- Generate VideoObject markup for each embedded video.
- Use the thumbnail and upload date from the video platform's data.

### Add Organization schema markup

The homepage should declare Organization markup with the name, URL, logo, and social
profile links, so that search engines can associate the brand with its site.

Check:

- Confirm that name, url, and logo are present and absolute.
- Confirm that sameAs links point to the brand's real profiles.

Fix:

- Add the Organization block to the homepage layout only.
- Use a logo URL that is publicly reachable and returns an image.

### Add author markup

Authors should be described as Person entities with a name, a profile URL, and links to
their external profiles.

Check:

- Confirm that each article links to an author page with a Person block.
- Confirm that sameAs links point to real profiles.

Fix:

- Generate a Person block from the author record.
- Link the article's author property to that block by its URL.

### Add WebSite search markup

Sites with internal search should declare WebSite markup with a SearchAction, so that a
sitelinks search box can be produced.

Check:

- Confirm that the homepage contains WebSite JSON-LD with a SearchAction.
- Confirm that the target template contains the query placeholder and that the search
  URL returns results.

Fix:

- Add the WebSite block to the homepage.
- Set the target to the search URL with a query-input property that names the parameter.

## Social sharing metadata

### Add Open Graph tags

Pages that may be shared should provide the core Open Graph tags with absolute URLs, so
that social platforms render accurate previews.

Check:

- Confirm that og:title, og:description, og:image, and og:url are present.
- Confirm that og:image is an absolute HTTPS URL.

Fix:

- Generate the tags in the metadata function from the page record.
- Use absolute URLs built from the site's base address.

### Open Graph image size

The og:image asset should be about 1200 by 630 pixels and should be declared with its
dimensions, so that platforms render a large preview.

Check:

- Check the image's pixel size and aspect ratio.
- Confirm that the image URL is absolute and returns an image type.

Fix:

- Create a 1200 by 630 image for each shareable page or use a generator route.
- Declare og:image:width and og:image:height.

### OG URL match

The og:url value must equal the canonical URL, so that share counts and previews attach
to one address.

Check:

- Compare og:url with the canonical link element on each page.
- Check for tracking parameters in og:url.

Fix:

- Build both values from the same canonical function.
- Remove query parameters from og:url.

### Add Twitter Card meta tags

Shareable pages should declare Twitter (X) Card tags, so that previews render with the
intended card type and image.

Check:

- Confirm that twitter:card is present with a valid card type.
- Confirm that twitter:title, twitter:description, and twitter:image are set when the
  card type requires them.

Fix:

- Add twitter:card set to summary_large_image for pages with an image.
- Fall back to the Open Graph values when the Twitter tags are absent.

### Add share buttons to content pages

Long-form content should expose sharing controls that link to the page's canonical URL,
so that readers can distribute it.

Check:

- Confirm that articles include share links with the encoded page URL.
- Confirm that share links do not depend on a script that blocks navigation.

Fix:

- Build share links from the canonical URL and the page title.
- Use encoded parameters and open the share target in a new tab with noopener.

## Content quality and readability

### Publish high-quality content

Pages that target search traffic should contain substantive, original content that
answers the query in full.

Check:

- Flag pages under about 300 words that serve an informational intent.
- Flag text that could apply to any business or repeats a single source.

Fix:

- Add specific facts, examples, and steps that answer the page's query.
- Remove templated or automatically generated sections that add no information.

### Avoid thin content on key pages

Key pages should contain enough substance to answer their query, rather than a few lines
of boilerplate.

Check:

- Compare the word count and topic coverage with the pages that rank for the query.
- Flag boilerplate or duplicated sections.

Fix:

- Expand the page with specific details that the search intent requires.
- Consolidate thin pages that target the same query.

### Avoid keyword stuffing

Titles, body text, and alt text must describe the content naturally, because repeated
keywords are read as manipulation.

Check:

- Count how often the same phrase repeats in a title, paragraph, or alt attribute.
- Flag hidden text that contains keyword lists.

Fix:

- Rewrite repeated phrases with natural synonyms and specific wording.
- Write alt text that describes the image rather than listing terms.

### Write at a clear reading level

Prose should use short sentences and plain vocabulary, so that the intended audience can
read it without difficulty.

Check:

- Measure the readability of long articles with a Flesch-Kincaid score or a similar
  tool.
- Flag long sentences and dense paragraphs.

Fix:

- Split long sentences and replace unnecessary jargon.
- Add subheadings and lists where they help the reader scan the page.

### Audit and refine AI-generated content

Content drafted with AI assistance must be checked for accuracy, originality, and human
review before publication.

Check:

- Verify factual claims against primary sources.
- Flag generic passages that could appear on any site.

Fix:

- Add review by a subject expert and a named editor.
- Replace unsupported claims with sourced statements or remove them.

## AI discoverability

### Make content easy for LLMs to parse

Informational content should use semantic structure and complete sentences, so that
language models can extract sections accurately.

Check:

- Confirm that the page uses article, section, and heading elements in order.
- Confirm that the main content is present in the initial HTML.

Fix:

- Replace generic div containers with semantic elements.
- Render important text on the server rather than after a client effect.

### Publish llms.txt for documentation-heavy sites

Documentation portals may publish an llms.txt index that lists the most useful, stable
pages in a concise form.

Check:

- Confirm that the file is served at the site root and returns text.
- Confirm that each linked page is stable, accessible without scripts, and useful.

Fix:

- Generate the file from a curated list of documentation pages.
- Add a short description to the file and link only canonical URLs.

```text
# Example Docs

> Public documentation for the example product.

- [Quickstart](https://example.com/docs/quickstart)
```

## Dates and freshness

### Show published and updated dates

Content pages should show a published date and an updated date in machine-readable form,
so that search engines can determine currency.

Check:

- Confirm that a time element with a datetime attribute appears on the page.
- Confirm that the Article markup contains datePublished and dateModified.

Fix:

- Render dates with the time element and an ISO 8601 datetime value.
- Populate dateModified from the record's last substantive update.

### Show content freshness signals

Content should expose freshness through visible dates, article metadata, and HTTP
headers, and the dates must reflect real updates.

Check:

- Check for the article published and modified metadata tags.
- Check for a Last-Modified header on HTML responses.

Fix:

- Set dateModified only when the content changes substantively.
- Enable Last-Modified on the server for HTML responses.

## Authorship, trust, and editorial policy

### Display clear author bylines

Content pages should show the name of the person responsible for the content, so that
readers can judge its origin.

Check:

- Confirm that each article shows a visible author name linked to an author page.
- Flag articles without a named author.

Fix:

- Render the author name in the article header from the content record.
- Link the name to a page that describes the author.

### Highlight author credentials and expertise

Author bios should state the credentials and experience relevant to the topic, so that
readers can assess the author's competence.

Check:

- Confirm that each author bio includes a role and relevant credentials.
- Flag bios that contain only a name.

Fix:

- Add a short bio with role, experience, and a link to credentials.
- Use semantic markup for the bio section.

### Create a dedicated About page

The site should have an About page that identifies the organization or people
responsible for it.

Check:

- Confirm that an About page exists and is reachable from the main navigation or the
  footer.
- Confirm that it names the publisher and describes its purpose.

Fix:

- Create the page with the organization's history, mission, and contact route.
- Link it from the footer.

### Create a comprehensive Contact page

The site should offer a Contact page with more than one way for visitors to reach the
owner.

Check:

- Confirm that a Contact page exists and is linked from the footer.
- Confirm that it offers at least two channels, such as email and a form.

Fix:

- Add a contact form and a visible email address or phone number.
- Link the page from the footer and the help section.

### Publish an editorial policy page

The site should publish its editorial standards, including sourcing, review, and
correction practices.

Check:

- Confirm that an editorial policy page exists and is linked from the footer.
- Confirm that it describes sourcing, review, and corrections.

Fix:

- Write the policy with the editorial team's real process.
- Link the policy from article bylines and the footer.

### Cite authoritative external sources

Factual claims should cite reputable external sources, so that readers and search
engines can verify them.

Check:

- Identify statistics and claims without a source link.
- Check that the sources are primary or well-established.

Fix:

- Link each claim to the originating report or study.
- Prefer primary sources over secondary summaries.

### Add disclaimers to sensitive content

Medical, legal, and financial content must carry a disclaimer that explains its limits
and points readers to qualified advice.

Check:

- Identify pages on health, legal, or financial topics.
- Confirm that each such page carries a visible disclaimer near the content.

Fix:

- Add a disclaimer element near the top of the content.
- Keep the disclaimer text reviewed by the responsible editor.

### Provide clear affiliate disclosures

Pages that contain affiliate or sponsored links must disclose that relationship clearly
and near the links.

Check:

- Identify links to affiliate programs and confirm that a disclosure is present.
- Check that the disclosure is visible without scrolling past the links.

Fix:

- Add a short disclosure at the top of the article or near the links.
- Mark affiliate links with rel sponsored.

```html
<a href="https://partner.example.com/" rel="sponsored noopener noreferrer">Tool</a>
```

### Show trust signals on key pages

Key conversion pages, such as checkout, contact, and pricing pages, should show
verifiable trust evidence.

Check:

- Identify conversion pages and the trust evidence they display.
- Confirm that badges and reviews link to verifiable sources.

Fix:

- Add verifiable reviews, certifications, and security information.
- Link each badge to the issuing body's verification page.

### Identify YMYL content on your site

Pages about health, finance, law, safety, or news must be identified as YMYL, since
search engines hold them to elevated trust standards.

Check:

- Classify each content type against the YMYL categories.
- Confirm that YMYL pages show credentials, sources, and review dates.

Fix:

- Tag YMYL pages in the content model.
- Apply the author, citation, and disclaimer rules to every tagged page.

### Link to active social profiles

The site should link to its active social profiles from the footer and from the
Organization markup.

Check:

- Confirm that the footer links to each profile the organization actively uses.
- Confirm that each link resolves and that the profile is maintained.

Fix:

- List only active profiles, using their real URLs.
- Add the same URLs to the sameAs property of the Organization markup.

## Local business and contact details

### Add LocalBusiness schema markup

Businesses that serve customers at a location should declare LocalBusiness markup with a
name, address, telephone, and opening hours.

Check:

- Confirm that name, address, telephone, and opening hours are present.
- Confirm that the markup matches the visible business details.

Fix:

- Generate the markup from the location record.
- Use the most specific LocalBusiness subtype that applies.

### Keep NAP details consistent

The business name, address, and phone number must be identical across the site and in
the structured data.

Check:

- Compare the name, address, and telephone values in the footer, the contact page, and
  the JSON-LD.
- Flag differences in abbreviations, punctuation, or suite numbers.

Fix:

- Store the details once and render them from that source.
- Choose one canonical written form and use it everywhere.

### Display a physical business address

Businesses with a physical location should show the full postal address in a semantic
address element.

Check:

- Confirm that the address is visible on the page and not only in an image.
- Confirm that the address element is used.

Fix:

- Render the address inside an address element in the footer or contact page.
- Include the address in the LocalBusiness markup.

### Service area pages

Businesses that serve several regions should use dedicated, well-structured area pages
rather than duplicate pages with changed city names.

Check:

- Confirm that each area page contains unique local content.
- Confirm that area pages carry their own canonical URLs and LocalBusiness data.

Fix:

- Write specific content for each region, such as local projects or staff.
- Consolidate area pages that contain only the city name changed.

### Use tel and mailto links

Phone numbers and email addresses should be actionable links, so that users can call or
write with one interaction, especially on mobile.

Check:

- Confirm that telephone numbers use a tel: link in E.164 format.
- Confirm that email addresses use a mailto: link.

Fix:

- Wrap the displayed number in a tel link with the international format.
- Keep the visible text readable and the href in E.164 form.

```html
<a href="tel:+15551234567">+1 (555) 123-4567</a>
```

### Add geo meta tags for regional targeting

Regional tags should use ISO 3166 codes and correct formats, but they have no documented
effect on Google ranking and matter mainly for other engines.

Check:

- Confirm that geo.region uses an ISO code such as US-CA.
- Confirm that geo.position uses the expected separator.

Fix:

- Replace country names with ISO codes.
- Treat the tags as optional and do not rely on them for Google rankings.

## XML sitemaps

### Create and submit an XML sitemap

The site should publish an XML sitemap at a known address that lists its important
pages.

Check:

- Confirm that the sitemap is reachable at its published URL.
- Confirm that it lists the important pages with absolute URLs.

Fix:

- Generate the sitemap from the route or content data.
- Reference the sitemap in robots.txt and submit it in Search Console.

```ts
export default async function sitemap() {
  const pages = await getPublishedPages();
  return pages.map((p) => ({ url: `https://example.com${p.path}` }));
}
```

### Keep XML sitemaps valid

Sitemap files must follow the sitemaps.org protocol, including encoding, namespace, URL
format, and per-file limits.

Check:

- Validate the XML and confirm the UTF-8 declaration and the urlset namespace.
- Confirm that each URL is absolute and entity-escaped.
- Confirm that each file stays within the protocol limits on URLs and size.

Fix:

- Escape ampersands and other reserved characters in URLs.
- Split large sitemaps into an index that references smaller files.

### Keep sitemap URLs on the correct domain

Sitemap entries must use the same domain and protocol as the sitemap and the canonical
URLs, because mismatched entries are ignored.

Check:

- Compare the host and protocol of each entry with the sitemap's host.
- Check the site base URL configuration.

Fix:

- Set one base URL from configuration and use it for all entries.
- Redirect the alternate host to the preferred one.

### Keep 4xx pages out of sitemaps

Sitemap entries must not point to URLs that return 4xx status codes, since they waste
crawl effort and signal poor maintenance.

Check:

- Request each sitemap URL and record URLs with 4xx responses.
- Check whether the removed pages were deleted from the data source.

Fix:

- Generate the sitemap only from published, non-deleted records.
- Remove stale entries and add redirects for pages that moved.

### Noindex pages in sitemap

A URL that carries a noindex directive must not be listed in the sitemap, because the
two signals contradict each other.

Check:

- Cross-check sitemap URLs against noindex meta tags and X-Robots-Tag headers.
- Confirm whether each listed page should be indexed.

Fix:

- Exclude noindex pages from the sitemap generator.
- Remove the noindex directive if the page should be indexed.

### Include indexable pages in your sitemap

Every indexable canonical page should appear in the sitemap, so that new and updated
pages are discovered promptly.

Check:

- Compare the list of indexable canonical URLs with the sitemap entries.
- Confirm that newly published pages are added automatically.

Fix:

- Build the sitemap from the set of published, indexable pages.
- Add the sitemap entry at publication time.
