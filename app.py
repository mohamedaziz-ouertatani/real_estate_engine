import sys
import asyncio
import streamlit as st
import plotly.express as px
from engine.engine import UnifiedPredictionEngine

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title="Tunisia Real Estate AI", page_icon="🏠", layout="wide")

def main():
    st.title("🏠 Tunisia Real Estate AI Predictor")
    
    with st.sidebar:
        st.header("⚙️ Engine Control")
        mode = st.selectbox("Market Model:", ["Auto", "Residential", "Land", "Rental", "Commercial"])
        if st.button("Clear Cache", width="stretch"): st.rerun()

    url = st.text_input("Enter Listing URL:")

    if st.button("Run AI Analysis", type="primary", width="stretch"):
        with st.spinner("🕵️ AI Analyzing..."):
            try:
                engine = UnifiedPredictionEngine()
                result = engine.predict(url, mode_override=mode)
                
                # Progress bar normalization
                diff = result['difference_percent']
                norm_val = max(0.0, min(1.0, (100 + diff) / 200))
                meta = result['metadata']
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("AI Market Value", f"{result['predicted_price']:,} DT")
                m2.metric("Listing Price", f"{result['seller_price']:,} DT")
                m3.metric("Gap", f"{diff}%", delta=f"{diff}%", delta_color="inverse")
                m4.metric("Model Used", result['category'])

                st.divider()
                
                col_left, col_right = st.columns(2)
                with col_left:
                    st.progress(norm_val, text=f"Value Alignment: {result['deal_label']}")
                    
                    # Organize basic facts in a grid-like style
                    st.write(f"📂 **Category:** {result.get('category', 'N/A')}")
                    st.write(f"📍 **Location:** {meta.get('locality', 'Unknown')}")
                    st.write(f"🏠 **Address:** {meta.get('address', meta.get('locality', 'Not provided'))}")
                    
                    # Surface and Rooms
                    surface = meta.get('surface_area') or meta.get('land_area') or "Unknown"
                    # Logic to find room numbers (checking common keys)
                    rooms = meta.get('rooms') or meta.get('bedrooms') or meta.get('nb_pieces') or "N/A"
                    
                    st.write(f"📐 **Surface Area:** {surface} m²")
                    st.write(f"🛏️ **Rooms/Bedrooms:** {rooms}")
                    
                    st.divider()
                    
                    # Description
                    description = meta.get('description', 'No description available.')
                    with st.expander("📝 **View Full Description**"):
                        st.write(description)

                with col_right:
                    fig = px.bar(x=["AI Value", "Listing Price"], y=[result['predicted_price'], result['seller_price']],
                                 color=["AI", "Seller"], color_discrete_sequence=["#00CC96", "#EF553B"])
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, width="stretch")

            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()