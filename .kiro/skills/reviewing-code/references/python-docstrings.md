# Python Docstring Guide

## Format

- Google Docstring format exclusively
- Content starts on the line after opening `"""`
- Maximum 73 characters per line; wrap as needed
- Always leave a blank line after the closing `"""`
- Always include a `Returns` section, even for `None` returns (end with ".")
- Generators use `Yields:` instead of `Returns:`
- Tab-indent multi-line return descriptions for the same result

## Internal spacing

Separate each section with a blank line:

```python
def example(name: str, count: int = 1) -> str:
    """
    Short description of the function.

    Args:
        name: Descriptive text.
        count: Descriptive text.

    Returns:
        Descriptive text.

    Raises:
        ValueError: Descriptive text.
    """

    return name * count
```

## When to skip docstrings

- Inline/nested functions of 1-2 lines (e.g. `re.sub` callbacks)
- Single-line `@property` methods
- `__init__.py` files

## Descriptions

- Write self-explanatory descriptions conveying full functionality without reading the
  implementation
- Assume basic Python knowledge — skip fundamental concept explanations
- Be clear and concise while maintaining completeness

## Type information

- Place types exclusively in function signatures, never in docstring text
- If type hints are missing, add them by inferring from usage context
- If default values are evident from code, add them to the signature

## Dataclasses and TypedDicts

- Use `Attributes:` section in the class docstring to document fields
- Do not repeat type information already present in the field annotations

```python
@dataclass
class FileDiff:
    """
    Diff summary for a single file.

    Attributes:
        path: File path relative to repo root.
        status: Git status letter (A/M/D/R).
        insertions: Lines added.
        deletions: Lines removed.
    """

    path: str
    status: str
    insertions: int = 0
    deletions: int = 0
```

## Performance and complexity

Include performance considerations or complexity notes only when:

- Complexity is non-trivial
- Significant performance implications exist
- Implementation details affect usage

## Examples

Include examples selectively:

- Skip for classes, class methods, and simple/self-evident functions
- Include when usage pattern is non-obvious or would significantly aid understanding
- Keep simple, focused on common use cases, properly formatted in Google style

## Additional sections

Add Notes, Warnings, or See Also sections only when they meaningfully improve clarity.

## Consistency

Identical parameters across functions use identical word-for-word descriptions. Maintain
consistent terminology throughout the codebase.
