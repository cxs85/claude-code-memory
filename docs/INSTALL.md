# Claude Code Memory — Installation Guide
**Version:** 1.1 | **Created:** 2026-02-24

## Prerequisites

- Claude Code CLI installed
- Python 3.8+ available as `python3`
- A shared folder for agent state (any synced directory works — Obsidian, Dropbox, Git, etc.)

## Step 1: Create Your Shared Folder Structure

```bash
mkdir -p /path/to/shared/{YourName}/logs
mkdir -p /path/to/shared/messages
mkdir -p /path/to/shared/handovers
```

Copy the daily log template:
```bash
cp templates/daily_log.md /path/to/shared/{YourName}/logs/TEMPLATE.md
```

Create your messages file:
```bash
touch /path/to/shared/messages/{yourname}.md
```

## Step 2: Install Hooks

### 2a. Copy hook files to `~/.claude/hooks/`

```bash
# From the repo root:
cp hooks/session_start.py       ~/.claude/hooks/session_start.py
cp hooks/pre_compact_handover.py ~/.claude/hooks/pre_compact_handover.py
cp hooks/heartbeat.py           ~/.claude/hooks/heartbeat.py
```

### 2b. Create your agent config

Create `~/.claude/hooks/agent_config.json`:

```json
{
  "agent": "YourName",
  "shared_path": "/path/to/your/shared/folder",
  "all_agents": ["YourName"]
}
```

**Important:** Adjust `shared_path` for your OS:
- Windows: `"C:\\Users\\you\\shared-agent-folder"`
- macOS/Linux: `"/Users/you/shared-agent-folder"`

### 2c. Register hooks in settings.json

Add to `~/.claude/settings.json` under the `"hooks"` key:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/session_start.py",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/heartbeat.py"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/pre_compact_handover.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Note:** Use full absolute paths on Windows:
```
"python3 C:/Users/yourname/.claude/hooks/session_start.py"
```

## Step 3: Update Your CLAUDE.md

Copy the hardened boot sequence from `templates/CLAUDE_TEMPLATE.md` into your project's `CLAUDE.md`.

Key sections to include:
1. **MANDATORY BOOT SEQUENCE** — 7 steps, in CAPS
2. **LOGGING PROTOCOL** — append-only, source of truth = shared folder
3. **ASK FIRST, ACT SECOND** — default to confirming when unclear

Customize paths and agent name for your setup.

## Step 4: Verify

### Test SessionStart hook:
```bash
echo '{"source":"startup","cwd":"/tmp"}' | python3 ~/.claude/hooks/session_start.py
```

Expected: JSON with `hookSpecificOutput.additionalContext` containing your log status.

### Test PreCompact hook:
```bash
echo '{"session_id":"test","cwd":"/tmp"}' | python3 ~/.claude/hooks/pre_compact_handover.py
```

Expected: JSON with `[MEMORY V2 PRE-COMPACT]` message. Check your daily log for auto-entry.

### Test Heartbeat hook:
```bash
echo '{}' | python3 ~/.claude/hooks/heartbeat.py
```

Expected: Empty output (no changes detected) or JSON with `additionalContext`.

## Step 5: Start a Session

Start Claude Code in your project. You should see:
- SessionStart hook fires and injects context about today's log
- On every prompt, heartbeat checks for shared doc changes
- If context compacts, PreCompact hook auto-logs your work

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Hook not firing | Check `~/.claude/settings.json` — hooks must be under the correct event name |
| "No module" error | Ensure `python3` is in PATH |
| Wrong agent name | Check `~/.claude/hooks/agent_config.json` |
| Shared path not found | Verify the shared folder path in agent_config.json |
| Daily log not created | Create `{Agent}/logs/` directory in shared folder |
| Hooks are slow | Check `timeout` values in settings.json (10s for SessionStart, 30s for PreCompact) |

## Updating

When hooks are updated in the repo:
1. Pull latest and copy new versions to `~/.claude/hooks/`
2. Test with the echo commands above
3. No restart needed — hooks are loaded fresh each invocation
