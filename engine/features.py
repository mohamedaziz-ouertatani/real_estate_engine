import pandas as pd
import numpy as np

def build_dataframe(data: dict) -> pd.DataFrame:
    # Cap bedrooms at 10 for model stability
    rooms = data.get("bedrooms_filled", 1)
    rooms = min(max(int(rooms), 1), 10)

    return pd.DataFrame([{
        "surface_area": float(data.get("surface_area", 0)),
        "bedrooms_filled": rooms,
        "region": data.get("region", "Tunis"),
        "property_type": data.get("property_type", "Apartment")
    }])