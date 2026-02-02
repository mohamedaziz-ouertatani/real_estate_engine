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

    # 2. Build the initial dictionary with available data
    # Use max cap for bedrooms as established in previous stable versions
    bedrooms = data.get("bedrooms_filled")
    if bedrooms and bedrooms > 10:
        bedrooms = 10

    # 3. Create the DataFrame and reindex to add missing columns with defaults
    df = pd.DataFrame([{
        "surface_area": data.get("surface_area", np.nan),
        "bedrooms_filled": bedrooms or 1,
        "photo_count": data.get("photo_count", 0),
        "has_air_conditioning": data.get("has_air_conditioning", False),
        "has_heating": data.get("has_heating", False),
        "has_elevator": data.get("has_elevator", False),
        "has_pool": data.get("has_pool", False),
        "has_garage": data.get("has_garage", False),
        "has_garden": data.get("has_garden", False),
        "region": data.get("region", "Missing"),
        "city": data.get("city", "Missing"),
        "locality": data.get("locality", "Missing"),
        "property_type": data.get("property_type", "Unknown")
    }])

    # 4. SAFETY CHECK: Reindex ensures order and existence of all columns
    # Any column in expected_cols not in df will be added as NaN/0/False
    df = df.reindex(columns=expected_cols).fillna({
        "photo_count": 0,
        "has_air_conditioning": False,
        "has_heating": False,
        "has_elevator": False,
        "has_pool": False,
        "has_garage": False,
        "has_garden": False,
        "city": "Unknown",
        "locality": "Unknown"
    })

    return df