import joblib
import numpy as np

from engine.router import get_scraper
from engine.features import build_dataframe
from engine.deal import assess_deal
from engine.category import detect_category


class UnifiedPredictionEngine:
    def __init__(self):
        self.models = {}
        self.pipeline = None

        model_paths = {
            "Residential": "models/sale_model_residential.pkl",
            "Land": "models/sale_model_land.pkl",
            "Commercial": "models/sale_model_commercial.pkl",
            "Rental": "models/rental_model.pkl"
        }

        for category, path in model_paths.items():
            try:
                self.models[category] = joblib.load(path)
            except Exception as e:
                print(f"❌ Failed to load {category} model: {e}")

    # ------------------------------------------------------------------
    # 🔧 Heuristic Adjustment Layer (Post-ML)
    # ------------------------------------------------------------------
    def _apply_location_premium(self, base_price: float, data: dict) -> float:
        """
        Smart geo + standing adjustment with rental safety guards.
        """

        is_rental = data.get("transaction_category") == "RENT"
        bedrooms = data.get("bedrooms_filled", 0)
        description = (data.get("description") or "").lower()

        geo_text = f"{data.get('locality','')} {data.get('city','')}".lower()

        # Base zone multipliers (REAL Tunis logic, not LinkedIn math)
        zone_multipliers = {
            "gammarth": 1.9,
            "la marsa": 1.8,
            "lac": 1.7,
            "menzah": 1.3,
            "ennasr": 1.3,
        }

        multiplier = 1.0
        for zone, value in zone_multipliers.items():
            if zone in geo_text:
                multiplier = max(multiplier, value)

        # Standing bonuses
        if any(x in description for x in ["piscine", "luxe", "haut standing"]):
            multiplier += 0.15

        if any(x in description for x in ["meublé", "meuble", "furnished"]) and is_rental:
            multiplier += 0.10

        final_price = base_price * multiplier

        # 🛑 Rental sanity brakes (prevent fantasy prices)
        if is_rental:
            if bedrooms <= 1 and final_price > 1300:
                return 1200 + (final_price - 1200) * 0.05

            if bedrooms == 2 and final_price > 1800:
                return 1700 + (final_price - 1700) * 0.10

        return final_price

    # ------------------------------------------------------------------
    # 🔮 Main Prediction Entry
    # ------------------------------------------------------------------
    def predict(self, url: str, mode_override: str = "Auto") -> dict:
        response = {
            "source": "Unknown",
            "category": "Unknown",
            "predicted_price": 0,
            "seller_price": 0,
            "difference_percent": 0,
            "deal_label": "ℹ️ Pending",
            "description": "",
            "location_detected": {"city": "Unknown", "locality": "Unknown"},
            "metadata": {},
            "error": None
        }

        if not self.models:
            response["error"] = "No ML models loaded."
            return response

        try:
            # -------------------- SCRAPING --------------------
            scraper = get_scraper(url)
            scraper.fetch()
            scraper.parse()
            data = scraper.normalize()

            if not data or not data.get("description"):
                response["error"] = "Failed to extract listing content."
                return response

            seller_price = data.get("price", 0)

            # -------------------- CATEGORY --------------------
            category = (
                mode_override
                if mode_override != "Auto"
                else detect_category(
                    data.get("property_type"),
                    data.get("transaction_category"),
                    seller_price
                )
            )

            model = self.models.get(category) or self.models.get("Rental")
            self.pipeline = model

            # -------------------- ML PREDICTION --------------------
            df = build_dataframe(data)
            log_pred = model.predict(df)[0]
            base_price = np.expm1(log_pred)

            final_price = self._apply_location_premium(base_price, data)
            diff_percent, label = assess_deal(final_price, seller_price)

            # -------------------- RESPONSE MAP --------------------
            response.update({
                "source": type(scraper).__name__,
                "category": category,
                "predicted_price": round(final_price),
                "seller_price": seller_price,
                "difference_percent": round(diff_percent, 1),
                "deal_label": label,
                "description": data.get("description"), # Sets the text for "Scraped Description"

                "location_detected": {
                    "city": data.get("city", "Unknown"),
                    "locality": data.get("locality", "Unknown"),
                },

                "metadata": {
                    "surface_area": data.get("surface_area"),
                    "bedrooms": data.get("bedrooms_filled"),
                    "property_type": data.get("property_type"),
                    "transaction_category": data.get("transaction_category"),
                    # These trigger the ✅/❌ icons in the UI
                    "has_air_conditioning": data.get("has_air_conditioning", False),
                    "has_heating": data.get("has_heating", False),
                    "has_elevator": data.get("has_elevator", False),
                    "has_pool": data.get("has_pool", False),
                    "has_garage": data.get("has_garage", False),
                    "has_garden": data.get("has_garden", False),
                }
            })

        except Exception as e:
            response["error"] = f"Engine Error: {e}"
            print(f"❌ Engine crash: {e}")

        return response

    # ------------------------------------------------------------------
    # 🧠 Explainability / Debug
    # ------------------------------------------------------------------
    def get_active_pipeline(self):
        if self.pipeline is None:
            raise RuntimeError("No active model. Run predict() first.")
        return self.pipeline
