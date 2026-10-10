> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Reasoning effort

> Control how much reasoning the model applies to balance speed, depth, and cost

Reasoning effort controls how much thinking the model applies to your prompts. Lower effort levels produce faster, shorter responses and use fewer credits. Higher levels spend more tokens on deeper analysis, multi-step reasoning, and thorough code generation.

| Capability | IDE | CLI | Web | Mobile |
|------------|:---:|:---:|:---:|:------:|
| Reasoning effort selection | ✓ | ✓ | — | — |

**Available levels:**

| Level | Behavior |
|-------|----------|
| `low` | Fast, concise responses. Good for simple questions and quick lookups. |
| `medium` | Balanced reasoning. Suitable for most development tasks. |
| `high` | Thorough analysis. Better for complex refactoring and architecture decisions. |
| `xhigh` | Extended reasoning. Useful for multi-file changes and nuanced problems. |
| `max` | Maximum depth. Best for difficult debugging, security analysis, and intricate logic. |

Not all models support every level. The picker only shows levels available for your current model - see [supported models](#supported-models) below.

## Setting effort level

    IDE
    CLI

Click the model name in the chat input bar to open the model selector, then choose an effort level from the **Effort** panel on the right side.

Your effort selection appears next to the model name (e.g., "Claude Opus 4.6 · max") and applies to all subsequent messages in the conversation.

Use the `/effort` command to change the reasoning level mid-session:

```bash
# Open interactive picker
/effort

# Set directly
/effort high
```

Or set the initial effort level when you start a session with the `--effort` flag:

```bash
kiro-cli chat --effort high
```

The flag accepts the same levels as `/effort` and applies from your first prompt, so quick lookups stay fast and complex work gets deeper reasoning from the start.

## Supported models

Each model defines the values it accepts for the reasoning-related fields in its configuration schema. The `output_config.effort` column lists the effort levels available for that model; `thinking.type` and `thinking.display` control reasoning behavior and visibility; `max_tokens` sets the output length limit.

**Claude models** use `output_config.effort` with `thinking.type` and `thinking.display` controls:

| Model | `thinking.type` | `thinking.display` | `output_config.effort` | `max_tokens` |
|-------|-----------------|--------------------|------------------------|--------------|
| Claude Opus 5 | `adaptive`, `disabled` | `summarized`, `omitted` | `low`, `medium`, `high`, `xhigh`, `max` | 1024–128000 |
| Claude Opus 4.8 | `adaptive`, `disabled` | `summarized`, `omitted` | `low`, `medium`, `high`, `xhigh`, `max` | 1024–128000 |
| Claude Opus 4.7 | `adaptive`, `disabled` | `summarized`, `omitted` | `low`, `medium`, `high`, `xhigh`, `max` | 1024–64000 |
| Claude Opus 4.6 | `adaptive`, `disabled` | `summarized`, `omitted` | `low`, `medium`, `high`, `max` | 1024–64000 |
| Claude Sonnet 5 | `adaptive`, `disabled` | `summarized`, `omitted` | `low`, `medium`, `high`, `xhigh`, `max` | 1024–128000 |
| Claude Sonnet 4.6 | `adaptive`, `disabled` | `summarized`, `omitted` | `low`, `medium`, `high`, `max` | 1024–64000 |

**GPT-5.6 models** use `reasoning.effort`:

| Model | `reasoning.effort` |
|-------|-------------------|
| GPT-5.6 Terra | `none`, `low`, `medium`, `high`, `xhigh`, `max` |
| GPT-5.6 Sol | `none`, `low`, `medium`, `high`, `xhigh`, `max` |
| GPT-5.6 Luna | `none`, `low`, `medium`, `high`, `xhigh`, `max` |

GPT-5.6 models default to `effort: "high"`.

## Persisting your effort level (CLI)

Your effort choice persists automatically. Set a level with `/effort` or `--effort` and Kiro remembers it for future sessions - there's no extra step to make it the default. Preferences are stored in `~/.kiro/settings/cli.json`. See [In-session settings](https://kiro.dev/docs/cli/chat/settings.md#persistence) for more on how preferences persist.

## Persistent defaults (CLI)

To set default model parameters per model - so you don't have to run `/effort` at the start of every session - add `chat.modelDefaults` to your settings file:

**Claude models** (use `output_config.effort`):

```json
{
  "chat.modelDefaults": {
    "claude-sonnet-4.6": {
      "output_config": {
        "effort": "high"
      }
    },
    "claude-opus-4.7": {
      "output_config": {
        "effort": "max"
      }
    }
  }
}
```

**GPT-5.6 models** (use `reasoning.effort`):

```json
{
  "chat.modelDefaults": {
    "gpt-5.6-sol": {
      "reasoning": {
        "effort": "max"
      }
    },
    "gpt-5.6-terra": {
      "reasoning": {
        "effort": "low"
      }
    }
  }
}
```

### Configuring thinking behavior

Control whether the model uses extended thinking and how it displays reasoning:

```json
{
  "chat.modelDefaults": {
    "claude-opus-4.8": {
      "thinking": {
        "type": "adaptive",
        "display": "summarized"
      }
    },
    "claude-sonnet-4.6": {
      "thinking": {
        "type": "disabled"
      }
    }
  }
}
```

- `thinking.type` - `adaptive` enables extended thinking when the model determines it's needed; `disabled` turns it off entirely.
- `thinking.display` - `summarized` shows a condensed version of reasoning; `omitted` hides it from output. Only applies when `type` is `adaptive`.

### Configuring max output tokens

Set the maximum number of tokens the model can generate per response:

```json
{
  "chat.modelDefaults": {
    "claude-opus-4.8": {
      "max_tokens": 128000
    },
    "claude-sonnet-4.6": {
      "max_tokens": 32000
    }
  }
}
```

**`max_tokens` limits per model:**

| Model | Minimum | Maximum |
|-------|---------|---------|
| Claude Opus 4.8 | 1024 | 128000 |
| Claude Opus 4.7 | 1024 | 64000 |
| Claude Opus 4.6 | 1024 | 64000 |
| Claude Sonnet 5 | 1024 | 128000 |
| Claude Sonnet 4.6 | 1024 | 64000 |
| GPT-5.6 Terra | 1024 | 128000 |
| GPT-5.6 Sol | 1024 | 128000 |
| GPT-5.6 Luna | 1024 | 128000 |

### Combining all options

You can combine `output_config`, `thinking`, and `max_tokens` in a single model entry:

**Claude example:**

```json
{
  "chat.modelDefaults": {
    "claude-opus-4.8": {
      "output_config": {
        "effort": "max"
      },
      "thinking": {
        "type": "adaptive",
        "display": "summarized"
      },
      "max_tokens": 128000
    }
  }
}
```

**GPT-5.6 example:**

```json
{
  "chat.modelDefaults": {
    "gpt-5.6-sol": {
      "reasoning": {
        "effort": "max"
      },
      "max_tokens": 128000
    }
  }
}
```

To open your settings file in your editor:

```bash
kiro-cli settings open
```

Or place a `.kiro/settings/cli.json` in your project root to set workspace-level defaults that apply to everyone working in that repository.

## Precedence

When determining the effort level for a session, Kiro applies this priority order:

1. **Session override** - value set via the effort picker, `/effort`, or `--effort` during the current session
2. **Workspace defaults** - `chat.modelDefaults` in `.kiro/settings/cli.json`
3. **User defaults** - `chat.modelDefaults` in `~/.kiro/settings/cli.json`
4. **Built-in defaults** - the model's standard effort level

## When to adjust effort

- **Bump up** when the agent is giving shallow answers, missing edge cases, or producing incomplete implementations
- **Bump down** when you need quick answers and don't want to wait for extended reasoning
- **Use `max`** for security reviews, complex debugging sessions, or when you need the agent to consider many interacting constraints

## Related

- [Models](https://kiro.dev/docs/models.md) - available models and their capabilities
- [Slash commands reference](https://kiro.dev/docs/reference/slash-commands.md#effort) - quick command reference
- [Settings](https://kiro.dev/docs/reference/settings.md) - all configurable settings
