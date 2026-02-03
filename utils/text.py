import re
from typing import Optional

# Configurable limit for sanity checking
MAX_BEDROOMS = 10

# Arabic word → number mapping
# Includes Standard Arabic dual forms and Tunisian dialect (Bit/Byout)
ARABIC_NUMBER_WORDS = {
    "غرفة": 1,
    "غرفه": 1,
    "بيت": 1,        # Tunisian: Bit (Room)
    "غرفتين": 2,      # Standard dual
    "غرفتان": 2,      # Formal dual
    "بيتين": 2,       # Tunisian dual
    "ثلاث": 3,
    "ثلاثة": 3,
    "اربعة": 4,
    "أربعة": 4,
    "خمسة": 5,
    "ستة": 6,
    "سبعة": 7,
    "ثمانية": 8,
    "تسعة": 9,
    "عشرة": 10,
    "غرف": None,      # Plural - handled by digit regex
    "بيوت": None,     # Plural - handled by digit regex
}

# Optimization: Pre-compile regex patterns at module level
_S_PLUS_PATTERN = re.compile(r"\bs\s*[\+\-]?\s*(\d+)", re.IGNORECASE)
_KEYWORD_PATTERN = re.compile(
    r"(\d+)\s*(?:pièce|piece|pièces|pieces|chambre|chambres|room|rooms|bureau|bureaux|بيت|بيوت|غرفة|غرف)",
    re.IGNORECASE
)
_F_PATTERN = re.compile(r"\bf\s*(\d+)\b", re.IGNORECASE)
_FALLBACK_PATTERN = re.compile(r"(\d+)\s*(?:bed|beds|ch|b|br)\b", re.IGNORECASE)

# Pre-compile Arabic word patterns for faster matching
_ARABIC_PATTERNS = {
    word: re.compile(rf"(?:^|\s){word}(?:\s|$)")
    for word, value in ARABIC_NUMBER_WORDS.items()
    if value is not None
}

def extract_bedrooms(description: str) -> Optional[int]:
    """
    Comprehensive bedroom extraction for Tunisian real estate.
    Handles multi-lingual listings (AR/FR/EN) and common dialectal shorthand.
    """

    if not description or not isinstance(description, str):
        return None

    # 1. Normalization: clean whitespace, non-breaking spaces, and zero-width chars
    txt = (
        description.lower()
        .replace("\xa0", " ")
        .replace("\u202f", " ")
        .replace("\u200b", "")
    )
    
    # Remove Arabic 'harakat' (tashkeel) so regex doesn't miss accented words
    txt = re.sub(r"[\u064B-\u0652]", "", txt)

    # ----------------------
    # 1. Studio
    # ----------------------
    if "studio" in txt:
        return 0

    # ----------------------
    # 2. S+X format (Standard Tunisia)
    # Optimized to catch "S+1", "S 1", "S+ 1", "s+2"
    # ----------------------
    s_plus_match = _S_PLUS_PATTERN.search(txt)
    if s_plus_match:
        return min(int(s_plus_match.group(1)), MAX_BEDROOMS)

    # ----------------------
    # 3. Multi-language Digit + Keywords
    # Handles: 4 pièces, 3 chambres, 5 bureaux, 2 rooms, 3 غرف
    # ----------------------
    keyword_match = _KEYWORD_PATTERN.search(txt)
    if keyword_match:
        count = int(keyword_match.group(1))
        
        # If listed as "Bureau", the digit is usually the exact room count
        if any(kw in txt for kw in ["bureau", "bureaux", "office"]):
            return min(count, MAX_BEDROOMS)
        
        # In Tunisia/France, "Pièce" or "Rooms" (T3/F3) includes the Salon. 
        # So a 3-piece is a 2-bedroom.
        if any(kw in keyword_match.group(0) for kw in ["pièce", "piece", "room"]):
            return min(max(count - 1, 0), MAX_BEDROOMS)
            
        return min(count, MAX_BEDROOMS)

    # ----------------------
    # 4. F-Type (French System: F3 = 2 Bedrooms)
    # ----------------------
    f_match = _F_PATTERN.search(txt)
    if f_match:
        return min(max(int(f_match.group(1)) - 1, 0), MAX_BEDROOMS)

    # ----------------------
    # 5. Arabic Number Words (Word-based duals and counts)
    # ----------------------
    for word, value in ARABIC_NUMBER_WORDS.items():
        if value is not None and _ARABIC_PATTERNS[word].search(txt):
            return min(value, MAX_BEDROOMS)

    # ----------------------
    # 6. Fallback (3 bed, 2 ch, 3 br)
    # ----------------------
    fallback_match = _FALLBACK_PATTERN.search(txt)
    if fallback_match:
        return min(int(fallback_match.group(1)), MAX_BEDROOMS)

    return None