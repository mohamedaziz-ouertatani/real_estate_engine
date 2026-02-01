import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
import joblib

# ---------------------------------------
# CONFIG
# ---------------------------------------
INPUT_FILE = "data/checkpoint_page_730.csv"
MODEL_OUTPUTS = {
    "Residential": "sale_model_residential.pkl",
    "Land": "sale_model_land.pkl",
    "Commercial": "sale_model_commercial.pkl",
    "Rental": "rental_model.pkl"
}
RANDOM_STATE = 42

def extract_bedrooms(description: str):
    if not isinstance(description, str): return None
    txt = description.lower()
    m = re.search(r"s\s*\+\s*(\d+)", txt)
    if m: return int(m.group(1))
    m = re.search(r"(\d+)\s*chambres?", txt)
    if m: return int(m.group(1))
    m = re.search(r"\bf\s*(\d+)", txt)
    if m: return max(int(m.group(1)) - 1, 0)
    if "studio" in txt: return 0
    return None

def detect_category(property_type, transaction_category, price):
    prop = (property_type or "").lower()
    trans = (transaction_category or "").lower()
    if any(x in prop for x in ["app", "villa", "duplex", "studio", "maison"]): return "Residential"
    if any(x in prop for x in ["terrain", "land", "terrain nu"]): return "Land"
    if any(x in prop for x in ["bureau", "local", "shop", "commerce", "commercial"]): return "Commercial"
    if "location" in trans or (price and price < 20000): return "Rental"
    return "Residential"

def train_model(df, model_name):
    numeric_features = ["surface_area", "bedrooms_filled", "photo_count"]
    boolean_features = ["has_air_conditioning", "has_heating", "has_elevator", "has_pool", "has_garage", "has_garden"]
    categorical_features = ["region", "city", "locality", "property_type"]

    X = df[numeric_features + boolean_features + categorical_features]
    y = df["log_price"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", Pipeline([
                ("impute", SimpleImputer(strategy="constant", fill_value="Missing")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ]), categorical_features),
            ("num", SimpleImputer(strategy="median"), numeric_features + boolean_features)
        ]
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=RANDOM_STATE))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
    print(f"🚀 Training {model_name}...")
    pipeline.fit(X_train, y_train)
    
    # Save
    joblib.dump(pipeline, MODEL_OUTPUTS[model_name])
    print(f"💾 Saved {model_name} model.\n")

def main():
    print("📥 Loading dataset...")
    df = pd.read_csv(INPUT_FILE)
    df = df[df["price"].notna()].copy()
    df["price"] = df["price"].astype(float)
    df["log_price"] = np.log1p(df["price"])
    df["bedrooms_filled"] = df["bedrooms"].fillna(df["description"].apply(extract_bedrooms))
    df = df[(df["surface_area"] > 10) & (df["surface_area"] < 10000)]
    
    df["category"] = df.apply(lambda x: detect_category(x.get("property_type"), x.get("transaction_category"), x.get("price")), axis=1)

    for cat in df["category"].unique():
        df_cat = df[df["category"] == cat].copy()
        if len(df_cat) > 10: train_model(df_cat, cat)

if __name__ == "__main__":
    main()