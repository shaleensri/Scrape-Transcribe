import json
from pathlib import Path
from typing import Dict, Any
import threading

STATE_FILE = Path("state.json")

DEFAULT_STATE = {"house": [], "senate": []}
STATE_LOCK = threading.RLock()

def load_state() -> Dict[str, Any]:
    """Load the state from JSON. Create/reset if missing, empty, or corrupted."""
    with STATE_LOCK:
        if not STATE_FILE.exists():
            return DEFAULT_STATE.copy()

        try:
            with open(STATE_FILE, "r") as f:
                content = f.read().strip()
                if not content:  # Empty file
                    return DEFAULT_STATE.copy()
                return json.loads(content)
        except json.JSONDecodeError:
            print("[Warning] state.json is corrupted. Resetting to empty.")
            return DEFAULT_STATE.copy()


def save_state(state: Dict[str, Any]):
    """Save state to JSON file."""
    with STATE_LOCK:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)


def is_processed(chamber: str, committee: str, recording_date: str, filename: str) -> bool:
    """Check if a file is already processed."""
    with STATE_LOCK:
        state = load_state()
        for entry in state.get(chamber, []):
            if (entry["committee"] == committee and
                entry["recording_date"] == recording_date and
                entry["filename"] == filename):
                return True
        return False


def mark_processed(chamber: str, committee: str, recording_date: str, filename: str):
    """Mark a file as processed in the state."""
    with STATE_LOCK:
        state = load_state()
        if chamber not in state:
            state[chamber] = []
        state[chamber].append({
            "committee": committee,
            "recording_date": recording_date,
            "filename": filename
        })
        save_state(state)
