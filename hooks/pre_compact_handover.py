"""
PreCompact Handover Hook — Memory v2 auto-logging + handover.

Fires on PreCompact (auto) event. Does TWO things:
1. AUTO-LOGS: Extracts recent work from transcript -> appends to today's daily log
2. HANDOVER: Saves transcript context to handover file for session resume

The daily log is the SOURCE OF TRUTH. The handover is a BACKUP.
This hook is the safety net — even if the agent forgot to log,
this catches it before compaction erases context.

Part of Claude Code Memory.

Config: reads agent name + shared path from agent_config.json
in the same directory as this script.
"""
import json
import os
import sys
from datetime import datetime, date
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

LOGS_DIR = SHARED / AGENT / "logs"
HANDOVER_DIR = SHARED / "handovers"
HANDOVER_DIR.mkdir(exist_ok=True)


def extract_work_from_transcript(transcript_path: str) -> dict:
    """Extract recent work items from transcript JSONL."""
    result = {
        "files_touched": set(),
        "actions": [],
        "last_messages": [],
        "tool_calls": 0,
        "bash_commands": [],
    }

    if not transcript_path or not os.path.exists(transcript_path):
        result["files_touched"] = list(result["files_touched"])
        return result

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            f.seek(0, 2)
            size = f.tell()
            read_from = max(0, size - 200_000)
            f.seek(read_from)
            tail = f.read()

        for raw_line in tail.split("\n"):
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                entry = json.loads(raw_line)
            except (json.JSONDecodeError, TypeError):
                continue

            if entry.get("type") == "assistant":
                msg = entry.get("message", {})
                for part in msg.get("content", []):
                    if not isinstance(part, dict):
                        continue

                    if part.get("type") == "text":
                        text = part.get("text", "").strip()
                        if len(text) > 30:
                            result["last_messages"].append(text[:300])

                    elif part.get("type") == "tool_use":
                        tool_name = part.get("name", "")
                        tool_input = part.get("input", {})
                        result["tool_calls"] += 1

                        if tool_name in ("Write", "Edit", "Read"):
                            fp = tool_input.get("file_path", "")
                            if fp:
                                result["files_touched"].add(
                                    os.path.basename(fp)
                                )

                        elif tool_name == "Bash":
                            desc = tool_input.get("description", "")
                            cmd = tool_input.get("command", "")
                            result["bash_commands"].append(
                                (desc or cmd)[:100]
                            )

                        if tool_name in ("Write", "Edit"):
                            fp = tool_input.get("file_path", "")
                            if fp:
                                result["actions"].append(
                                    f"{tool_name}: {os.path.basename(fp)}"
                                )

        result["files_touched"] = list(result["files_touched"])
        result["last_messages"] = result["last_messages"][-5:]
        result["actions"] = result["actions"][-20:]
        result["bash_commands"] = result["bash_commands"][-10:]

    except Exception as e:
        result["files_touched"] = list(result["files_touched"])
        result["error"] = str(e)

    return result


def auto_log_to_daily(work: dict, cwd: str):
    """Append an auto-generated log entry to today's daily log."""
    today = date.today().isoformat()
    log_path = LOGS_DIR / f"{today}.md"
    now = datetime.now().strftime("%H:%M")

    files = ", ".join(work["files_touched"][:10]) if work["files_touched"] else "none extracted"
    project = os.path.basename(cwd) if cwd else "unknown"

    outcome = "Work in progress (auto-captured before compaction)"
    if work["last_messages"]:
        last_msg = work["last_messages"][-1]
        outcome = last_msg.split(".")[0][:200] if "." in last_msg[:200] else last_msg[:200]

    entry = f"""
### {now} — [AUTO-LOGGED] Pre-Compact Work Capture
- **project:** {project}
- **type:** mixed
- **status:** in-progress (compaction imminent)
- **files_touched:** {files}
- **cost_usd:** 0
- **tokens_used:** ~{work['tool_calls'] * 500} (estimated from {work['tool_calls']} tool calls)
- **outcome:** {outcome}
- **notes:** Auto-logged by pre_compact_handover.py. {len(work['actions'])} file operations, {len(work['bash_commands'])} bash commands. Review and refine next session.
"""

    if log_path.exists():
        content = log_path.read_text(encoding="utf-8")
        if "## Metrics" in content:
            content = content.replace("## Metrics", entry + "\n## Metrics", 1)
        else:
            content += entry
        log_path.write_text(content, encoding="utf-8")
    else:
        header = f"""# Daily Log — {today}
**Agent:** {AGENT} | **Session start:** {now} UTC | **Session end:** TBD

## Summary
Auto-created by pre-compact hook. Fill in summary next session.

## Work Log
{entry}
"""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_path.write_text(header, encoding="utf-8")


def save_handover(event_data: dict, work: dict) -> str:
    """Save handover document."""
    session_id = event_data.get("session_id", "unknown")
    trigger = event_data.get("trigger", "auto")
    cwd = event_data.get("cwd", "unknown")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# PreCompact Handover — {now}",
        f"**Agent:** {AGENT}",
        f"**Session:** {session_id[:12]}",
        f"**Trigger:** {trigger}",
        f"**CWD:** {cwd}",
        f"**Tool calls:** {work['tool_calls']}",
        f"**Files touched:** {', '.join(work['files_touched'][:15])}",
        "",
        "---",
        "",
    ]

    if work["actions"]:
        lines.append("## Recent File Operations")
        for action in work["actions"][-10:]:
            lines.append(f"- {action}")
        lines.append("")

    if work["bash_commands"]:
        lines.append("## Recent Commands")
        for cmd in work["bash_commands"][-5:]:
            lines.append(f"- {cmd}")
        lines.append("")

    if work["last_messages"]:
        lines.append("## Recent Context (last assistant messages)")
        for i, msg in enumerate(work["last_messages"][-3:], 1):
            lines.append(f"\n### Message {i}")
            lines.append(msg)
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Resume Instructions",
        f"1. Read today's daily log: {AGENT}/logs/{date.today().isoformat()}.md",
        "2. Check messages inbox",
        "3. Continue from where this handover left off",
        "",
        f"*Auto-generated by pre_compact_handover.py at {now}*",
    ])

    content = "\n".join(lines)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sid = session_id[:8]
    filepath = HANDOVER_DIR / f"handover_{ts}_{sid}.md"
    filepath.write_text(content, encoding="utf-8")

    latest = HANDOVER_DIR / "LATEST_HANDOVER.md"
    latest.write_text(content, encoding="utf-8")

    handovers = sorted(HANDOVER_DIR.glob("handover_*.md"), key=lambda p: p.name)
    for old in handovers[:-10]:
        try:
            old.unlink()
        except OSError:
            pass

    return str(filepath)


def main():
    try:
        raw = sys.stdin.read()
        event_data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, Exception):
        event_data = {}

    transcript_path = event_data.get("transcript_path", "")
    cwd = event_data.get("cwd", os.getcwd())

    work = extract_work_from_transcript(transcript_path)

    try:
        auto_log_to_daily(work, cwd)
        log_status = "auto-logged to daily log"
    except Exception as e:
        log_status = f"auto-log FAILED: {e}"

    try:
        handover_path = save_handover(event_data, work)
        handover_status = f"saved to {os.path.basename(handover_path)}"
    except Exception as e:
        handover_status = f"handover FAILED: {e}"

    context = (
        f"[MEMORY V2 PRE-COMPACT] Work {log_status}. "
        f"Handover {handover_status}. "
        f"{work['tool_calls']} tool calls, "
        f"{len(work['files_touched'])} files touched."
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreCompact",
            "additionalContext": context
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
