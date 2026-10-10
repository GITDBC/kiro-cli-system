> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Thinking tool

> See AI reasoning process for complex problems

The thinking tool enables Kiro to show its reasoning process when working through complex problems, providing transparency into how conclusions are reached.

**ℹ️ Thinking tool vs. thinking display:** This page covers the experimental thinking **tool** (`chat.enableThinking`), which Kiro invokes to reason through a problem. It is different from the **thinking display** (`chat.showThinking`), the terminal UI feature that streams the model's own reasoning blocks inline and is enabled by default. To show or hide reasoning blocks, see [Thinking display](https://kiro.dev/docs/cli/chat/settings.md#thinking-display).

## Overview

When enabled, the thinking tool allows Kiro to break down complex reasoning into visible steps, helping you understand the decision-making process and learn from the AI's approach to problem-solving.

## Enabling thinking tool

```bash
kiro-cli settings chat.enableThinking true
```

Or use the experiment command:

```bash
/experiment
# Select "Thinking" from the list
```

## How it works

When Kiro encounters a complex problem that requires multi-step reasoning, it will:

1. **Show its thought process** as it works through the problem
2. **Break down the reasoning** into logical steps
3. **Explain intermediate conclusions** before reaching the final answer
4. **Make the decision-making transparent** so you can follow along

## When thinking appears

The thinking tool is automatically invoked by Kiro when:

- **Complex problem-solving** requires multiple logical steps
- **Analyzing trade-offs** between different approaches
- **Planning multi-step implementations** with dependencies
- **Debugging complex issues** that need systematic analysis
- **Making architectural decisions** with multiple considerations

## Example usage

### Without thinking tool

```
> What's the best way to implement caching for our API?

I recommend using Redis for caching your API responses...
```

### With thinking tool

```
> What's the best way to implement caching for our API?

🧠 Thinking...

Let me think through the caching requirements:

1. First, I need to consider the type of data being cached
   - API responses suggest read-heavy workload
   - Need to handle cache invalidation

2. Evaluating caching solutions:
   - In-memory (fast but limited by RAM)
   - Redis (distributed, persistent, feature-rich)
   - Memcached (simple, fast, but less features)

3. Considering your use case:
   - API responses benefit from distributed cache
   - Need TTL support for automatic expiration
   - May need cache invalidation on updates

4. Redis appears best because:
   - Supports complex data structures
   - Built-in TTL and eviction policies
   - Can be distributed across nodes
   - Persistent if needed

Based on this analysis, I recommend using Redis for caching your API responses...
```

## Benefits

### For learning

- **Understand reasoning patterns**: See how complex problems are broken down
- **Learn problem-solving approaches**: Observe systematic analysis
- **Identify gaps in logic**: Spot where reasoning might be flawed

### For debugging

- **Trace decision paths**: Understand why certain recommendations were made
- **Verify assumptions**: Check if the AI's assumptions match your context
- **Catch errors early**: Spot logical errors before implementation

### For complex tasks

- **Follow multi-step plans**: See how complex tasks are decomposed
- **Understand dependencies**: Identify relationships between steps
- **Validate approach**: Confirm the reasoning aligns with your goals

## Use cases

### Architectural decisions

```
> Should we use microservices or a monolith for our new project?

🧠 Thinking...

Let me analyze this architectural decision:

1. Project characteristics to consider:
   - Team size and structure
   - Expected scale and growth
   - Deployment requirements
   - Development velocity needs

2. Microservices advantages:
   - Independent scaling
   - Technology flexibility
   - Isolated failures
   - But: increased complexity, operational overhead

3. Monolith advantages:
   - Simpler deployment
   - Easier debugging
   - Lower operational cost
   - But: scaling limitations, tight coupling

4. Decision factors:
   - Small team → Monolith likely better
   - Unclear requirements → Start with monolith
   - Need rapid iteration → Monolith faster initially
   - Can refactor to microservices later if needed

Based on this analysis...
```

### Algorithm selection

```
> What sorting algorithm should I use for this data?

🧠 Thinking...

Let me think through the sorting requirements:

1. Data characteristics:
   - Size of dataset
   - Is data partially sorted?
   - Memory constraints
   - Stability requirements

2. Algorithm options:
   - Quick Sort: O(n log n) average, O(n²) worst
   - Merge Sort: O(n log n) guaranteed, stable
   - Heap Sort: O(n log n), in-place
   - Tim Sort: Optimized for real-world data

3. Trade-offs:
   - If data is partially sorted → Tim Sort excels
   - If memory is limited → Heap Sort (in-place)
   - If stability matters → Merge Sort or Tim Sort
   - For general case → Quick Sort often fastest

4. Recommendation depends on...
```

### Debugging complex issues

```
> My application is slow but I don't know why

🧠 Thinking...

Let me systematically analyze potential performance issues:

1. Common performance bottlenecks:
   - Database queries (N+1 problem, missing indexes)
   - Network latency (API calls, external services)
   - Memory issues (leaks, excessive allocation)
   - CPU-bound operations (complex calculations)

2. Diagnostic approach:
   - First, profile to identify hotspots
   - Check database query patterns
   - Monitor network requests
   - Analyze memory usage patterns

3. Most likely culprits based on typical patterns:
   - Database queries often account for 60-80% of slowness
   - Should start there before optimizing code

4. Recommended investigation order...
```

## Configuration

### Enable/disable

```bash
# Enable
kiro-cli settings chat.enableThinking true

# Disable
kiro-cli settings chat.enableThinking false

# Check status
kiro-cli settings chat.enableThinking
```

## Limitations

### Performance impact

- **Slower responses**: Thinking adds time to generate responses
- **More tokens used**: Thinking process consumes additional tokens
- **Longer output**: Responses are more verbose

### When not to use

- **Simple questions**: Thinking overhead not needed for straightforward queries
- **Quick iterations**: May slow down rapid back-and-forth
- **Well-defined tasks**: When you just need the answer, not the reasoning

## Best practices

### When to enable

- **Learning new concepts**: Understand the reasoning behind recommendations
- **Complex decisions**: Need to validate the decision-making process
- **Debugging**: Want to see systematic problem analysis
- **Code reviews**: Understand why certain approaches are suggested

### When to disable

- **Simple tasks**: Straightforward questions don't need reasoning
- **Speed priority**: Need quick responses without explanation
- **Familiar territory**: Already understand the reasoning patterns

### Workflow integration

1. **Enable for complex tasks**: Turn on when starting difficult problems
2. **Learn from reasoning**: Observe how problems are broken down
3. **Disable for execution**: Turn off when implementing known solutions
4. **Re-enable for review**: Turn back on when validating approaches

## Troubleshooting

### Thinking not appearing

1. **Verify it's enabled**:
   ```bash
   kiro-cli settings chat.enableThinking
   ```

2. **Try a complex question**: Simple questions may not trigger thinking

3. **Restart chat session**: Changes may require new session

### Too much thinking

If thinking output is overwhelming:

1. **Disable for simpler tasks**:
   ```bash
   kiro-cli settings chat.enableThinking false
   ```

2. **Ask for concise answers**: Request brief responses explicitly

3. **Use for specific questions**: Enable only when needed

## Related features

- [Experimental Features](https://kiro.dev/docs/cli/experimental.md)
- [Tangent Mode](https://kiro.dev/docs/cli/experimental/tangent-mode.md) - Explore reasoning without affecting main conversation
- [TODO Lists](https://kiro.dev/docs/cli/experimental/todo-lists.md) - Break down complex tasks

## Next steps

- [Enable other experimental features](https://kiro.dev/docs/cli/experimental.md)
- [Configure settings](https://kiro.dev/docs/reference/settings.md)
- [Learn about custom agents](https://kiro.dev/docs/custom-agents.md)
