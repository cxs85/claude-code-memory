# Claude Code Memory

A memory, logging, and workflow system for AI coding agents. Built for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), extensible to other agent frameworks.

## The Problem

AI coding agents forget. Context windows compact, MCP memory is unreliable, and there's no audit trail of what happened. When an agent forgets mid-session, you lose hours of work.

**Three root causes:**
1. **Compaction loss (~60%)** — context summarization is lossy by design
2. **Never-saved context (~25%)** — agents don't log unless forced
3. **Poor retrieval (~15%)** — even when state is saved, boot-time loading misses it

## The Solution

Claude Code Memory is a 4-layer system that makes agent memory durable, observable, and recoverable:

```
Layer 1: HOOKS        — Automatic lifecycle hooks (zero effort)
Layer 2: ENFORCEMENT  — CLAUDE.md hardened rules (non-negotiable)
Layer 3: SHARED STATE — Append-only logs in Obsidian/filesystem
Layer 4: CONSOLIDATION — Weekly "sleep" cycle (deliberate, not reactive)
```

### How It Works

- **SessionStart hook** fires on every boot — injects today's log, inbox, team activity, and handover context automatically
- **PreCompact hook** fires before context compaction — auto-extracts work from the transcript and appends to daily log (the safety net)
- **Heartbeat hook** fires on every prompt — watches shared docs and inboxes for changes
- **CLAUDE.md enforcement** — hardened boot sequence, mandatory logging, "ask before doing" rule
- **Weekly consolidation** — distills 7 days of logs into updated long-term memory (not reactive to context pressure)

## Features

- **Append-only daily logs** — source of truth that survives any number of compactions
- **Auto-logging before compaction** — even if the agent forgets, the hook catches it
- **Multi-agent coordination** — shared task board, inter-agent messages, cross-agent visibility
- **Config-driven hooks** — same code works for any agent, just change `agent_config.json`
- **Human-readable** — all state is markdown files. Open them in Obsidian, VS Code, or any editor.
- **No external dependencies** — pure Python hooks, no API keys, no databases, no servers

## Quick Start

### 1. Clone

```bash
git clone https://github.com/your-org/claude-code-memory.git
cd claude-code-memory
```

### 2. Copy hooks to Claude Code

```bash
cp hooks/session_start.py      ~/.claude/hooks/
cp hooks/pre_compact_handover.py ~/.claude/hooks/
cp hooks/heartbeat.py          ~/.claude/hooks/
```

### 3. Create your agent config

Create `~/.claude/hooks/agent_config.json`:

```json
{
  "agent": "YourName",
  "shared_path": "/path/to/your/shared/folder",
  "all_agents": ["YourName"]
}
```

### 4. Register hooks

Add to `~/.claude/settings.json`:

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
    ]
  }
}
```

### 5. Create your shared folder structure

```bash
mkdir -p /path/to/shared/{YourName}/logs
mkdir -p /path/to/shared/messages
mkdir -p /path/to/shared/handovers
cp templates/daily_log.md /path/to/shared/{YourName}/logs/TEMPLATE.md
```

### 6. Add enforcement to your CLAUDE.md

Copy the relevant sections from `templates/CLAUDE_TEMPLATE.md` into your project's `CLAUDE.md`.

That's it. Start Claude Code and the hooks will fire automatically.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   CLAUDE CODE MEMORY SYSTEM                    │
│                                                                │
│  LAYER 1: HOOKS (automatic)                                   │
│  SessionStart → inject daily log + messages + team activity    │
│  PreCompact   → auto-log work + save handover                 │
│  Heartbeat    → watch shared docs for changes                 │
│                                                                │
│  LAYER 2: ENFORCEMENT (CLAUDE.md)                             │
│  1. MANDATORY BOOT SEQUENCE                                    │
│  2. LOGGING IS NOT OPTIONAL                                    │
│  3. ASK FIRST, ACT SECOND                                     │
│                                                                │
│  LAYER 3: SHARED STATE (filesystem)                           │
│  {Agent}/logs/YYYY-MM-DD.md  ← daily logs (append-only)      │
│  messages/{agent}.md         ← inter-agent messages           │
│  handovers/                  ← pre-compact backups            │
│  TASKS.md                    ← cross-agent task board         │
│                                                                │
│  LAYER 4: CONSOLIDATION (weekly)                              │
│  Distill 7 days of logs → update MEMORY.md                    │
│  Cyclical & deliberate, NOT reactive to context pressure      │
└──────────────────────────────────────────────────────────────┘
```

## Repo Structure

```
claude-code-memory/
├── README.md              ← you are here
├── LICENSE
├── hooks/
│   ├── session_start.py       ← SessionStart lifecycle hook
│   ├── pre_compact_handover.py ← PreCompact lifecycle hook
│   ├── heartbeat.py           ← UserPromptSubmit lifecycle hook
│   └── agent_config.template.json
├── skills/
│   ├── session-start.md       ← manual deep refresh skill
│   ├── session-end.md         ← session wrap-up skill
│   ├── pre-compact.md         ← manual handover skill
│   └── weekly-consolidate.md  ← memory "sleep" cycle skill
├── templates/
│   ├── CLAUDE_TEMPLATE.md     ← hardened CLAUDE.md with boot sequence
│   ├── daily_log.md           ← daily log format
│   └── TASKS.md               ← shared task board format
├── docs/
│   ├── SPEC.md                ← full system specification
│   ├── INSTALL.md             ← detailed installation guide
│   └── MULTI_AGENT.md         ← multi-agent setup guide
└── examples/
    └── agent_config.json      ← example configuration
```

## Multi-Agent Setup

Claude Code Memory supports teams of agents with:

- **Shared task board** (`TASKS.md`) — assign, track, and hand off work
- **Inter-agent messages** (`messages/{agent}.md`) — async communication
- **Cross-agent visibility** — each agent sees others' recent activity at boot
- **Handover continuity** — pre-compact snapshots enable seamless session resume

See `docs/MULTI_AGENT.md` for full setup instructions.

## How It Compares

| | Context window only | MCP Memory | MEMORY.md | **Claude Code Memory** |
|---|---|---|---|---|
| Survives compaction | No | Partial | Yes | **Yes** |
| Auto-captures work | No | No | No | **Yes (hooks)** |
| Human-readable audit trail | No | No | Partial | **Yes** |
| Multi-agent coordination | No | No | No | **Yes** |
| Zero config after install | Yes | Yes | Yes | **Yes** |
| Weekly consolidation | No | No | Manual | **Structured** |

## Requirements

- Claude Code CLI
- Python 3.8+
- A shared folder (Obsidian vault, Dropbox, or any synced directory)

## License

MIT

## Contributing

PRs welcome. The system is designed to be modular — hooks, skills, and templates can be improved independently.
