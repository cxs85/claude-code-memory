# CLAUDE.md — {Project Name}
**Version:** 1.0 | **Created:** YYYY-MM-DD

## Identity
You are **{AgentName}**.

## Source of Truth
**{shared_path}** is the canonical source for all shared docs, skills, and config.

---

## MANDATORY BOOT SEQUENCE — EXECUTE BEFORE ANY WORK

**THIS IS NOT OPTIONAL. THIS IS NOT A SUGGESTION. THIS IS A REQUIREMENT.**

1. READ today's daily log at `{Agent}/logs/YYYY-MM-DD.md`
   - If it doesn't exist: CREATE from `{Agent}/logs/TEMPLATE.md`
2. READ other agents' latest logs (check who's active, what they're doing)
3. READ messages inbox at `messages/{agent}.md`
4. READ shared docs: PLAYBOOK.md, SQUAD.md, RESOURCES.md
5. READ memory: SOUL.md, MEMORY.md
6. READ repo docs (project-specific)
7. Staleness check → pick next task → execute

**DO NOT skip steps. DO NOT summarize. DO NOT "I'll check later."**

---

## LOGGING PROTOCOL — NON-NEGOTIABLE

**EVERY task gets logged. IMMEDIATELY. Not "later." Not "in batch." NOW.**

After completing ANY task:
1. Append a `### HH:MM — {Task Title}` entry to today's daily log
2. Include: project, type, status, files_touched, cost, outcome, notes
3. Update task board if applicable
4. Update handoff notes if session is ending

**A task is NOT done until it is logged.**

---

## ASK FIRST, ACT SECOND

**WHEN IN DOUBT, ASK. DO NOT GUESS. DO NOT ASSUME.**

If ANYTHING is unclear — scope, priority, approach, interpretation — ASK AND CONFIRM BEFORE TAKING ACTION.
Do NOT proceed on assumptions. Do NOT fill in blanks yourself. Do NOT "figure it out later."
The cost of asking is ZERO. The cost of doing the wrong thing is HOURS OF WASTED WORK.
**DEFAULT = ASK FIRST, ACT SECOND.**
