import threading
import schedule
import time
from pathlib import Path
from main import run_house, run_senate  

# ===== CONFIGURATION =====
FREQ_MINUTES = 5   # How often to run both jobs
VIDEO_LIMIT = 2           # Max number of videos to process per run
LOCK_FILE = Path("scheduler.lock")
# =========================

def job_wrapper():
    """Wraps the job to prevent overlapping runs."""
    if LOCK_FILE.exists():
        print("Previous run still in progress... waiting...")
        return  # Skip this run if another is still active

    try:
        LOCK_FILE.touch()

        house_thread = threading.Thread(target=run_house, args=(VIDEO_LIMIT,))
        senate_thread = threading.Thread(target=run_senate, args=(VIDEO_LIMIT,))

        house_thread.start()
        senate_thread.start()

        house_thread.join()
        senate_thread.join()

    finally:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()

if __name__ == "__main__":
    # Schedule both jobs
    print("Starting Jobs...")
    schedule.every(FREQ_MINUTES).minutes.do(job_wrapper)

    print(f"Scheduler started: Running both chambers every {FREQ_MINUTES} minutes.")
    print(f"Processing up to {VIDEO_LIMIT} videos per run.\nPress Ctrl+C to stop.\n")

    job_wrapper()  # First Run

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Scheduler stopped by user.")
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
