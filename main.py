import sys
import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
from engine.engine import UnifiedPredictionEngine
from utils.text import extract_bedrooms

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title="Tunisia Real Estate AI", page_icon="🏠", layout="wide")

def main():
    st.title("🏠 Tunisia Real Estate AI Predictor")
    st.caption("Deep market analysis for listings in Tunisia (2026 Edition)")

    with st.sidebar:
        st.header("⚙️ Engine Control")
        mode = st.selectbox("Market Model:", ["Auto", "Residential", "Land", "Rental", "Commercial"])
        if st.button("Clear Cache", width="stretch"): st.rerun()

    url = st.text_input("Enter Listing URL:", placeholder="Paste Tayara, Facebook, or other link...")

    # UPDATED: width="stretch" for 2026 compliance
    if st.button("Run AI Analysis", type="primary", width="stretch"):
        with st.spinner("🕵️ AI Analyzing..."):
            try:
                engine = UnifiedPredictionEngine()
                result = engine.predict(url, mode_override=mode)
                
                # Progress bar normalization for the Gap display
                diff = result['difference_percent']
                norm_val = max(0.0, min(1.0, (100 + diff) / 200))
                meta = result['metadata']
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("AI Market Value", f"{result['predicted_price']:,} DT")
                m2.metric("Listing Price", f"{result['seller_price']:,} DT")
                m3.metric("Gap", f"{diff}%", delta=f"{diff}%", delta_color="inverse")
                m4.metric("Market", result['category'])

                st.divider()
                
                col_left, col_right = st.columns(2)
                with col_left:
                    st.progress(norm_val, text=f"Value Alignment: {result['deal_label']}")
                    # Surface parsing is now fixed in features.py
                    st.write(f"📐 **Surface:** {meta.get('surface_area') or meta.get('land_area')} m²")
                    st.write(f"📍 **Locality:** {meta.get('locality')}")

                with col_right:
                    fig = px.bar(x=["AI", "Listing"], y=[result['predicted_price'], result['seller_price']])
                    # UPDATED: width="stretch" for 2026 compliance
                    st.plotly_chart(fig, width="stretch")

            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()