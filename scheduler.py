import schedule
import time
from pathlib import Path
from main import run_house, run_senate  

# ===== CONFIGURATION =====
HOUSE_FREQ_MINUTES = 5    # How often to run House job
SENATE_FREQ_MINUTES = 5   # How often to run Senate job
VIDEO_LIMIT = 2           # Max number of videos to process per run
LOCK_FILE = Path("scheduler.lock")
# =========================

def job_wrapper(job_func, *args):
    """Wraps the job to prevent overlapping runs."""
    if LOCK_FILE.exists():
        print("Previous run still in progress... waiting...")
        return  # Skip this run if another is still active

    try:
        LOCK_FILE.touch()
        job_func(*args)
    finally:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()

def job_house():
    print("\n Starting House job...")
    job_wrapper(run_house, VIDEO_LIMIT)

def job_senate():
    print("\n Starting Senate job...")
    job_wrapper(run_senate, VIDEO_LIMIT)

if __name__ == "__main__":
    # Schedule both jobs
    print("Starting Jobs...")
    # Initial run

    schedule.every(HOUSE_FREQ_MINUTES).minutes.do(job_house)
    schedule.every(SENATE_FREQ_MINUTES).minutes.do(job_senate)

    print(f"Scheduler started: House every {HOUSE_FREQ_MINUTES} min, Senate every {SENATE_FREQ_MINUTES} min.")
    print(f"Processing up to {VIDEO_LIMIT} videos per run.\nPress Ctrl+C to stop.\n")

    job_house()
    job_senate()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Scheduler stopped by user.")
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
