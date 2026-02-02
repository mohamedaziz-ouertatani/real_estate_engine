import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from scrapers.base import BaseScraper
from utils.text import extract_bedrooms
from utils.nlp import extract_entities_from_text

class TunisieAnnonceScraper(BaseScraper):

    def fetch(self):
        # Utilisation de headers plus complets pour éviter les blocages du site
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        }
        try:
            r = requests.get(self.url, headers=headers, timeout=25)
            r.encoding = "ISO-8859-1"
            self.soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            print(f"Fetch Error: {e}")
            self.soup = None

    def parse(self):
        # SECURITÉ : Initialisation immédiate d'un dictionnaire par défaut
        self.raw = { 
            "surface_area": 0, 
            "price": 0, 
            "description": "", 
            "city": "Unknown", 
            "locality": "Unknown", 
            "property_type": "Villa" 
        }
        
        if not self.soup: return

        # Table Parsing (Extraction classique)
        labels = self.soup.select("td.da_label_field")
        for label in labels:
            key = label.text.strip().lower()
            value_td = label.find_next_sibling("td", class_="da_field_text")
            if not value_td: continue
            
            value = value_td.get_text(" ", strip=True)

            if "surface" in key:
                m = re.search(r"(\d+)", value)
                if m: self.raw["surface_area"] = int(m.group(1))
            elif "prix" in key:
                m = re.sub(r"[^\d]", "", value)
                if m: self.raw["price"] = int(m)
            elif "texte" in key:
                self.raw["description"] = value

        # ✅ FALLBACK: Si la description est vide, on cherche le bloc de texte principal
        if not self.raw["description"]:
            # Essaie de trouver la cellule de texte standard qui est souvent l'avant-dernière ligne
            main_text = self.soup.select_one("table.da_table_detail tr:nth-last-child(2) td")
            if main_text:
                self.raw["description"] = main_text.get_text(" ", strip=True)

        # Parsing de la localisation via les liens
        links = self.soup.select("td.da_field_text a[href*='rech_cod_vil']")
        for a in links:
            qs = parse_qs(urlparse(a['href']).query)
            if "rech_cod_vil" in qs: self.raw["city"] = a.text.strip()
            if "rech_cod_loc" in qs: self.raw["locality"] = a.text.strip()

        # Photos count check
        self.raw["photo_count"] = len(self.soup.select("img[id^='PhotoMax_']"))
        
        # Type extraction
        type_td = self.soup.select_one("td.da_field_text a[href*='rech_cod_type']")
        if type_td:
            self.raw["property_type"] = type_td.text.strip()

    def normalize(self) -> dict:
        # SECURITÉ : On garantit que data est un dictionnaire utilisable
        data = self.raw if isinstance(self.raw, dict) else {}
        
        desc = data.get("description", "")
        nlp_data = extract_entities_from_text(desc)

        # Fallback IA si la ville n'est pas trouvée dans le tableau
        city = data.get("city", "Unknown")
        if city == "Unknown":
            city = nlp_data.get("city") or "Tunis"
            
        locality = data.get("locality", "Unknown")
        if locality == "Unknown":
            locality = nlp_data.get("locality") or "Unknown"

        return {
            "surface_area": data.get("surface_area") or nlp_data.get("surface_area") or 0,
            "bedrooms_filled": extract_bedrooms(desc) or nlp_data.get("bedrooms") or 2,
            "photo_count": data.get("photo_count", 0),
            "price": data.get("price"),

            "has_air_conditioning": "clim" in desc.lower(),
            "has_heating": "chauffage" in desc.lower(),
            "has_elevator": "ascenseur" in desc.lower(),
            "has_pool": "piscine" in desc.lower(),
            "has_garage": "garage" in desc.lower(),
            "has_garden": "jardin" in desc.lower(),

            "region": city,  # Mapping simple City -> Region
            "city": city,
            "locality": locality,
            "property_type": data.get("property_type", "Residential"),
            "transaction_category": "RENT" if data.get("price", 0) < 20000 else "SALE",
            "description": desc
        }