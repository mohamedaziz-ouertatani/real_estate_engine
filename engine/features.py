# engine/features.py
import pandas as pd
import numpy as np

def build_dataframe(data: dict) -> pd.DataFrame:
    # 1. Define the exact columns the model expects (must match training)
    expected_cols = [
        "surface_area", "bedrooms_filled", "photo_count",
        "has_air_conditioning", "has_heating", "has_elevator", 
        "has_pool", "has_garage", "has_garden",
        "region", "city", "locality", "property_type"
    ]

    # 2. Create defaults for all expected columns
    defaults = {
        "surface_area": np.nan,
        "bedrooms_filled": 1,
        "photo_count": 0,
        "has_air_conditioning": False,
        "has_heating": False,
        "has_elevator": False,
        "has_pool": False,
        "has_garage": False,
        "has_garden": False,
        "region": "Missing",
        "city": "Missing",
        "locality": "Missing",
        "property_type": "Unknown"
    }

    # 3. Merge data with defaults in one pass (only keep expected columns)
    row = {**defaults, **{k: v for k, v in data.items() if k in expected_cols}}
    
    # 4. Cap bedrooms to reasonable maximum
    if row.get("bedrooms_filled", 0) > 10:
        row["bedrooms_filled"] = 10

    # 5. Create DataFrame with correct column order
    return pd.DataFrame([row])[expected_cols]