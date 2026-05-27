# dashboard.py
# CAFE ORBIT CAFE FINDER — Full Streamlit App
# Page 1: Main Lead List | Page 2: Segregated (Pending/Rejected)

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import data_store as ds
from dummy_data import get_dummy_cafes

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="CAFE ORBIT CAFE FINDER",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Color palette ────────────────────────────────────────────────
BLACK   = "#000000"
VIOLET  = "#7D39EB"
LIME    = "#C6FF33"
WHITE   = "#FFFFFF"
RED     = "#FF2222"
DARKBG  = "#0d0d0d"
CARDPURP= "#1a0a2e"

# ── Global CSS ───────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Barlow:wght@400;700;900&display=swap');

/* ── Reset & base ── */
html, body, [data-testid="stAppViewContainer"] {{
    background: {BLACK} !important;
    color: {WHITE} !important;
    font-family: 'Barlow', sans-serif !important;
}}
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="stHeader"] {{ background: transparent !important; }}
footer {{ visibility: hidden !important; }}
.block-container {{ padding: 0.5rem 1rem 2rem 1rem !important; max-width: 100% !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {BLACK}; }}
::-webkit-scrollbar-thumb {{ background: {VIOLET}; border-radius: 3px; }}

/* ── Top bar title ── */
.top-title {{
    font-family: 'Black Han Sans', sans-serif !important;
    font-size: 1.6rem;
    color: {LIME};
    letter-spacing: 0.08em;
    line-height: 1;
    text-shadow: 0 0 20px {LIME}55;
}}
.top-subtitle {{
    font-family: 'Black Han Sans', sans-serif !important;
    font-size: 0.75rem;
    color: {VIOLET};
    letter-spacing: 0.15em;
}}

/* ── Action buttons ── */
.stButton > button {{
    font-family: 'Black Han Sans', sans-serif !important;
    font-weight: 900 !important;
    letter-spacing: 0.08em !important;
    border-radius: 6px !important;
    border: none !important;
    padding: 0.45rem 0.8rem !important;
    font-size: 0.78rem !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    filter: brightness(1.15) !important;
}}

/* ── Cafe row card ── */
.cafe-card {{
    background: {CARDPURP};
    border: 1px solid {VIOLET}44;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    position: relative;
    transition: border-color 0.2s;
}}
.cafe-card:hover {{
    border-color: {VIOLET};
}}

/* ── Metric box ── */
.metric-box {{
    border-radius: 8px;
    padding: 6px 10px;
    text-align: center;
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1.1rem;
    font-weight: 900;
    letter-spacing: 0.05em;
    position: relative;
    cursor: default;
    min-width: 64px;
    transition: transform 0.15s;
    user-select: none;
}}
.metric-box:hover {{ transform: scale(1.05); }}
.metric-good {{ background: {LIME}; color: {BLACK}; }}
.metric-bad  {{ background: {RED};  color: {WHITE}; }}

/* ── Tooltip popup ── */
.metric-box .tooltip {{
    display: none;
    position: absolute;
    bottom: calc(100% + 12px);
    left: 50%;
    transform: translateX(-50%);
    background: {BLACK};
    border: 2px solid {VIOLET};
    border-radius: 10px;
    padding: 12px 16px;
    min-width: 260px;
    z-index: 9999;
    pointer-events: none;
    box-shadow: 0 8px 32px {VIOLET}66;
}}
.metric-box:hover .tooltip {{ display: block; }}
.tooltip-arrow {{
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    width: 0; height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 12px solid {VIOLET};
}}
.tooltip-title {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.75rem;
    color: {WHITE};
    letter-spacing: 0.12em;
    text-align: center;
    margin-bottom: 2px;
}}
.tooltip-sub {{
    font-family: 'Barlow', sans-serif;
    font-size: 0.65rem;
    color: {VIOLET};
    letter-spacing: 0.1em;
    text-align: center;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid {VIOLET}55;
}}
.tooltip-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 4px 0;
}}
.tooltip-num {{
    color: {WHITE};
    font-family: 'Barlow', sans-serif;
    font-size: 0.75rem;
    opacity: 0.6;
    min-width: 18px;
}}
.tooltip-val {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1rem;
    color: {LIME};
    flex: 1;
    text-align: center;
}}
.tooltip-line {{
    flex: 2;
    height: 3px;
    background: {VIOLET}44;
    border-radius: 2px;
    margin: 0 6px;
    position: relative;
    overflow: visible;
}}
.tooltip-dot {{
    position: absolute;
    top: -4px;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: {LIME};
    transform: translateX(-50%);
}}

/* ── Social icon buttons ── */
.icon-btn {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px; height: 40px;
    border-radius: 10px;
    font-size: 1.3rem;
    text-decoration: none !important;
    transition: transform 0.15s, filter 0.15s;
    cursor: pointer;
}}
.icon-btn:hover {{ transform: scale(1.12); filter: brightness(1.2); }}
.btn-fb  {{ background: #1877F2; }}
.btn-ig  {{ background: linear-gradient(135deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); }}
.btn-map {{ background: {WHITE}; color: #EA4335 !important; font-size:1.4rem; }}
.btn-msg {{ background: linear-gradient(135deg,#0084FF,#00C6FF); }}
.btn-disabled {{ background: #333; color: #666 !important; cursor: not-allowed; filter: grayscale(1); }}

/* ── Profile card (left panel) ── */
.profile-panel {{
    background: {CARDPURP};
    border: 2px solid {VIOLET};
    border-radius: 16px;
    padding: 20px 16px;
    min-height: 400px;
    text-align: center;
    position: sticky;
    top: 60px;
}}
.profile-avatar {{
    font-size: 4rem;
    width: 80px; height: 80px;
    border-radius: 50%;
    background: {VIOLET}33;
    border: 3px solid {VIOLET};
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 12px auto;
}}
.profile-name {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1rem;
    color: {WHITE};
    margin-bottom: 4px;
    letter-spacing: 0.04em;
}}
.profile-loc {{
    font-size: 0.75rem;
    color: {VIOLET};
    margin-bottom: 8px;
}}
.profile-followers {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1.4rem;
    color: {LIME};
}}
.profile-followers-label {{
    font-size: 0.65rem;
    color: {WHITE}88;
    letter-spacing: 0.1em;
}}
.panel-placeholder {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 300px;
    color: {VIOLET}88;
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    gap: 12px;
}}

/* ── Section headers ── */
.sec-header {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1.4rem;
    color: {LIME};
    letter-spacing: 0.12em;
    text-shadow: 0 0 16px {LIME}44;
    margin-bottom: 4px;
}}

/* ── Pending/Rejected list rows ── */
.seg-row {{
    background: {CARDPURP};
    border: 1px solid {VIOLET}44;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.seg-name {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.9rem;
    color: {WHITE};
    flex: 1;
}}
.seg-loc {{
    font-size: 0.75rem;
    color: {VIOLET};
    flex: 1;
}}

/* ── Divider ── */
.vdivider {{
    width: 2px;
    background: {VIOLET}55;
    border-radius: 2px;
    min-height: 400px;
    margin: 0 8px;
}}

/* ── Cafe name & location text ── */
.cafe-name {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.95rem;
    color: {WHITE};
    letter-spacing: 0.04em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.cafe-loc {{
    font-size: 0.72rem;
    color: {VIOLET};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* ── Empty state ── */
.empty-state {{
    text-align: center;
    padding: 60px 20px;
    color: {VIOLET}88;
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1rem;
    letter-spacing: 0.1em;
}}

/* ── Hide streamlit checkbox label ── */
.stCheckbox label span {{ display: none !important; }}
.stCheckbox {{ margin: 0 !important; padding: 0 !important; }}

/* ── Bottom tooltip fix: show above ── */
.tooltip-bottom {{
    top: calc(100% + 12px) !important;
    bottom: auto !important;
}}
.tooltip-arrow-bottom {{
    bottom: -12px !important;
    top: auto !important;
    border-bottom: none !important;
    border-top: 12px solid {VIOLET} !important;
}}
</style>
""", unsafe_allow_html=True)


# ── Session state init ───────────────────────────────────────────
def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "selected_cafe" not in st.session_state:
        st.session_state.selected_cafe = None
    if "checked" not in st.session_state:
        st.session_state.checked = {}
    if "initialized" not in st.session_state:
        # Seed main list if empty
        main = ds.load_main()
        if main.empty:
            cafes = get_dummy_cafes()
            ds.seed_main_list(cafes)
        st.session_state.initialized = True

init_state()


# ════════════════════════════════════════════════════════════════
#  HELPER: Build tooltip HTML
# ════════════════════════════════════════════════════════════════
def build_tooltip_gap(gap_labels):
    rows = ""
    n = len(gap_labels)
    max_val = max(
        [float(g.replace("D","").replace("H","")) * (24 if "D" in g else 1) for g in gap_labels],
        default=1
    )
    for i, g in enumerate(gap_labels):
        val_h = float(g.replace("D","").replace("H","")) * (24 if "D" in g else 1)
        pct = min(100, int(val_h / max(max_val,1) * 100))
        rows += f"""
        <div class='tooltip-row'>
            <span class='tooltip-num'>{i+1}</span>
            <div class='tooltip-line'>
                <div class='tooltip-dot' style='left:{pct}%'></div>
            </div>
            <span class='tooltip-val'>{g}</span>
        </div>"""
    return f"""
    <div class='tooltip'>
        <div class='tooltip-arrow'></div>
        <div class='tooltip-title'>AVERAGE POSTING GAP</div>
        <div class='tooltip-sub'>LAST 5 POSTS</div>
        {rows}
    </div>"""


def build_tooltip_eng(eng_rates):
    rows = ""
    max_val = max(eng_rates) if eng_rates else 1
    for i, r in enumerate(eng_rates):
        pct = min(100, int(r / max(max_val, 0.01) * 100))
        rows += f"""
        <div class='tooltip-row'>
            <span class='tooltip-num'>{i+1}</span>
            <div class='tooltip-line'>
                <div class='tooltip-dot' style='left:{pct}%'></div>
            </div>
            <span class='tooltip-val'>{r:.1f}%</span>
        </div>"""
    return f"""
    <div class='tooltip'>
        <div class='tooltip-arrow'></div>
        <div class='tooltip-title'>AVERAGE POSTING ENGAGEMENT</div>
        <div class='tooltip-sub'>LAST 5 POSTS</div>
        {rows}
    </div>"""


def build_tooltip_gain(weekly_gains):
    rows = ""
    max_abs = max([abs(g) for g in weekly_gains], default=1) or 1
    for i, g in enumerate(weekly_gains):
        pct = min(100, int(abs(g) / max_abs * 100))
        sign = "+" if g >= 0 else ""
        color = LIME if g >= 0 else RED
        rows += f"""
        <div class='tooltip-row'>
            <span class='tooltip-num'>{i+1}</span>
            <div class='tooltip-line'>
                <div class='tooltip-dot' style='left:{pct}%;background:{color}'></div>
            </div>
            <span class='tooltip-val' style='color:{color}'>{sign}{g}</span>
        </div>"""
    return f"""
    <div class='tooltip'>
        <div class='tooltip-arrow'></div>
        <div class='tooltip-title'>AVERAGE WEEKLY FOLLOWERS GAIN</div>
        <div class='tooltip-sub'>LAST 5 WEEKS</div>
        {rows}
    </div>"""


# ════════════════════════════════════════════════════════════════
#  HELPER: Profile card HTML
# ════════════════════════════════════════════════════════════════
def render_profile_card(cafe=None):
    if cafe is None:
        st.markdown(f"""
        <div class='profile-panel'>
            <div class='panel-placeholder'>
                <div style='font-size:2.5rem'>☕</div>
                <div>SELECT A CAFE TO</div>
                <div>VIEW PROFILE</div>
            </div>
        </div>""", unsafe_allow_html=True)
        return

    name = cafe.get("name","")
    loc  = cafe.get("location","")
    icon = cafe.get("profile_photo","☕")
    followers = cafe.get("follower_count", 0)
    fb_url  = cafe.get("facebook_url","#")
    ig_url  = cafe.get("instagram_url","")
    map_url = cafe.get("maps_url","#")
    msg_url = cafe.get("messenger_url","#")
    ig_btn  = f"<a href='{ig_url}' target='_blank' class='icon-btn btn-ig'>📷</a>" if ig_url else f"<span class='icon-btn btn-disabled'>📷</span>"

    avg_gap = cafe.get("avg_gap_days", 0)
    avg_eng = cafe.get("avg_engagement", 0)
    avg_gain= cafe.get("avg_gain", 0)

    gap_cls = "metric-bad" if cafe.get("gap_bad") else "metric-good"
    eng_cls = "metric-bad" if cafe.get("engagement_bad") else "metric-good"
    gn_cls  = "metric-bad" if cafe.get("gain_bad") else "metric-good"
    sign    = "+" if avg_gain >= 0 else ""

    st.markdown(f"""
    <div class='profile-panel'>
        <div class='profile-avatar'>{icon}</div>
        <div class='profile-name'>{name}</div>
        <div class='profile-loc'>📍 {loc}</div>
        <div style='margin:8px 0 4px 0'>
            <div class='profile-followers'>{followers:,}</div>
            <div class='profile-followers-label'>FOLLOWERS</div>
        </div>
        <div style='display:flex;gap:8px;justify-content:center;margin:14px 0 10px 0;flex-wrap:wrap'>
            <a href='{fb_url}' target='_blank' class='icon-btn btn-fb'>f</a>
            {ig_btn}
            <a href='{map_url}' target='_blank' class='icon-btn btn-map'>📍</a>
            <a href='{msg_url}' target='_blank' class='icon-btn btn-msg'>💬</a>
        </div>
        <div style='border-top:1px solid {VIOLET}44;padding-top:12px;margin-top:4px'>
            <div style='font-size:0.65rem;color:{VIOLET};letter-spacing:0.1em;margin-bottom:8px;font-family:Barlow,sans-serif'>METRICS SUMMARY</div>
            <div style='display:flex;gap:6px;justify-content:center;flex-wrap:wrap'>
                <div class='metric-box {gap_cls}' style='font-size:0.85rem;min-width:54px'>{cafe.get("gap_display","—")}</div>
                <div class='metric-box {eng_cls}' style='font-size:0.85rem;min-width:54px'>{avg_eng:.1f}%</div>
                <div class='metric-box {gn_cls}' style='font-size:0.85rem;min-width:54px'>{sign}{avg_gain:.1f}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  PAGE 1 — MAIN LIST
# ════════════════════════════════════════════════════════════════
def page_main():
    main_df = ds.load_main()

    # ── Top bar ─────────────────────────────────────────────────
    t1, t2, t3, t4, t5, t6, t7 = st.columns([2.2, 1.6, 1.8, 1.6, 1.4, 1.4, 1.2])

    with t1:
        st.markdown(f"""
        <div class='top-title'>CAFE ORBIT</div>
        <div class='top-subtitle'>☕ CAFE FINDER</div>
        """, unsafe_allow_html=True)

    with t2:
        if st.button("📣 BATCH OUTREACH", key="batch_btn",
                     help="Send Messenger DMs to all checked cafés"):
            checked_ids = [k for k,v in st.session_state.checked.items() if v]
            if not checked_ids:
                st.toast("⚠️ No cafés checked!", icon="⚠️")
            else:
                rows = main_df[main_df["id"].isin(checked_ids)]
                links = []
                for _, r in rows.iterrows():
                    links.append(r["messenger_url"])
                # Open all messenger links via JS
                js = "".join([f"window.open('{l}','_blank');" for l in links])
                st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)
                st.toast(f"✅ Opened {len(links)} Messenger chats!", icon="✅")
        st.markdown(f"<style>[data-testid='stButton']:nth-child(1) button{{background:{VIOLET};color:{WHITE};}}</style>", unsafe_allow_html=True)

    with t3:
        if st.button("📋 VIEW SEGREGATED LIST", key="seg_btn"):
            st.session_state.page = "segregated"
            st.rerun()

    with t4:
        csv_data = ds.get_main_as_csv_string()
        st.download_button(
            label="⬇ DOWNLOAD CSV",
            data=csv_data,
            file_name=f"cafe_orbit_leads_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="dl_btn"
        )

    with t5:
        refresh = st.button("🔄 REFRESH LIST", key="refresh_btn")
        st.markdown(f"<style>div[data-testid='column']:nth-child(6) button{{background:{LIME};color:{BLACK};}}</style>", unsafe_allow_html=True)

    with t6:
        delete = st.button("🗑 DELETE", key="delete_btn")
        st.markdown(f"<style>div[data-testid='column']:nth-child(7) button{{background:{RED};color:{WHITE};}}</style>", unsafe_allow_html=True)

    # Handle refresh
    if refresh:
        from dummy_data import get_dummy_cafes
        cafes = get_dummy_cafes()
        ds.seed_main_list(cafes)
        st.session_state.checked = {}
        st.session_state.selected_cafe = None
        st.toast("✅ List refreshed!", icon="☕")
        st.rerun()

    # Handle delete
    if delete:
        checked_ids = [k for k,v in st.session_state.checked.items() if v]
        if not checked_ids:
            st.toast("⚠️ No cafés checked!", icon="⚠️")
        else:
            ds.delete_from_main(checked_ids)
            for cid in checked_ids:
                st.session_state.checked.pop(cid, None)
            st.toast(f"🗑 Deleted {len(checked_ids)} café(s).", icon="🗑")
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Two-column layout: profile panel + list ──────────────────
    left_col, right_col = st.columns([1, 3.5])

    with left_col:
        render_profile_card(st.session_state.selected_cafe)

    with right_col:
        if main_df.empty:
            st.markdown(f"<div class='empty-state'>☕<br><br>NO CAFÉS IN LIST<br><br>CLICK REFRESH LIST TO LOAD</div>", unsafe_allow_html=True)
        else:
            # Column headers
            h1,h2,h3,h4,h5,h6,h7,h8,h9,h10 = st.columns([0.4,0.5,0.5,0.5,0.5,1.8,1.4,1.1,1.1,1.1])
            for col, label in zip([h6,h7,h8,h9,h10], ["CAFE","LOCATION","GAP","ENG%","GAIN"]):
                col.markdown(f"<div style='font-size:0.65rem;color:{VIOLET};letter-spacing:0.1em;font-family:Barlow,sans-serif;padding:0 4px'>{label}</div>", unsafe_allow_html=True)

            # ── Each café row ─────────────────────────────────────
            for _, row in main_df.iterrows():
                cid = row["id"]
                gap_labels = row["gap_labels"] if isinstance(row["gap_labels"], list) else json.loads(row["gap_labels"])
                eng_rates  = row["engagement_rates"] if isinstance(row["engagement_rates"], list) else json.loads(row["engagement_rates"])
                wk_gains   = row["weekly_follower_gains"] if isinstance(row["weekly_follower_gains"], list) else json.loads(row["weekly_follower_gains"])

                gap_cls = "metric-bad" if row["gap_bad"] else "metric-good"
                eng_cls = "metric-bad" if row["engagement_bad"] else "metric-good"
                gn_cls  = "metric-bad" if row["gain_bad"] else "metric-good"
                sign    = "+" if row["avg_gain"] >= 0 else ""

                tt_gap  = build_tooltip_gap(gap_labels)
                tt_eng  = build_tooltip_eng(eng_rates)
                tt_gain = build_tooltip_gain(wk_gains)

                c1,c2,c3,c4,c5,c6,c7,c8,c9,c10 = st.columns([0.4,0.5,0.5,0.5,0.5,1.8,1.4,1.1,1.1,1.1])

                # Checkbox
                with c1:
                    checked = st.checkbox("", key=f"chk_{cid}",
                                          value=st.session_state.checked.get(cid, False))
                    st.session_state.checked[cid] = checked

                # Social buttons
                with c2:
                    st.markdown(f"<a href='{row['facebook_url']}' target='_blank' class='icon-btn btn-fb' style='width:34px;height:34px;font-size:1rem;font-weight:900'>f</a>", unsafe_allow_html=True)
                with c3:
                    if row["instagram_url"]:
                        st.markdown(f"<a href='{row['instagram_url']}' target='_blank' class='icon-btn btn-ig' style='width:34px;height:34px;font-size:1rem'>📷</a>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span class='icon-btn btn-disabled' style='width:34px;height:34px;font-size:1rem'>📷</span>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<a href='{row['maps_url']}' target='_blank' class='icon-btn btn-map' style='width:34px;height:34px;font-size:1rem'>📍</a>", unsafe_allow_html=True)
                with c5:
                    st.markdown(f"<a href='{row['messenger_url']}' target='_blank' class='icon-btn btn-msg' style='width:34px;height:34px;font-size:1rem'>💬</a>", unsafe_allow_html=True)

                # Name & location — clicking updates profile panel
                with c6:
                    st.markdown(f"""
                    <div class='cafe-name'>{row['name']}</div>
                    <div class='cafe-loc'>📍 {row['location']}</div>
                    """, unsafe_allow_html=True)
                    if st.button("▶", key=f"sel_{cid}", help="View profile"):
                        st.session_state.selected_cafe = row.to_dict()
                        st.rerun()

                # Metric boxes with hover tooltips
                with c8:
                    st.markdown(f"""
                    <div class='metric-box {gap_cls}'>
                        {row['gap_display']}
                        {tt_gap}
                    </div>""", unsafe_allow_html=True)
                with c9:
                    st.markdown(f"""
                    <div class='metric-box {eng_cls}'>
                        {row['avg_engagement']:.1f}%
                        {tt_eng}
                    </div>""", unsafe_allow_html=True)
                with c10:
                    st.markdown(f"""
                    <div class='metric-box {gn_cls}'>
                        {sign}{row['avg_gain']:.0f}
                        {tt_gain}
                    </div>""", unsafe_allow_html=True)

                # Segregation arrows — in c7
                with c7:
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button("🟢", key=f"pend_{cid}", help="Move to Pending"):
                            ds.move_to_pending([cid])
                            st.session_state.checked.pop(cid, None)
                            if st.session_state.selected_cafe and st.session_state.selected_cafe.get("id") == cid:
                                st.session_state.selected_cafe = None
                            st.toast(f"✅ Moved to Pending", icon="🟢")
                            st.rerun()
                    with ac2:
                        if st.button("🔴", key=f"rej_{cid}", help="Move to Rejected"):
                            ds.move_to_rejected([cid])
                            st.session_state.checked.pop(cid, None)
                            if st.session_state.selected_cafe and st.session_state.selected_cafe.get("id") == cid:
                                st.session_state.selected_cafe = None
                            st.toast(f"❌ Moved to Rejected", icon="🔴")
                            st.rerun()

                st.markdown("<hr style='border:0;border-top:1px solid #1a0a2e;margin:2px 0'>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  PAGE 2 — SEGREGATED LIST (Pending + Rejected)
# ════════════════════════════════════════════════════════════════
def page_segregated():
    # Back button
    bc1, bc2 = st.columns([1, 5])
    with bc1:
        if st.button("← BACK TO MAIN", key="back_btn"):
            st.session_state.page = "main"
            st.rerun()

    st.markdown(f"<div style='height:10px'></div>", unsafe_allow_html=True)

    pending_df  = ds.load_pending()
    rejected_df = ds.load_rejected()

    left, div, right = st.columns([1, 0.05, 1])

    # ── PENDING LIST ────────────────────────────────────────────
    with left:
        st.markdown(f"<div class='sec-header'>PENDING LIST</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.7rem;color:{VIOLET};margin-bottom:12px;font-family:Barlow,sans-serif'>{len(pending_df)} CAFE(S)</div>", unsafe_allow_html=True)

        if pending_df.empty:
            st.markdown(f"<div class='empty-state' style='padding:30px'>NO PENDING CAFÉS</div>", unsafe_allow_html=True)
        else:
            for _, row in pending_df.iterrows():
                cid = row["id"]
                pc1, pc2, pc3, pc4 = st.columns([2, 2, 1, 1])
                with pc1:
                    st.markdown(f"<div class='seg-name'>{row['name']}</div>", unsafe_allow_html=True)
                with pc2:
                    st.markdown(f"<div class='seg-loc'>📍 {row['location']}</div>", unsafe_allow_html=True)
                with pc3:
                    if st.button("ADD", key=f"padd_{cid}"):
                        ds.move_pending_to_main([cid])
                        st.toast(f"✅ {row['name']} moved to Main List!", icon="✅")
                        st.rerun()
                with pc4:
                    if st.button("DELETE", key=f"pdel_{cid}"):
                        ds.delete_from_pending([cid])
                        st.toast(f"🗑 Deleted from Pending.", icon="🗑")
                        st.rerun()
                st.markdown("<hr style='border:0;border-top:1px solid #1a0a2e;margin:4px 0'>", unsafe_allow_html=True)

    # ── Divider ──────────────────────────────────────────────────
    with div:
        st.markdown(f"<div class='vdivider'></div>", unsafe_allow_html=True)

    # ── REJECTED LIST ────────────────────────────────────────────
    with right:
        st.markdown(f"<div class='sec-header' style='color:{RED};text-shadow:0 0 16px {RED}44'>REJECTED LIST</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.7rem;color:{RED}88;margin-bottom:12px;font-family:Barlow,sans-serif'>{len(rejected_df)} CAFE(S)</div>", unsafe_allow_html=True)

        if rejected_df.empty:
            st.markdown(f"<div class='empty-state' style='padding:30px'>NO REJECTED CAFÉS</div>", unsafe_allow_html=True)
        else:
            for _, row in rejected_df.iterrows():
                cid = row["id"]
                rc1, rc2, rc3, rc4 = st.columns([2, 2, 1, 1])
                with rc1:
                    st.markdown(f"<div class='seg-name'>{row['name']}</div>", unsafe_allow_html=True)
                with rc2:
                    st.markdown(f"<div class='seg-loc'>📍 {row['location']}</div>", unsafe_allow_html=True)
                with rc3:
                    if st.button("RECON", key=f"recon_{cid}"):
                        ds.move_rejected_to_pending([cid])
                        st.toast(f"🔄 {row['name']} moved to Pending!", icon="🔄")
                        st.rerun()
                with rc4:
                    if st.button("DELETE", key=f"rdel_{cid}"):
                        ds.delete_from_rejected([cid])
                        st.toast(f"🗑 Deleted from Rejected.", icon="🗑")
                        st.rerun()
                st.markdown("<hr style='border:0;border-top:1px solid #1a0a2e;margin:4px 0'>", unsafe_allow_html=True)

    # ── Style segregation buttons ────────────────────────────────
    st.markdown(f"""
    <style>
    /* ADD = lime green */
    button[kind="secondary"][data-testid*="padd"] {{ background:{LIME}!important;color:{BLACK}!important; }}
    /* RECON = lime green */
    button[kind="secondary"][data-testid*="recon"] {{ background:{LIME}!important;color:{BLACK}!important; }}
    /* DELETE = red */
    button[kind="secondary"][data-testid*="pdel"],
    button[kind="secondary"][data-testid*="rdel"] {{ background:{RED}!important;color:{WHITE}!important; }}
    </style>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  ROUTER
# ════════════════════════════════════════════════════════════════
def apply_button_styles():
    """Apply color overrides to named buttons."""
    st.markdown(f"""
    <style>
    /* Batch Outreach = violet */
    div[data-testid="column"]:nth-child(2) button {{ background:{VIOLET}!important;color:{WHITE}!important; }}
    /* View Segregated = dark */
    div[data-testid="column"]:nth-child(3) button {{ background:#222!important;color:{WHITE}!important;border:1px solid {VIOLET}!important; }}
    /* Download CSV = dark violet */
    div[data-testid="column"]:nth-child(4) button,
    div[data-testid="column"]:nth-child(4) .stDownloadButton button {{ background:#2d1060!important;color:{WHITE}!important; }}
    /* Refresh = lime */
    div[data-testid="column"]:nth-child(5) button {{ background:{LIME}!important;color:{BLACK}!important; }}
    /* Delete = red */
    div[data-testid="column"]:nth-child(6) button {{ background:{RED}!important;color:{WHITE}!important; }}
    /* Row select arrow */
    button[data-testid*="sel_"] {{ background:transparent!important;color:{VIOLET}!important;border:none!important;width:auto!important;padding:0!important;font-size:0.8rem!important; }}
    /* Green/red arrow buttons */
    button[data-testid*="pend_"] {{ background:transparent!important;border:none!important;font-size:1.2rem!important;width:auto!important; }}
    button[data-testid*="rej_"]  {{ background:transparent!important;border:none!important;font-size:1.2rem!important;width:auto!important; }}
    /* Back button */
    button[data-testid="back_btn"] {{ background:#222!important;color:{WHITE}!important;border:1px solid {VIOLET}!important; }}
    /* Pending ADD */
    button[data-testid*="padd_"] {{ background:{LIME}!important;color:{BLACK}!important;font-family:'Black Han Sans',sans-serif!important; }}
    /* Pending DELETE */
    button[data-testid*="pdel_"] {{ background:{RED}!important;color:{WHITE}!important;font-family:'Black Han Sans',sans-serif!important; }}
    /* Rejected RECON */
    button[data-testid*="recon_"] {{ background:{LIME}!important;color:{BLACK}!important;font-family:'Black Han Sans',sans-serif!important; }}
    /* Rejected DELETE */
    button[data-testid*="rdel_"] {{ background:{RED}!important;color:{WHITE}!important;font-family:'Black Han Sans',sans-serif!important; }}
    </style>
    """, unsafe_allow_html=True)


if st.session_state.page == "main":
    page_main()
elif st.session_state.page == "segregated":
    page_segregated()

apply_button_styles()
