# fetcher/house_scraper_static.py

from bs4 import BeautifulSoup
import requests
from .base_scraper import BaseScraper

class HouseScraperStatic(BaseScraper):
    def __init__(self):
        super().__init__("https://www.house.mi.gov/VideoArchive")

    def scrape(self) -> list:
        soup = self.fetch_page()
        results = []

        sections = soup.select("li.page-search-container")

        for section in sections:
            header = section.select_one("div.text-clickable strong")
            committee = header.get_text(strip=True).split("|")[0].strip() if header else "Unknown Committee"

            video_links = section.select("div.page-search-object a")

            for link in video_links:
                href = link.get("href", "")
                if not href.endswith(".mp4"):
                    continue

                full_url = f"https://www.house.mi.gov{href}"
                date_text = link.get_text(strip=True)

                results.append({
                    "committee": committee,
                    "date": date_text,
                    "url": full_url
                })

        return results


if __name__ == "__main__":
    scraper = HouseScraperStatic()
    videos = scraper.scrape()

    print(f"Found {len(videos)} videos:")
    for video in videos:
        print(video)
