import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from app import load_or_refresh_cache

st.set_page_config(page_title="Growthory Cafe Finder", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #5d35b0; color: white; }
    .cafe-row { background-color: #2e1a5e; margin-bottom: 10px; padding: 10px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; }
    .social-icons a { background: #1877f2; color: white; padding: 8px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-right: 5px; font-size: 12px; }
    .social-icons a.ig { background: #e1306c; }
    .social-icons a.map { background: white; color: black; }
    .social-icons a.msg { background: #00b2ff; }
    .cafe-info { flex: 1; margin-left: 15px; font-weight: bold; }
    .cafe-loc { border-left: 2px solid #b2ff33; padding-left: 10px; margin-left: 10px; color: #ccc; }
    .metric-box { width: 60px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-left: 10px; cursor: pointer; color: black; position: relative; }
    .bg-green { background-color: #b2ff33; }
    .bg-red { background-color: #ff3333; color: white; }
    .tooltip-content { visibility: hidden; position: absolute; top: 50px; left: 50%; transform: translateX(-50%); background-color: #000; color: white; padding: 15px; border-radius: 10px; width: 300px; z-index: 100; text-align: center; }
    .metric-box:hover .tooltip-content { visibility: visible; }
</style>
""", unsafe_allow_html=True)

# ─── Logic ────────────────────────────────────────────────────────
def generate_svg_graph(data, labels, color="#b2ff33"):
    if not data or len(data) < 2: return ""
    max_v = max(data) if max(data) != 0 else 1
    points = [f"{10 + i * (260/4)},{50 - (val/max_v * 40)}" for i, val in enumerate(data)]
    polyline = f'<polyline fill="none" stroke="white" stroke-width="2" points="{" ".join(points)}" />'
    return f'<svg width="280px" height="75px">{polyline}</svg>'

if "app_state" not in st.session_state:
    data = load_or_refresh_cache()
    st.session_state.app_state = {"main": data.get("cafes", []), "pending": [], "rejected": [], "page": "main"}

state = st.session_state.app_state

def move_cafe(name, from_l, to_l):
    cafe = next((c for c in state[from_l] if c["name"] == name), None)
    if cafe:
        state[from_l].remove(cafe)
        if to_l: state[to_l].append(cafe)

# ─── Navigation ────────────────────────────────────────────────────────
col_logo, col_nav = st.columns([2, 8])
with col_logo: st.markdown("<h2 style='color:#b2ff33;'>GROWTHORY</h2>", unsafe_allow_html=True)
with col_nav:
    if st.button("REFRESH LIST", type="primary"):
        state["main"] = load_or_refresh_cache().get("cafes", [])
        st.rerun()

# ─── Main View ────────────────────────────────────────────────────────
left, right = st.columns([3, 7])
with left:
    st.markdown('<div style="border: 15px solid #222; border-radius: 30px; height: 750px; background: white;"><iframe name="mobile_frame" src="https://m.facebook.com/" width="100%" height="100%" style="border:none;"></iframe></div>', unsafe_allow_html=True)

with right:
    for cafe in state["main"]:
        m = cafe.get("metrics", {"avg_gap_days": 0, "avg_engagement": 0, "avg_weekly_followers": 0, "gap_history": [], "engagement_history": [], "follower_history": []})
        
        row_html = f"""
        <div class="cafe-row">
            <div class="social-icons">
                <a href="{cafe.get('fb_url', '#')}" target="mobile_frame">f</a>
                <a href="{cafe.get('ig_url', '#')}" target="mobile_frame" class="ig">IG</a>
                <a href="{cafe.get('map_url', '#')}" target="mobile_frame" class="map">📍</a>
            </div>
            <div class="cafe-info">{cafe['name']} <span class="cafe-loc">{cafe['location']}</span></div>
            <div class="metric-box {'bg-red' if m['avg_gap_days'] > 5 else 'bg-green'}">{int(m['avg_gap_days'])}D</div>
            <div class="metric-box {'bg-red' if m['avg_engagement'] < 10 else 'bg-green'}">{int(m['avg_engagement'])}%</div>
        </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)
