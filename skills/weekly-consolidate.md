# Weekly Consolidation — Memory "Sleep" Cycle

Execute this skill at the start of each week (or when explicitly requested).
This is the agent equivalent of human sleep — cyclical, deliberate memory consolidation.

**NOT the same as compaction.** Compaction is reactive (back against the wall, context full).
Consolidation is cyclical (weekly cadence, deliberate, processes meaning not just tokens).

## Process

### 1. Gather the Raw Material

Read all daily logs from the past 7 days:
- `{shared_path}/{AGENT}/logs/{YYYY-MM-DD}.md`
- For each day: extract work entries, decisions, learnings, blockers, outcomes
- Also read: TASKS.md (task board), messages/ (inter-agent comms)

### 2. Distill Patterns

From the 7 days of logs, identify:
- **Recurring themes** — What kept coming up? What patterns emerged?
- **Key decisions** — What was decided and why? Are those decisions still valid?
- **Learnings** — What was discovered that future sessions need to know?
- **Blockers resolved** — What was blocked and how was it unblocked?
- **Blockers remaining** — What's still stuck?
- **Completed work** — What shipped? What's the cumulative output?
- **Wasted effort** — What was done that turned out to be unnecessary? Why?

### 3. Update MEMORY.md

Apply the distilled insights:
- **Add** new learnings that are durable (will matter next week too)
- **Remove** entries that are no longer relevant (resolved blockers, completed features)
- **Update** entries that have evolved (better understanding, corrected information)
- **Keep MEMORY.md under 200 lines** — this is loaded every session, tokens matter
- Move detailed content to topic files (e.g., `repo-guide.md`, `debugging.md`)

### 4. Update Project Trackers

For each active project:
- Update `{AGENT}/logs/{PROJECT}_TRACKER.md` with current status
- Update MASTER_PLAN if workstream statuses have changed
- Update TASKS.md — close completed tasks, add newly identified tasks

### 5. Create Weekly Summary

Write a weekly summary to: `{AGENT}/logs/WEEKLY_{YYYY-Www}.md`

Format:
```markdown
# Weekly Summary — {AGENT} — Week {N} ({date range})

## Highlights
- {3-5 bullet points of key accomplishments}

## Metrics
| Metric | Value |
|--------|-------|
| Tasks completed | N |
| Files created | N |
| Files modified | N |
| Total API cost | $X.XX |

## Key Decisions
- {Decision}: {Rationale}

## Learnings
- {Learning}: {Context}

## Next Week Priorities
1. {Priority 1}
2. {Priority 2}
3. {Priority 3}

## Risks & Blockers
- {What could go wrong}
```

### 6. Prune Old Handovers

- Delete handover files older than 7 days from `handovers/`
- They've been consolidated into weekly summaries now

### 7. Report

Summarize what was consolidated, what was pruned, and what changed in MEMORY.md.
Tag the summary with the consolidation date so future sessions know when the last "sleep" happened.

## Key Principles

- **Consolidation preserves MEANING, not tokens.** 7 days of "fixed X, then fixed Y, then fixed Z" becomes "Fixed 3 bugs in module X — root cause was Y, added regression tests."
- **Don't lose decisions.** Every decision in a daily log should either be in DECISIONS.md or in a project tracker. Consolidation ensures nothing falls through.
- **Equally weighted.** Unlike compaction (which loses early context), consolidation processes the full week with equal attention to Monday and Friday.
- **Audit trail.** Weekly summaries are permanent. Daily logs are permanent. Nothing is deleted — just distilled.
