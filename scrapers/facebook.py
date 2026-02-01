import re
import time
import spacy
from playwright.sync_api import sync_playwright
from scrapers.base import BaseScraper
from utils.text import extract_bedrooms

class FacebookMarketplaceScraper(BaseScraper):

    def __init__(self, url):
        super().__init__(url)
        try:
            self.nlp = spacy.load("fr_core_news_sm")
        except:
            self.nlp = None

    def fetch(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            self.page = context.new_page()
            try:
                self.page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                self.page.wait_for_selector("h1", timeout=15000)
                self.full_text = self.page.inner_text("body")
            finally:
                browser.close()

    def parse(self):
        # Parsing already handled in fetch()
        pass

    def normalize(self) -> dict:
        text = self.full_text.lower()
        nlp_data = self.nlp_extract(text)

        rooms = extract_bedrooms(text)

        price_match = re.search(r"(\d[\d\s]+)\s*dt", text)
        price = int(price_match.group(1).replace(" ", "")) if price_match else None

        return {
            "price": price,
            "surface_area": nlp_data["surface"] or self._regex_surface(text),
            "bedrooms_filled": rooms,
            "photo_count": 0,

            "has_air_conditioning": "clim" in text,
            "has_heating": "chauffage" in text,
            "has_elevator": "ascenseur" in text,
            "has_pool": "piscine" in text,
            "has_garage": "garage" in text,
            "has_garden": "jardin" in text,

            "region": "Missing",
            "city": "Tunis",
            "locality": "Missing",

            "property_type": "Villa" if "villa" in text else "Appartement",
            "transaction_category": "RENT" if price and price < 20000 else "SALE",
            "description": text
        }
