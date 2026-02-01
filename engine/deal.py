def assess_deal(predicted, seller):
    if not seller:
        return None, "ℹ️ No seller price"

    diff = (predicted - seller) / seller * 100

    if diff > 15:
        return diff, "💰 Great Deal"
    if diff < -15:
        return diff, "⚠️ Overpriced"

    return diff, "✅ Fair Price"
