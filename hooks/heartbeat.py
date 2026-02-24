"""
Heartbeat hook — checks shared docs and inbox for changes.
Runs on every UserPromptSubmit. Outputs nothing if no changes (0 tokens).
Outputs JSON additionalContext if changes detected.

Part of Claude Code Memory.

Config: reads agent name + shared path from agent_config.json
in the same directory as this script.
"""
import os, sys, json, time
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

STATE_FILE = os.path.join(os.environ.get("TEMP", "/tmp"), "claude_heartbeat_last.json")

# Files to watch (high-signal, low-noise)
WATCH = {
    "CHANGELOG.md": "CHANGELOG",
    "DECISIONS.md": "DECISIONS",
    "RESOURCES.md": "RESOURCES",
    "SQUAD.md": "SQUAD",
}


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def check_messages_inbox():
    """Check messages/ folder for direct agent messages."""
    alerts = []
    msg_dir = SHARED / "messages"
    try:
        for f in os.listdir(msg_dir):
            if f.endswith(".md"):
                filepath = msg_dir / f
                mtime = os.path.getmtime(filepath)
                ago = int(time.time() - mtime)
                if ago < 3600:
                    agent_name = f.replace(".md", "")
                    alerts.append(f"Message in messages/{f} ({ago//60}m ago)")
    except FileNotFoundError:
        pass
    return alerts


def main():
    # Read stdin (hook event data) — required but we don't need it
    try:
        sys.stdin.read()
    except:
        pass

    state = load_state()
    changed = []
    new_state = dict(state)

    # Check shared docs
    for filename, label in WATCH.items():
        path = SHARED / filename
        try:
            mtime = os.path.getmtime(path)
            new_state[filename] = mtime
            last_seen = state.get(filename, 0)
            if mtime > last_seen and last_seen > 0:
                ago = int(time.time() - mtime)
                if ago < 3600:
                    mins = ago // 60
                    changed.append(f"{label} ({mins}m ago)" if mins > 0 else f"{label} (just now)")
        except FileNotFoundError:
            pass

    # Check messages/ inbox
    inbox_alerts = check_messages_inbox()
    changed.extend(inbox_alerts)

    save_state(new_state)

    if changed:
        msg = f"[HEARTBEAT] Updates: {'; '.join(changed)}"
        print(json.dumps({"additionalContext": msg}))


if __name__ == "__main__":
    main()
