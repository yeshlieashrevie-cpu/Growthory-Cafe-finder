import os
import json
import sqlite3
import requests
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Growthory CRM",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# HIDE STREAMLIT UI
# =========================================================

st.markdown("""
<style>

#MainMenu {
    visibility:hidden;
}

header {
    visibility:hidden;
}

footer {
    visibility:hidden;
}

.block-container{
    padding-top:0rem;
    padding-bottom:0rem;
    padding-left:0rem;
    padding-right:0rem;
    max-width:100%;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================

DB_NAME = "cafes.db"

# =========================================================
# SQLITE INIT
# =========================================================

def init_db():

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS cafes (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,
        location TEXT,

        facebook_url TEXT,
        instagram_url TEXT,
        messenger_url TEXT,
        map_url TEXT,

        avg_gap_days REAL,
        avg_engagement REAL,
        weekly_followers INTEGER,

        posting_history TEXT,
        engagement_history TEXT,
        followers_history TEXT,

        status TEXT DEFAULT 'main',

        created_at TEXT
    )
    """)

    conn.commit()

    conn.close()

init_db()

# =========================================================
# DEMO DATA
# =========================================================

def seed_demo_data():

    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()

    c.execute(
        "SELECT COUNT(*) FROM cafes"
    )

    count = c.fetchone()[0]

    if count == 0:

        cafes = [

            (
                "Brewed Awakening",
                "Makati",
                "https://facebook.com",
                "https://instagram.com",
                "https://m.me",
                "https://maps.google.com",
                3.2,
                11.4,
                18,
                json.dumps([2,3,4,3,4]),
                json.dumps([8,12,10,15,11]),
                json.dumps([100,120,130,145,163]),
                "main",
                datetime.now().isoformat()
            ),

            (
                "Roast Republic",
                "Taguig",
                "https://facebook.com",
                "https://instagram.com",
                "https://m.me",
                "https://maps.google.com",
                7.1,
                4.3,
                -3,
                json.dumps([8,7,6,7,8]),
                json.dumps([4,3,5,4,5]),
                json.dumps([200,190,188,185,182]),
                "main",
                datetime.now().isoformat()
            )
        ]

        c.executemany("""
        INSERT INTO cafes (

            name,
            location,

            facebook_url,
            instagram_url,
            messenger_url,
            map_url,

            avg_gap_days,
            avg_engagement,
            weekly_followers,

            posting_history,
            engagement_history,
            followers_history,

            status,
            created_at

        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, cafes)

        conn.commit()

    conn.close()

seed_demo_data()

# =========================================================
# GET CAFES
# =========================================================

def get_cafes():

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM cafes
    ORDER BY avg_engagement DESC
    """)

    rows = [
        dict(x)
        for x in c.fetchall()
    ]

    conn.close()

    return rows

# =========================================================
# META CONFIG
# =========================================================

try:

    META_ACCESS_TOKEN = st.secrets[
        "META_ACCESS_TOKEN"
    ]

except:

    META_ACCESS_TOKEN = ""

# =========================================================
# LOAD FRONTEND FILES
# =========================================================

with open(
    "index.html",
    "r",
    encoding="utf-8"
) as f:

    html = f.read()

with open(
    "style.css",
    "r",
    encoding="utf-8"
) as f:

    css = f.read()

with open(
    "script.js",
    "r",
    encoding="utf-8"
) as f:

    js = f.read()

# =========================================================
# INJECT DATA
# =========================================================

cafes_data = get_cafes()

injected_data = f"""

window.CAFE_DATA = {json.dumps(cafes_data)};

"""

# =========================================================
# FINAL PAGE
# =========================================================

final_page = f"""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
/>

<title>Growthory CRM</title>

<link
href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
rel="stylesheet"
/>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

{css}

</style>

</head>

<body>

{html}

<script>

{injected_data}

</script>

<script>

{js}

</script>

</body>

</html>

"""

# =========================================================
# SIDEBAR STATUS
# =========================================================

with st.sidebar:

    st.title("Growthory CRM")

    st.success("Frontend Loaded")

    if META_ACCESS_TOKEN:

        st.success(
            "Meta Connected"
        )

    else:

        st.warning(
            "Meta Token Missing"
        )

# =========================================================
# RENDER APP
# =========================================================

components.html(
    final_page,
    height=5000,
    scrolling=True
)
