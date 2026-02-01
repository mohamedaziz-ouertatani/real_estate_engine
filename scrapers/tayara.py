import re
from playwright.sync_api import sync_playwright
from scrapers.base import BaseScraper
from utils.text import extract_bedrooms
from bs4 import BeautifulSoup

class TayaraScraper(BaseScraper):
    def fetch(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0")
            page.goto(self.url, timeout=60000)
            page.wait_for_selector("data[value]", timeout=10000)
            
            # Extract location before closing browser
            # Tayara usually has a location span or link
            loc_element = page.query_selector('span[class*="location"]')
            self.raw_location = loc_element.inner_text() if loc_element else ""
            
            self.soup = BeautifulSoup(page.content(), "html.parser")
            browser.close()

    def parse(self):
        self.raw = {}
        # Price
        price_tag = self.soup.select_one("data[value]")
        self.raw["price"] = int(price_tag["value"]) if price_tag else 0
        
        # Text fields
        title_tag = self.soup.select_one("h1")
        self.raw["title"] = title_tag.get_text().strip() if title_tag else ""
        desc_tag = self.soup.select_one("p.whitespace-pre-line")
        self.raw["description"] = desc_tag.get_text(" ", strip=True) if desc_tag else ""

        # Location extraction from scraped text
        loc_parts = self.raw_location.split(",")
        self.raw["city"] = loc_parts[0].strip() if len(loc_parts) > 0 else "Unknown"
        self.raw["locality"] = loc_parts[1].strip() if len(loc_parts) > 1 else self.raw["city"]

        # Surface/Rooms
        criteria_items = self.soup.select("li.col-span-6")
        for item in criteria_items:
            text = item.get_text().lower()
            val = re.search(r"(\d+)", text)
            if not val: continue
            if "superficie" in text: self.raw["surface_area"] = int(val.group(1))
            elif "chambres" in text: self.raw["bedrooms"] = int(val.group(1))

    def normalize(self):
        combined = f"{self.raw.get('title')} {self.raw.get('description')}".lower()
        return {
            "surface_area": self.raw.get("surface_area", 100),
            "bedrooms_filled": self.raw.get("bedrooms") or extract_bedrooms(combined),
            "price": self.raw.get("price"),
            "city": self.raw.get("city"),
            "locality": self.raw.get("locality"),
            "property_type": "Terrain" if "terrain" in combined else "Appartement",
            "transaction_category": "SALE", # Typically sale unless specified
            "description": combined
        }