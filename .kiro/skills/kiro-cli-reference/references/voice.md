> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Voice mode

> Speech-to-text for Kiro CLI chat using local Whisper transcription, with push-to-talk and a remote server option for cloud desktops

Voice mode lets you speak your prompts instead of typing them. Your speech is transcribed locally with [OpenAI Whisper](https://github.com/openai/whisper) (via [whisper.cpp](https://github.com/ggml-org/whisper.cpp)) and, by default, submitted to the assistant automatically. You can switch to review-before-send if you prefer. It runs entirely on your machine by default, so no audio leaves your computer and no cloud API key is required. The speech model downloads once, on first use.

**ℹ️ Info:** Voice mode is a speech-to-text input feature for the Kiro CLI. It requires a microphone (or a [remote voice server](#remote-voice-server-for-cloud-desktops) for cloud desktops) and a build of `kiro-cli` with the `voice` feature compiled in. This is separate from voice in KiroCrew, which offers both speech-to-text and text-to-speech in the dashboard.

## How it works

1. Start a recording with `/voice` or by holding `Space`.
2. Speak your prompt while the recording indicator shows your audio level in real time.
3. Stop by pressing `Enter`, or let it auto-stop after a period of silence.
4. The transcription is submitted to the assistant automatically by default, or placed in the prompt for review when you set `voice.autoSubmit false`.

```
Recording, press ENTER when done... 3.5sec ░░░█████████
```

Partial text streams into the input as you speak, so you can watch the transcription form before you stop.

## Starting voice input

### Slash command

```
/voice
```

Starts a single recording session in the current chat.

### Push-to-talk with Space

Hold the `Space` key at the prompt for 1.5 seconds to start recording. Release `Space` to stop and transcribe. Useful for a quick voice input without pressing `Enter`.

## First run: downloading the speech model

The Whisper model is downloaded on first use, and the download is never silent.

  
### Run /voice

The command detects that no model is present.

  
### Confirm the download

A panel shows the model name, its size (about 148 MB for the default `base` model), and its license (MIT). Press `y` to download or `n` to cancel.

  
### Voice is ready

The model is cached under `~/.cache/kiro/models/`. Subsequent recordings start instantly.

If you trigger voice with `Space` (push-to-talk) before the model is downloaded, Kiro prompts you to run `/voice` for the interactive setup.

**ℹ️ Info:** In headless or piped invocations there is no interactive panel. Pass `--confirm-download` on the CLI command directly to approve the one-time download.

## Transcription backends

### Local Whisper (default)

Local transcription uses whisper-rs (Rust bindings for whisper.cpp) and needs no internet after the initial model download. Two model sizes are available:

| Model | Download size | Speed | Accuracy |
|---|---|---|---|
| `base` (default) | ~148 MB | Faster | Good |
| `small` | ~466 MB | Slower | Better |

Set the model size:

```bash
kiro-cli settings set voice.modelSize small
```

### Remote voice server (for cloud desktops)

When you work on a cloud desktop with no microphone, voice mode can stream audio to a small server running on your local machine. Voice mode falls back to the remote server automatically when no local microphone is detected.

Manual setup:

```bash
# On your local machine (the one with a microphone):
kiro-cli voice-serve

# Open a reverse tunnel when you SSH to the cloud desktop:
ssh -R 19876:localhost:19876 cloud-desktop

# On the cloud desktop, point voice mode at the tunnel before starting Kiro:
export KIRO_VOICE_SERVER_URL=http://127.0.0.1:19876
kiro-cli
```

You can also force the remote backend for a single session with `/voice --model remote` (the default is `--model local-whisper`).

#### Cloud setup helper

From your local machine, `voice-cloud-setup` starts the local voice server and opens the reverse tunnel:

```bash
kiro-cli voice-cloud-setup <cloud-hostname>
```

Then, on the cloud desktop, set the server URL in the same shell before starting Kiro and activating voice mode:

```bash
export KIRO_VOICE_SERVER_URL=http://127.0.0.1:19876
kiro-cli
```

The helper verifies SSH connectivity, starts `voice-serve` locally, and opens the reverse tunnel. It does not currently configure `voice.serverUrl` on the cloud desktop.

| Option | Description |
|---|---|
| `--port <port>` | Port for the voice server (default: `19876`) |
| `--remote-bin <path>` | Path to `kiro-cli` on the cloud desktop |
| `-i <identity>` | SSH identity file |

**ℹ️ Info:** Set `KIRO_VOICE_SERVER_URL` on the cloud desktop before starting Kiro. When it is set, the local voice binary is skipped and audio streams to the server. Add the export to your shell profile if you want it to persist across sessions.

## Accuracy: VAD and context

Voice mode uses Silero Voice Activity Detection to tell speech from background noise. It detects when you start and stop talking, filters out keyboard clicks and fan noise, and drives the silence auto-stop, which prevents false transcriptions from ambient sound.

Recent conversation context is also passed to Whisper's initial prompt, which improves accuracy for code identifiers, function names, and project-specific vocabulary discussed earlier in the session.

## Configuration

Voice behavior is controlled through `kiro-cli settings`. All settings are optional.

| Setting | Type | Default | Description |
|---|---|---|---|
| `voice.modelSize` | string | `base` | Whisper model size: `base` or `small` |
| `voice.language` | string | `en` | Transcription language (`auto` to detect) |
| `voice.silenceTimeout` | integer | `5` | Seconds of silence before recording auto-stops |
| `voice.maxSessionTime` | integer | `300` | Maximum recording length in seconds |
| `voice.autoSubmit` | boolean | `true` | Submit the transcription automatically instead of placing it in the input for review |
| `voice.serverUrl` | string | none | Remote voice server URL for cloud desktops |

Examples:

```bash
# Favor speed
kiro-cli settings set voice.modelSize base
kiro-cli settings set voice.silenceTimeout 3

# Favor accuracy
kiro-cli settings set voice.modelSize small
kiro-cli settings set voice.silenceTimeout 8

# Review each transcription before it is sent
kiro-cli settings set voice.autoSubmit false

# Transcribe Spanish
kiro-cli settings set voice.language es

# View your voice settings
kiro-cli settings list | grep voice
```

## Privacy and security

- With local Whisper, audio is captured, transcribed, and discarded on your machine. Nothing is sent to any server.
- The remote voice server option streams audio only to the server URL you configure (typically your own laptop over an SSH tunnel).
- Kiro verifies the Whisper model file against a pinned SHA-256 digest after download and before every use. A corrupt, tampered, or attacker-planted model is rejected. If a cached model fails the check, Kiro deletes it and re-downloads from the official CDN automatically. No action is needed.
- On Unix systems, the model directory is restricted to owner-only access (mode `0700`) as defense in depth.

## Examples

### Basic voice input

```
> /voice
Recording, press ENTER when done... 2.1sec ░░░████████

"Fix the bug in the authentication module"

> Analyzing the authentication module...
```

### Push-to-talk continuing a typed prompt

1. Type the start of your prompt: `How do I`
2. Hold `Space` and speak: "implement pagination in the users API"
3. Release `Space` to stop and transcribe
4. The submitted prompt reads: "How do I implement pagination in the users API"

## Limitations

- Requires a physical microphone, or a remote voice server for cloud desktops.
- Local transcription is CPU-bound. The `small` model is more accurate but slower, and there is no GPU acceleration yet.
- Optimized for English by default; multilingual support is limited.
- No wake word activation.

## Troubleshooting

| Problem | Fix |
|---|---|
| "No microphone detected" | Grant microphone permission, or set up a [remote voice server](#remote-voice-server-for-cloud-desktops) on a cloud desktop |
| Recording stops too early | Increase `voice.silenceTimeout` (for example, to `10`) |
| Poor transcription accuracy | Switch to the `small` model, speak clearly, and reduce background noise |
| First use is slow | The model downloads once on first use, then recordings start instantly |
| "Model integrity check failed" | Kiro deletes the invalid file and re-downloads automatically. If it persists, check your network or proxy |
| "Voice binary not found" | Reinstall `kiro-cli`, or confirm `KIRO_CHAT_CLI_BIN` points to a build with the `voice` feature compiled in |
| High CPU during transcription | Use the `base` model and let a transcription finish before starting new work |

## Related

- [Chat](https://kiro.dev/docs/cli/chat.md): the interactive session that voice input feeds into
- [Terminal UI](https://kiro.dev/docs/cli/terminal-ui.md): the interface that renders the live recording indicator
- [In-session settings](https://kiro.dev/docs/cli/chat/settings.md): adjusting settings during a session
