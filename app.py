import sys
import asyncio
import streamlit as st
import plotly.graph_objects as go

from engine.engine import UnifiedPredictionEngine
from utils.feature_importance import extract_feature_importance, aggregate_by_prefix
from utils.visualization import plot_feature_importance

# ---------------- ASYNC FIX (WINDOWS) ----------------
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Tunisia Real Estate AI 2026",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- GLOBAL DARK UI CSS ----------------
st.markdown("""
<style>
/* Metric Cards */
div[data-testid="stMetric"] {
    background-color: #1e1e1e;
    border: 1px solid #333;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}
div[data-testid="stMetricLabel"] > div {
    color: #9ea0a5 !important;
    font-size: 14px;
    font-weight: bold;
}
div[data-testid="stMetricValue"] > div {
    color: #ffffff !important;
}

/* Amenity Tags */
.amenity-tag {
    background-color: #262730;
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    border: 1px solid #444;
    margin: 4px;
    display: inline-block;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- MAIN APP ----------------
def main():
    st.title("🏠 Tunisia Real Estate AI Predictor")
    st.caption("2026 Edition · ML Pricing · NLP Extraction · Explainable AI")

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.header("⚙️ Engine Control")

        mode = st.selectbox(
            "Market Model Override",
            ["Auto", "Residential", "Land", "Rental", "Commercial"]
        )

        st.divider()
        st.subheader("Display Options")
        show_explainability = st.checkbox("📊 Model Explainability", value=True)
        show_raw = st.checkbox("🗄️ Show Raw Metadata", value=False)

    # ---------- INPUT ----------
    url = st.text_input(
        "Enter Listing URL",
        placeholder="Facebook Marketplace, Tayara, Tunisie-Annonce..."
    )

    if st.button("Run AI Analysis", type="primary", use_container_width=True):
        if not url:
            st.warning("You need to paste a URL. The AI is good, not psychic.")
            return

        with st.spinner("🕵️ Scraping, parsing, predicting…"):
            try:
                engine = UnifiedPredictionEngine()
                result = engine.predict(url, mode_override=mode)

                if result.get("error"):
                    st.error(result["error"])
                    return

                meta = result.get("metadata", {})

                # ---------- METRICS ----------
                m1, m2, m3, m4 = st.columns(4)

                ai_price = result["predicted_price"]
                seller_price = result["seller_price"]
                gap = result["difference_percent"]

                m1.metric("AI Market Value", f"{ai_price:,} DT")
                m2.metric("Listing Price", f"{seller_price:,} DT")
                m3.metric(
                    "Market Gap",
                    f"{gap}%",
                    delta=f"{gap}%",
                    delta_color="normal" if gap > 0 else "inverse"
                )
                m4.metric("Model Used", result["category"])

                st.divider()

                # ---------- MAIN LAYOUT ----------
                left, right = st.columns([1, 1.2])

                # ===== LEFT PANEL =====
                with left:
                    st.subheader("📍 Property Details")
                    st.write(f"**Location:** {meta.get('locality', 'Unknown')}, {meta.get('city', 'Unknown')}")
                    st.write(f"**Category:** {meta.get('transaction_category', 'N/A')} ({meta.get('property_type', 'N/A')})")
                    st.write(f"**Surface:** {meta.get('surface_area', 0)} m²")
                    st.write(f"**Rooms:** {meta.get('bedrooms', 0)} Bedrooms")

                    st.subheader("✨ Features & Amenities")
                    features = {
                        "Air Conditioning": meta.get("has_air_conditioning"),
                        "Central Heating": meta.get("has_heating"),
                        "Elevator": meta.get("has_elevator"),
                        "Swimming Pool": meta.get("has_pool"),
                        "Garden": meta.get("has_garden"),
                        "Garage / Parking": meta.get("has_garage")
                    }

                    for name, exists in features.items():
                        icon = "✅" if exists else "❌"
                        st.markdown(
                            f"<div class='amenity-tag'>{icon} {name}</div>",
                            unsafe_allow_html=True
                        )

                    st.subheader("⚖️ AI Verdict")
                    label = result.get("deal_label", "N/A")
                    if "Great" in label:
                        st.success(label)
                    elif "Overpriced" in label:
                        st.warning(label)
                    else:
                        st.info(label)

                # ===== RIGHT PANEL =====
                with right:
                    st.subheader("📈 Price Positioning")

                    fig = go.Figure([
                        go.Bar(name="AI Value", x=["Comparison"], y=[ai_price], marker_color="#00CC96"),
                        go.Bar(name="Seller Price", x=["Comparison"], y=[seller_price], marker_color="#EF553B"),
                    ])
                    fig.update_layout(
                        barmode="group",
                        height=350,
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📝 Scraped Description"):
                        st.write(meta.get("description", "No description available."))

                # ---------- EXPLAINABILITY ----------
                if show_explainability:
                    st.divider()
                    st.subheader("📊 Why this price?")

                    try:
                        pipeline = engine.get_active_pipeline()
                        raw_df = extract_feature_importance(pipeline, top_n=25)
                        agg_df = aggregate_by_prefix(raw_df)
                        fig_imp = plot_feature_importance(agg_df, title="Factor Influence Breakdown")
                        st.plotly_chart(fig_imp, use_container_width=True)
                    except Exception:
                        st.warning("Explainability not available for this model type.")

                # ---------- RAW DATA ----------
                if show_raw:
                    st.divider()
                    st.subheader("🗄️ Raw Engine Output")
                    st.json(result)

            except Exception as e:
                st.error(f"Engine crashed: {e}")
                st.exception(e)

if __name__ == "__main__":
    main()
