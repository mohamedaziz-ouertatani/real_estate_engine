"""
Centralized amenity detection to eliminate code duplication across scrapers.
"""

AMENITY_KEYWORDS = {
    "air_conditioning": ["clim", "climatisation", "split", "climatisé", "air conditionné"],
    "heating": ["chauffage", "central", "chaudière"],
    "elevator": ["ascenseur", "monte-charge"],
    "pool": ["piscine", "pool", "مسبح"],
    "garage": ["garage", "parking", "abri", "stationnement"],
    "garden": ["jardin", "garden", "espace vert"]
}

def detect_amenities(text: str) -> dict:
    """
    Detect amenities from text description.
    
    Args:
        text: Property description text
        
    Returns:
        Dictionary with has_* keys for each amenity
    """
    if not text:
        return {
            "has_air_conditioning": False,
            "has_heating": False,
            "has_elevator": False,
            "has_pool": False,
            "has_garage": False,
            "has_garden": False
        }
    
    text_lower = text.lower()
    return {
        f"has_{key}": any(keyword in text_lower for keyword in keywords)
        for key, keywords in AMENITY_KEYWORDS.items()
    }
