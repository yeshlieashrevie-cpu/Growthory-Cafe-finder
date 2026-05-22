import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timezone
# Import the logic classes from your original app.py
from app import MetaAPIClient, MetricsEngine, DemoDataEngine, _parse_ts, CACHE_FILE, DEMO_MODE, META_ACCESS_TOKEN

# Page Setup
st.set_page_config(page_title="Cafe Tracker", layout="wide")
st.title("☕ Cafe Intelligence Tracker")

# Logic to load data
def get_data():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return DemoDataEngine.generate()

# UI Layout
data = get_data()
cafes = data.get("cafes", [])

st.sidebar.subheader("Dashboard Status")
st.sidebar.write(f"Last Refresh: {data.get('last_updated', 'N/A')}")

# Metrics
col1, col2 = st.columns(2)
col1.metric("Cafes Tracked", len(cafes))
col2.metric("Mode", "DEMO" if data.get("demo_mode") else "LIVE")

# Table
st.subheader("Cafe Performance")
if cafes:
    df = pd.DataFrame(cafes)
    st.dataframe(df[["name", "location", "priority_score", "avg_engagement_rate"]], use_container_width=True)
else:
    st.info("No data available.")

# Refresh Button
if st.button("Refresh Data"):
    # Trigger your fetch function here
    st.rerun()
