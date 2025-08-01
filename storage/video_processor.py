from pathlib import Path
from transcriber.whisper_transcriber import WhisperTranscriber
from storage.file_manager import download_house_video_ffmpeg, download_senate_video_ffmpeg, upload_file_to_gcs
from storage.state_tracker import is_processed, mark_processed

BUCKET_NAME = "legislature-videos-shaleen"

def process_video(chamber, committee, recording_date, filename, download_args):
    """Generic video processing: download, transcribe and upload to cloud
    @param chamber: house/senate
    @param committee: Committee name
    @param recording_date: Date of the recording
    @param filename: Name of the video file
    @param download_args: real_url or video_id based on chamber
    """

    if is_processed(chamber, committee, recording_date, filename):
        print(f"[{chamber.capitalize()}]\
              [Skip] Already processed: {committee} | {recording_date} | {filename}")
        return

    output_dir = Path(f"downloads/{chamber}")
    output_dir.mkdir(parents=True, exist_ok=True)
    local_path = output_dir / filename

    # Download based on chamber
    if chamber == "house":
        real_url = download_args["real_url"]
        print(f"\nHouse: Downloading from {real_url}")
        download_house_video_ffmpeg(real_url, local_path)
    elif chamber == "senate":
        video_id = download_args["video_id"]
        print(f"\nSenate: Downloading video ID: {video_id}")
        local_path = download_senate_video_ffmpeg(video_id, output_dir)

    print(f"{chamber.capitalize()}: Download complete.")

    # Transcribe
    print(f"\n{chamber.capitalize()}: transcribing...")
    transcriber = WhisperTranscriber()
    transcript_path = transcriber.transcribe(local_path)
    print(f"\n{chamber.capitalize()}: Transcript Done:\n")

    # Upload
    print(f"\nUploading {chamber} video and transcript to GCS...")
    cloud_dir = f"{chamber}/{committee}/{recording_date}"
    upload_file_to_gcs(BUCKET_NAME, local_path, f"{cloud_dir}/{local_path.name}")
    upload_file_to_gcs(BUCKET_NAME, transcript_path, f"{cloud_dir}/{transcript_path.name}")
    print(f"{chamber.capitalize()}: Upload complete.")

    # Mark as processed
    mark_processed(chamber, committee, recording_date, filename)

    # Cleanup local files
    try:
        local_path.unlink()
        transcript_path.unlink()
        print(f"[{chamber.capitalize()}][Cleanup] Deleted local files: {local_path.name}, {transcript_path.name}")
    except Exception as e:
        print(f"[{chamber.capitalize()}][Warning] Could not delete files: {e}")



"""
 ======================= No Cloud Upload Approach =======================
 - Tried this approach to avoid using cloud storage but eventually reverted to cloud upload.
 - Can discuss during interview about its pros/cons.
 - Commented out on purpose

def process_video(chamber, committee, recording_date, filename, download_args):
    
    output_dir = Path(f"downloads/{chamber}")
    output_dir.mkdir(parents=True, exist_ok=True)
    if chamber == "senate":
        if not filename.endswith(".mp4"):
            filename += ".mp4"

    local_path = output_dir / filename

    # Skip if file already exists
    if local_path.exists():
        print(f"[Skip] Already downloaded: {local_path.name}")
        return
    
    # Download based on chamber
    if chamber == "house":
        real_url = download_args["real_url"]
        print(f"\nHouse: Downloading from {real_url}")
        download_house_video_ffmpeg(real_url, local_path)
    elif chamber == "senate":
        video_id = download_args["video_id"]
        print(f"\nSenate: Downloading video ID: {video_id}")
        local_path = download_senate_video_ffmpeg(video_id, output_dir)

    print(f"{chamber.capitalize()}: Download complete.")

    # Transcribe
    print(f"\n{chamber.capitalize()}: Transcribing...")
    transcriber = WhisperTranscriber()
    transcript_path = transcriber.transcribe(local_path)

    # Show transcript preview
    preview = Path(transcript_path).read_text()
    print("\nTranscript Preview:\n")
    print(preview[:1000] + "..." if len(preview) > 1000 else preview)
    print(f"\n{chamber.capitalize()}: Transcription complete.")

    print(f"[Done] {chamber.capitalize()} video processed locally.")

"""