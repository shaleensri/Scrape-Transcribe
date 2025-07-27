# main.py

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




def main():
    video_path = Path("test.mp4")  
    transcriber = WhisperTranscriber(model_size="base") 
    transcript = transcriber.transcribe(video_path)

    print("\n--- TRANSCRIPT ---\n")
    print(transcript)

if __name__ == "__main__":
    main()
"""