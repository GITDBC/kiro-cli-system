# Security

This file covers the security rules of the front-end practices skill. It lists each rule
with its priority, difficulty, and a one-sentence statement that names the threat the
rule mitigates, and it gives the checks that detect violations together with the fixes
that resolve them. It is the reference the skill loads when a review or remediation
involves transport encryption, HTTP response headers, cookies and session tokens,
third-party resources, form and password input, dependencies, or error exposure in
client-facing applications.

## Rule index

| Rule                      | Priority | Difficulty   | Rule statement                                                                                                                                                     |
| ------------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `https`                   | critical | beginner     | Every page and resource is served over HTTPS so that traffic cannot be read or altered in transit.                                                                 |
| `http-to-https`           | critical | beginner     | Plain HTTP requests receive a permanent 301 redirect to HTTPS, which prevents users from remaining on an unencrypted connection.                                   |
| `form-https`              | critical | beginner     | Form actions and client-side API calls target HTTPS URLs, which prevents interception of submitted data.                                                           |
| `leaked-secrets`          | critical | intermediate | Secrets are kept out of HTML, bundles, and repositories, which prevents credential theft by anyone who views the source.                                           |
| `content-security-policy` | high     | advanced     | A Content Security Policy restricts the sources of scripts and resources, which limits cross-site scripting and data exfiltration.                                 |
| `dependency-audit`        | high     | beginner     | Dependencies are scanned for known vulnerabilities and critical findings block releases, which prevents exploitation of vulnerable packages.                       |
| `hsts`                    | high     | intermediate | HTTPS responses carry a Strict-Transport-Security header, which prevents protocol downgrade and cookie hijacking.                                                  |
| `mixed-content`           | high     | intermediate | HTTPS pages load only HTTPS sub-resources, which prevents substitution of scripts, styles, or media in transit.                                                    |
| `password-field-security` | high     | intermediate | Password inputs use correct types, autocomplete values, and accessible controls, which prevents credential exposure and supports password managers.                |
| `session-cookie-flags`    | high     | beginner     | Session and authentication cookies carry the Secure, HttpOnly, and SameSite attributes, which prevents interception, script theft, and cross-site request forgery. |
| `stack-trace-exposure`    | high     | intermediate | Production error responses return generic messages, which prevents reconnaissance from stack traces and internal paths.                                            |
| `token-storage-security`  | high     | intermediate | Authentication tokens are held in httpOnly cookies rather than Web Storage, which prevents theft by injected scripts.                                              |
| `x-content-type`          | high     | beginner     | Responses carry `X-Content-Type-Options: nosniff`, which prevents browsers from executing content under a different MIME type.                                     |
| `x-frame-options`         | high     | beginner     | Pages declare whether they may be framed, which prevents clickjacking through invisible iframes.                                                                   |
| `cross-origin-isolation`  | medium   | advanced     | COOP, COEP, and CORP are enabled only where the application requires isolation, which limits cross-origin side-channel and window-reference attacks.               |
| `form-captcha`            | medium   | intermediate | Public forms are protected by server-validated bot checks and rate limits, which prevents spam, credential stuffing, and automated abuse.                          |
| `new-tab`                 | medium   | beginner     | Links that open a new tab carry `rel="noopener noreferrer"`, which prevents reverse tabnabbing.                                                                    |
| `permissions-policy`      | medium   | intermediate | Unused browser features are denied through a Permissions-Policy header, which limits abuse of sensors and payment APIs by compromised scripts or frames.           |
| `referrer-policy`         | medium   | beginner     | A Referrer-Policy header limits the URL information sent to other sites, which prevents leakage of sensitive query values.                                         |
| `terms-of-service`        | medium   | beginner     | A Terms of Service page is linked from every page and accepted at sign-up, which mitigates unenforceable usage terms.                                              |
| `blocked-links`           | low      | intermediate | Functionality does not depend on tracking domains that filter lists commonly block, which prevents broken features and skewed measurement.                         |
| `element-hiding`          | low      | intermediate | Class names and IDs avoid patterns used by ad-blocker filter lists, which prevents hidden layout and hidden legitimate content.                                    |

## Transport security

### Serve the entire site over HTTPS

Every page and resource is delivered over HTTPS so that user data in transit cannot be
read or modified by a network attacker.

Check:

- Confirm that every page and asset loads over `https://` and that the certificate is
  valid, unexpired, and covers `www` and every other hostname.
- Confirm that plain HTTP requests return a 301 redirect.

Fix:

- Obtain a certificate from Let's Encrypt or from the managed TLS service of the hosting
  provider, and configure the server with it.
- Replace hard-coded `http://` URLs in links and resources with `https://` equivalents.

### Redirect HTTP to HTTPS permanently

A permanent redirect ensures that requests for the plain HTTP address reach the
encrypted site, which prevents a downgrade on the first request to the domain.

Check:

- Run `curl -I http://<domain>` and confirm a 301 status with a `Location` header
  pointing to the HTTPS address.
- Confirm that the path and query string are preserved in the `Location` header.

Fix:

- Configure the redirect at the server or CDN, never in client-side JavaScript.
- Add HSTS after the HTTPS redirect has been validated.

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

### Submit forms and API calls over HTTPS

Form actions and client-side requests use HTTPS so that submitted credentials and
personal data are encrypted and cannot be intercepted on the network.

Check:

- Search HTML for `<form action="http://` and JavaScript for `http://` endpoints in
  `fetch` and `XMLHttpRequest` calls.
- Confirm that a form without an explicit `action` belongs to a page served over HTTPS.

Fix:

- Replace every `http://` form action and API endpoint with its `https://` equivalent.
- Redirect the HTTP origin with a 301 so that any residual link is corrected.

### Enforce HTTPS with HSTS

The Strict-Transport-Security header instructs browsers to refuse plain HTTP for the
domain, which prevents downgrade attacks and cookie hijacking over HTTP.

Check:

- Confirm that every HTTPS response carries the header with a `max-age` of at
  least 31536000.
- Confirm that `includeSubDomains` is present where all subdomains use HTTPS, and that
  `preload` is requested only after review.

Fix:

- Send `Strict-Transport-Security: max-age=31536000; includeSubDomains` on HTTPS
  responses only.
- Test the policy thoroughly before adding `preload`, because removal is slow.

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Remove insecure sub-resource URLs

An HTTPS page that loads resources over HTTP exposes those resources to substitution by
a network attacker, and browsers block or warn about active content.

Check:

- Scan `<script src>`, `<link href>`, `<img src>`, `<iframe src>`, and CSS `url()`
  values for `http://` addresses.
- Check the Content Security Policy for `upgrade-insecure-requests`.

Fix:

- Replace each `http://` resource with an `https://` address, or host the resource
  locally when the provider lacks HTTPS.
- Add `upgrade-insecure-requests` to the policy as a safety net for legacy content.

## Response headers

### Restrict sources with a Content Security Policy

A Content Security Policy limits which origins may supply scripts and other resources,
which prevents injected code from executing or sending data to hostile hosts.

Check:

- Confirm that a policy is sent and inspect it for `unsafe-inline` and `unsafe-eval`.
- Search for `innerHTML`, `dangerouslySetInnerHTML`, and unsanitised template injection
  that the policy must constrain.

Fix:

- Begin with `Content-Security-Policy-Report-Only`, then enforce the policy after the
  reports are clean, using nonces or hashes instead of `unsafe-inline`.
- Sanitise untrusted HTML with a library such as DOMPurify before rendering it.

```text
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'
```

### Set X-Content-Type-Options to nosniff

The `nosniff` directive stops browsers from reinterpreting a response as a different
type, which prevents a disguised script from being executed.

Check:

- Confirm that HTML, JavaScript, CSS, and API responses carry the header.
- Verify the result with `curl -I` against each response type.

Fix:

- Add `X-Content-Type-Options: nosniff` at the web server or framework level.
- Send correct `Content-Type` values on every response.

### Prevent framing with X-Frame-Options

The header declares whether the page may be embedded in a frame, which prevents
clickjacking through invisible iframes placed over attacker content.

Check:

- Confirm that the response carries `X-Frame-Options` or a CSP `frame-ancestors`
  directive.
- Confirm whether the page is legitimately embedded anywhere.

Fix:

- Send `X-Frame-Options: DENY` unless framing is required, or `SAMEORIGIN` when
  same-origin framing is needed.
- Prefer `frame-ancestors` for fine-grained control over the permitted embedding
  origins.

### Limit referrer information

A restrictive Referrer-Policy prevents URL paths and query values, which may contain
tokens or identifiers, from being disclosed to third-party destinations.

Check:

- Confirm that a `Referrer-Policy` header is sent and inspect its value.
- Identify pages whose URLs carry sensitive parameters such as reset tokens.

Fix:

- Set `Referrer-Policy: strict-origin-when-cross-origin` as the default.
- Use `no-referrer` or `same-origin` on pages with sensitive URLs, and never use
  `unsafe-url`.

### Deny unused browser features

Permissions-Policy disables powerful features the site does not use, which limits abuse
of the camera, microphone, geolocation, or payment APIs by compromised scripts or
embedded frames.

Check:

- Confirm whether the header is sent and which features are enabled.
- Identify features that are enabled but not required by the application.

Fix:

- Send a header that denies unused features, starting with
  `camera=(), microphone=(), geolocation=()`.
- Expand the list only for features the application demonstrably uses.

```text
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
```

### Isolate cross-origin only when required

Cross-origin isolation is enabled only for applications that need it, because COOP and
COEP break third-party resources and limit cross-origin side-channel attacks when they
are applied without an audit.

Check:

- Determine whether the application uses features that require isolation, such as
  `SharedArrayBuffer`.
- Audit embedded scripts, frames, images, workers, and fonts for CORP or CORS support.
- Verify `self.crossOriginIsolated` in the browser.

Fix:

- Send `Cross-Origin-Opener-Policy: same-origin` and
  `Cross-Origin-Embedder-Policy: require-corp` after the audit.
- Serve subresources with `Cross-Origin-Resource-Policy` or CORS as required.

## Cookies and session tokens

### Set Secure, HttpOnly, and SameSite on session cookies

Session cookies carry the Secure, HttpOnly, and SameSite attributes, which prevents
interception over HTTP, theft by injected scripts, and cross-site request forgery.

Check:

- Inspect the `Set-Cookie` header for each session and authentication cookie.
- Confirm that `SameSite=None` is never used without `Secure`.

Fix:

- Add `Secure`, `HttpOnly`, and `SameSite=Strict` or `SameSite=Lax` in the server cookie
  configuration.
- Apply the same options to every cookie that represents a session.

```text
Set-Cookie: session_id=<opaque>; Path=/; Secure; HttpOnly; SameSite=Strict
```

### Store authentication tokens in httpOnly cookies

Tokens are held in httpOnly cookies because any script on the page can read values in
localStorage or sessionStorage, so an injected script can steal them.

Check:

- Search client code for tokens written to or read from `localStorage` or
  `sessionStorage`.
- Verify that POST, PUT, PATCH, and DELETE requests carry a CSRF token or an equivalent
  anti-forgery control.

Fix:

- Have the server set the token in an httpOnly cookie with `Secure` and `SameSite`.
- Use short-lived access tokens, rotate refresh tokens on use, and protect every
  state-changing route against CSRF.

```javascript
// Avoid: any script on the page can read this value
localStorage.setItem("authToken", token);
```

## Secrets and error exposure

### Keep secrets out of client-side code

Anything shipped to the browser is public, so credentials stay on the server, which
prevents theft of API keys and tokens by anyone who views the page source.

Check:

- Scan HTML, JavaScript bundles, and built assets for patterns such as `sk_`, `AIza`,
  `ghp_`, and `AKIA`, and for base64-encoded credentials.
- Check for environment variables with public prefixes, such as `NEXT_PUBLIC_`, that
  hold secret values, and search git history for committed credentials.

Fix:

- Move each call that needs a secret to a server-side route or proxy.
- Rotate every credential found in client code or history, and install a secret scanner
  such as GitLeaks or git-secrets in a pre-commit hook.

### Hide stack traces in production errors

Production responses return a generic message and a correlation identifier, while the
full detail is kept in server logs, which prevents attackers from learning internal
paths, framework versions, and query structure.

Check:

- Trigger error responses on the API and inspect bodies for stack traces, file paths,
  SQL fragments, or framework names.

Fix:

- Route all errors through a central handler that logs full details server-side.
- Return a sanitised message and a correlation identifier that support staff can match
  to the logs.

### Audit dependencies for known vulnerabilities

Dependencies are audited before release and in CI, because vulnerable third-party
packages are a common route into production applications.

Check:

- Run `npm audit` or `pnpm audit` and record the critical and high findings.
- Confirm that a lock file is committed and that CI runs automated scanning.

Fix:

- Upgrade, patch, or replace each vulnerable package.
- Enable Dependabot or Snyk in CI and treat critical and high findings as release
  blockers.

## Forms and authentication input

### Configure password fields correctly

Password fields use the correct type and autocomplete values, which lets password
managers generate and fill credentials and prevents plain-text exposure of the value.

Check:

- Confirm that each password input has `type="password"` and an `autocomplete` value of
  `new-password` or `current-password`.
- Confirm that any visibility toggle is a labelled button with state announced to
  assistive technology.

Fix:

- Set the autocomplete value according to whether the form creates or verifies a
  password.
- Add a labelled visibility toggle and a strength indicator with visible requirements.

```html
<label for="new-pw">New password</label>
<input id="new-pw" name="password" type="password" autocomplete="new-password" />
```

### Protect public forms from automated abuse

Public forms are guarded by bot checks that are verified on the server, which prevents
spam, credential stuffing, and automated account creation.

Check:

- List public forms: contact, registration, login, password reset, and comments.
- Confirm that each has a CAPTCHA, honeypot field, or server-side rate limit, and that
  tokens are verified on the server.

Fix:

- Integrate an invisible challenge such as Cloudflare Turnstile, reCAPTCHA v3, or
  hCaptcha, and verify its token on the server before processing.
- Add rate limiting as defence in depth, and use a honeypot for low-risk forms.

## Third-party and browsing

### Protect links that open new tabs

Links with `target="_blank"` carry `rel="noopener noreferrer"`, which prevents the
opened page from redirecting the original tab to a phishing page.

Check:

- Find each anchor with `target="_blank"` and confirm that it has the `rel` value.
- Flag external links that open in a new tab without it.

Fix:

- Add `rel="noopener noreferrer"` to every such anchor.
- Enable an ESLint rule that flags missing values so that the defect does not recur.

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Example</a>
```

### Publish and link Terms of Service

A Terms of Service page is linked from every page and accepted explicitly at sign-up,
which establishes the terms under which the service is used and reduces the risk that
they are held unenforceable.

Check:

- Confirm that the footer of every page, including interior pages, links to the page.
- For services with accounts, confirm that registration requires an acceptance step.

Fix:

- Add the footer link and keep its URL stable.
- Add an acceptance checkbox at registration that links to the terms, and keep the terms
  current.

### Avoid dependence on blockable tracking domains

Critical scripts and links do not depend on domains that filter lists commonly block,
which prevents broken functionality and undercounted analytics for a large share of
users.

Check:

- Identify scripts, images, iframes, and anchors that point to known tracking or
  advertising domains.
- Load the page with a content blocker enabled and compare the behaviour.

Fix:

- Self-host or proxy critical scripts through the first-party domain.
- Replace tracking redirect links with direct destination URLs.

### Avoid class names that match ad-blocker filters

Class names and IDs avoid the patterns used by ad-blocker filter lists, which prevents
legitimate banners, notices, and consent controls from being hidden.

Check:

- Review class names and IDs for `ad`, `ads`, `banner`, `sponsor`, `cookie-banner`, and
  `consent`.
- Test the page with a content blocker enabled and look for missing content.

Fix:

- Rename affected elements with specific, content-focused names such as
  `cookie-preferences`.
- Keep the rename consistent across the stylesheet and scripts that use the name.
