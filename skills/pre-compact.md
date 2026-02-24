# Pre-Compact — Emergency Handover Before Context Loss

**NOTE:** The PreCompact hook (`~/.claude/hooks/pre_compact_handover.py`) now auto-extracts
work from the transcript and appends it to today's daily log. It also saves a handover doc.
This skill is for MANUAL invocation when you know compaction is coming and want to do a
more thorough handover than the auto-hook provides.

Execute when context usage is >70% or compaction/reboot is imminent.

**MANDATORY: Log first, handover second.**

## Step 1: LOG ALL UNLOGGED WORK (PRIMARY)

Append entries to today's daily log (`{AGENT}/logs/{YYYY-MM-DD}.md`) for every task
completed since the last log entry. Use the standard format:

```
### {HH:MM} — {Task Title}
- **project:** {project_name}
- **type:** {build|fix|research|deploy|config|crawl|enrichment|design|review}
- **status:** {done|in-progress|blocked|handed-off}
- **files_touched:** {list of key files}
- **cost_usd:** {API costs if any}
- **outcome:** {1-2 sentence result}
- **notes:** {anything notable}
```

**DO NOT SKIP THIS STEP. The daily log is the source of truth. Everything else is backup.**

## Step 2: HANDOVER DOC (BACKUP)

Write a handover section to the daily log (or STATUS.md):

```
## Session Handover — [DATE] [AGENT]
### Current Task
[What I was working on, exactly where I left off]
### In-Progress Work
[Files being edited, background agents running, subprocesses]
### Completed This Session
[Bullet list of concrete outputs]
### Next Steps (pickup-ready)
[Numbered, specific enough to execute without re-deriving]
### Decisions Made
[Any decisions that should go to DECISIONS.md]
```

## Step 3: UPDATE SHARED DOCS (if time)

Only if you have context left:
- TASKS.md — Update task statuses
- CHANGELOG.md — Post if changes affect other agents
- MEMORY.md — Record key learnings

**The golden rule:** If a fresh agent read only today's daily log + TASKS.md, could they resume your work? If not, add more detail.
