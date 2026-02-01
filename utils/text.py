import re

def extract_bedrooms(description: str):
    if not isinstance(description, str):
        return None

    txt = description.lower()

    # --- TUNISIAN "S+X" EXTRACTION ---
    # Matches "S+1", "S+2", "S 2", "s+3", etc.
    s_plus_match = re.search(r"s\s*[\+\-]?\s*(\d+)", txt)
    if s_plus_match:
        return int(s_plus_match.group(1))

    # Standard "X chambres" notation
    m = re.search(r"(\d+)\s*chambres?", txt)
    if m:
        return int(m.group(1))

    # French "FX" notation (e.g., F3 is typically 2 bedrooms + 1 living room)
    m = re.search(r"\bf\s*(\d+)", txt)
    if m:
        return max(int(m.group(1)) - 1, 0)

    if "studio" in txt:
        return 0

    return None