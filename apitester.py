import requests
from datetime import datetime
import re

def parse_recording_date(filename: str) -> str:
    """
    Extracts 'YY-MM-DD' from filename and converts to 'YYYY-MM-DD'
    """
    match = re.search(r"(\d{2})-(\d{2})-(\d{2})", filename)
    if match:
        yy, mm, dd = match.groups()
        try:
            return datetime.strptime(f"{yy}-{mm}-{dd}", "%y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            pass
    return "Unknown"

def fetch_senate_videos_all():
    url = "https://tf4pr3wftk.execute-api.us-west-2.amazonaws.com/default/api/all"
    payload = {
        "_id": "61b3adc8124d7d000891ca5c",  # misenate
        "page": 1,
        "results": 30                     # try 50 or 100 later
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json().get("allFiles", [])

    results = []
    for item in data:
        _id = item.get("_id")
        upload_date_raw = item.get("date", "")
        metadata = item.get("metadata", {})
        title = metadata.get("filename", "Untitled")

        # Parse dates
        recording_date = parse_recording_date(title)
        try:
            upload_date = datetime.fromisoformat(upload_date_raw.rstrip("Z")).strftime("%Y-%m-%d")
        except Exception:
            upload_date = upload_date_raw

        video_url = f"https://cloud.castus.tv/vod/misenate/video/{_id}?id={_id}&page=HOME"

        results.append({
            "title": title,
            "recording_date": recording_date,
            "upload_date": upload_date,
            "url": video_url
        })

    return results


if __name__ == "__main__":
    videos = fetch_senate_videos_all()
    for video in videos:
        print(video)
