import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from scrapers.base import BaseScraper
from utils.text import extract_bedrooms

class TunisieAnnonceScraper(BaseScraper):

    def fetch(self):
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(self.url, headers=headers, timeout=20)
        r.encoding = "ISO-8859-1"
        self.soup = BeautifulSoup(r.text, "html.parser")

    def parse(self):
        self.raw = {}

        labels = self.soup.select("td.da_label_field")
        for label in labels:
            key = label.text.strip().lower()
            value_td = label.find_next_sibling("td", class_="da_field_text")
            if not value_td:
                continue

            value = value_td.get_text(" ", strip=True)

            if "surface" in key:
                m = re.search(r"\d+", value)
                self.raw["surface_area"] = int(m.group()) if m else None

            elif "prix" in key:
                m = re.sub(r"[^\d]", "", value)
                self.raw["price"] = int(m) if m else None

            elif "texte" in key:
                self.raw["description"] = value

        # location
        self.raw["region"] = self.raw["city"] = self.raw["locality"] = "Missing"
        for a in self.soup.select("td.da_field_text a[href*='rech_cod_']"):
            qs = parse_qs(urlparse(a["href"]).query)
            if "rech_cod_reg" in qs:
                self.raw["region"] = a.text.strip()
            if "rech_cod_vil" in qs:
                self.raw["city"] = a.text.strip()
            if "rech_cod_loc" in qs:
                self.raw["locality"] = a.text.strip()

        # photos
        self.raw["photo_count"] = len(self.soup.select("img[id^='PhotoMax_']"))

        # property type
        type_td = self.soup.select_one("td.da_field_text a[href*='rech_cod_type']")
        self.raw["property_type"] = type_td.text.strip() if type_td else "Unknown"

    def normalize(self):
        desc = (self.raw.get("description") or "").lower()

        return {
            "surface_area": self.raw.get("surface_area"),
            "bedrooms_filled": extract_bedrooms(desc),
            "photo_count": self.raw.get("photo_count", 0),
            "price": self.raw.get("price"),

            "has_air_conditioning": "clim" in desc,
            "has_heating": "chauffage" in desc,
            "has_elevator": "ascenseur" in desc,
            "has_pool": "piscine" in desc,
            "has_garage": "garage" in desc,
            "has_garden": "jardin" in desc,

            "region": self.raw.get("region", "Missing"),
            "city": self.raw.get("city", "Missing"),
            "locality": self.raw.get("locality", "Missing"),

            "property_type": self.raw.get("property_type", "Unknown"),
            "transaction_category": "RENT" if (self.raw.get("price") or 0) < 20000 else "SALE",
            "description": self.raw.get("description", "")
        }
