import os
import time
import socket
import threading
import requests
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

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
# HIDE STREAMLIT DEFAULT UI
# =========================================================

HIDE_STREAMLIT_STYLE = """
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
    max-width: 100%;
}

section[data-testid="stSidebar"] {
    display: none;
}

</style>
"""

st.markdown(
    HIDE_STREAMLIT_STYLE,
    unsafe_allow_html=True
)

# =========================================================
# IMPORT FLASK APP
# =========================================================

from app import app

# =========================================================
# FLASK SERVER STATE
# =========================================================

if "flask_started" not in st.session_state:
    st.session_state.flask_started = False

# =========================================================
# START FLASK SERVER
# =========================================================

def run_flask():

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )

# =========================================================
# CHECK IF PORT IS ACTIVE
# =========================================================

def is_port_open(host="127.0.0.1", port=5000):

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as s:

        s.settimeout(1)

        return s.connect_ex((host, port)) == 0

# =========================================================
# START BACKEND
# =========================================================

if not is_port_open():

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    time.sleep(3)

    st.session_state.flask_started = True

# =========================================================
# VERIFY BACKEND
# =========================================================

BACKEND_RUNNING = False

try:

    response = requests.get(
        "http://127.0.0.1:5000/api/status",
        timeout=5
    )

    if response.status_code == 200:
        BACKEND_RUNNING = True

except Exception:
    BACKEND_RUNNING = False

# =========================================================
# ERROR SCREEN
# =========================================================

if not BACKEND_RUNNING:

    st.error(
        """
        Backend failed to start.

        Check:
        • app.py exists
        • requirements.txt is correct
        • no syntax errors in app.py
        """
    )

    st.stop()

# =========================================================
# LOAD FRONTEND FILES
# =========================================================

BASE_DIR = Path(__file__).parent

HTML_PATH = BASE_DIR / "index.html"
CSS_PATH = BASE_DIR / "style.css"
JS_PATH = BASE_DIR / "script.js"

# =========================================================
# VERIFY FILES EXIST
# =========================================================

required_files = [
    HTML_PATH,
    CSS_PATH,
    JS_PATH
]

missing_files = []

for file in required_files:

    if not file.exists():
        missing_files.append(str(file))

if missing_files:

    st.error(
        f"""
        Missing frontend files:

        {chr(10).join(missing_files)}
        """
    )

    st.stop()

# =========================================================
# LOAD FILE CONTENTS
# =========================================================

with open(
    HTML_PATH,
    "r",
    encoding="utf-8"
) as f:

    html_content = f.read()

with open(
    CSS_PATH,
    "r",
    encoding="utf-8"
) as f:

    css_content = f.read()

with open(
    JS_PATH,
    "r",
    encoding="utf-8"
) as f:

    js_content = f.read()

# =========================================================
# INJECT API BASE
# =========================================================

API_BASE = "http://127.0.0.1:5000"

js_content = f"""
const API_BASE = "{API_BASE}";
{js_content}
"""

# =========================================================
# BUILD FULL PAGE
# =========================================================

final_page = f"""

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
/>

<title>Growthory CRM</title>

<link
    rel="preconnect"
    href="https://fonts.googleapis.com"
/>

<link
    rel="preconnect"
    href="https://fonts.gstatic.com"
    crossorigin
/>

<link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
    rel="stylesheet"
/>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

{css_content}

</style>

</head>

<body>

{html_content}

<script>

{js_content}

</script>

</body>

</html>
"""

# =========================================================
# RENDER FULLSCREEN APP
# =========================================================

components.html(
    final_page,
    height=5000,
    scrolling=True
)

# =========================================================
# FOOTER STATUS
# =========================================================

st.markdown(
    """
    <div style="
        position: fixed;
        bottom: 10px;
        right: 15px;
        z-index: 9999;
        background: #111827;
        color: #9ca3af;
        padding: 8px 14px;
        border-radius: 12px;
        font-size: 12px;
        border: 1px solid #1f2937;
        font-family: Inter;
    ">
        Growthory CRM Backend Connected
    </div>
    """,
    unsafe_allow_html=True
)
