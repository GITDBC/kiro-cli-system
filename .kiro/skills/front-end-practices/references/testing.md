# Testing

This file covers the testing rules of the front-end practices skill. It lists each rule
with its priority, difficulty, and a one-sentence statement, and gives the checks that
detect missing or weak test coverage together with the steps that establish it. It is
the reference the skill loads when a review or remediation involves unit, integration,
and end-to-end tests, cross-browser and mobile verification, accessibility and visual
checks, mutation and coverage measurement, contract tests, or production error and
performance monitoring.

## Rule index

| Rule                    | Priority | Difficulty   | Rule statement                                                                                                           |
| ----------------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `accessibility-testing` | high     | intermediate | Automated accessibility checks run against components and pages in the test suite and in CI.                             |
| `cross-browser-testing` | high     | intermediate | The application is tested in Chrome, Firefox, Safari, and Edge, on desktop and mobile.                                   |
| `e2e-testing`           | high     | intermediate | Critical user journeys are covered by end-to-end tests that run in CI and keep artifacts on failure.                     |
| `error-monitoring`      | high     | intermediate | A production monitoring service captures unhandled errors, rejections, and failed requests and raises alerts.            |
| `integration-testing`   | high     | intermediate | Interactions between units, such as routes with databases or components with state, are tested with real dependencies.   |
| `mobile-testing`        | high     | intermediate | Key flows are verified at common mobile viewports and on real devices, not only on desktop emulation.                    |
| `unit-tests`            | high     | intermediate | Business logic, utilities, and edge cases are covered by unit tests with descriptive names and meaningful coverage.      |
| `contract-testing`      | medium   | advanced     | Consumer-driven contract tests verify the frontend's API expectations against the provider in CI.                        |
| `mock-best-practices`   | medium   | intermediate | Mocks replace only external boundaries, are restored after each test, and assert behaviour rather than internals.        |
| `mutation-testing`      | medium   | advanced     | Mutation testing on critical modules shows whether the tests detect injected faults, with a target score of 80% or more. |
| `performance-budget`    | medium   | intermediate | Performance budgets for bundle size and Lighthouse or Core Web Vitals metrics fail the CI build when exceeded.           |
| `test-coverage`         | medium   | beginner     | Coverage thresholds must meet the project floor of 80% minimum, enforced by the SonarQube gate.                          |
| `visual-regression`     | medium   | intermediate | Screenshots of components and pages are compared with approved baselines to detect unintended visual changes.            |

## Unit and integration

### Write unit tests for business logic

Unit tests cover business logic, utilities, and edge cases so that defects in the
behaviour of individual functions are detected before integration.

Check:

- Identify modules that contain business rules or utilities without a test file.
- Review test names and confirm that each describes an observable behaviour.

Fix:

- Add tests for each public function, including boundary and invalid inputs.
- Run the suite in CI so that regressions fail the pipeline.

```javascript
test("applyDiscount rejects a negative percentage", () => {
  expect(() => applyDiscount(100, -5)).toThrow(RangeError);
});
```

### Test integration points with real dependencies

Integration tests exercise the boundary where components meet, such as an API route and
its database, because mocking every collaborator hides the defects that occur at those
seams.

Check:

- Identify where API routes call services, services query the database, and components
  read or write shared state.
- Determine which of these interactions have a test that runs them together.

Fix:

- Write tests for the critical happy paths and the most important error paths.
- Use a test database or an in-memory database rather than mocking the data layer.

### Mock external boundaries only

Mocks are limited to external boundaries, restored after each test, and used to assert
behaviour, because over-mocking produces tests that pass while the real integration is
broken.

Check:

- Search the test files for mocks of internal modules that contain business logic.
- Confirm that each mock is restored in `afterEach` and that assertions target outputs
  rather than call sequences.

Fix:

- Mock network, database, and file system boundaries, and use MSW for realistic HTTP
  mocks without coupling to the implementation.
- Restore all mocks after each test with the restore call of the framework, such as
  `jest.restoreAllMocks()`.

### Measure test strength with mutation testing

Mutation testing shows whether the tests detect defects, which coverage cannot establish
because a line can be executed without its behaviour being verified.

Check:

- Confirm whether Stryker is configured for the critical modules.
- Review the mutation score and the surviving mutants on critical business paths.

Fix:

- Run Stryker on one module at a time to keep CI time bounded.
- Add assertions that kill the surviving mutants, targeting a score of 80% or more.

### Enforce coverage thresholds

Coverage thresholds are configured and enforced in CI so that new code cannot reduce
coverage below an agreed level without the pipeline failing.

Check:

- Read the coverage configuration in Jest, Vitest, or the active framework.
- Confirm that CI runs the coverage command and fails when a threshold is not met.
- Confirm that the threshold applied is the project floor: 80% minimum, enforced by the
  SonarQube gate, as set in `.kiro/steering/code-standards-summary.md`.

Fix:

- Set the coverage threshold to the project floor of 80% minimum, enforced by the
  SonarQube gate, and do not lower it for individual modules without a recorded reason.
- Exclude generated code, type declarations, and configuration files from the report.
- Example, not adopted in this repository: the upstream default sets global thresholds
  of 70% for branches and 80% for lines, functions, and statements, and raises them to
  90% or more for critical utilities. Use these figures only where a project adopts them
  explicitly.

### Verify API contracts consumer-first

Consumer-driven contracts record what the frontend expects from the API, which catches
provider changes that would break the client before deployment and removes the need for
fragile end-to-end runs against both services.

Check:

- Determine whether consumer tests exist for the frontend API client.
- Determine whether the contracts are published and verified by the provider in CI.

Fix:

- Write Pact consumer tests for the API client and publish the contracts to a broker.
- Add provider verification to the backend pipeline so that breaking changes fail.

## End-to-end and cross-environment

### Cover critical journeys end to end

End-to-end tests drive the application through the journeys that matter most, such as
authentication, checkout, and core forms, using a browser automation framework.

Check:

- List the critical journeys and confirm that each has an end-to-end test.
- Confirm that selectors use stable attributes and that CI uploads artifacts on failure.

Fix:

- Add Playwright or Cypress tests for each missing journey.
- Use `data-testid` attributes for selectors and a Page Object Model for shared steps.

### Test across major browsers

Behaviour is verified in each major browser because layout and API support differ
between rendering engines and between desktop and mobile versions.

Check:

- Inspect the test configuration for projects covering Chrome, Firefox, Safari, and
  Edge.
- Check CSS and API features against support data before relying on them.

Fix:

- Configure a browser project for each engine in Playwright, or use a cloud service for
  engines not available in CI.
- Provide a graceful fallback for features that a browser does not support.

### Test on mobile viewports and devices

Mobile verification covers touch behaviour, viewport breakpoints, and rendering that
desktop emulation does not reproduce.

Check:

- Search the test configuration for mobile device presets or viewport tests.
- Confirm that breakpoints such as 375 px, 390 px, and 768 px are exercised.

Fix:

- Add Playwright tests that use mobile device presets for the key user flows.
- Verify the main flows on at least one Android Chrome and one iOS Safari device.

## Accessibility and visual

### Automate accessibility checks

Automated accessibility checks detect WCAG violations in components and pages before
they reach users, which complements manual review but does not replace it.

Check:

- Review the test suite for axe-core coverage at component and page level.
- Confirm that the accessibility checks run in CI and fail on violations.

Fix:

- Add `jest-axe` for component tests and `@axe-core/playwright` or `cypress-axe` for
  end-to-end tests.
- Test specific rules, such as colour contrast, individually where failures recur.

### Compare screenshots against approved baselines

Screenshot comparison detects visual regressions that functional tests cannot see, such
as a changed style that leaves the behaviour intact.

Check:

- Determine whether visual tests exist for key components and pages.
- Inspect the pixel difference threshold, which should tolerate sub-pixel rendering.

Fix:

- Add Playwright screenshot assertions or Storybook-based tests with Chromatic for
  component-level coverage.
- Set a pixel threshold that prevents flaky failures and run the comparison in CI.

## Production and performance

### Monitor errors in production

A monitoring service captures errors that occur only in production, so that they are
discovered and triaged before users report them.

Check:

- Confirm that an SDK such as Sentry, Datadog, or Bugsnag is initialised at the
  application entry point.
- Confirm that it captures unhandled exceptions, promise rejections, framework errors,
  and failed network requests.

Fix:

- Tag events with the environment, release version, and user context.
- Configure alerts for critical error thresholds and capture Core Web Vitals as
  real-user metrics.

### Enforce performance budgets in CI

Budgets for bundle size and page metrics fail the build when they are exceeded, which
prevents performance regressions from reaching production unnoticed.

Check:

- Search `package.json` and the CI configuration for size or Lighthouse thresholds.
- Confirm whether the budgets are enforced on every pull request.

Fix:

- Set bundle size limits with size-limit and Lighthouse CI assertions in the pipeline.
- Start with loose budgets, tighten them as optimisation proceeds, and monitor real-user
  metrics after deployment.
