# Multi-Agent Setup Guide

Claude Code Memory supports teams of AI agents working on shared projects. This guide covers setup for 2+ agents.

## Prerequisites

- Each agent has completed the [basic installation](./INSTALL.md)
- All agents share the same `shared_path` (via Obsidian Sync, Dropbox, Git, etc.)

## Shared Folder Structure

```
shared_folder/
├── AgentA/
│   └── logs/
│       ├── TEMPLATE.md
│       └── 2026-02-24.md
├── AgentB/
│   └── logs/
│       ├── TEMPLATE.md
│       └── 2026-02-24.md
├── messages/
│   ├── agenta.md          ← messages TO AgentA
│   └── agentb.md          ← messages TO AgentB
├── handovers/
│   └── LATEST_HANDOVER.md
├── TASKS.md               ← shared task board
├── CHANGELOG.md           ← cross-agent change log
└── DECISIONS.md           ← decision audit trail
```

## Agent Configuration

Each agent's `agent_config.json` must list ALL agents:

```json
{
  "agent": "AgentA",
  "shared_path": "/path/to/shared/folder",
  "all_agents": ["AgentA", "AgentB"]
}
```

## How Agents See Each Other

### At Boot (SessionStart Hook)

The SessionStart hook automatically reads:
1. **This agent's daily log** — full parse with sections
2. **Other agents' daily logs** — first meaningful line from today/yesterday
3. **Messages inbox** — any messages addressed to this agent
4. **Shared task board** — tasks assigned to this agent

### During Work (Heartbeat Hook)

The Heartbeat hook watches for:
- Changes to shared docs (CHANGELOG, DECISIONS, etc.)
- New messages in the inbox

### Before Compaction (PreCompact Hook)

The PreCompact hook:
- Auto-logs this agent's work to its daily log
- Saves a handover document to `handovers/`

## Inter-Agent Communication

### Sending a Message

Write to the target agent's inbox file:

```
messages/{target_agent}.md
```

Format:
```markdown
## From {YourName} — YYYY-MM-DD HH:MM

{Your message here}
```

### Checking for Messages

The SessionStart hook checks your inbox automatically. You can also manually read `messages/{your_name}.md`.

### Clearing Messages

After reading and acting on messages, clear the file (or archive old messages below a `---` line).

## Task Board Protocol

The shared `TASKS.md` enables cross-agent task management:

- **Assignment**: Put agent name in the Owner column
- **Handoff**: Change owner, add note about what's done and what's left
- **Visibility**: All agents see the full board at boot
- **Logging**: Every task status change gets logged in the agent's daily log

## Sync Methods

| Method | Pros | Cons |
|--------|------|------|
| **Obsidian Sync** | Real-time, visual UI | Paid, macOS/Windows/mobile |
| **Dropbox/OneDrive** | Free tier, cross-platform | Conflict resolution |
| **Git repo** | Version history, merge | Manual push/pull needed |
| **NFS/SMB mount** | Instant, no sync | Same network required |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Agent doesn't see other agents | Check `all_agents` list in `agent_config.json` |
| Messages not appearing | Check `messages/` folder exists with correct filenames |
| Task board out of sync | Check shared folder sync status |
| Stale handover data | Handovers are per-agent; check `handovers/` timestamps |
