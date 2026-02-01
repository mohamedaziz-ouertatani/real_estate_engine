import joblib
import numpy as np
from engine.router import get_scraper
from engine.category import detect_category
from engine.features import build_dataframe

class UnifiedPredictionEngine:
    def __init__(self):
        self.models = {
            "Residential": joblib.load("models/sale_model_residential.pkl"),
            "Rental": joblib.load("models/rental_model.pkl")
        }

    def predict(self, url: str, mode_override: str = "Auto") -> dict:
        """Updated to accept mode_override argument."""
        scraper = get_scraper(url)
        scraper.fetch()
        data = scraper.normalize()
        price = data.get("price", 0)

        # Logic for auto-routing or manual override
        if mode_override == "Auto":
            category = "Residential" if price > 50000 else detect_category(None, None, price)
        else:
            category = mode_override

        model = self.models.get(category, self.models["Residential"])
        df = build_dataframe(data)
        
        log_pred = model.predict(df)[0]
        prediction = np.expm1(log_pred)

        return {
            "predicted_price": round(prediction),
            "seller_price": price,
            "category": category,
            "metadata": data
        }