from pathlib import Path
import threading
from urllib.parse import urlparse, parse_qs

from fetcher.house_scraper_static import HouseScraperStatic
from fetcher.senate_scraper import SenateScraper
from storage.file_manager import (
    download_house_video,
    download_senate_video_ffmpeg,
    upload_file_to_gcs
)
from transcriber.whisper_transcriber import WhisperTranscriber
from storage.state_tracker import is_processed, mark_processed

BUCKET_NAME = "legislature-videos-shaleen"

def get_filename_from_url(url):
    query = parse_qs(urlparse(url).query)
    return query.get("video", ["video.mp4"])[0]

def process_video(chamber, committee, recording_date, filename, download_args):
    """Generic video processing: download, transcribe, upload, mark processed, cleanup"""

    if is_processed(chamber, committee, recording_date, filename):
        print(f"[Skip] Already processed: {committee} | {recording_date} | {filename}")
        return

    output_dir = Path(f"downloads/{chamber}")
    output_dir.mkdir(parents=True, exist_ok=True)
    local_path = output_dir / filename

    # Download based on chamber
    if chamber == "house":
        real_url = download_args["real_url"]
        print(f"\nHouse: Downloading from {real_url}")
        download_house_video(real_url, local_path)
    elif chamber == "senate":
        video_id = download_args["video_id"]
        print(f"\nSenate: Downloading video ID: {video_id}")
        local_path = download_senate_video_ffmpeg(video_id, output_dir)

    print(f"{chamber.capitalize()}: Download complete.")

    # Transcribe
    print("\nTranscribing...")
    transcriber = WhisperTranscriber()
    transcript_path = transcriber.transcribe(local_path)

    # Show transcript preview
    preview = Path(transcript_path).read_text()
    print("\nTranscript Preview:\n")
    print(preview[:1000] + "..." if len(preview) > 1000 else preview)

    # Upload
    cloud_dir = f"{chamber}/{committee}/{recording_date}"
    upload_file_to_gcs(BUCKET_NAME, local_path, f"{cloud_dir}/{local_path.name}")
    upload_file_to_gcs(BUCKET_NAME, transcript_path, f"{cloud_dir}/{transcript_path.name}")

    # Mark as processed
    mark_processed(chamber, committee, recording_date, filename)

    # Cleanup local files
    try:
        local_path.unlink()
        transcript_path.unlink()
        print(f"[Cleanup] Deleted local files: {local_path.name}, {transcript_path.name}")
    except Exception as e:
        print(f"[Warning] Could not delete files: {e}")

def run_house():
    print("Scraping House videos...")
    house_scraper = HouseScraperStatic()
    house_videos = house_scraper.scrape()
    print(f"Found {len(house_videos)} House videos.\n")

    for idx, video in enumerate(house_videos[:5], start=1):
        print(f"{idx}. {video['committee']} | Date: {video['date']} | URL: {video['url']}")

    # Demo: first video
    target_video = house_videos[3]
    filename = get_filename_from_url(target_video["url"])
    committee = target_video["committee"]
    recording_date = target_video["date"]
    real_url = f"https://www.house.mi.gov/ArchiveVideoFiles/{filename}"

    process_video(
        chamber="house",
        committee=committee,
        recording_date=recording_date,
        filename=filename,
        download_args={"real_url": real_url}
    )

def run_senate():
    print("Scraping Senate videos...")
    scraper = SenateScraper()
    videos = scraper.scrape(batch_size=30, max_pages=1)
    print(f"Found {len(videos)} Senate videos.\n")

    for idx, video in enumerate(videos[:5], start=1):
        print(f"{idx}. {video['title']} | Uploaded: {video['upload_date']} | ID: {video['video_id']}")

    # Demo: first video
    target_video = videos[3]
    filename = target_video["title"]
    committee = filename.rsplit(" ", 1)[0].strip()
    recording_date = target_video["recording_date"]

    process_video(
        chamber="senate",
        committee=committee,
        recording_date=recording_date,
        filename=filename,
        download_args={"video_id": target_video["video_id"]}
    )

if __name__ == "__main__":
    # Choose which to run
    house_thread = threading.Thread(target=run_house)
    senate_thread = threading.Thread(target=run_senate)
    house_thread.start()
    senate_thread.start()
    house_thread.join()
    senate_thread.join()