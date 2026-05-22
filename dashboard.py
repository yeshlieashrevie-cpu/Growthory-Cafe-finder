import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Import backend logic
from app import load_or_refresh_cache

st.set_page_config(page_title="Growthory Cafe Finder", layout="wide", initial_sidebar_state="collapsed")

# ─── Custom CSS & Theme ────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global Theme */
    .stApp { background-color: #5d35b0; color: white; }
    h1, h2, h3, p { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Top Menu Buttons */
    .top-btn {
        padding: 10px 20px; font-weight: bold; border-radius: 8px; border: none;
        color: black; cursor: pointer; text-align: center; margin-right: 10px; text-decoration: none;
    }
    .btn-dark { background-color: #1a1a1a; color: white; }
    .btn-lime { background-color: #b2ff33; }
    .btn-red { background-color: #ff3333; color: white; }
    
    /* List Item Row */
    .cafe-row {
        background-color: #2e1a5e; margin-bottom: 10px; padding: 10px;
        border-radius: 8px; display: flex; align-items: center; justify-content: space-between;
    }
    .social-icons a {
        background: #1877f2; color: white; padding: 8px; border-radius: 6px; 
        text-decoration: none; font-weight: bold; margin-right: 5px; font-size: 12px;
    }
    .social-icons a.ig { background: #e1306c; }
    .social-icons a.map { background: white; color: black; }
    .social-icons a.msg { background: #00b2ff; }
    
    .cafe-info { flex: 1; margin-left: 15px; font-weight: bold; color: white; }
    .cafe-loc { border-left: 2px solid lime; padding-left: 10px; margin-left: 10px; color: #ccc; }
    
    /* Metric Boxes & Tooltips */
    .metric-box {
        position: relative; width: 60px; height: 40px; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; margin-left: 10px; cursor: pointer; color: black;
    }
    .bg-green { background-color: #b2ff33; }
    .bg-red { background-color: #ff3333; color: white; }
    
    .tooltip-content {
        visibility: hidden; position: absolute; top: 50px; left: 50%;
        transform: translateX(-50%); background-color: #000; color: white;
        padding: 15px; border-radius: 10px; width: 300px; z-index: 100;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.5); text-align: center;
    }
    .tooltip-content::after {
        content: ""; position: absolute; bottom: 100%; left: 50%;
        margin-left: -10px; border-width: 10px; border-style: solid;
        border-color: transparent transparent black transparent;
    }
    .metric-box:hover .tooltip-content { visibility: visible; }
    .tooltip-title { font-size: 10px; letter-spacing: 1px; margin-bottom: 10px; color: white; }
    
    /* Action Arrows */
    .arrow-btn {
        background: none; border: none; font-size: 20px; cursor: pointer; margin: 0 5px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Helper Functions ──────────────────────────────────────────────────────────

def generate_svg_graph(data, labels, color="#b2ff33"):
    """Generates an inline SVG sparkline graph with points based on the last 5 stats."""
    if not data or len(data) < 5: return ""
    max_v = max(data) if max(data) != 0 else 1
    points = []
    width, height = 280, 50
    for i, val in enumerate(data):
        x = 10 + i * ((width - 20) / 4)
        y = height - (max(0.1, val) / max_v * height * 0.8) # 20% padding
        points.append(f"{x},{y}")
    
    polyline = f'<polyline fill="none" stroke="white" stroke-width="2" points="{" ".join(points)}" />'
    circles = "".join([f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="4" fill="white" />' for p in points])
    
    # Add text labels below points
    texts = "".join([f'<text x="{p.split(",")[0]}" y="{height + 15}" fill="{color}" font-size="12" font-weight="bold" text-anchor="middle">{labels[i]}</text>' for i, p in enumerate(points)])
    
    return f'<svg width="{width}px" height="{height + 25}px">{polyline}{circles}{texts}</svg>'

# ─── State Management ──────────────────────────────────────────────────────────

if "app_state" not in st.session_state:
    data = load_or_refresh_cache()
    st.session_state.app_state = {
        "main": data.get("cafes", []),
        "pending": [],
        "rejected": [],
        "page": "main"
    }

state = st.session_state.app_state

def move_cafe(cafe_name, from_list, to_list):
    cafe = next((c for c in state[from_list] if c["name"] == cafe_name), None)
    if cafe:
        state[from_list] = [c for c in state[from_list] if c["name"] != cafe_name]
        if to_list:
            state[to_list].append(cafe)

# ─── Top Navigation ────────────────────────────────────────────────────────────

col_logo, col_nav = st.columns([2, 8])
with col_logo:
    st.markdown("<h2 style='color:#b2ff33; margin:0;'>GROWTHORY<br>CAFE FINDER</h2>", unsafe_allow_html=True)

with col_nav:
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("BATCH OUTREACH", use_container_width=True):
        st.toast("Batch Outreach Triggered!")
    if c2.button("MAIN LIST" if state["page"] == "segregated" else "VIEW SEGREGATED", use_container_width=True):
        state["page"] = "main" if state["page"] == "segregated" else "segregated"
        st.rerun()
    if c3.button("DOWNLOAD CSV", use_container_width=True):
        st.toast("Downloading CSV...")
    if c4.button("REFRESH LIST", type="primary", use_container_width=True):
        data = load_or_refresh_cache()
        state["main"] = data.get("cafes", [])
        st.rerun()
    if c5.button("DELETE", use_container_width=True):
        st.toast("Delete triggered on checkboxes.")

st.markdown("<hr style='border-color: #4b2a8f; margin-top: 5px;'>", unsafe_allow_html=True)

# ─── Page 1: Main View ─────────────────────────────────────────────────────────

if state["page"] == "main":
    left_col, right_col = st.columns([3, 7])
    
    # Mobile Window (Pure HTML Iframe to prevent Streamlit re-runs)
    with left_col:
        st.markdown("""
        <div style="border: 15px solid #222; border-radius: 30px; overflow: hidden; height: 750px; background: white;">
            <iframe name="mobile_frame" src="https://m.facebook.com/" width="100%" height="100%" style="border:none;"></iframe>
        </div>
        """, unsafe_allow_html=True)
        
    with right_col:
        for i, cafe in enumerate(state["main"]):
            m = cafe["metrics"]
            
            # Logic for color coding boxes
            gap_cls = "bg-red" if m["avg_gap_days"] > 5 else "bg-green"
            gap_txt = f"{int(m['avg_gap_days'])} D" if m["avg_gap_days"] >= 1 else f"{int(m['avg_gap_days']*24)} H"
            
            eng_cls = "bg-red" if m["avg_engagement"] < 10 else "bg-green"
            eng_txt = f"{int(m['avg_engagement'])}%"
            
            fol_cls = "bg-red" if m["avg_weekly_followers"] < 5 else "bg-green"
            fol_txt = f"+{int(m['avg_weekly_followers'])}" if m["avg_weekly_followers"] > 0 else f"{int(m['avg_weekly_followers'])}"

            # SVG Graphs
            svg_gap = generate_svg_graph(m["gap_history"], [f"{int(x)}D" for x in m["gap_history"]])
            svg_eng = generate_svg_graph(m["engagement_history"], [f"{int(x)}%" for x in m["engagement_history"]])
            svg_fol = generate_svg_graph(m["follower_history"], [f"{int(x)}" for x in m["follower_history"]])

            # UI Component
            row_html = f"""
            <div class="cafe-row">
                <input type="checkbox" style="width: 20px; height: 20px; margin-right: 15px;">
                <div class="social-icons">
                    <a href="{cafe['fb_url']}" target="mobile_frame">f</a>
                    <a href="{cafe['ig_url']}" target="mobile_frame" class="ig">IG</a>
                    <a href="{cafe['map_url']}" target="mobile_frame" class="map">📍</a>
                    <a href="{cafe['msg_url']}" target="mobile_frame" class="msg">💬</a>
                </div>
                <div class="cafe-info">
                    [{cafe['name']}] <span class="cafe-loc">[{cafe['location']}]</span>
                </div>
                
                <div class="metric-box {gap_cls}">
                    {gap_txt}
                    <div class="tooltip-content">
                        <div class="tooltip-title">AVERAGE POSTING GAP (LAST 5 POSTS)</div>
                        {svg_gap}
                    </div>
                </div>
                
                <div class="metric-box {eng_cls}">
                    {eng_txt}
                    <div class="tooltip-content">
                        <div class="tooltip-title">AVERAGE ENGAGEMENT (LAST 5 POSTS)</div>
                        {svg_eng}
                    </div>
                </div>
                
                <div class="metric-box {fol_cls}">
                    {fol_txt}
                    <div class="tooltip-content">
                        <div class="tooltip-title">WEEKLY FOLLOWERS GAIN (LAST 5 WKS)</div>
                        {svg_fol}
                    </div>
                </div>
            </div>
            """
            
            rc1, rc2, rc3 = st.columns([8.5, 0.75, 0.75])
            with rc1:
                st.markdown(row_html, unsafe_allow_html=True)
            with rc2:
                if st.button("🟢", key=f"pend_{cafe['name']}", help="Move to Pending"):
                    move_cafe(cafe['name'], "main", "pending")
                    st.rerun()
            with rc3:
                if st.button("🔴", key=f"rej_{cafe['name']}", help="Move to Rejected"):
                    move_cafe(cafe['name'], "main", "rejected")
                    st.rerun()

# ─── Page 2: Segregated Lists ──────────────────────────────────────────────────

elif state["page"] == "segregated":
    col_pend, col_rej = st.columns(2)
    
    with col_pend:
        st.markdown("<h3 style='color:#b2ff33;'>PENDING LIST</h3>", unsafe_allow_html=True)
        for cafe in state["pending"]:
            pc1, pc2, pc3 = st.columns([6, 2, 2])
            with pc1:
                st.markdown(f"<div class='cafe-row' style='margin-bottom:0;'><b>[{cafe['name']}]</b> <span class='cafe-loc'>[{cafe['location']}]</span></div>", unsafe_allow_html=True)
            with pc2:
                if st.button("ADD", key=f"add_{cafe['name']}", use_container_width=True):
                    move_cafe(cafe['name'], "pending", "main")
                    st.rerun()
            with pc3:
                if st.button("DELETE", key=f"del_p_{cafe['name']}", use_container_width=True):
                    move_cafe(cafe['name'], "pending", None)
                    st.rerun()

    with col_rej:
        st.markdown("<h3 style='color:#ff3333;'>REJECTED LIST</h3>", unsafe_allow_html=True)
        for cafe in state["rejected"]:
            rc1, rc2, rc3 = st.columns([6, 2, 2])
            with rc1:
                st.markdown(f"<div class='cafe-row' style='margin-bottom:0;'><b>[{cafe['name']}]</b> <span class='cafe-loc'>[{cafe['location']}]</span></div>", unsafe_allow_html=True)
            with rc2:
                if st.button("RECON", key=f"recon_{cafe['name']}", use_container_width=True):
                    move_cafe(cafe['name'], "rejected", "pending")
                    st.rerun()
            with rc3:
                if st.button("DELETE", key=f"del_r_{cafe['name']}", use_container_width=True):
                    move_cafe(cafe['name'], "rejected", None)
                    st.rerun()
