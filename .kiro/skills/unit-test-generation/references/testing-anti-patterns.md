# Testing Anti-Patterns

Anti-patterns to actively check for after enumerating scenarios and before finalizing a
pytest suite. Adapted from mattpocock/skills (MIT); rewritten for pytest idioms — the
source material's TypeScript/Vitest mocking guidance is not ported (see Rejected below).

## Tautological tests

A test is tautological when its expected value is derived by re-running the same logic
the code under test uses, so the test passes by construction regardless of whether the
logic is correct.

```python
# BAD: expected is recomputed the same way the function computes it
def test_calculate_total_sums_line_items():
    items = [{"price": 10}, {"price": 5}]
    expected = sum(i["price"] for i in items)
    assert calculate_total(items) == expected


# GOOD: expected is an independent, known literal
def test_calculate_total_sums_line_items():
    assert calculate_total([{"price": 10}, {"price": 5}]) == 15
```

The check: could the test still pass if the implementation had a bug that the expected
value's derivation shares? If the expected value is computed with the same formula,
loop, or library call as the code under test, replace it with a literal or an
independently-sourced fixture value.

## Implementation-detail tests

Tests coupled to internal structure rather than observable behavior break on every
refactor that preserves behavior, which defeats the purpose of a regression suite.

Red flags:

- Mocking internal collaborators (functions/classes owned by the same package) rather
  than system boundaries (I/O, network, time, randomness, third-party APIs).
- Asserting on `mock.call_count` or `mock.call_args` as the primary assertion, when the
  interaction itself is not the behavior under test.
- Reaching around the public interface to verify state directly (e.g. querying the
  database after calling a function that already returns the created record).

```python
# BAD: bypasses the interface to verify
def test_create_user_saves_to_database(db_session):
    create_user(db_session, name="Alice")
    row = db_session.execute(text("SELECT * FROM users WHERE name = :n"), {"n": "Alice"})
    assert row.fetchone() is not None


# GOOD: verifies through the interface
def test_create_user_makes_user_retrievable(db_session):
    user = create_user(db_session, name="Alice")
    retrieved = get_user(db_session, user.id)
    assert retrieved.name == "Alice"
```

Tests that describe WHAT the unit does (behavior) survive internal refactors; tests that
describe HOW it does it (implementation) do not. Prefer the former.

## Mocking discipline (pytest)

Mock at system boundaries only: I/O, network calls, `time.time`/`datetime.now`, random
sources, and third-party clients. Use `unittest.mock.patch` or `pytest-mock`'s `mocker`
fixture scoped to the boundary call, not to internal collaborators the test could
exercise for real at negligible cost.

```python
# GOOD: mocks the external payment client at the boundary
def test_checkout_confirms_with_valid_payment(mocker):
    mock_client = mocker.patch("app.payments.stripe_client")
    mock_client.charge.return_value = {"status": "succeeded"}
    result = checkout(cart=sample_cart(), payment_client=mock_client)
    assert result.status == "confirmed"
```

Dependency injection (passing the client in rather than constructing it inside the
function under test) is what makes this boundary mockable without monkeypatching
module-level globals — prefer the injected-parameter form already used across the
codebase's `senior-developer` patterns.

## Rejected from the source material

The source's `mocking.md` also recommends an SDK-style interface pattern — replacing a
single generic fetch function with one small named function per external operation, so
each is independently mockable. That guidance is written for TypeScript/Vitest object
mocks and does not transfer: pytest's `mocker.patch` already targets an arbitrary
attribute path without needing the production code restructured into a per-endpoint SDK
object. Not adopted.
