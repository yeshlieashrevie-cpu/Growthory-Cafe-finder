import os
import json
import math
import sqlite3
import logging
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd

# =========================================================
# INITIALIZATION
# =========================================================

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

log = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# =========================================================
# CONFIG
# =========================================================

GRAPH_API_VERSION = "v19.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_APP_ID = os.getenv("META_APP_ID", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "growthory_verify")

DATABASE_NAME = "cafes.db"

CACHE_TTL_HOURS = 6

# =========================================================
# DATABASE
# =========================================================

class DatabaseManager:

    def __init__(self):
        self.init_db()

    def connect(self):
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):

        conn = self.connect()
        c = conn.cursor()

        # MAIN TABLE

        c.execute("""
        CREATE TABLE IF NOT EXISTS cafes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT,
            facebook_url TEXT,
            instagram_url TEXT,
            messenger_url TEXT,
            map_url TEXT,

            fb_page_id TEXT,
            ig_business_id TEXT,

            avg_gap_days REAL,
            avg_engagement REAL,
            weekly_followers INTEGER,
            priority_score REAL,

            posting_history TEXT,
            engagement_history TEXT,
            followers_history TEXT,

            recommended_message TEXT,

            status TEXT DEFAULT 'main',

            last_updated TEXT,
            created_at TEXT
        )
        """)

        # CACHE TABLE

        c.execute("""
        CREATE TABLE IF NOT EXISTS cache_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_refresh TEXT
        )
        """)

        conn.commit()
        conn.close()

db = DatabaseManager()

# =========================================================
# META CLIENT
# =========================================================

class MetaAPIClient:

    def __init__(self):

        self.token = META_ACCESS_TOKEN

        self.session = requests.Session()

    def _get(self, endpoint, params=None):

        if params is None:
            params = {}

        params["access_token"] = self.token

        url = f"{GRAPH_API_BASE}/{endpoint}"

        try:

            response = self.session.get(
                url,
                params=params,
                timeout=20
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:

            log.error(f"Meta API Error: {e}")

            return {}

    # =====================================================
    # FACEBOOK PAGE INFO
    # =====================================================

    def get_page_info(self, page_id):

        return self._get(page_id, {
            "fields":
            "name,fan_count,link,category"
        })

    # =====================================================
    # FACEBOOK POSTS
    # =====================================================

    def get_page_posts(self, page_id):

        data = self._get(f"{page_id}/posts", {
            "fields":
            "created_time,likes.summary(true),comments.summary(true),shares",
            "limit": 10
        })

        return data.get("data", [])

    # =====================================================
    # INSTAGRAM ACCOUNT
    # =====================================================

    def get_instagram_info(self, ig_id):

        return self._get(ig_id, {
            "fields":
            "followers_count,media_count,username"
        })

    # =====================================================
    # INSTAGRAM MEDIA
    # =====================================================

    def get_instagram_media(self, ig_id):

        data = self._get(f"{ig_id}/media", {
            "fields":
            "timestamp,like_count,comments_count",
            "limit": 10
        })

        return data.get("data", [])

# =========================================================
# METRICS ENGINE
# =========================================================

class MetricsEngine:

    @staticmethod
    def posting_gap_history(post_dates):

        if len(post_dates) < 2:
            return []

        parsed = sorted(post_dates)

        gaps = []

        for i in range(len(parsed) - 1):

            gap = (
                parsed[i + 1] - parsed[i]
            ).days

            gaps.append(gap)

        return gaps[-5:]

    @staticmethod
    def average_gap(gaps):

        if not gaps:
            return 0

        return round(sum(gaps) / len(gaps), 1)

    @staticmethod
    def engagement_history(posts, followers):

        history = []

        for post in posts[:5]:

            likes = post.get(
                "likes",
                {}
            ).get(
                "summary",
                {}
            ).get(
                "total_count",
                0
            )

            comments = post.get(
                "comments",
                {}
            ).get(
                "summary",
                {}
            ).get(
                "total_count",
                0
            )

            shares = post.get(
                "shares",
                {}
            ).get(
                "count",
                0
            )

            total = likes + comments + shares

            if followers > 0:

                rate = (
                    total / followers
                ) * 100

            else:

                rate = 0

            history.append(round(rate, 2))

        return history

    @staticmethod
    def average_engagement(history):

        if not history:
            return 0

        return round(sum(history) / len(history), 2)

    @staticmethod
    def followers_history(current_followers):

        history = []

        current = current_followers

        for i in range(5):

            current -= int(
                current * 0.01
            )

            history.append(current)

        return history[::-1]

    @staticmethod
    def weekly_followers_gain(history):

        if len(history) < 2:
            return 0

        return history[-1] - history[-2]

    @staticmethod
    def priority_score(
        avg_gap,
        engagement,
        weekly_growth
    ):

        score = 0

        score += avg_gap * 3

        score += max(0, 10 - engagement)

        score += max(0, 5 - weekly_growth)

        return round(score, 2)

# =========================================================
# DEMO DATA
# =========================================================

DEMO_CAFES = [
    {
        "name": "Brewed Awakening",
        "location": "Makati",
        "facebook_url": "https://facebook.com",
        "instagram_url": "https://instagram.com",
        "messenger_url": "https://m.me",
        "map_url": "https://maps.google.com",
        "fb_page_id": "",
        "ig_business_id": ""
    },
    {
        "name": "Roast Republic",
        "location": "Taguig",
        "facebook_url": "https://facebook.com",
        "instagram_url": "https://instagram.com",
        "messenger_url": "https://m.me",
        "map_url": "https://maps.google.com",
        "fb_page_id": "",
        "ig_business_id": ""
    }
]

# =========================================================
# DATA ENGINE
# =========================================================

class CafeDataEngine:

    def __init__(self):

        self.client = MetaAPIClient()

    def refresh_all(self):

        log.info("Refreshing cafes...")

        conn = db.connect()
        c = conn.cursor()

        c.execute("DELETE FROM cafes")

        for cafe in DEMO_CAFES:

            try:

                followers = 1000

                posts = []

                post_dates = []

                for i in range(5):

                    dt = (
                        datetime.now(timezone.utc)
                        - timedelta(days=(i + 1) * 2)
                    )

                    post_dates.append(dt)

                    posts.append({
                        "likes": {
                            "summary": {
                                "total_count": 50 + i * 10
                            }
                        },
                        "comments": {
                            "summary": {
                                "total_count": 5 + i
                            }
                        },
                        "shares": {
                            "count": 2 + i
                        }
                    })

                gaps = MetricsEngine.posting_gap_history(
                    post_dates
                )

                avg_gap = MetricsEngine.average_gap(
                    gaps
                )

                engagement_history = MetricsEngine.engagement_history(
                    posts,
                    followers
                )

                avg_engagement = MetricsEngine.average_engagement(
                    engagement_history
                )

                followers_history = MetricsEngine.followers_history(
                    followers
                )

                weekly_growth = MetricsEngine.weekly_followers_gain(
                    followers_history
                )

                priority_score = MetricsEngine.priority_score(
                    avg_gap,
                    avg_engagement,
                    weekly_growth
                )

                recommended_message = f"""
Hi {cafe['name']},

We noticed your social engagement has potential for improvement.

We help cafes improve:
• customer engagement
• posting consistency
• local reach
• audience growth

Would you be interested in discussing growth opportunities?
"""

                c.execute("""
                INSERT INTO cafes (
                    name,
                    location,

                    facebook_url,
                    instagram_url,
                    messenger_url,
                    map_url,

                    fb_page_id,
                    ig_business_id,

                    avg_gap_days,
                    avg_engagement,
                    weekly_followers,
                    priority_score,

                    posting_history,
                    engagement_history,
                    followers_history,

                    recommended_message,

                    status,

                    last_updated,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (

                    cafe["name"],
                    cafe["location"],

                    cafe["facebook_url"],
                    cafe["instagram_url"],
                    cafe["messenger_url"],
                    cafe["map_url"],

                    cafe["fb_page_id"],
                    cafe["ig_business_id"],

                    avg_gap,
                    avg_engagement,
                    weekly_growth,
                    priority_score,

                    json.dumps(gaps),
                    json.dumps(engagement_history),
                    json.dumps(followers_history),

                    recommended_message,

                    "main",

                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))

            except Exception as e:

                log.error(f"Error processing cafe: {e}")

        conn.commit()
        conn.close()

        log.info("Refresh completed")

engine = CafeDataEngine()

# =========================================================
# INITIAL DATA LOAD
# =========================================================

conn = db.connect()
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM cafes")

count = c.fetchone()[0]

conn.close()

if count == 0:
    engine.refresh_all()

# =========================================================
# SCHEDULER
# =========================================================

scheduler = BackgroundScheduler()

scheduler.add_job(
    engine.refresh_all,
    "interval",
    hours=CACHE_TTL_HOURS
)

scheduler.start()

# =========================================================
# ROUTES
# =========================================================

@app.route("/api/cafes")
def get_cafes():

    conn = db.connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM cafes
    ORDER BY priority_score DESC
    """)

    rows = [
        dict(row)
        for row in c.fetchall()
    ]

    conn.close()

    return jsonify(rows)

# =========================================================
# MOVE STATUS
# =========================================================

@app.route("/api/move", methods=["POST"])
def move_cafe():

    data = request.json

    cafe_id = data.get("id")
    status = data.get("status")

    conn = db.connect()
    c = conn.cursor()

    c.execute("""
    UPDATE cafes
    SET status = ?
    WHERE id = ?
    """, (status, cafe_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })

# =========================================================
# DELETE
# =========================================================

@app.route("/api/delete", methods=["POST"])
def delete_cafes():

    data = request.json

    ids = data.get("ids", [])

    conn = db.connect()
    c = conn.cursor()

    for i in ids:

        c.execute("""
        DELETE FROM cafes
        WHERE id = ?
        """, (i,))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })

# =========================================================
# REFRESH
# =========================================================

@app.route("/api/refresh", methods=["POST"])
def refresh_data():

    engine.refresh_all()

    return jsonify({
        "success": True
    })

# =========================================================
# EXPORT CSV
# =========================================================

@app.route("/api/export")
def export_csv():

    conn = db.connect()

    df = pd.read_sql_query(
        "SELECT * FROM cafes",
        conn
    )

    conn.close()

    csv_path = "cafes_export.csv"

    df.to_csv(csv_path, index=False)

    return send_file(
        csv_path,
        as_attachment=True
    )

# =========================================================
# OUTREACH TEMPLATE
# =========================================================

@app.route("/api/outreach/<int:cafe_id>")
def outreach_template(cafe_id):

    conn = db.connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM cafes
    WHERE id = ?
    """, (cafe_id,))

    cafe = c.fetchone()

    conn.close()

    if not cafe:

        return jsonify({
            "error": "Cafe not found"
        }), 404

    return jsonify({
        "message":
        cafe["recommended_message"]
    })

# =========================================================
# WEBHOOK
# =========================================================

@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if (
        mode == "subscribe"
        and token == VERIFY_TOKEN
    ):

        return challenge, 200

    return "Verification failed", 403

# =========================================================
# WEBHOOK EVENTS
# =========================================================

@app.route("/webhook", methods=["POST"])
def webhook_event():

    data = request.json

    log.info(f"Webhook Event: {data}")

    return "EVENT_RECEIVED", 200

# =========================================================
# STATUS
# =========================================================

@app.route("/api/status")
def status():

    return jsonify({
        "status": "running",
        "meta_connected": bool(META_ACCESS_TOKEN),
        "database": DATABASE_NAME,
        "cache_hours": CACHE_TTL_HOURS
    })

# =========================================================
# ROOT
# =========================================================

@app.route("/")
def root():

    return jsonify({
        "message":
        "Growthory CRM Backend Running"
    })

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    log.info("=" * 60)
    log.info("Growthory CRM Backend Started")
    log.info("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
