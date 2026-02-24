"""
SessionStart hook — Memory v2 boot context injection.

Fires on every SessionStart (startup, resume, compact, clear).
Reads today's daily log, messages inbox, other agents' recent activity,
and recent handovers. Injects all as additionalContext so the agent
knows exactly where it left off.

Part of Claude Code Memory. Source of truth: shared folder logs.

Config: reads agent name + shared path from agent_config.json
in the same directory as this script.
"""
import json
import os
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path

# === CONFIG (from agent_config.json) ===
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "agent_config.json"

try:
    with open(CONFIG_PATH) as f:
        _cfg = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _cfg = {}

AGENT = _cfg.get("agent", "Agent")
SHARED = Path(_cfg.get("shared_path", str(SCRIPT_DIR)))
ALL_AGENTS = _cfg.get("all_agents", [AGENT])
OTHER_AGENTS = [a for a in ALL_AGENTS if a != AGENT]

LOGS_DIR = SHARED / AGENT / "logs"
MESSAGES_FILE = SHARED / "messages" / f"{AGENT.lower()}.md"
TASKS_FILE = SHARED / "TASKS.md"
HANDOVER_DIR = SHARED / "handovers"
MAX_CONTEXT = 4000  # chars — keep injection lean


def get_today_log():
    """Read today's daily log or flag that it needs creation."""
    today = date.today().isoformat()
    log_path = LOGS_DIR / f"{today}.md"

    if log_path.exists():
        content = log_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        sections = {"summary": [], "last_work": [], "handoff": [], "blockers": []}
        current = None
        work_entries = []
        work_buf = []

        for line in lines:
            if line.startswith("## Summary"):
                current = "summary"
                continue
            elif line.startswith("## Work Log"):
                current = "work"
                continue
            elif line.startswith("## Handoff Notes") or line.startswith("## Handoff"):
                current = "handoff"
                continue
            elif line.startswith("## Blockers"):
                current = "blockers"
                continue
            elif line.startswith("## ") and current:
                current = None
                continue

            if current == "summary":
                sections["summary"].append(line)
            elif current == "work":
                if line.startswith("### "):
                    if work_buf:
                        work_entries.append("\n".join(work_buf))
                    work_buf = [line]
                elif work_buf:
                    work_buf.append(line)
            elif current == "handoff":
                sections["handoff"].append(line)
            elif current == "blockers":
                sections["blockers"].append(line)

        if work_buf:
            work_entries.append("\n".join(work_buf))

        parts = []
        parts.append(f"**Log exists** ({len(lines)} lines, {len(work_entries)} work entries)")

        summary_text = "\n".join(sections["summary"]).strip()
        if summary_text:
            parts.append(f"Summary: {summary_text[:300]}")

        if work_entries:
            parts.append("Last entries:")
            for entry in work_entries[-2:]:
                parts.append(entry[:200])

        handoff = "\n".join(sections["handoff"]).strip()
        if handoff:
            parts.append(f"Handoff: {handoff[:300]}")

        blockers = "\n".join(sections["blockers"]).strip()
        if blockers:
            parts.append(f"Blockers: {blockers[:200]}")

        return "\n".join(parts)
    else:
        return (
            f"**NO LOG FOR TODAY ({today}).** "
            f"CREATE ONE IMMEDIATELY from {AGENT}/logs/TEMPLATE.md before doing any work."
        )


def get_messages():
    """Read messages inbox. Return content if recent."""
    if MESSAGES_FILE.exists():
        mtime = MESSAGES_FILE.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        content = MESSAGES_FILE.read_text(encoding="utf-8").strip()
        if content and age_hours < 24:
            if len(content) > 600:
                content = content[:600] + "\n[...truncated — read full file]"
            return f"**Messages ({int(age_hours)}h ago):**\n{content}"
    return ""


def get_other_agents_recent():
    """Get summary of other agents' recent activity."""
    summaries = []
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    for agent in OTHER_AGENTS:
        for d, label in [(today, "today"), (yesterday, "yesterday")]:
            log_path = SHARED / agent / "logs" / f"{d}.md"
            if log_path.exists():
                content = log_path.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if line.strip() and not line.startswith("#") and not line.startswith("**"):
                        summaries.append(f"**{agent}** ({label}): {line.strip()[:150]}")
                        break
                else:
                    summaries.append(f"**{agent}**: Log exists for {label}")
                break
        else:
            summaries.append(f"**{agent}**: No recent logs")

    return summaries


def get_active_tasks():
    """Read shared task board for tasks assigned to this agent."""
    if TASKS_FILE.exists():
        content = TASKS_FILE.read_text(encoding="utf-8")
        my_tasks = []
        for line in content.split("\n"):
            if AGENT in line and ("In Progress" in line or "TODO" in line or "Assigned" in line):
                my_tasks.append(line.strip())
        if my_tasks:
            return "**My active tasks:** " + " | ".join(my_tasks[:5])
    return ""


def get_latest_handover(source):
    """Check for recent handover from pre-compact (only on compact/resume)."""
    if source not in ("compact", "resume"):
        return ""

    latest = HANDOVER_DIR / "LATEST_HANDOVER.md"
    if latest.exists():
        age_minutes = (time.time() - latest.stat().st_mtime) / 60
        if age_minutes < 120:
            content = latest.read_text(encoding="utf-8")
            if len(content) > 800:
                content = content[:800] + "\n[...truncated]"
            return f"**Recent handover ({int(age_minutes)}m ago):**\n{content}"
    return ""


def main():
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        event = {}

    source = event.get("source", "startup")
    cwd = event.get("cwd", os.getcwd())
    now = datetime.now()

    parts = []
    parts.append(f"# {AGENT} Session Start ({source})")
    parts.append(f"**Date:** {now.strftime('%Y-%m-%d')} | **Time:** {now.strftime('%H:%M')} | **CWD:** {os.path.basename(cwd)}")
    parts.append("")

    parts.append("## Today's Log")
    parts.append(get_today_log())
    parts.append("")

    msgs = get_messages()
    if msgs:
        parts.append("## Inbox")
        parts.append(msgs)
        parts.append("")

    agent_info = get_other_agents_recent()
    if agent_info:
        parts.append("## Team Activity")
        parts.extend(agent_info)
        parts.append("")

    tasks = get_active_tasks()
    if tasks:
        parts.append("## Tasks")
        parts.append(tasks)
        parts.append("")

    handover = get_latest_handover(source)
    if handover:
        parts.append("## Handover Context")
        parts.append(handover)
        parts.append("")

    context = "\n".join(parts)

    if len(context) > MAX_CONTEXT:
        context = context[:MAX_CONTEXT] + "\n[...context trimmed to stay lean]"

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
