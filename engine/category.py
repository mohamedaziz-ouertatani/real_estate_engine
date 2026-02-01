def detect_category(property_type, transaction_category, price):
    prop = (property_type or "").lower()
    trans = (transaction_category or "").lower()
    
    # --- 1. THE SAFETY OVERRIDE (2026 MARKET CALIBRATION) ---
    # If price > 50,000 DT, it is almost certainly a Sale/Land/Commercial purchase.
    if price and price > 50000:
        if any(x in prop for x in ["terrain", "land"]): 
            return "Land"
        if any(x in prop for x in ["bureau", "local", "commerce"]): 
            return "Commercial"
        return "Residential"

    # --- 2. RENTAL DETECTION ---
    # Keywords for rent or prices typically associated with monthly rates.
    rental_keywords = ["louer", "location", "rent", "vacance", "nuitée"]
    if any(x in trans for x in rental_keywords) or (price and price < 20000):
        return "Rental"

    # --- 3. STANDARD CATEGORY DETECTION ---
    if any(x in prop for x in ["terrain", "land"]): 
        return "Land"
    if any(x in prop for x in ["bureau", "local", "commerce"]): 
        return "Commercial"
    
    return "Residential"