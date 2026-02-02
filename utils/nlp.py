import re
from typing import Dict, Optional

try:
    import spacy
    NLP = spacy.load("fr_core_news_sm")
except Exception:
    NLP = None

def extract_entities_from_text(text: str) -> Dict[str, Optional[any]]:
    result = {
        "bedrooms": None, 
        "surface_area": None, 
        "city": None, 
        "locality": None, 
        "property_intent": None
    }
    if not text: return result

    # 1. Cleaning: Remove emojis, currency symbols, and phone number blocks
    clean_text = re.sub(r'[💰💲🚩☎🌐#]|(?:\d{2,}\s?){3,}', '', text)
    txt_l = clean_text.lower()
    
    # 2. Precise Surface Area (Priority to "X m2" pattern)
    surf_m = re.search(r"(\d[\d\s]{1,5})\s*(m2|m²|mètre)", txt_l)
    if surf_m:
        result["surface_area"] = int(surf_m.group(1).replace(" ", ""))

    # 3. Intelligent Geo-Mapping (Tunisia 2026 Expansion)
    geo_map = {
        # --- TUNIS & NORTHERN SUBURBS ---
        "soukra": ("Tunis", "La Soukra"),
        "ain zaghouan": ("Tunis", "Ain Zaghouan"),
        "l'aouina": ("Tunis", "L'Aouina"),
        "marsa": ("Tunis", "La Marsa"),
        "lac 1": ("Tunis", "Berges du Lac 1"),
        "lac 2": ("Tunis", "Berges du Lac 2"),
        "lac 3": ("Tunis", "Jardins de Carthage"),
        "jardins de carthage": ("Tunis", "Jardins de Carthage"),
        "carthage": ("Tunis", "Carthage"),
        "sidi bou said": ("Tunis", "Sidi Bou Said"),
        "gammarth": ("Tunis", "Gammarth"),
        "ennasr": ("Ariana", "Ennasr"),
        "menzah": ("Tunis", "El Menzah"),

        # --- SOUSSE & SAHEL ---
        "mall of sousse": ("Sousse", "Kalâa Kebira"),
        "kalaa kebira": ("Sousse", "Kalâa Kebira"),
        "kantaoui": ("Sousse", "Hammam Sousse"),
        "sahloul": ("Sousse", "Sahloul"),
        "chott mariem": ("Sousse", "Akouda"),
        
        # --- HAMMAMET & CAP BON ---
        "hammamet": ("Nabeul", "Hammamet"),
        "حمامات": ("Nabeul", "Hammamet"), # Support Arabic
        "نابل": ("Nabeul", "Nabeul Ville"),
        "nabeul": ("Nabeul", "Nabeul Ville"),

        "aouina": ("Tunis", "L'Aouina"),
        "wahat": ("Tunis", "L'Aouina"),
        "wajat": ("Tunis", "L'Aouina"), # Handling the user's typo in the listing

        # Add inside geo_map in utils/nlp.py
        # Add these specific lines to the geo_map in nlp.py
        "jaafar": ("Ariana", "Raoued"),
        "jaafar 2": ("Ariana", "Raoued"),
        "raoued": ("Ariana", "Raoued"),
        "ariana soghra": ("Ariana", "Sidi Thabet"),

        # Add these inside the geo_map dictionary in utils/nlp.py
        "mourouj": ("Ben Arous", "El Mourouj"),
        "mourouj 1": ("Ben Arous", "El Mourouj 1"),
        "mourouj 2": ("Ben Arous", "El Mourouj 2"),
        "mourouj 3": ("Ben Arous", "El Mourouj 3"),
        "mourouj 4": ("Ben Arous", "El Mourouj 4"),
        "mourouj 5": ("Ben Arous", "El Mourouj 5"),
        "mourouj 6": ("Ben Arous", "El Mourouj 6"),
        # Add inside geo_map in utils/nlp.py
        "المروج": ("Ben Arous", "El Mourouj"), # Arabic support for your listing
    }
    
    for key, (city, loc) in geo_map.items():
        if key in txt_l:
            result["city"] = city
            result["locality"] = loc
            break

    # 4. Spacy Fallback
    if not result["city"] and NLP:
        doc = NLP(clean_text)
        locs = [ent.text for ent in doc.ents if ent.label_ == "LOC"]
        if locs:
            result["city"] = locs[-1]
            result["locality"] = locs[0]

    if any(x in txt_l for x in ["terrain", "agricole", "lot"]):
        result["property_intent"] = "Land"

    return result