# Claude Code Memory — Agent Memory & Workflow System
**Version:** 1.1 | **Created:** 2026-02-24
**Status:** Production
**Repo:** `claude-code-memory` (open source)

## What This Is

Claude Code Memory is a memory, logging, and workflow system for multi-agent teams using Claude Code.
It solves three problems:

1. **Agents forget** — context compaction is lossy, MCP memory is unreliable, MEMORY.md gets stale
2. **No audit trail** — when agents forget, there's no fallback. No one can verify what happened.
3. **No observability** — humans can't see what agents did without asking them (and they might not remember)

## Design Principles

1. **Filesystem = source of truth.** Not context window, not MCP, not MEMORY.md. Append-only logs on disk.
2. **Observability for humans.** Humans can open any file and see what every agent did, is doing, and plans to do.
3. **Backup by default.** Logs are git-trackable, human-readable markdown. Survive any system failure.
4. **Consolidation != compaction.** Memory consolidation is cyclical and deliberate (weekly "sleep" cycle), not reactive to context pressure.
5. **Ask before assuming.** When anything is unclear, agents ask and confirm before acting.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE MEMORY SYSTEM                   │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  LAYER 1: HOOKS (automatic, zero-effort)                │  │
│  │                                                         │  │
│  │  SessionStart hook                                      │  │
│  │  ├── Reads today's daily log (or flags it missing)      │  │
│  │  ├── Reads messages inbox                               │  │
│  │  ├── Reads other agents' recent activity                │  │
│  │  ├── Checks TASKS.md for assigned work                  │  │
│  │  ├── Loads handover context on compact/resume           │  │
│  │  └── Injects all as additionalContext (max 4K chars)    │  │
│  │                                                         │  │
│  │  PreCompact hook                                        │  │
│  │  ├── Reads transcript JSONL (last 200KB)                │  │
│  │  ├── Extracts tool calls, files touched, messages       │  │
│  │  ├── AUTO-APPENDS structured entry to daily log         │  │
│  │  └── Saves handover doc to handovers/ (backup)          │  │
│  │                                                         │  │
│  │  Heartbeat hook (UserPromptSubmit)                      │  │
│  │  ├── Watches shared docs for changes                    │  │
│  │  └── Checks messages/ inbox for inter-agent messages    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  LAYER 2: ENFORCEMENT (CLAUDE.md hardened rules)        │  │
│  │                                                         │  │
│  │  Three non-negotiable rules in CAPS:                    │  │
│  │  1. MANDATORY BOOT SEQUENCE (7 steps before any work)   │  │
│  │  2. LOGGING IS NOT OPTIONAL (immediate, never batch)    │  │
│  │  3. ASK FIRST, ACT SECOND (when anything is unclear)    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  LAYER 3: SHARED STATE (filesystem)                     │  │
│  │                                                         │  │
│  │  {Agent}/logs/YYYY-MM-DD.md  ← daily logs (append-only) │  │
│  │  TASKS.md                    ← cross-agent task board   │  │
│  │  messages/{agent}.md         ← inter-agent messages     │  │
│  │  handovers/                  ← pre-compact backups      │  │
│  │  CHANGELOG.md                ← cross-agent changes      │  │
│  │  DECISIONS.md                ← decision audit trail     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  LAYER 4: CONSOLIDATION (weekly "sleep" cycle)          │  │
│  │                                                         │  │
│  │  Weekly skill (manual trigger):                         │  │
│  │  ├── Read 7 days of logs → distill patterns             │  │
│  │  ├── Update MEMORY.md (add/remove/update)               │  │
│  │  ├── Update project trackers                            │  │
│  │  ├── Create weekly summary                              │  │
│  │  └── Prune old handovers                                │  │
│  │                                                         │  │
│  │  Key: cyclical & deliberate, NOT reactive to context    │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Components

### Hooks (automatic)

| Hook | Event | File | Purpose |
|------|-------|------|---------|
| Session Start | `SessionStart` | `hooks/session_start.py` | Injects daily log + messages + team activity on boot |
| Pre-Compact | `PreCompact` | `hooks/pre_compact_handover.py` | Auto-logs work + saves handover before compaction |
| Heartbeat | `UserPromptSubmit` | `hooks/heartbeat.py` | Watches shared docs for changes |

All hooks read from `hooks/agent_config.json`:
```json
{
  "agent": "YourAgentName",
  "shared_path": "/path/to/shared/folder",
  "all_agents": ["AgentA", "AgentB"]
}
```

### Skills (manual invocation)

| Skill | File | Purpose |
|-------|------|---------|
| Session Start | `skills/session-start.md` | Deep refresh beyond auto-hook |
| Pre-Compact | `skills/pre-compact.md` | Manual handover (more thorough than auto-hook) |
| Session End | `skills/session-end.md` | Full wrap-up: update all shared docs |
| Weekly Consolidate | `skills/weekly-consolidate.md` | Memory "sleep" cycle |

### Templates

| Template | File | Purpose |
|----------|------|---------|
| CLAUDE.md | `templates/CLAUDE_TEMPLATE.md` | Agent boot config with hardened rules |
| Daily Log | `templates/daily_log.md` | Structured log entry format |
| Task Board | `templates/TASKS.md` | Shared cross-agent task board |

### Shared State Files

| File | Location | Purpose |
|------|----------|---------|
| Daily logs | `{Agent}/logs/YYYY-MM-DD.md` | Append-only work record (source of truth) |
| Task board | `TASKS.md` | Cross-agent task tracking + delegation |
| Messages | `messages/{agent}.md` | Inter-agent communication |
| Handovers | `handovers/LATEST_HANDOVER.md` | Last pre-compact snapshot |
| Changelog | `CHANGELOG.md` | Cross-agent change notifications |
| Decisions | `DECISIONS.md` | Decision audit trail |

## Daily Log Format

```markdown
# Daily Log — YYYY-MM-DD
**Agent:** {name} | **Session start:** HH:MM UTC | **Session end:** HH:MM UTC

## Summary
{1-3 sentence overview}

## Work Log

### HH:MM — {Task Title}
- **project:** {project_name}
- **type:** {build|fix|research|deploy|config|design|review}
- **status:** {done|in-progress|blocked|handed-off}
- **files_touched:** {list}
- **cost_usd:** {API costs}
- **outcome:** {1-2 sentence result}
- **notes:** {anything notable}

## Metrics
| Metric | Value |
|--------|-------|
| Tasks completed | N |
| Files created | N |
| Total API cost | $X.XX |

## Handoff Notes
{What the next session needs to know}
```

**Rules:**
- Append-only. NEVER edit previous entries.
- Use `[CORRECTION]` entries to fix errors.
- NEVER claim state without checking AND logging the check.
- A task is NOT done until it is logged.

## Task Board Protocol

```
| ID | Task | Owner | Priority | Status | Assigned By | Notes |
```

- **Human assigns** — task appears with `assigned_by: {human}`
- **Agents self-assign** — claim with name in Owner column
- **One owner per task** — split if coordination needed
- **Priority:** P0 (drop everything) → P1 (today) → P2 (this week) → P3 (backlog)
- **Every status change** gets logged in daily log

## Boot Sequence (CLAUDE.md)

Every session, every agent, NO EXCEPTIONS:

1. READ today's log (or create from template)
2. READ other agents' latest logs
3. READ messages inbox
4. READ shared docs (PLAYBOOK, SQUAD, etc.)
5. READ memory (SOUL.md, MEMORY.md)
6. READ repo docs
7. Staleness check → pick next task → execute

## How Hooks Fire

```
Session start
    │
    ▼
┌──────────────┐     ┌──────────────────────┐
│ SessionStart │────▶│ session_start.py     │
│ hook fires   │     │ injects context      │
└──────────────┘     └──────────────────────┘
    │
    ▼
Agent works (reads CLAUDE.md boot sequence, logs tasks)
    │
    ▼
┌──────────────┐     ┌──────────────────────┐
│ Each prompt  │────▶│ heartbeat.py         │
│ submit       │     │ checks for changes   │
└──────────────┘     └──────────────────────┘
    │
    ▼
Context fills up...
    │
    ▼
┌──────────────┐     ┌──────────────────────┐
│ PreCompact   │────▶│ pre_compact_handover │
│ hook fires   │     │ auto-logs + handover │
└──────────────┘     └──────────────────────┘
    │
    ▼
Context compacted → SessionStart fires again → cycle repeats
```

## Weekly Consolidation ("Sleep" Cycle)

Triggered manually at start of each week. NOT the same as compaction.

| | Compaction | Consolidation |
|---|-----------|---------------|
| **Trigger** | Reactive (context full) | Cyclical (weekly) |
| **Input** | Current context window | 7 days of daily logs |
| **Process** | Summarize + discard | Distill patterns + preserve |
| **Output** | Compressed context | Updated MEMORY.md + weekly summary |
| **Lossy?** | Very (60%+ lost) | Deliberately selective |
| **Weighting** | Recent bias | Equal attention to all days |

## File Layout

```
shared_folder/
├── Claude Code Memory/
│   ├── SPEC.md                   ← this file
│   └── INSTALL.md                ← setup guide
├── config/
│   └── hooks/
│       ├── session_start.py      ← source of truth
│       ├── pre_compact_handover.py
│       ├── heartbeat.py
│       └── agent_config.template.json
├── skills/
│   ├── session-start.md
│   ├── session-end.md
│   ├── pre-compact.md
│   └── weekly-consolidate.md
├── AgentA/
│   └── logs/
│       ├── TEMPLATE.md
│       └── 2026-02-24.md
├── AgentB/
│   └── logs/
├── messages/
│   ├── agenta.md
│   └── agentb.md
├── handovers/
│   └── LATEST_HANDOVER.md
├── TASKS.md
├── CHANGELOG.md
└── DECISIONS.md
```

## Why This Works

The system addresses the three root causes of agent forgetting:

1. **Compaction loss (60%)** — Solved by append-only daily logs that persist outside the context window. PreCompact hook auto-captures work before compaction. Logs are permanent — they survive any number of compactions.

2. **Never-saved context (25%)** — Solved by enforcement. CLAUDE.md mandates logging after every task in CAPS. PreCompact hook is the automated safety net — if the agent forgot to log, the hook catches it.

3. **Poor retrieval (15%)** — Solved by SessionStart hook injecting today's log, messages, and team activity at boot. Agent starts every session with full context of what happened.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-24 | Initial release: 3 hooks, 4 skills, task board, weekly consolidation |
| 1.1 | 2026-02-24 | Renamed, scrubbed for open source release |
