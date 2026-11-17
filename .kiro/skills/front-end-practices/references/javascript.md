# JavaScript

This file covers the JavaScript rules of the front-end practices skill. It lists each
rule with its priority, difficulty, and a one-sentence statement, and gives the checks
that detect violations together with the fixes that resolve them. It is the reference
the skill loads when a review or remediation involves module structure, language
features, typing, data handling, runtime errors, event handling, memory, or linting in
client-side JavaScript.

## Rule index

| Rule                          | Priority | Difficulty   | Rule statement                                                                                                  |
| ----------------------------- | -------- | ------------ | --------------------------------------------------------------------------------------------------------------- |
| `avoid-eval`                  | critical | beginner     | Strings must never be executed as code through eval, the Function constructor, or string-based timers.          |
| `code-splitting`              | high     | intermediate | Large bundles are split by route and feature so that heavy code loads on demand.                                |
| `const-let`                   | high     | beginner     | Variables are declared with `const` or `let`, never with `var`.                                                 |
| `cross-origin-security`       | high     | intermediate | Cross-origin messages, CORS policies, and redirect targets are validated before any data is trusted.            |
| `debounce-throttle`           | high     | intermediate | High-frequency event handlers are debounced or throttled.                                                       |
| `dom-performance`             | high     | intermediate | DOM reads and writes are batched so that the browser does not compute forced synchronous layouts.               |
| `error-handling`              | high     | intermediate | Asynchronous operations and UI components handle failures explicitly and never swallow errors silently.         |
| `es-modules`                  | high     | beginner     | Code uses ECMAScript module syntax rather than CommonJS, which enables static analysis and tree-shaking.        |
| `javascript-inline`           | high     | beginner     | Behaviour lives in external scripts bound with event listeners, not in inline handlers or script blocks.        |
| `javascript-minification`     | high     | beginner     | Production bundles are minified and unused code is removed.                                                     |
| `memory-leaks`                | high     | intermediate | Listeners, timers, DOM references, and pending requests are released when their owner is destroyed.             |
| `runtime-validation`          | high     | intermediate | Data entering the application from outside is validated at runtime with a schema library.                       |
| `typescript-strict-mode`      | high     | beginner     | The TypeScript configuration enables `strict` so that null and implicit-any defects are caught at compile time. |
| `console-cleanup`             | medium   | beginner     | Console statements other than critical error reporting are removed from production code.                        |
| `event-delegation`            | medium   | intermediate | A single listener on a stable ancestor serves dynamic children instead of one listener per element.             |
| `immutable-patterns`          | medium   | intermediate | Functions produce new objects and arrays instead of mutating their inputs.                                      |
| `javascript-linter`           | medium   | beginner     | All JavaScript is checked with ESLint using a shared configuration, locally and in CI.                          |
| `json-safety`                 | medium   | beginner     | Every `JSON.parse` call is guarded and its result is validated before use.                                      |
| `modern-array-methods`        | medium   | beginner     | Manual loops are replaced with declarative array and object methods where these clarify intent.                 |
| `no-explicit-any`             | medium   | intermediate | The `any` type is replaced with `unknown`, generics, or validated types.                                        |
| `no-unchecked-indexed-access` | medium   | intermediate | The `noUncheckedIndexedAccess` compiler option is enabled so that indexed reads include `undefined`.            |
| `scheduler-yield`             | medium   | intermediate | Synchronous work longer than 50 ms yields to the browser between chunks.                                        |
| `translation-strings`         | medium   | intermediate | Translatable text uses named placeholders and ICU message patterns, not string concatenation.                   |
| `type-coercion`               | medium   | beginner     | Strict equality and explicit conversions replace loose comparison and implicit coercion.                        |
| `web-storage`                 | medium   | beginner     | `localStorage` and `sessionStorage` are accessed defensively and never hold sensitive values.                   |
| `type-only-imports`           | low      | beginner     | Imports that exist only for type information use the `import type` form.                                        |

## Modules and bundling

### Use ECMAScript module syntax

Modules use `import` and `export` so that bundlers can determine statically which code
is used.

Check:

- Search new or modified files for `require(`, `module.exports`, and `exports.`.
- Confirm whether the build pipeline or the browser loads the output as modules.

Fix:

- Convert `require` calls to `import` declarations and `module.exports` to named
  `export` statements.
- Load classic browser scripts with `type="module"` or through a bundler.

### Mark type-only imports explicitly

Imports that supply only type information use the `import type` form so that they are
erased at compile time.

Check:

- Review TypeScript files for imports whose bindings appear only in type positions.
- Confirm whether the compiler option `verbatimModuleSyntax` is enabled.

Fix:

- Rewrite such imports as `import type { User } from './models'`.
- Enable `verbatimModuleSyntax` so that the compiler enforces the distinction.

### Split large bundles

Heavy features are loaded through dynamic `import()` only when the user needs them,
which reduces the initial download.

Check:

- Identify large third-party or feature modules that are imported statically at the top
  of an entry or route file.
- Inspect the bundle with a visualiser to confirm which chunks are large.

Fix:

- Replace the static import with `await import(...)` at the point of use.
- Split routes so that each page loads only its own code, and show a loading state while
  a chunk is fetched.

```javascript
// Before: the module is part of the entry bundle
// import { generatePDF } from './pdf-generator.js'

async function handleExportClick() {
  const { generatePDF } = await import("./pdf-generator.js");
  generatePDF(document);
}
```

### Minify production bundles

Production JavaScript is minified so that comments and whitespace are removed and
identifiers are shortened.

Check:

- Confirm that the production build configuration enables minification.
- Compare the size of the served files with the size of the source files.

Fix:

- Enable the minifier of the build tool, such as Terser or esbuild in Vite, or set the
  production mode in webpack.
- Verify that tree-shaking is active and keep source maps available if debugging
  requires them.

### Keep behaviour out of inline markup

Behaviour is kept in external files and bound with listeners, because inline handlers
prevent caching and conflict with a strict Content Security Policy.

Check:

- Search HTML templates for `on*` attributes, `javascript:` URLs, and inline `<script>`
  blocks that contain application logic.
- Confirm whether a Content Security Policy forbids inline scripts.

Fix:

- Move the logic into external files loaded with `defer`, and bind handlers with
  `addEventListener`.
- Use data attributes to pass configuration from markup to the script.

```html
<!-- Before -->
<button onclick="save()">Save</button>

<!-- After -->
<button class="js-save" data-action="save">Save</button>
<script src="js/app.js" defer></script>
```

## Language features

### Declare variables with const and let

Block-scoped declarations avoid the hoisting and function-scope defects of `var` and
make reassignment explicit.

Check:

- Scan the file for every occurrence of `var` and record its line number.
- Determine for each binding whether it is reassigned.

Fix:

- Use `const` for bindings that are never reassigned and `let` otherwise.
- Enable the ESLint rules `no-var` and `prefer-const` to prevent regression.

### Prefer non-mutating updates

Functions that return new objects and arrays keep data flow predictable and simplify
debugging and state management.

Check:

- Locate direct property assignments to function parameters.
- Locate `push`, `splice`, and `sort` calls on arrays that are shared or received as
  arguments.

Fix:

- Build modified copies with the spread operator and non-mutating methods such as `map`,
  `filter`, and `toSorted`.
- Apply `Object.freeze` to configuration objects that must never change.

### Use declarative array and object methods

Methods such as `map`, `filter`, `reduce`, `find`, and `flatMap` express the intent of a
transformation more directly than index-based loops.

Check:

- Find `for` and `while` loops that build a new array, search for an element with
  `break`, or transform object entries.
- Find deep copies implemented as `JSON.parse(JSON.stringify(...))`.

Fix:

- Replace the loops with the matching method, and use `Object.entries` and
  `Object.fromEntries` for object transformations.
- Use `structuredClone` for deep copies, after confirming that the values are cloneable.

### Use strict equality and explicit conversion

Loose equality and implicit coercion produce results that depend on operand types, for
example `'5' + 3` yields `'53'`.

Check:

- Search for `==` and `!=` and for arithmetic or concatenation on values read from the
  DOM or from URL parameters.
- Look for `typeof` checks used to detect arrays.

Fix:

- Replace `==` with `===` and `!=` with `!==`.
- Convert values explicitly with `Number`, `String`, or `parseInt(value, 10)`, and use
  `Array.isArray` for array detection.

### Eliminate eval and string-based code execution

Strings passed to `eval`, the `Function` constructor, or string timers are executed as
code, which turns any attacker-controlled input into a cross-site scripting vector.

Check:

- Search the code for `eval(`, `new Function(`, and `setTimeout` or `setInterval` called
  with a string argument.
- Inspect the Content Security Policy for `unsafe-eval`.

Fix:

- Parse data with `JSON.parse` and dispatch dynamic actions through an explicit lookup
  table of functions.
- Pass function references to timers instead of strings.

```javascript
// Before: the string is compiled and executed at runtime
// setTimeout('updateUI()', 1000)

// After: a function reference is passed
setTimeout(updateUI, 1000);
```

## Typing

### Enable TypeScript strict mode

The `strict` flag activates the compiler checks that detect null dereferences and
implicit `any` types before the code runs.

Check:

- Read `tsconfig.json` and report whether `"strict": true` is set and which strict flags
  are missing.
- Count the type errors that appear when strict mode is enabled.

Fix:

- Set `"strict": true` in `compilerOptions`.
- In a legacy codebase, enable `strictNullChecks` first, resolve its errors, and then
  enable the remaining flags incrementally.

### Replace any with unknown, generics, or guards

The `any` type disables type checking for a value and propagates to its callers, so
defects that the compiler would report are silently accepted.

Check:

- Search for `: any`, `<any>`, `as any`, and parameters without annotations that are
  implicitly `any`.
- Note whether each occurrence sits on internal logic or on an external boundary.

Fix:

- Use `unknown` for values of unknown shape and narrow them with type guards.
- Use generics for functions whose input and output types must correspond, and a schema
  library at external boundaries.

### Enable noUncheckedIndexedAccess

Without this option an indexed read such as `items[0]` is typed as present even when the
array is empty, which produces runtime errors the compiler cannot see.

Check:

- Confirm whether `noUncheckedIndexedAccess` is set in `tsconfig.json`.
- Search for index accesses such as `arr[i]` and `record[key]`.

Fix:

- Enable the option, then handle the `undefined` case in each reported access with a
  guard or a fallback through `??`.

## Data handling

### Validate external data at runtime

Validation is performed at runtime because TypeScript types are erased, so an API
response or a stored value can differ from its declared type without a compile error.

Check:

- List the entry points where external data arrives: `fetch` responses, form inputs,
  storage reads, and environment variables.
- Identify those that are typed only by assertion or annotation.

Fix:

- Define a schema with Zod or Valibot and call `safeParse` at the entry point.
- Derive the TypeScript type from the schema so that the two cannot diverge.

```typescript
const ProductSchema = z.object({
  id: z.string(),
  price: z.number().positive(),
});
const json: unknown = await res.json();
const result = ProductSchema.safeParse(json);
```

### Parse JSON defensively

`JSON.parse` must be guarded because it throws a `SyntaxError` on malformed input and a
well-formed document can still have an unexpected shape.

Check:

- Find each `JSON.parse` call and determine whether it sits inside a `try` block.
- Determine whether the parsed value is checked before its properties are read.

Fix:

- Wrap the call in `try` with a defined fallback value.
- Validate the parsed structure with a schema before using it.

### Access Web Storage defensively

Storage access is guarded because operations throw when the quota is exceeded or storage
is disabled, and values held in these stores are readable by every script on the page.

Check:

- Find each `localStorage` and `sessionStorage` call and check for a `try` block.
- Check that stored objects are serialised and validated on read, and that no tokens,
  passwords, or personal data are stored.

Fix:

- Wrap the access in a helper that returns a fallback on failure.
- Move authentication tokens to httpOnly cookies set by the server.

### Use placeholder-based translation messages

Translated text uses named placeholders and ICU patterns because concatenation fixes the
word order of one language and cannot express plural or gender forms in others.

Check:

- Search for string concatenation that includes a translated string.
- Search for conditionals in code that choose plural or gender wording.

Fix:

- Use named placeholders and ICU MessageFormat patterns, and let the translation library
  select plural and select forms.

```text
"You have {count, plural, one {# message} other {# messages}}"
```

## Runtime errors and memory

### Handle asynchronous and UI errors explicitly

Failures are handled explicitly because an unhandled rejection leaves the interface
broken and an empty `catch` hides the defect from everyone.

Check:

- Locate `async` functions and promise chains without `try` or `.catch`.
- Locate `catch` blocks that are empty or only discard the error, and check that
  component trees have error boundaries.

Fix:

- Wrap asynchronous operations in `try`, log the error with its context, and either
  rethrow it or show a recoverable state.
- Add error boundaries at route and widget level.

### Release listeners, timers, and references

Listeners, intervals, and references are released when their owner is destroyed, because
those that outlive it keep objects in memory and continue to run work.

Check:

- Find `addEventListener` calls without a matching removal in the teardown path.
- Find `setInterval` and `setTimeout` calls without a clear, and fetches that complete
  after the view is destroyed.

Fix:

- Remove listeners in the cleanup function, or pass an `AbortController` signal so that
  a single `abort()` releases a group of listeners.
- Clear timers during teardown and cancel stale requests with `AbortController`.

```javascript
const controller = new AbortController();
window.addEventListener("scroll", onScroll, { signal: controller.signal });
window.addEventListener("resize", onResize, { signal: controller.signal });
// On teardown:
controller.abort();
```

## Events and main thread

### Delegate events to a stable ancestor

A single listener on a stable container replaces one listener per child, which reduces
memory use and covers elements added after the page has loaded.

Check:

- Find loops that attach one handler to many elements of the same kind.
- Check whether those elements are created dynamically.

Fix:

- Attach one listener to the nearest stable container, and use
  `event.target.closest(selector)` to identify the intended element.
- Remove the container listener when the container itself is removed.

### Limit the rate of high-frequency handlers

Debouncing and throttling bound the number of calls for input, scroll, resize, and
mouse-movement handlers, which can fire dozens of times per second.

Check:

- List handlers attached to `input`, `scroll`, `resize`, and `mousemove`.
- Determine whether each handler performs network or layout work.

Fix:

- Debounce input-driven handlers with a delay of 150 to 300 ms.
- Throttle scroll and resize handlers to roughly 100 ms, and remove them on teardown.

### Batch DOM reads before writes

Reads and writes are batched because alternating a layout read such as `offsetHeight`
with a style write forces a synchronous layout on every iteration.

Check:

- Find loops in which layout reads and style or class writes are interleaved.
- Find `scroll`, `touchstart`, and `wheel` listeners that do not call `preventDefault`.

Fix:

- Read all required values into variables first, then perform all writes.
- Schedule visual updates with `requestAnimationFrame`, and mark listeners that never
  cancel scrolling with `{ passive: true }`.

### Yield during long tasks

Long tasks are divided into chunks because a synchronous task longer than 50 ms blocks
input handling and degrades the Interaction to Next Paint metric.

Check:

- Identify loops, recursive traversals, and bulk DOM operations over large collections.
- Estimate the duration of each task on a representative device.

Fix:

- Process the work in chunks and await `scheduler.yield()` between them, with a
  `MessageChannel` fallback where the API is unavailable.

### Validate cross-origin messages, CORS, and redirects

Origins are validated because unchecked messages, permissive CORS policies, and open
redirects let hostile sites inject data, read authenticated responses, or send users to
phishing destinations.

Check:

- Find `message` event listeners that do not compare `event.origin` with an allow-list.
- Find `Access-Control-Allow-Origin: *` on authenticated endpoints and redirect
  parameters such as `next` used without validation.

Fix:

- Compare `event.origin` with an explicit allow-list before reading `event.data`.
- Restrict CORS to known origins and validate redirect targets against an allow-list.

```javascript
window.addEventListener("message", (event) => {
  if (event.origin !== "https://app.example.com") return;
  handleMessage(event.data);
});
```

## Linting and console

### Lint all JavaScript with ESLint

A shared lint configuration enforces consistent style and detects syntax defects across
the team when it runs both in the editor and in CI.

Check:

- Confirm that an ESLint configuration exists and extends a recommended preset.
- Confirm that the lint command runs in the CI pipeline and fails on errors.

Fix:

- Initialise ESLint and extend `eslint:recommended` and, for TypeScript,
  `typescript-eslint`.
- Resolve the reported errors and add the lint command to CI.

### Remove debug console output from production

Console output is removed from production builds because it exposes internal state to
anyone who opens the developer tools.

Check:

- Search for `console.log`, `console.debug`, `console.table`, and `console.warn`.
- Determine whether a build step already strips them.

Fix:

- Configure the minifier to drop console calls in production builds, for example with
  `drop_console` in Terser.
- Replace diagnostic output with an environment-aware logger, and keep `console.error`
  only where it is required for error tracking.
