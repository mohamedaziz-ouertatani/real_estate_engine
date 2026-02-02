import re
import time
from playwright.sync_api import sync_playwright
from scrapers.base import BaseScraper
from utils.text import extract_bedrooms
from utils.nlp import extract_entities_from_text

class FacebookMarketplaceScraper(BaseScraper):
    def fetch(self):
        """Récupère le contenu complet en forçant l'expansion du bouton 'Voir plus'."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/119.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()

            try:
                page.goto(self.url, wait_until="networkidle", timeout=60000)
                page.wait_for_selector("h1", timeout=15000)

                # --- FORCE L'EXPANSION DU TEXTE ---
                # On cherche le bouton par texte (français, anglais, arabe)
                selectors = [
                    "text=Voir plus", 
                    "text=See more", 
                    "text=عرض المزيد"
                ]
                
                for selector in selectors:
                    try:
                        button = page.locator(selector).first
                        if button.is_visible():
                            button.click()
                            # Attendre que le texte "Voir plus" disparaisse ou que le texte s'allonge
                            page.wait_for_timeout(1000) 
                    except:
                        continue

                # Extraction du bloc principal après expansion
                main_text = page.locator("div[role='main']").inner_text()
                self.text = (
                    main_text
                    .replace("\xa0", " ")
                    .replace("\u202f", " ")
                )
            except Exception as e:
                print(f"❌ Facebook fetch error: {e}")
                self.text = ""
            finally:
                browser.close()

    def parse(self):
        """Extraction de la description, du prix et de la surface."""
        raw_text = self.text or ""

        # Extraction de la description entre les balises de structure FB
        desc_match = re.search(
            r"(?:Description|Détails|تفاصيل)\n?(.*?)(?=\nSignalez cette annonce|\nEnvoyer un message|$)",
            raw_text,
            re.DOTALL | re.IGNORECASE
        )

        if desc_match and len(desc_match.group(1).strip()) > 50:
            description = desc_match.group(1).strip()
        else:
            # Fallback si le regex échoue : on prend les lignes significatives
            lines = raw_text.split("\n")
            description = "\n".join(lines[5:80]) if len(lines) > 5 else raw_text[:4000]

        # Nettoyage final pour supprimer le résidu "Voir plus" s'il existe encore par erreur
        description = description.replace("Voir plus", "").replace("See more", "").strip()

        # ---------- EXTRACTION PRIX ----------
        price = 0
        search_text = (raw_text + " " + description).lower()
        price_patterns = [
            r"(\d[\d\s,.]*)\s*(?:dt|tnd|dinar)",
            r"(?:prix|loyer)\s*[:]*\s*(\d[\d\s,.]*)"
        ]

        for pattern in price_patterns:
            match = re.search(pattern, search_text)
            if match:
                digits = re.sub(r"[^\d]", "", match.group(1))
                if digits:
                    price = int(digits)
                    break

        # ---------- EXTRACTION SURFACE ----------
        surf_match = re.search(
            r"(?:surface|superficie|مساحة).*?(\d{2,4})\s*(?:m2|m²|م|mètre)",
            search_text
        )
        surface = int(surf_match.group(1)) if surf_match else 0

        self.raw = {
            "description": description,
            "price": price,
            "surface_area": surface
        }

    def normalize(self) -> dict:
        """Standardisation avec détection des équipements (Amenities)."""
        text = self.raw.get("description", "")
        text_lower = text.lower()
        nlp_data = extract_entities_from_text(text)
        price = self.raw.get("price", 0)

        # Chambres
        s_plus = re.search(r"s\s?\+\s?(\d)", text_lower)
        bedrooms = int(s_plus.group(1)) if s_plus else (extract_bedrooms(text) or 2)

        # Surface
        surface = self.raw.get("surface_area") or 130

        # Heuristiques équipements (Tunisie)
        has_ac = any(x in text_lower for x in ["clim", "climatisation", "air con", "centrale"])
        has_heat = any(x in text_lower for x in ["chauffage", "central", "chaudière", "gaz de ville"])
        has_garage = any(x in text_lower for x in ["garage", "parking", "abri", "sous-sol"])

        return {
            "surface_area": surface,
            "bedrooms_filled": bedrooms,
            "price": price,
            "has_air_conditioning": has_ac,
            "has_heating": has_heat,
            "has_elevator": "ascenseur" in text_lower,
            "has_pool": any(x in text_lower for x in ["piscine", "pool", "mseb"]),
            "has_garage": has_garage,
            "has_garden": any(x in text_lower for x in ["jardin", "pelouse", "garden"]),
            "city": nlp_data.get("city") or "Tunis",
            "locality": nlp_data.get("locality") or "Gammarth",
            "transaction_category": "RENT" if price < 40000 else "SALE",
            "property_type": "Residential",
            "description": text
        }