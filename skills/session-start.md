# Session Start — Wake-Up Protocol

**NOTE:** The SessionStart hook (`~/.claude/hooks/session_start.py`) now auto-injects
today's log status, messages, team activity, and handover context on every session start.
This skill is for MANUAL invocation when you need a deeper refresh beyond what the hook provides.

Execute the full wake-up protocol:

1. **Read TODAY'S LOG** → `{shared_path}/{AGENT}/logs/{YYYY-MM-DD}.md`
   - If it doesn't exist, CREATE IT from `{AGENT}/logs/TEMPLATE.md`
   - If it exists, read the last entry to know where you left off
   - **FAILURE TO DO THIS = YOU WILL REPEAT WORK OR LOSE CONTEXT**

2. **Read OTHER AGENTS' LATEST LOGS** → check other agent directories under `{shared_path}/`
   - Check what they did. Don't duplicate. Note anything that affects you.

3. **Read MESSAGES** → `messages/{agent}.md`
   - Other agents leave instructions here. READ THEM.

4. **Read PLAYBOOK.md** at `{shared_path}/PLAYBOOK.md` — operating rules and shared learnings

5. **Read SQUAD.md** at `{shared_path}/SQUAD.md` — who exists, what they're doing

6. **Read shared strategy docs** at `{shared_path}/`:
   - VISION.md (mission, thesis, strategy)
   - Your MASTER_PLAN_{AGENT}.md (your master plan)
   - TASKS.md (shared task board — check what's assigned to you)
   - RESOURCES.md (budget, compute — check before using)
   - CHANGELOG.md (recent changes from other agents)
   - DECISIONS.md (skim recent decisions)

7. **Read memory**: SOUL.md, MEMORY.md

8. **Read repo docs**: project-specific status and implementation docs

9. **Staleness check**: Is anything you just read out of date? Fix it now.

10. **Report**: Summarize current state, what's changed since last session, and recommend next task from TASKS.md to pick up.
