# fetcher/senate_scraper.py

from .base_scraper import BaseScraper
import requests
from datetime import datetime
import re

class SenateScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://tf4pr3wftk.execute-api.us-west-2.amazonaws.com/default/api/all")
        self.api_payload = {
            "_id": "61b3adc8124d7d000891ca5c",
            "page": 1,
            "results": 30
        }

    def fetch_data(self, page=1, results=30):
        payload = {
            "_id": "61b3adc8124d7d000891ca5c",
            "page": page,
            "results": results
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(self.base_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("allFiles", [])

    def parse_recording_date(self, filename: str) -> str:
        """
        Extracts 'YY-MM-DD' from filename and returns 'YYYY-MM-DD'
        """
        match = re.search(r"(\d{2})-(\d{2})-(\d{2})", filename)
        if match:
            yy, mm, dd = match.groups()
            try:
                return datetime.strptime(f"{yy}-{mm}-{dd}", "%y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                pass
        return "Unknown"
    
    def scrape(self, max_pages, batch_size=30 ):
        all_results = []
        page = 1

        while True:
            print(f"Fetching page {page}...")

            payload = {
                "_id": "61b3adc8124d7d000891ca5c",
                "page": page,
                "results": batch_size
            }

            try:
                response = requests.post(self.base_url, json=payload, headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                })
                response.raise_for_status()
                data = response.json().get("allFiles", [])
            except Exception as e:
                print(f"Failed on page {page}: {e}")
                break

            if not data:
                print("All pages fetched.")
                break

            for item in data:
                video_id = item.get("_id")
                metadata = item.get("metadata", {})
                filename = metadata.get("filename", "Untitled")
                upload_date_raw = item.get("date", "")

                recording_date = self.parse_recording_date(filename)
                try:
                    upload_date = datetime.fromisoformat(upload_date_raw.rstrip("Z")).strftime("%Y-%m-%d")
                except Exception:
                    upload_date = upload_date_raw

                all_results.append({
                    "video_id": video_id,
                    "title": filename,
                    "recording_date": recording_date,
                    "upload_date": upload_date
                })
            if page >= max_pages:
                print("Reached max page limit for test.")
                break
            page += 1


        return all_results
"""
    def scrape(self) -> list:
        data = self.fetch_data()
        results = []

        for item in data:
            video_id = item.get("_id")
            metadata = item.get("metadata", {})
            filename = metadata.get("filename", "Untitled")
            upload_date_raw = item.get("date", "")

            # Extract dates
            recording_date = self.parse_recording_date(filename)
            try:
                upload_date = datetime.fromisoformat(upload_date_raw.rstrip("Z")).strftime("%Y-%m-%d")
            except Exception:
                upload_date = upload_date_raw

            results.append({
                "video_id": video_id,
                "title": filename,
                "recording_date": recording_date,
                "upload_date": upload_date
            })

        return results
"""

if __name__ == "__main__":
    scraper = SenateScraper()
    videos = scraper.scrape()
    for video in videos[:5]:  # Show sample
        print(video)
