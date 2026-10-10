> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Session Management

> Automatic session saving, resumption, and custom storage integration

Kiro CLI automatically saves all chat sessions on every conversation turn. Sessions are stored per-directory in the database, allowing you to resume from any previous session, export to files, or integrate with custom storage solutions.

## Auto-save

**Automatic**: Every conversation turn saved to database  
**Scope**: Per-directory (each project has own sessions)  
**Storage**: Local database (`~/.kiro/`)  
**Session ID**: UUID for each session

## Managing sessions

### From command line

```bash
# Resume most recent session
kiro-cli chat --resume

# Interactive picker
kiro-cli chat --resume-picker

# Resume a specific session by ID
kiro-cli chat --resume-id <SESSION_ID>

# List all sessions
kiro-cli chat --list-sessions

# Delete session
kiro-cli chat --delete-session <SESSION_ID>
```

### From chat

```bash
# Start a fresh conversation (saves current session automatically)
/chat new

# Start a fresh conversation with an initial prompt
/chat new how do I set up a React project

# Resume session (interactive)
/chat resume

# Print the current session ID
/session-id

# Save to file
/chat save <path>

# Load from file
/chat load <path>
```

**ℹ️ Resume hint on exit:** When you exit a session, Kiro CLI prints the session ID along with the command to resume it (`kiro-cli chat --resume-id <ID>`). Use `/session-id` mid-session to print the same ID on demand.

**ℹ️ File extension:** The `.json` extension is optional when loading sessions.

## Session dashboard (V3)

The V3 session dashboard combines local and cloud sessions from all workspaces in one view. Open it before starting a chat or from an active V3 session:

```bash
# Open the dashboard at launch
kiro-cli chat --sessions

# Open the dashboard from a V3 session
/sessions
```

Browse with the arrow keys and press `Enter` to resume the selected session. Local sessions from another workspace ask you to confirm the directory change before Kiro loads them. Cloud sessions resume from the cloud store.

Press `Tab` to move focus between the controls and session results. When a control has focus, press `Enter` to move into the results.

By default, sessions appear as a flat list sorted by **Last used**. Use the list controls to sort by **Last used**, **Session name**, or **Message count**. Kiro remembers the last sort order you choose.

### Search sessions

Start typing anywhere in the dashboard to search. The immediate filter matches session titles, workspace names and paths, session IDs, and tags; prefix a tag with `#` to narrow by tag. Queries of three or more characters also search indexed session content from local V2 and V3 transcripts.

By default, the content index covers your prompts and the agent's responses. Run `/settings` in a V3 session and choose **Session search** to switch between **Prompts only** and **Prompts and agent responses**; the choice is stored as `chat.sessionDashboard.indexResponses`. Tool output is not indexed in either mode. If your local index currently covers prompts only, `/sessions` asks once before rebuilding it to include responses. Classic sessions and cloud sessions still match listing metadata (titles, workspace, session ID, and tags), but their transcript content is not part of the local content index.

### Delete and clean up sessions

Highlight a session and press `Ctrl+D` to stage its deletion. Press `y` to confirm; any other key cancels. You cannot delete the active session or one that is open in another terminal.

To review empty local sessions for a workspace, highlight its `more` row and press `Ctrl+D`. The cleanup view excludes active, locked, recently active, marked, and derived sessions and shows the candidates before deletion. After reviewing the list, press `Ctrl+D` again, then press `y` to confirm.

You can also run cleanup directly:

```bash
# Show which empty local sessions would be deleted and which are exempt
/sessions clean

# Permanently delete the reported empty local sessions
/sessions clean --yes
```

Cleanup cannot be undone. Kiro scans again before deletion, so a session that is no longer empty is not removed.

### V3 launch behavior

The dashboard is a V3-only surface. `/sessions` is not available in V1 or V2. `kiro-cli chat --sessions` selects V3 when you have not chosen an agent harness. If you explicitly pass a non-V3 harness or save `chat.agentEngine` as `v1` or `v2`, Kiro reports the conflict instead of silently switching. Run `kiro-cli chat --v3 --sessions` for that launch, or change your saved setting. To run a single session on the V2 harness regardless of that saved value, pass `--v2`.

## Cloud sessions

Sessions started with `--cloud` run in a managed cloud sandbox and are stored in your account's cloud session store rather than the local per-directory database — see [Cloud sessions](https://kiro.dev/docs/cloud-sessions.md). They appear alongside local sessions in `--list-sessions` and the in-session `/sessions` picker, with columns showing each session's environment and status.

`--resume-id` detects a cloud session ID automatically, so no `--cloud` flag is needed to resume — and because the session lives in the cloud, you can resume it from any machine:

```bash
kiro-cli --resume-id <SESSION_ID>
```

`/chat save` and `/chat load` operate on the local session archive and aren't available in cloud sessions.

## Custom storage via scripts

Use custom scripts to save/load sessions from version control, cloud storage, or databases.

### Save via script

```bash
/chat save-via-script <script-path>
```

Script receives session JSON via stdin.

**Example: Save to Git Notes**
```bash
#!/bin/bash
COMMIT=$(git rev-parse HEAD)
TEMP=$(mktemp)
cat > "$TEMP"
git notes --ref=kiro/notes add -F "$TEMP" "$COMMIT" --force
rm "$TEMP"
echo "Saved to commit ${COMMIT:0:8}" >&2
```

### Load via script

```bash
/chat load-via-script <script-path>
```

Script outputs session JSON to stdout.

**Example: Load from Git Notes**
```bash
#!/bin/bash
COMMIT=$(git rev-parse HEAD)
git notes --ref=kiro/notes show "$COMMIT"
```

## Session storage

**Database**: Sessions auto-saved per-directory  
**Files**: Manual export via `/chat save`  
**Custom**: Script-based integration

**Session ID**: UUID format (e.g., `f2946a26-3735-4b08-8d05-c928010302d5`)

## Examples

### Resume last session

```bash
kiro-cli chat --resume
```

Continues most recent conversation.

### Pick session interactively

```bash
kiro-cli chat --resume-picker
```

Shows a list of sessions to choose from.

### Export to file

```
/chat save backup.json
```

Exports current session to file.

### Version control integration

```bash
# Save to git notes
/chat save-via-script ./scripts/save-to-git.sh

# Load from git notes
/chat load-via-script ./scripts/load-from-git.sh
```

## Troubleshooting

### Session is active in another process

**Symptom**: "Failed to start session: Session is active in another process (PID XXXXX)"  
**Cause**: You're trying to resume a session that's already open in another terminal window or tab.  
**Solution**: Sessions can only be active in one process at a time to prevent conversation corruption. You have two options:
1. Close the other terminal that has the session open, then resume.
2. Fork the session into a new one using `/chat save` in the original terminal, then `/chat load` in the new terminal. This creates a separate copy you can use independently.

**ℹ️ Why single-process?:** Each session maintains a sequential conversation history. Allowing two processes to write to the same session simultaneously would corrupt the message ordering and could cause data loss.

### No sessions to resume

**Symptom**: "No saved chat sessions"  
**Cause**: No sessions in current directory  
**Solution**: Sessions are per-directory. Navigate to correct directory.

### Script save fails

**Symptom**: Script exits with error  
**Cause**: Script returned non-zero exit code  
**Solution**: Test script manually. Ensure it exits 0 on success.

### Script load fails

**Symptom**: Can't load session  
**Cause**: Script didn't output valid JSON  
**Solution**: Test script outputs valid session JSON to stdout.

## Limitations

- Sessions can only be active in one process at a time (no multi-window sharing)
- Sessions stored per-directory
- Auto-save to database only (not files)
- Session IDs are UUIDs (not human-readable)
- Local sessions don't sync across machines (use scripts for custom storage); [cloud sessions](https://kiro.dev/docs/cloud-sessions.md) are stored in the cloud and resume from anywhere
- Content search covers local V2 and V3 sessions. Your prompts and the agent's responses are both indexed by default; choose **Session search** in `/settings` to index prompts only. Tool output, classic-session transcripts, and cloud-session transcripts are not indexed; use title, workspace, session ID, or tag matching for those sessions

## Technical details

**Storage**: SQLite database in `~/.kiro/`

**Scope**: Sessions keyed by directory path

**Auto-save**: After every conversation turn

**Script interface**: 
- Save: JSON via stdin, exit 0 on success
- Load: JSON via stdout, exit 0 on success

## Next steps

- Learn about [Chat Commands](https://kiro.dev/docs/reference/slash-commands.md#chat)
- See [Interactive Chat Mode](https://kiro.dev/docs/cli/chat.md)
- Review [Context Management](https://kiro.dev/docs/cli/chat/context.md)
- Use [Rewind](https://kiro.dev/docs/checkpoints.md) to fork a conversation at an earlier turn
