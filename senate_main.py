from pathlib import Path
from fetcher.senate_scraper import SenateScraper
from transcriber.whisper_transcriber import WhisperTranscriber
from storage.file_manager import download_senate_video_ffmpeg, upload_file_to_gcs
from storage.state_tracker import is_processed, mark_processed

BUCKET_NAME = "legislature-videos-shaleen"


def main():
    # Step 1: Scrape all Senate videos
    scraper = SenateScraper()
    videos = scraper.scrape(batch_size=30, max_pages=1)

    print(f" Found {len(videos)} Senate videos.\n")

    for idx, video in enumerate(videos[:5], start=1):
        print(f"{idx}. {video['title']} | Uploaded: {video['upload_date']} | ID: {video['video_id']}")

    # Step 2: Pick the first video for demo
    target_video = videos[0]
    video_id = target_video["video_id"]
    filename = target_video['title']
    recording_date = target_video["recording_date"]  # already formatted as YYYY-MM-DD
    committee = target_video["title"].rsplit(" ", 1)[0].strip()
    cloud_dir = f"senate/{committee}/{recording_date}"

    # Skip if already processed
    if is_processed("senate", committee, recording_date, filename):
        print(f"[Skip] Already processed: {committee} | {recording_date} | {filename}")
        return

    # Step 3: Download video using ffmpeg
    output_dir = Path("downloads/senate")
    local_path = download_senate_video_ffmpeg(video_id, output_dir)
    print(f"\n Video downloaded to: {local_path}")

    # Step 4: Transcribe
    print("\n Transcribing...")
    transcriber = WhisperTranscriber()
    transcript_path = transcriber.transcribe(local_path)

    # Step 5: Show transcript preview
    print("\n Transcript Preview:\n")
    preview = Path(transcript_path).read_text()
    print(preview[:1000] + "..." if len(preview) > 1000 else preview)

    # Step 6: Upload video and transcript
    upload_file_to_gcs(BUCKET_NAME, local_path, f"{cloud_dir}/{local_path.name}")
    upload_file_to_gcs(BUCKET_NAME, transcript_path, f"{cloud_dir}/{transcript_path.name}")

    # Step 7: Mark as processed
    mark_processed("senate", committee, recording_date, filename)

    # Step 8: Delete local files
    try:
        local_path.unlink()
        transcript_path.unlink()
        print(f"[Cleanup] Deleted local files: {local_path.name}, {transcript_path.name}")
    except Exception as e:
        print(f"[Warning] Could not delete files: {e}")


if __name__ == "__main__":
    main()
