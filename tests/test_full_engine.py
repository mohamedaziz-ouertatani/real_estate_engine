from engine.engine import UnifiedPredictionEngine

engine = UnifiedPredictionEngine()

url = input("Paste listing URL: ")
result = engine.predict(url)

print("\n--- RESULT ---")
for k, v in result.items():
    print(f"{k}: {v}")
