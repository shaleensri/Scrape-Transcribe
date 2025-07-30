# main.py
# main.py

from fetcher.senate_scraper import SenateScraper
from transcriber.whisper_transcriber import WhisperTranscriber
from storage.state_tracker import is_processed, mark_processed
from storage.file_manager import download_house_video, download_senate_video_ffmpeg, upload_file_to_gcs
from fetcher.house_scraper_static import HouseScraperStatic
from urllib.parse import urlparse, parse_qs


from pathlib import Path
BUCKET_NAME = "legislature-videos-shaleen"

def get_filename_from_url(url):
    query = parse_qs(urlparse(url).query)
    return query.get("video", ["video.mp4"])[0]

def main():
    # Step 1: Scrape all Senate videos
    house_scraper = HouseScraperStatic()
    house_videos = house_scraper.scrape()
    #senate_scraper = SenateScraper()
    #videos = senate_scraper.scrape(batch_size=30, max_pages=1)

    print(f" Found {len(house_videos)} House videos.\n")
    #print(f" Found {len(videos)} Senate videos.\n")

    for idx, video in enumerate(house_videos[:5], start=1):
        print(f"{idx}. {video['committee']} | Date: {video['date']} | URL: {video['url']}")
    
    target_video = house_videos[0]
    filename = get_filename_from_url(target_video["url"])
    committee = target_video["committee"]
    recording_date = target_video["date"] 
    # Might need to normalize format to YYYY-MM-DD
    cloud_dir = f"house/{committee}/{recording_date}"
    
    if is_processed("house", committee, recording_date, filename):
        print(f"[Skip] Already processed: {committee} | {recording_date} | {filename}")
        return
    
    output_dir = Path("downloads/house")
    output_dir.mkdir(parents=True, exist_ok=True)
    local_path = output_dir / filename

    video_id = get_filename_from_url(target_video["url"])
    real_url = f"https://www.house.mi.gov/ArchiveVideoFiles/{video_id}"

    print(f"\n Downloading from {real_url}")
    download_house_video(real_url, local_path)
    print(" Download complete.")

    print("\n Transcribing...")
    transcriber = WhisperTranscriber()
    transcript_path = transcriber.transcribe(local_path)

    # Step 6: Show transcript preview
    print("\n Transcript Preview:\n")
    preview = Path(transcript_path).read_text()
    print(preview[:1000] + "..." if len(preview) > 1000 else preview)

    
    upload_file_to_gcs(
        bucket_name=BUCKET_NAME,
        local_path=local_path,
        blob_path=f"{cloud_dir}/{local_path.name}"
    )

    upload_file_to_gcs(
        bucket_name=BUCKET_NAME,
        local_path=transcript_path,
        blob_path=f"{cloud_dir}/{transcript_path.name}"
    )

    mark_processed("house", committee, recording_date, local_path.name)

    # Delete local files after upload
    try:
        local_path.unlink()
        transcript_path.unlink()
        print(f"[Cleanup] Deleted local files: {local_path.name}, {transcript_path.name}")
    except Exception as e:
        print(f"[Warning] Could not delete files: {e}")


    # Step 2: Print sample list
    #for idx, video in enumerate(videos[:5], start=1):
        #print(f"{idx}. {video['title']} | Uploaded: {video['upload_date']} | ID: {video['video_id']}")

    # Step 3: Select one video to download and transcribe
    """
    target_video = videos[0]  # You can change this to index or filter logic
    video_id = target_video["video_id"]
    output_dir = Path("downloads/senate")
    filename = target_video["title"]  # e.g., "Senate Session 25-07-17"
    recording_date = target_video["recording_date"]  # already formatted as YYYY-MM-DD
    committee = filename.rsplit(" ", 1)[0].strip()  #  committee (everything before the last space-date pattern)
    cloud_dir = f"senate/{committee}/{recording_date}"

    # Step 4: Download video using ffmpeg
    local_path = download_senate_video_ffmpeg(video_id, output_dir)
    print(f"\n Video downloaded to: {local_path}")

    # Step 5: Transcribe
    transcriber = WhisperTranscriber()
    transcript_path = transcriber.transcribe(local_path)

    # Step 6: Show transcript preview
    print("\n Transcript Preview:\n")
    preview = Path(transcript_path).read_text()
    print(preview[:1000] + "..." if len(preview) > 1000 else preview)

    upload_file_to_gcs(
    bucket_name=BUCKET_NAME,
    local_path=local_path,
    blob_path=f"{cloud_dir}/{local_path.name}"
    )

    upload_file_to_gcs(
        bucket_name=BUCKET_NAME,
        local_path=transcript_path,
        blob_path=f"{cloud_dir}/{transcript_path.name}"
    )
    """
if __name__ == "__main__":
    main()


"""
from fetcher.house_scraper_static import HouseScraperStatic
from storage.file_manager import download_file
from transcriber.whisper_transcriber import WhisperTranscriber
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import os

def get_filename_from_url(url):
    query = parse_qs(urlparse(url).query)
    return query.get("video", ["video.mp4"])[0]

def main():
    # STEP 1: Scrape metadata
    scraper = HouseScraperStatic()
    videos = scraper.scrape()

    if not videos:
        print(" No videos found.")
        return

    # STEP 2: Pick first video
    # Pick first video
    video = videos[0]
    print(f" Selected video:\n{video}")

    # Clean file name from URL
    filename = get_filename_from_url(video["url"])
    real_url = f"https://www.house.mi.gov/ArchiveVideoFiles/{filename}"
    local_path = Path("downloads") / filename

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    if not local_path.exists():
        print(f"\n Downloading from {real_url}")
        download_file(real_url, local_path)
        print("Download complete.")
    else:
        print(f"\n Already downloaded: {local_path}")


    print("\n Transcribing...")
    transcriber = WhisperTranscriber(model_size="base", compute_type="float32")
    transcript = transcriber.transcribe(local_path)

    # Output transcript preview
    print("\n Transcript (first 500 characters):\n")
    print(transcript[:500])


if __name__ == "__main__":
    main()


"""
"""



def main():
    video_path = Path("test.mp4")  
    transcriber = WhisperTranscriber(model_size="base") 
    transcript = transcriber.transcribe(video_path)

    print("\n--- TRANSCRIPT ---\n")
    print(transcript)

if __name__ == "__main__":
    main()
"""