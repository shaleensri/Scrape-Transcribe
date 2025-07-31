from pathlib import Path
import threading
from urllib.parse import urlparse, parse_qs

from fetcher.house_scraper_static import HouseScraperStatic
from fetcher.senate_scraper import SenateScraper
from storage.file_manager import (
    download_house_video_ffmpeg,
    download_senate_video_ffmpeg,
    upload_file_to_gcs
)
from storage.video_processor import process_video
from transcriber.whisper_transcriber import WhisperTranscriber

BUCKET_NAME = "legislature-videos-shaleen"

def get_filename_from_url(url):
    query = parse_qs(urlparse(url).query)
    return query.get("video", ["video.mp4"])[0]


def run_house(limit=None):
    print("Scraping House videos...")
    house_scraper = HouseScraperStatic()
    house_videos = house_scraper.scrape()
    print(f"Found {len(house_videos)} House videos.\n")

    processed_count = 0
    for video in house_videos:
        filename = get_filename_from_url(video["url"])
        committee = video["committee"]
        recording_date = video["date"]
        real_url = f"https://www.house.mi.gov/ArchiveVideoFiles/{filename}"
        processed_count += 1
        process_video(
            chamber="house",
            committee=committee,
            recording_date=recording_date,
            filename=filename,
            download_args={"real_url": real_url}
        )
        #print(f"house processed_count: {processed_count} | {filename}")
        if limit and processed_count >= limit:
            break



def run_senate(limit=None):
    print("Scraping Senate videos...")
    scraper = SenateScraper()
    videos = scraper.scrape(batch_size=30, max_pages=1)
    print(f"Found {len(videos)} Senate videos.\n")

    processed_count = 0
    for video in videos:  
        filename = video["title"]
        if not filename.endswith(".mp4"):
            filename += ".mp4"
        committee = filename.rsplit(" ", 1)[0].strip()
        recording_date = video["recording_date"]

        processed_count += 1
        process_video(
            chamber="senate",
            committee=committee,
            recording_date=recording_date,
            filename=filename,
            download_args={"video_id": video["video_id"]}
        )
        #print(f"senate processed_count: {processed_count} | {filename}")
        if limit and processed_count >= limit:
            break

if __name__ == "__main__":
    # Choose which to run
    house_thread = threading.Thread(target=run_house, args=(2,))
    senate_thread = threading.Thread(target=run_senate, args=(2,))
    house_thread.start()
    senate_thread.start()
    house_thread.join()
    senate_thread.join()