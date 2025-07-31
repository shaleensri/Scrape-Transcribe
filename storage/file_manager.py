# storage/file_manager.py

import requests
import re
from pathlib import Path
import subprocess
from google.cloud import storage

def upload_file_to_gcs(bucket_name: str, local_path: Path, blob_path: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(str(local_path))
    print(f"[Uploaded] {local_path.name} → gs://{bucket_name}/{blob_path}")

def get_video_duration(url: str) -> float:
    """Returns the duration of a video in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def run_ffmpeg_with_progress(cmd, duration: float, label: str):
    """Run ffmpeg command and log progress at 20% intervals."""
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
    last_update = 0

    for line in process.stderr:
        if "time=" in line and duration > 0:
            match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                elapsed = hours * 3600 + minutes * 60 + seconds
                percent = int((elapsed / duration) * 100)

                if percent // 20 > last_update // 20:
                    print(f"[{label}] Download progress: {percent}%")
                    last_update = percent

    process.wait()
    if process.returncode == 0:
        print(f"[{label}] ✅ Download complete")
    else:
        print(f"[{label}] ❌ ffmpeg failed")


def download_video_with_progress(source_url: str, output_path: Path, label: str):
    """Common video download function with progress logging."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"[{label}] Video already exists: {output_path.name}")
        return output_path

    duration = get_video_duration(source_url)
    cmd = [
        "ffmpeg",
        "-y",
        "-i", source_url,
        "-c", "copy",
        str(output_path)
    ]

    run_ffmpeg_with_progress(cmd, duration, label)
    return output_path


def download_house_video_ffmpeg(url, destination):
    return download_video_with_progress(url, destination, label="House")


def download_senate_video_ffmpeg(video_id: str, output_dir: Path) -> Path:
    # Try both possible m3u8 paths
    patterns = [
        f"https://dlttx48mxf9m3.cloudfront.net/outputs/{video_id}/Default/HLS/out1080p.m3u8",
        f"https://dlttx48mxf9m3.cloudfront.net/outputs/{video_id}/Default/HLS/1080p.m3u8"
    ]

    m3u8_url = None
    for url in patterns:
        try:
            resp = requests.head(url, timeout=5)
            if resp.status_code == 200:
                m3u8_url = url
                break
        except requests.RequestException:
            continue

    if not m3u8_url:
        print(f"[Senate] ❌ Could not find a valid m3u8 for video {video_id}")
        return None

    output_path = output_dir / f"{video_id}.mp4"
    return download_video_with_progress(m3u8_url, output_path, label="Senate")

    """
        Downloads a Senate video via ffmpeg using the predictable 1080p HLS (.m3u8) structure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Construct m3u8 download URL
    patterns = [
        f"https://dlttx48mxf9m3.cloudfront.net/outputs/{video_id}/Default/HLS/out1080p.m3u8",
        f"https://dlttx48mxf9m3.cloudfront.net/outputs/{video_id}/Default/HLS/1080p.m3u8"
    ]

    m3u8_url = None
    for url in patterns:
        try:
            resp = requests.head(url, timeout=5)
            if resp.status_code == 200:
                m3u8_url = url
                break
        except requests.RequestException:
            continue
    
    if not m3u8_url:
        print(f" Could not find a valid m3u8 for video {video_id}")
        return None
    
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

