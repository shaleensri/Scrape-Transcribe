# storage/file_manager.py

import requests
from pathlib import Path
import subprocess

def download_file(url, destination):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

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
        print(f" Download complete: {output_path}")
    else:
        print(f" ffmpeg failed:\n{result.stderr}")

    return output_path
