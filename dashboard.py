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

# ── Constants ────────────────────────────────────────────────────
BLACK    = "#000000"
VIOLET   = "#7D39EB"
LIME     = "#C6FF33"
WHITE    = "#FFFFFF"
RED      = "#FF2222"
CARDPURP = "#1a0a2e"

# YOUR personal links — FB/IG buttons always open these
MY_FACEBOOK  = "https://www.facebook.com/share/1V3QgrCcC5/"
MY_INSTAGRAM = "https://www.instagram.com/invites/contact/?utm_source=ig_contact_invite&utm_medium=copy_link&utm_content=epdw1ve"

# ── Global CSS ───────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Barlow:wght@400;700;900&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    background: {BLACK} !important;
    color: {WHITE} !important;
    font-family: 'Barlow', sans-serif !important;
}}
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="stHeader"] {{ background: transparent !important; }}
footer {{ visibility: hidden !important; }}
.block-container {{ padding: 0.5rem 1rem 2rem 1rem !important; max-width: 100% !important; }}

::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {BLACK}; }}
::-webkit-scrollbar-thumb {{ background: {VIOLET}; border-radius: 3px; }}

/* ── FIX 1: Bigger clickable buttons ── */
.stButton > button {{
    font-family: 'Black Han Sans', sans-serif !important;
    font-weight: 900 !important;
    letter-spacing: 0.08em !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.65rem 1.2rem !important;
    font-size: 0.82rem !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
    min-height: 42px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    filter: brightness(1.15) !important;
    box-shadow: 0 4px 16px rgba(125,57,235,0.4) !important;
}}
.stDownloadButton > button {{
    font-family: 'Black Han Sans', sans-serif !important;
    font-weight: 900 !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.65rem 1.2rem !important;
    font-size: 0.82rem !important;
    min-height: 42px !important;
    width: 100% !important;
    background: #2d1060 !important;
    color: {WHITE} !important;
    cursor: pointer !important;
}}
.stDownloadButton > button:hover {{
    filter: brightness(1.2) !important;
    transform: translateY(-2px) !important;
}}

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

/* ── FIX 2: Icon buttons — larger hit area ── */
.icon-btn {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 10px;
    font-size: 1.2rem;
    text-decoration: none !important;
    transition: transform 0.15s, filter 0.15s;
    cursor: pointer;
    font-weight: 900;
}}
.icon-btn:hover {{ transform: scale(1.12); filter: brightness(1.2); }}
.btn-fb  {{ background: #1877F2; color: white !important; }}
.btn-ig  {{ background: linear-gradient(135deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); color: white !important; }}
.btn-map {{ background: {WHITE}; color: #EA4335 !important; }}
.btn-msg {{ background: linear-gradient(135deg,#0084FF,#00C6FF); color: white !important; }}
.btn-disabled {{ background: #222; color: #555 !important; cursor: not-allowed; }}

/* ── FIX 3: Metric box tooltips — pure CSS hover, properly scoped ── */
.metric-wrap {{
    position: relative;
    display: inline-block;
    width: 100%;
}}
.metric-box {{
    border-radius: 8px;
    padding: 8px 6px;
    text-align: center;
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1rem;
    font-weight: 900;
    letter-spacing: 0.05em;
    cursor: default;
    width: 100%;
    transition: transform 0.15s;
    user-select: none;
    box-sizing: border-box;
}}
.metric-box:hover {{ transform: scale(1.06); }}
.metric-good {{ background: {LIME}; color: {BLACK}; }}
.metric-bad  {{ background: {RED};  color: {WHITE}; }}

/* Tooltip hidden by default */
.tt-popup {{
    visibility: hidden;
    opacity: 0;
    position: absolute;
    bottom: calc(100% + 14px);
    left: 50%;
    transform: translateX(-50%);
    background: #000;
    border: 2px solid {VIOLET};
    border-radius: 12px;
    padding: 14px 18px;
    min-width: 240px;
    z-index: 99999;
    pointer-events: none;
    box-shadow: 0 8px 32px {VIOLET}88;
    transition: opacity 0.18s ease, visibility 0.18s ease;
    white-space: nowrap;
}}
/* Arrow pointing down from tooltip */
.tt-popup::after {{
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 8px solid transparent;
    border-top-color: {VIOLET};
}}
/* Show on hover of the WRAP */
.metric-wrap:hover .tt-popup {{
    visibility: visible;
    opacity: 1;
}}
.tt-title {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.72rem;
    color: {WHITE};
    letter-spacing: 0.12em;
    text-align: center;
    margin-bottom: 2px;
}}
.tt-sub {{
    font-family: 'Barlow', sans-serif;
    font-size: 0.62rem;
    color: {VIOLET};
    letter-spacing: 0.1em;
    text-align: center;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid {VIOLET}55;
}}
.tt-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 5px 0;
}}
.tt-num {{
    color: {WHITE}88;
    font-family: 'Barlow', sans-serif;
    font-size: 0.7rem;
    min-width: 14px;
    text-align: right;
}}
.tt-bar-wrap {{
    flex: 1;
    height: 6px;
    background: {VIOLET}22;
    border-radius: 3px;
    overflow: hidden;
}}
.tt-bar {{
    height: 100%;
    border-radius: 3px;
    background: {LIME};
    transition: width 0.3s;
}}
.tt-bar-bad {{ background: {RED}; }}
.tt-val {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.85rem;
    min-width: 44px;
    text-align: right;
}}

/* ── Cafe row ── */
.cafe-row {{
    background: {CARDPURP};
    border: 1px solid {VIOLET}33;
    border-radius: 10px;
    padding: 8px 10px;
    margin-bottom: 6px;
    transition: border-color 0.2s;
}}
.cafe-row:hover {{ border-color: {VIOLET}; }}
.cafe-name {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.92rem;
    color: {WHITE};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.cafe-loc {{
    font-size: 0.7rem;
    color: {VIOLET};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* ── Profile panel ── */
.profile-panel {{
    background: {CARDPURP};
    border: 2px solid {VIOLET};
    border-radius: 16px;
    padding: 18px 14px;
    min-height: 380px;
    text-align: center;
    position: sticky;
    top: 60px;
}}
.profile-avatar {{
    font-size: 3rem;
    width: 72px; height: 72px;
    border-radius: 50%;
    background: {VIOLET}33;
    border: 3px solid {VIOLET};
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 10px auto;
}}
.profile-name {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.95rem;
    color: {WHITE};
    margin-bottom: 4px;
}}
.profile-loc {{
    font-size: 0.72rem;
    color: {VIOLET};
    margin-bottom: 10px;
}}
.profile-followers {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1.5rem;
    color: {LIME};
}}
.profile-followers-label {{
    font-size: 0.62rem;
    color: {WHITE}88;
    letter-spacing: 0.1em;
    margin-bottom: 14px;
}}
.panel-placeholder {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 280px;
    color: {VIOLET}66;
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    gap: 10px;
}}

/* ── Seg page ── */
.sec-header {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1.4rem;
    color: {LIME};
    letter-spacing: 0.1em;
    text-shadow: 0 0 16px {LIME}44;
    margin-bottom: 4px;
}}
.seg-name {{
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.88rem;
    color: {WHITE};
}}
.seg-loc {{
    font-size: 0.72rem;
    color: {VIOLET};
}}
.vdivider {{
    width: 2px;
    background: {VIOLET}44;
    border-radius: 2px;
    min-height: 400px;
    margin: 0 6px;
}}
.empty-state {{
    text-align: center;
    padding: 50px 20px;
    color: {VIOLET}66;
    font-family: 'Black Han Sans', sans-serif;
    font-size: 0.9rem;
    letter-spacing: 0.1em;
}}

/* Hide streamlit checkbox label text */
.stCheckbox label p {{ display: none !important; }}
.stCheckbox {{ margin: 0 !important; padding: 0 !important; }}
.stCheckbox > label {{ padding: 0 !important; min-height: 44px !important; display: flex !important; align-items: center !important; }}
</style>
""", unsafe_allow_html=True)


# ── Session state ────────────────────────────────────────────────
def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "selected_cafe" not in st.session_state:
        st.session_state.selected_cafe = None
    if "checked" not in st.session_state:
        st.session_state.checked = {}
    if "initialized" not in st.session_state:
        main = ds.load_main()
        if main.empty:
            ds.seed_main_list(get_dummy_cafes())
        st.session_state.initialized = True

init_state()


# ════════════════════════════════════════════════════════════════
#  TOOLTIP BUILDERS — proper visual bar charts
# ════════════════════════════════════════════════════════════════
def _tt_rows(labels, values, max_val, bad_fn, suffix=""):
    rows = ""
    for i, (lbl, val) in enumerate(zip(labels, values)):
        pct = min(100, int(abs(val) / max(abs(max_val), 0.01) * 100))
        bad = bad_fn(val)
        bar_cls = "tt-bar-bad" if bad else "tt-bar"
        color = RED if bad else LIME
        rows += f"""
        <div class='tt-row'>
            <span class='tt-num'>{i+1}</span>
            <div class='tt-bar-wrap'><div class='{bar_cls}' style='width:{pct}%'></div></div>
            <span class='tt-val' style='color:{color}'>{lbl}</span>
        </div>"""
    return rows


def build_tt_gap(gap_labels, gap_hours):
    max_v = max(gap_hours) if gap_hours else 1
    rows  = _tt_rows(gap_labels, gap_hours, max_v, lambda v: v > 120)
    return f"""
    <div class='tt-popup'>
        <div class='tt-title'>AVERAGE POSTING GAP</div>
        <div class='tt-sub'>LAST 5 POSTS</div>
        {rows}
    </div>"""


def build_tt_eng(eng_rates):
    max_v = max(eng_rates) if eng_rates else 1
    lbls  = [f"{r:.1f}%" for r in eng_rates]
    rows  = _tt_rows(lbls, eng_rates, max_v, lambda v: v < 3.0)
    return f"""
    <div class='tt-popup'>
        <div class='tt-title'>AVERAGE POSTING ENGAGEMENT</div>
        <div class='tt-sub'>LAST 5 POSTS</div>
        {rows}
    </div>"""


def build_tt_gain(weekly_gains):
    max_v = max(abs(g) for g in weekly_gains) if weekly_gains else 1
    sign  = lambda v: f"+{v}" if v >= 0 else str(v)
    lbls  = [sign(g) for g in weekly_gains]
    rows  = _tt_rows(lbls, weekly_gains, max_v, lambda v: v < 3)
    return f"""
    <div class='tt-popup'>
        <div class='tt-title'>AVERAGE WEEKLY FOLLOWERS GAIN</div>
        <div class='tt-sub'>LAST 5 WEEKS</div>
        {rows}
    </div>"""


# ════════════════════════════════════════════════════════════════
#  PROFILE CARD
# ════════════════════════════════════════════════════════════════
def render_profile_card(cafe=None):
    if cafe is None:
        st.markdown(f"""
        <div class='profile-panel'>
            <div class='panel-placeholder'>
                <div style='font-size:2.5rem'>☕</div>
                <div>CLICK ▶ ON A CAFE</div>
                <div>TO VIEW PROFILE</div>
            </div>
        </div>""", unsafe_allow_html=True)
        return

    name      = cafe.get("name", "")
    loc       = cafe.get("location", "")
    icon      = cafe.get("profile_photo", "☕")
    followers = cafe.get("follower_count", 0)
    map_url   = cafe.get("maps_url", "#")
    msg_url   = cafe.get("messenger_url", "#")
    avg_eng   = cafe.get("avg_engagement", 0)
    avg_gain  = cafe.get("avg_gain", 0)
    sign      = "+" if avg_gain >= 0 else ""

    gap_cls = "metric-bad" if cafe.get("gap_bad") else "metric-good"
    eng_cls = "metric-bad" if cafe.get("engagement_bad") else "metric-good"
    gn_cls  = "metric-bad" if cafe.get("gain_bad") else "metric-good"

    st.markdown(f"""
    <div class='profile-panel'>
        <div class='profile-avatar'>{icon}</div>
        <div class='profile-name'>{name}</div>
        <div class='profile-loc'>📍 {loc}</div>
        <div class='profile-followers'>{followers:,}</div>
        <div class='profile-followers-label'>FOLLOWERS</div>
        <div style='display:flex;gap:10px;justify-content:center;margin:12px 0 14px 0;flex-wrap:wrap'>
            <a href='{MY_FACEBOOK}' target='_blank' class='icon-btn btn-fb'>f</a>
            <a href='{MY_INSTAGRAM}' target='_blank' class='icon-btn btn-ig'>📷</a>
            <a href='{map_url}' target='_blank' class='icon-btn btn-map'>📍</a>
            <a href='{msg_url}' target='_blank' class='icon-btn btn-msg'>💬</a>
        </div>
        <div style='border-top:1px solid {VIOLET}44;padding-top:12px'>
            <div style='font-size:0.62rem;color:{VIOLET};letter-spacing:0.1em;margin-bottom:8px'>METRICS SUMMARY</div>
            <div style='display:flex;gap:6px;justify-content:center'>
                <div class='metric-box {gap_cls}' style='min-width:60px;font-size:0.85rem'>{cafe.get("gap_display","—")}</div>
                <div class='metric-box {eng_cls}' style='min-width:60px;font-size:0.85rem'>{avg_eng:.1f}%</div>
                <div class='metric-box {gn_cls}'  style='min-width:60px;font-size:0.85rem'>{sign}{avg_gain:.1f}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  PAGE 1 — MAIN LIST
# ════════════════════════════════════════════════════════════════
def page_main():
    main_df = ds.load_main()

    # ── Top bar ──────────────────────────────────────────────────
    t1, t2, t3, t4, t5, t6 = st.columns([2, 1.7, 1.9, 1.7, 1.5, 1.3])

    with t1:
        st.markdown(f"""
        <div class='top-title'>CAFE ORBIT</div>
        <div class='top-subtitle'>☕ CAFE FINDER</div>
        """, unsafe_allow_html=True)

    with t2:
        if st.button("📣 BATCH OUTREACH", key="batch_btn"):
            checked_ids = [k for k, v in st.session_state.checked.items() if v]
            if not checked_ids:
                st.toast("⚠️ No cafés checked!", icon="⚠️")
            else:
                rows = main_df[main_df["id"].isin(checked_ids)]
                js   = "".join([f"window.open('{r}','_blank');" for r in rows["messenger_url"]])
                st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)
                st.toast(f"✅ Opened {len(checked_ids)} Messenger chats!", icon="✅")

    with t3:
        if st.button("📋 VIEW SEGREGATED LIST", key="seg_btn"):
            st.session_state.page = "segregated"
            st.rerun()

    with t4:
        st.download_button(
            label="⬇ DOWNLOAD CSV",
            data=ds.get_main_as_csv_string(),
            file_name=f"cafe_orbit_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="dl_btn",
        )

    with t5:
        if st.button("🔄 REFRESH LIST", key="refresh_btn"):
            ds.seed_main_list(get_dummy_cafes())
            st.session_state.checked = {}
            st.session_state.selected_cafe = None
            st.toast("✅ List refreshed!", icon="☕")
            st.rerun()

    with t6:
        if st.button("🗑 DELETE", key="delete_btn"):
            checked_ids = [k for k, v in st.session_state.checked.items() if v]
            if not checked_ids:
                st.toast("⚠️ No cafés checked!", icon="⚠️")
            else:
                ds.delete_from_main(checked_ids)
                for cid in checked_ids:
                    st.session_state.checked.pop(cid, None)
                st.toast(f"🗑 Deleted {len(checked_ids)} café(s).", icon="🗑")
                st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Two-column layout ────────────────────────────────────────
    left_col, right_col = st.columns([1, 3.6])

    with left_col:
        render_profile_card(st.session_state.selected_cafe)

    with right_col:
        if main_df.empty:
            st.markdown(f"<div class='empty-state'>☕<br><br>NO CAFÉS IN LIST<br>CLICK REFRESH LIST TO LOAD</div>",
                        unsafe_allow_html=True)
            return

        # Column headers
        hcols = st.columns([0.45, 0.5, 0.5, 0.5, 0.5, 1.9, 1.2, 1.0, 1.0, 1.0])
        for col, lbl in zip(hcols[5:], ["CAFE / LOCATION", "ARROWS", "GAP", "ENG %", "GAIN"]):
            col.markdown(f"<div style='font-size:0.62rem;color:{VIOLET};letter-spacing:0.1em;padding:0 2px'>{lbl}</div>",
                         unsafe_allow_html=True)

        # ── Rows ─────────────────────────────────────────────────
        for _, row in main_df.iterrows():
            cid = row["id"]

            gap_labels = row["gap_labels"]   if isinstance(row["gap_labels"], list)              else json.loads(row["gap_labels"])
            eng_rates  = row["engagement_rates"] if isinstance(row["engagement_rates"], list)    else json.loads(row["engagement_rates"])
            wk_gains   = row["weekly_follower_gains"] if isinstance(row["weekly_follower_gains"], list) else json.loads(row["weekly_follower_gains"])
            gap_hours  = row["posting_gaps"] if isinstance(row["posting_gaps"], list)            else json.loads(row["posting_gaps"])

            gap_cls = "metric-bad" if row["gap_bad"] else "metric-good"
            eng_cls = "metric-bad" if row["engagement_bad"] else "metric-good"
            gn_cls  = "metric-bad" if row["gain_bad"] else "metric-good"
            sign    = "+" if row["avg_gain"] >= 0 else ""

            tt_gap  = build_tt_gap(gap_labels, gap_hours)
            tt_eng  = build_tt_eng(eng_rates)
            tt_gain = build_tt_gain(wk_gains)

            c = st.columns([0.45, 0.5, 0.5, 0.5, 0.5, 1.9, 1.2, 1.0, 1.0, 1.0])

            # Checkbox — bigger touch area via CSS
            with c[0]:
                checked = st.checkbox("", key=f"chk_{cid}",
                                      value=st.session_state.checked.get(cid, False))
                st.session_state.checked[cid] = checked

            # ── FIX: FB/IG always open YOUR pages ──
            with c[1]:
                st.markdown(
                    f"<a href='{MY_FACEBOOK}' target='_blank' "
                    f"class='icon-btn btn-fb' title='Open your Facebook'>f</a>",
                    unsafe_allow_html=True)
            with c[2]:
                st.markdown(
                    f"<a href='{MY_INSTAGRAM}' target='_blank' "
                    f"class='icon-btn btn-ig' title='Open your Instagram'>📷</a>",
                    unsafe_allow_html=True)
            with c[3]:
                st.markdown(
                    f"<a href='{row['maps_url']}' target='_blank' "
                    f"class='icon-btn btn-map' title='Open Maps'>📍</a>",
                    unsafe_allow_html=True)
            with c[4]:
                st.markdown(
                    f"<a href='{row['messenger_url']}' target='_blank' "
                    f"class='icon-btn btn-msg' title='Open Messenger'>💬</a>",
                    unsafe_allow_html=True)

            # Name + location + select button
            with c[5]:
                col_name, col_sel = st.columns([4, 1])
                with col_name:
                    st.markdown(f"""
                    <div class='cafe-name'>{row['name']}</div>
                    <div class='cafe-loc'>📍 {row['location']}</div>
                    """, unsafe_allow_html=True)
                with col_sel:
                    if st.button("▶", key=f"sel_{cid}", help="View profile"):
                        st.session_state.selected_cafe = row.to_dict()
                        st.rerun()

            # Green / Red segregation arrows
            with c[6]:
                a1, a2 = st.columns(2)
                with a1:
                    if st.button("🟢", key=f"pend_{cid}", help="Pending"):
                        ds.move_to_pending([cid])
                        st.session_state.checked.pop(cid, None)
                        if st.session_state.selected_cafe and \
                           st.session_state.selected_cafe.get("id") == cid:
                            st.session_state.selected_cafe = None
                        st.toast("✅ Moved to Pending", icon="🟢")
                        st.rerun()
                with a2:
                    if st.button("🔴", key=f"rej_{cid}", help="Rejected"):
                        ds.move_to_rejected([cid])
                        st.session_state.checked.pop(cid, None)
                        if st.session_state.selected_cafe and \
                           st.session_state.selected_cafe.get("id") == cid:
                            st.session_state.selected_cafe = None
                        st.toast("❌ Moved to Rejected", icon="🔴")
                        st.rerun()

            # ── FIX: Metric boxes with working hover tooltips ──
            with c[7]:
                st.markdown(f"""
                <div class='metric-wrap'>
                    <div class='metric-box {gap_cls}'>{row['gap_display']}</div>
                    {tt_gap}
                </div>""", unsafe_allow_html=True)

            with c[8]:
                st.markdown(f"""
                <div class='metric-wrap'>
                    <div class='metric-box {eng_cls}'>{row['avg_engagement']:.1f}%</div>
                    {tt_eng}
                </div>""", unsafe_allow_html=True)

            with c[9]:
                st.markdown(f"""
                <div class='metric-wrap'>
                    <div class='metric-box {gn_cls}'>{sign}{row['avg_gain']:.0f}</div>
                    {tt_gain}
                </div>""", unsafe_allow_html=True)

            st.markdown(
                "<hr style='border:0;border-top:1px solid #140824;margin:3px 0'>",
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  PAGE 2 — SEGREGATED LIST
# ════════════════════════════════════════════════════════════════
def page_segregated():
    bc1, _ = st.columns([1.2, 5])
    with bc1:
        if st.button("← BACK TO MAIN", key="back_btn"):
            st.session_state.page = "main"
            st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    pending_df  = ds.load_pending()
    rejected_df = ds.load_rejected()

    left, div, right = st.columns([1, 0.04, 1])

    # ── PENDING ──────────────────────────────────────────────────
    with left:
        st.markdown(f"<div class='sec-header'>PENDING LIST</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.68rem;color:{VIOLET};margin-bottom:10px'>{len(pending_df)} CAFE(S)</div>",
                    unsafe_allow_html=True)
        if pending_df.empty:
            st.markdown("<div class='empty-state'>NO PENDING CAFÉS</div>", unsafe_allow_html=True)
        else:
            for _, row in pending_df.iterrows():
                cid = row["id"]
                pc = st.columns([2.2, 2, 1, 1])
                with pc[0]:
                    st.markdown(f"<div class='seg-name'>{row['name']}</div>", unsafe_allow_html=True)
                with pc[1]:
                    st.markdown(f"<div class='seg-loc'>📍 {row['location']}</div>", unsafe_allow_html=True)
                with pc[2]:
                    if st.button("ADD", key=f"padd_{cid}"):
                        ds.move_pending_to_main([cid])
                        st.toast(f"✅ Added to Main List!", icon="✅")
                        st.rerun()
                with pc[3]:
                    if st.button("DELETE", key=f"pdel_{cid}"):
                        ds.delete_from_pending([cid])
                        st.toast("🗑 Deleted.", icon="🗑")
                        st.rerun()
                st.markdown("<hr style='border:0;border-top:1px solid #1a0a2e;margin:4px 0'>",
                            unsafe_allow_html=True)

    with div:
        st.markdown(f"<div class='vdivider'></div>", unsafe_allow_html=True)

    # ── REJECTED ─────────────────────────────────────────────────
    with right:
        st.markdown(f"<div class='sec-header' style='color:{RED};text-shadow:0 0 16px {RED}44'>REJECTED LIST</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.68rem;color:{RED}88;margin-bottom:10px'>{len(rejected_df)} CAFE(S)</div>",
                    unsafe_allow_html=True)
        if rejected_df.empty:
            st.markdown("<div class='empty-state'>NO REJECTED CAFÉS</div>", unsafe_allow_html=True)
        else:
            for _, row in rejected_df.iterrows():
                cid = row["id"]
                rc = st.columns([2.2, 2, 1, 1])
                with rc[0]:
                    st.markdown(f"<div class='seg-name'>{row['name']}</div>", unsafe_allow_html=True)
                with rc[1]:
                    st.markdown(f"<div class='seg-loc'>📍 {row['location']}</div>", unsafe_allow_html=True)
                with rc[2]:
                    if st.button("RECON", key=f"recon_{cid}"):
                        ds.move_rejected_to_pending([cid])
                        st.toast("🔄 Moved to Pending!", icon="🔄")
                        st.rerun()
                with rc[3]:
                    if st.button("DELETE", key=f"rdel_{cid}"):
                        ds.delete_from_rejected([cid])
                        st.toast("🗑 Deleted.", icon="🗑")
                        st.rerun()
                st.markdown("<hr style='border:0;border-top:1px solid #1a0a2e;margin:4px 0'>",
                            unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  BUTTON COLOR OVERRIDES
# ════════════════════════════════════════════════════════════════
def apply_button_styles():
    st.markdown(f"""
    <style>
    /* Top bar buttons */
    div[data-testid="column"]:nth-child(2) .stButton button {{ background:{VIOLET}!important;color:{WHITE}!important; }}
    div[data-testid="column"]:nth-child(3) .stButton button {{ background:#1a1a2e!important;color:{WHITE}!important;border:1px solid {VIOLET}!important; }}
    div[data-testid="column"]:nth-child(5) .stButton button {{ background:{LIME}!important;color:{BLACK}!important; }}
    div[data-testid="column"]:nth-child(6) .stButton button {{ background:{RED}!important;color:{WHITE}!important; }}
    /* Row select arrow — transparent */
    button[data-testid*="sel_"] {{
        background:transparent!important;color:{VIOLET}!important;
        border:none!important;width:auto!important;
        padding:4px!important;font-size:0.85rem!important;
        min-height:32px!important;
    }}
    /* Segregation arrows — transparent */
    button[data-testid*="pend_"],
    button[data-testid*="rej_"]  {{
        background:transparent!important;border:none!important;
        font-size:1.3rem!important;width:auto!important;
        min-height:36px!important;padding:2px!important;
    }}
    /* Back button */
    button[data-testid="back_btn"] {{
        background:#1a1a2e!important;color:{WHITE}!important;
        border:1px solid {VIOLET}!important;
    }}
    /* ADD / RECON = lime */
    button[data-testid*="padd_"],
    button[data-testid*="recon_"] {{
        background:{LIME}!important;color:{BLACK}!important;
        font-family:'Black Han Sans',sans-serif!important;
    }}
    /* DELETE = red */
    button[data-testid*="pdel_"],
    button[data-testid*="rdel_"]  {{
        background:{RED}!important;color:{WHITE}!important;
        font-family:'Black Han Sans',sans-serif!important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ── Router ───────────────────────────────────────────────────────
if st.session_state.page == "main":
    page_main()
elif st.session_state.page == "segregated":
    page_segregated()

apply_button_styles()
