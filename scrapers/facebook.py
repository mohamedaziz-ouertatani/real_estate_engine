import re
import time
from playwright.sync_api import sync_playwright
from scrapers.base import BaseScraper
from utils.text import extract_bedrooms
from utils.nlp import extract_entities_from_text
from utils.amenities import detect_amenities

class FacebookMarketplaceScraper(BaseScraper):
    def fetch(self):
        """Récupère le contenu et force l'expansion avant de nettoyer le texte parasite."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                page.goto(self.url, wait_until="networkidle", timeout=60000)
                page.wait_for_selector("div[role='main']", timeout=20000)

                # --- OPTIMIZED EXPANSION LOGIC ---
                # Combined selector with OR logic for better performance
                # Reduced sleep to improve speed; click force=True handles most loading cases
                expand_selector = "div[role='button'] >> text=/Voir plus|See more|عرض المزيد/"
                
                try:
                    buttons = page.locator(expand_selector)
                    for i in range(buttons.count()):
                        btn = buttons.nth(i)
                        if btn.is_visible():
                            btn.scroll_into_view_if_needed()
                            btn.click(force=True)
                            time.sleep(0.7)  # Balanced: faster than 1s, safer than 0.5s
                except Exception:
                    pass

                raw_text = page.locator("div[role='main']").inner_text()
                
                # --- OPTIMIZED CLEANING LOGIC (STOPPERS) ---
                # Use single regex split instead of multiple loops
                stoppers = [
                    "Sélection du jour", 
                    "Suggested for you",
                    "Annonces suggérées",
                    "Annonce récente",
                    "Signalez cette annonce",
                    "Envoyer un message"
                ]
                
                stoppers_pattern = re.compile('|'.join(re.escape(s) for s in stoppers))
                clean_text = stoppers_pattern.split(raw_text)[0]
                clean_text = re.sub(r"Voir plus\s*$", "", clean_text, flags=re.IGNORECASE).strip()
                self.text = clean_text
                
            except Exception as e:
                print(f"❌ Facebook fetch error: {e}")
                self.text = ""
            finally:
                browser.close()

    def parse(self):
        """Extraction des données de base depuis le texte nettoyé."""
        text = self.text or ""
        
        # Extraction du prix (ex: 1 400 TND)
        price_match = re.search(r"(\d[\d\s,.]*)\s?(DT|TND|dt|tnd|dinars?)", text, re.IGNORECASE)
        price = 0
        if price_match:
            price_str = re.sub(r"[^\d]", "", price_match.group(1))
            price = int(price_str) if price_str else 0

        self.raw = {
            "description": text,
            "price": price,
            "title": text.split('\n')[0] if text else "Annonce Facebook"
        }

    def normalize(self) -> dict:
        """
        Normalisation finale pour l'IA. 
        Implémentation obligatoire de la méthode abstraite de BaseScraper.
        """
        text = self.raw.get("description", "")
        text_lower = text.lower()
        
        # Extraction via NLP utilitaire
        nlp_data = {}
        try:
            nlp_data = extract_entities_from_text(text)
        except Exception:
            nlp_data = {}
        
        # Surface Area
        surface = nlp_data.get("surface_area")
        if not surface:
            match = re.search(r"(\d+)\s?m(?:\s|²|2|s\b)", text_lower)
            if match:
                surface = int(match.group(1))
        
        # Bedrooms
        s_plus = re.search(r"s\s?\+\s?(\d)", text_lower)
        bedrooms = int(s_plus.group(1)) if s_plus else (extract_bedrooms(text) or 1)

        # Localisation
        city = nlp_data.get("city") or "Tunis"
        locality = nlp_data.get("locality") or "Inconnu"
        if "menzah" in text_lower:
            # Correction spécifique pour les quartiers Menzah
            if any(x in text_lower for x in ["9c", "9 c"]):
                locality = "Menzah 9c"
            else:
                locality = "El Menzah"

        # Use centralized amenity detection
        amenities = detect_amenities(text)

        return {
            "surface_area": surface or 90,
            "bedrooms_filled": bedrooms,
            "price": self.raw.get("price", 0),
            "description": text,
            "city": city,
            "locality": locality,
            "property_type": "Residential",
            "transaction_category": "RENT" if self.raw.get("price", 0) < 20000 else "SALE",
            **amenities  # Merge amenities dict
        }