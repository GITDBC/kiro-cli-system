> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Analyze Requirements

> Deep analysis that catches logical inconsistencies, ambiguities, and gaps in your requirements before implementation

Before moving from requirements to design, you can ask Kiro to analyze your requirements for logical inconsistencies, ambiguities, and gaps. This deep analysis reasons across your full requirement set - not just each requirement in isolation - to find issues that are hard to catch in a read-through.

## What it catches

- **Logical inconsistencies** - two requirements that individually make sense but are collectively impossible
- **Ambiguities** - language like "large files" or "fast response times" that would produce divergent implementations
- **Conflicting constraints** - functional and non-functional requirements that can't all be satisfied at once
- **Unstated assumptions** - references to undefined concepts or behaviors
- **Missing edge cases** - failure modes, boundary conditions, and concurrent access scenarios not covered by the happy path

## How to invoke it

    IDE
    CLI
    Web

    After requirements are generated, you'll see **Analyze Requirements** as an option in two places:

    - In chat, alongside the other options for how to proceed
    - In the Continue dropdown in the editor, alongside **Proceed to Design**

    

    Run `/spec analyze_requirements` in a chat session. With no arguments, a searchable picker lists every spec that has a `requirements.md`:

    ```bash
    > /spec analyze_requirements
    ```

    Pass a feature name to start the analysis immediately:

    ```bash
    > /spec analyze_requirements my-feature
    ```

    The CLI switches to spec mode and analyzes that spec's `requirements.md`. If no spec has requirements yet, create one first with `/spec new <feature-name>`.

    Analyze Requirements is not currently available in Kiro Web. Use [Spec mode](https://kiro.dev/docs/specs.md) to create and refine requirements, a technical design, and implementation tasks before execution.

## What to expect

The analysis takes minutes, not seconds - cross-requirement reasoning is more computationally intensive than typical Kiro operations. As findings are ready, clarifying questions stream into chat.

Each question includes the requirements involved, a plain-language explanation of the issue, and suggested fixes you can select. You can also type a custom answer or dismiss a question if the ambiguity is intentional. As you resolve questions, Kiro updates `requirements.md` in the editor.

## When to use it

Analysis is especially valuable for complex features with many requirements, domain-sensitive projects (financial services, healthcare, compliance), and [Quick Spec](https://kiro.dev/docs/specs/quick-spec.md) sessions where requirements were auto-generated without manual review. For small or well-understood specs, you can skip the analysis and proceed directly to design.

You can re-run the analysis after editing requirements manually - Kiro will re-analyze affected requirements and their interactions.
