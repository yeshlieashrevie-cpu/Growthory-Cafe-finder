import os
import json
import sqlite3
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Growthory CRM",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# HIDE STREAMLIT DEFAULT UI
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
# DATABASE HELPERS
# =========================================================

def get_connection():

    return sqlite3.connect(DB_NAME)

# =========================================================
# INIT DATABASE
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

# =========================================================
# SEED STARTER CAFES
# =========================================================

def seed_starter_cafes():

    conn = get_connection()

    c = conn.cursor()

    c.execute(
        "SELECT COUNT(*) FROM cafes"
    )

    count = c.fetchone()[0]

    if count == 0:

        cafes = [

            (
                "Yardstick Coffee",
                "Makati",
                "https://facebook.com",
                "https://instagram.com/yardstickcoffee",
                "https://m.me",
                "https://maps.google.com",
                3.1,
                12.4,
                18,
                json.dumps([2,3,4,3,4]),
                json.dumps([8,12,10,15,11]),
                json.dumps([100,120,130,145,163]),
                "main",
                datetime.now().isoformat()
            ),

            (
                "The Curator Coffee",
                "Makati",
                "https://facebook.com",
                "https://instagram.com",
                "https://m.me",
                "https://maps.google.com",
                5.2,
                6.8,
                4,
                json.dumps([5,6,5,7,5]),
                json.dumps([6,7,6,8,7]),
                json.dumps([200,203,205,207,211]),
                "main",
                datetime.now().isoformat()
            ),

            (
                "Commune",
                "Makati",
                "https://facebook.com",
                "https://instagram.com",
                "https://m.me",
                "https://maps.google.com",
                7.3,
                3.2,
                -2,
                json.dumps([8,7,9,8,7]),
                json.dumps([3,4,2,4,3]),
                json.dumps([500,490,485,480,478]),
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

# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()

seed_starter_cafes()

    conn = get_connection()

    c = conn.cursor()

    c.execute(
        "SELECT COUNT(*) FROM cafes"
    )

    count = c.fetchone()[0]

    if count == 0:

        cafes = [

            (
                "Yardstick Coffee",
                "Makati",
                "https://facebook.com",
                "https://instagram.com/yardstickcoffee",
                "https://m.me",
                "https://maps.google.com",
                3.1,
                12.4,
                18,
                json.dumps([2,3,4,3,4]),
                json.dumps([8,12,10,15,11]),
                json.dumps([100,120,130,145,163]),
                "main",
                datetime.now().isoformat()
            ),

            (
                "The Curator Coffee",
                "Makati",
                "https://facebook.com",
                "https://instagram.com",
                "https://m.me",
                "https://maps.google.com",
                5.2,
                6.8,
                4,
                json.dumps([5,6,5,7,5]),
                json.dumps([6,7,6,8,7]),
                json.dumps([200,203,205,207,211]),
                "main",
                datetime.now().isoformat()
            ),

            (
                "Commune",
                "Makati",
                "https://facebook.com",
                "https://instagram.com",
                "https://m.me",
                "https://maps.google.com",
                7.3,
                3.2,
                -2,
                json.dumps([8,7,9,8,7]),
                json.dumps([3,4,2,4,3]),
                json.dumps([500,490,485,480,478]),
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

# =========================================================
# SIDEBAR CRM PANEL
# =========================================================

with st.sidebar:

    st.title("Growthory CRM")

    st.markdown("---")

    st.subheader("Add Cafe")

    with st.form("add_cafe_form"):

        name = st.text_input(
            "Cafe Name"
        )

        location = st.text_input(
            "Location"
        )

        facebook_url = st.text_input(
            "Facebook URL"
        )

        instagram_url = st.text_input(
            "Instagram URL"
        )

        messenger_url = st.text_input(
            "Messenger URL"
        )

        map_url = st.text_input(
            "Google Maps URL"
        )

        submitted = st.form_submit_button(
            "Add Cafe"
        )

        if submitted:

            if not name:

                st.error(
                    "Cafe name required."
                )

            else:

                add_cafe(
                    name,
                    location,
                    facebook_url,
                    instagram_url,
                    messenger_url,
                    map_url
                )

                st.success(
                    f"{name} added successfully."
                )

                st.rerun()

    st.markdown("---")

    st.subheader("Database")

    cafes_count = len(get_cafes())

    st.metric(
        "Total Cafes",
        cafes_count
    )

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

st.write(cafes_data)

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
# RENDER FRONTEND
# =========================================================

components.html(
    final_page,
    height=5000,
    scrolling=True
)
