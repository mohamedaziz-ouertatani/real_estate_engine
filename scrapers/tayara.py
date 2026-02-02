import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from utils.text import extract_bedrooms
from utils.nlp import extract_entities_from_text

class TayaraScraper(BaseScraper):
    def fetch(self):
        """Fetch content with specific wait for Tayara's dynamic criteria."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()
            
            try:
                page.goto(self.url, timeout=60000, wait_until="networkidle")
                # Wait specifically for the description or criteria to load
                page.wait_for_selector("p.whitespace-pre-line", timeout=15000)
                
                # Capture location from the breadcrumbs or header
                loc_el = page.query_selector('span[class*="location"], svg + span')
                self.raw_location = loc_el.inner_text() if loc_el else ""
                
                self.soup = BeautifulSoup(page.content(), "html.parser")
            except Exception as e:
                print(f"❌ Tayara fetch error: {e}")
                self.soup = None
            finally:
                browser.close()

    def parse(self):
        """Refined parsing to avoid '5000 bedrooms' logic errors."""
        self.raw = {
            "title": "", "description": "", "price": 0,
            "surface_area": None, "bedrooms": None,
            "city": "Unknown", "locality": "Unknown"
        }
        if not self.soup: return

        # 1. Price extraction (Priority: Structured Data)
        price_tag = self.soup.select_one("data[value]")
        if price_tag and price_tag.has_attr("value"):
            try:
                self.raw["price"] = int(float(price_tag["value"]))
            except: pass

        # 2. Description & Title
        title_tag = self.soup.find("h1")
        if title_tag: self.raw["title"] = title_tag.get_text(strip=True)

        desc_tag = self.soup.select_one("p.whitespace-pre-line")
        # FIX: Ensure description isn't just "Moins" or empty
        if desc_tag: 
            self.raw["description"] = desc_tag.get_text(" ", strip=True).replace("Moins", "").strip()

        # 3. Location Parsing (El Menzah 9, Tunis)
        if self.raw_location:
            parts = [p.strip() for p in self.raw_location.split(",") if p.strip()]
            if len(parts) >= 2:
                self.raw["city"], self.raw["locality"] = parts[-1], parts[0]

        # 4. Criteria Parsing (Surface & Bedrooms) - REFINED
        for li in self.soup.select("li"):
            text = li.get_text().lower()
            match = re.search(r"(\d+)", text)
            if not match: continue
            val = int(match.group(1))

            # BUG FIX: Ignore values that match the price to prevent "5000 bedrooms"
            if val == self.raw["price"]: continue

            if "superficie" in text or "m²" in text:
                self.raw["surface_area"] = val
            elif "chambre" in text or "pièce" in text:
                # Limit reasonable bedroom counts for residential logic
                self.raw["bedrooms"] = val if val < 20 else 2

    def normalize(self) -> dict:
        """Enhanced normalization for professional/commercial usage."""
        data = self.raw
        desc_blob = f"{data['title']} {data['description']}".lower()
        nlp = extract_entities_from_text(desc_blob)
        
        price = data.get("price") or 0
        
        # Determine property type: Detect "usage professionnel" or "bureau"
        is_professional = any(x in desc_blob for x in ["professionnel", "bureau", "siège", "cabinet"])
        prop_type = "Commercial" if is_professional else "Residential"
        if "terrain" in desc_blob and "villa" not in desc_blob:
            prop_type = "Land"

        # Amenity detection (Fixing the ❌ icons)
        has_garage = any(x in desc_blob for x in ["garage", "parking", "stationnement"])
        has_garden = any(x in desc_blob for x in ["jardin", "espace vert"])
        has_ac = any(x in desc_blob for x in ["clim", "climatisation"])
        has_heat = any(x in desc_blob for x in ["chauffage"])

        return {
            "surface_area": data.get("surface_area") or nlp.get("surface_area") or 0,
            "bedrooms_filled": data.get("bedrooms") or 2,
            "price": price,
            "city": data.get("city") if data.get("city") != "Unknown" else (nlp.get("city") or "Tunis"),
            "locality": data.get("locality") if data.get("locality") != "Unknown" else (nlp.get("locality") or "Unknown"),
            "property_type": prop_type,
            "transaction_category": "RENT" if price < 20000 else "SALE",
            "description": data["description"],
            # Explicit amenity mapping
            "has_air_conditioning": has_ac,
            "has_heating": has_heat,
            "has_elevator": "ascenseur" in desc_blob,
            "has_pool": "piscine" in desc_blob,
            "has_garage": has_garage,
            "has_garden": has_garden
        }