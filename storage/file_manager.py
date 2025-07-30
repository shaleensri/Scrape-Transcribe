# storage/file_manager.py

import requests
from pathlib import Path
import subprocess
from google.cloud import storage

def upload_file_to_gcs(bucket_name: str, local_path: Path, blob_path: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(str(local_path))
    print(f"[Uploaded] {local_path.name} → gs://{bucket_name}/{blob_path}")

def download_house_video(url, destination):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


"""
def download_senate_video_ffmpeg_to_gcs(video_id: str, bucket_name: str) -> str:
    
    Downloads a Senate video via ffmpeg and uploads directly to GCS.
    Returns the cloud path.
    
    # Construct URL and destination path
    m3u8_url = f"https://dlttx48mxf9m3.cloudfront.net/outputs/{video_id}/Default/HLS/1080p.m3u8"
    blob_path = f"senate/{video_id}.mp4"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    if blob.exists():
        print(f"[Skip] Video already exists in GCS: gs://{bucket_name}/{blob_path}")
        return f"gs://{bucket_name}/{blob_path}"

    print(f"[Download → GCS] {video_id}")

    # Run ffmpeg and capture stdout
    cmd = [
        "ffmpeg",
        "-i", m3u8_url,
        "-c", "copy",
        "-f", "mp4",   # ensure proper stream format
        "pipe:1"       # output to stdout
    ]

    # Use subprocess to stream stdout and write to GCS
    with blob.open("wb") as gcs_file:
        process = subprocess.Popen(cmd, stdout=gcs_file, stderr=subprocess.PIPE, bufsize=10**8)
        _, stderr = process.communicate()

    if process.returncode == 0:
        print(f"[Uploaded] gs://{bucket_name}/{blob_path}")
        return f"gs://{bucket_name}/{blob_path}"
    else:
        print(f"[ffmpeg ERROR] {stderr.decode()}")
        return None

"""


def download_senate_video_ffmpeg(video_id: str, output_dir: Path) -> Path:
    """
        Downloads a Senate video via ffmpeg using the predictable 1080p HLS (.m3u8) structure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Construct m3u8 download URL
    m3u8_url = f"https://dlttx48mxf9m3.cloudfront.net/outputs/{video_id}/Default/HLS/1080p.m3u8"
    output_path = output_dir / f"{video_id}.mp4"

    if output_path.exists():
        print(f"Video already exists: {output_path.name}")
        return output_path

    print(f" Downloading video: {video_id}")
    cmd = [
        "ffmpeg",
        "-i", m3u8_url,
        "-c", "copy",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Download complete: {output_path}")
    else:
        print(f"ffmpeg failed:\n{result.stderr}")

    return output_path