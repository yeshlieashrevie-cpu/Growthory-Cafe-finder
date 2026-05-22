import streamlit as st
import pandas as pd
from app import load_or_refresh_cache, MetricsEngine

# Page configuration
st.set_page_config(page_title="Cafe Intelligence Dashboard", layout="wide")

st.title("☕ Cafe Intelligence Tracker")
st.markdown("---")

# Load data using your existing function from app.py
try:
    data = load_or_refresh_cache()
    cafes = data.get("cafes", [])
    last_updated = data.get("last_updated", "N/A")

    st.sidebar.subheader("Dashboard Status")
    st.sidebar.write(f"Last Refresh: {last_updated}")
    
    if data.get("demo_mode"):
        st.sidebar.warning("Running in DEMO MODE")
    else:
        st.sidebar.success("Running in LIVE MODE")

    # Display Metrics in columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cafes Tracked", len(cafes))
    col2.metric("System Status", "Operational")
    col3.metric("Mode", "Demo" if data.get("demo_mode") else "Live")

    # Display data in a nice table
    st.subheader("Cafe Performance Table")
    
    # Convert list of dicts to DataFrame for nice Streamlit display
    if cafes:
        df = pd.DataFrame(cafes)
        
        # Select and rename columns for a cleaner view
        display_cols = ["name", "location", "avg_gap_days", "avg_engagement_rate", "priority_score"]
        st.dataframe(df[display_cols], use_container_width=True)
    else:
        st.info("No cafe data found.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.write("Ensure your app.py is in the same folder as this dashboard.py file.")

# Instructions
st.markdown("---")
st.caption("This dashboard reads data from `daily_cache.json` created by `app.py`.")
