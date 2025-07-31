# fetcher/base_scraper.py

from abc import ABC, abstractmethod
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# bs because it is straightforward scraping. we are not doing anything too complex

class BaseScraper(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url

    # will remove -> later.
    def fetch_page(self, url: str = None) -> BeautifulSoup:
        url = url or self.base_url
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Failed to fetch {url}: {e}")

        return BeautifulSoup(response.text, "html.parser")

    @abstractmethod
    def scrape(self) -> list:
        """Return a list of dicts with 'committee', 'date', and 'url'."""
        pass
