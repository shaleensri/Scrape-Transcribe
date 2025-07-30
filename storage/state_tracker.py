import json
from pathlib import Path
from typing import Dict, Any

STATE_FILE = Path("state.json")


def load_state() -> Dict[str, Any]:
    """Load the state from JSON, return empty structure if not found."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"house": [], "senate": []}


def save_state(state: Dict[str, Any]):
    """Save state to JSON file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_processed(chamber: str, committee: str, recording_date: str, filename: str) -> bool:
    """Check if a file is already processed."""
    state = load_state()
    for entry in state.get(chamber, []):
        if (entry["committee"] == committee and
            entry["recording_date"] == recording_date and
            entry["filename"] == filename):
            return True
    return False


def mark_processed(chamber: str, committee: str, recording_date: str, filename: str):
    """Mark a file as processed in the state."""
    state = load_state()
    if chamber not in state:
        state[chamber] = []
    state[chamber].append({
        "committee": committee,
        "recording_date": recording_date,
        "filename": filename
    })
    save_state(state)
