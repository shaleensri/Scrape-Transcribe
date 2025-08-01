import json
from pathlib import Path
from typing import Dict, Any
import threading

STATE_FILE = Path("state.json")

#Empty state file
DEFAULT_STATE = {"house": [], "senate": []}

# Added RLock instead of Lock to allow nested state access
# Esp. for load_state() called within mark_processed() / is_processed()
STATE_LOCK = threading.RLock()

def load_state() -> Dict[str, Any]:
    """Load the state from JSON. Create/reset 
        if missing, empty, or corrupted.
        @return: Dict with keys "house" and "senate" 
                containing lists of processed videos
        """
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
    """Save state to JSON file.
    @param state: Dict with keys "house" and "senate" 
                containing lists of processed videos
    """
    with STATE_LOCK:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)


def is_processed(chamber: str, committee: str, recording_date: str, filename: str) -> bool:
    """Check if a file is already processed.
    @param chamber: house/senate
    @param committee: Name of committee
    @param recording_date: Date of recording
    @param filename: Name of the file
    @return: True if processed, False otherwise
    """
    with STATE_LOCK:
        state = load_state()
        for entry in state.get(chamber, []):
            if (entry["filename"] == filename):
                return True
        return False


def mark_processed(chamber: str, committee: str, recording_date: str, filename: str):
    """Mark a file as processed in the state.
    @param chamber: house/senate
    @param committee: Name of committee
    @param recording_date: Date of recording
    @param filename: Name of the file
    """
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
