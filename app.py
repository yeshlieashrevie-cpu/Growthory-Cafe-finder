"""
Cafe Intelligence Tracker — Powered by Meta Graph API
Backend updated for 5-point historical data requirements.
"""

import os
import json
import math
import logging
import requests
import random
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import atexit

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

GRAPH_API_VERSION = "v19.0"
GRAPH_API_BASE    = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
DEMO_MODE         = not bool(META_ACCESS_TOKEN)
CACHE_FILE        = "daily_cache.json"
CONFIG_FILE       = "cafes_config.json"
CACHE_TTL_HOURS   = 24

def _parse_ts(ts_str: str):
    if not ts_str: return None
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None

class MetricsEngine:
    @staticmethod
    def posting_consistency(post_dates: list) -> dict:
        if not post_dates:
            return {"avg_gap_days": 999, "days_since_last_post": 999, "gap_history": [0,0,0,0,0]}
        
        parsed = sorted([d for d in [_parse_ts(ts) for ts in post_dates] if d])
        if len(parsed) <= 1:
            days_since = (datetime.now(timezone.utc) - parsed[-1]).days if parsed else 999
            return {"avg_gap_days": days_since, "days_since_last_post": days_since, "gap_history": [days_since]*5}

        gaps_days = [(parsed[i + 1] - parsed[i]).total_seconds() / 86400 for i in range(len(parsed) - 1)]
        avg_gap = sum(gaps_days) / len(gaps_days)
        days_since = (datetime.now(timezone.utc) - parsed[-1]).days
        
        # Ensure we return exactly 5 data points for the UI graph
        history = [round(g, 1) for g in gaps_days[-5:]]
        while len(history) < 5:
            history.insert(0, round(avg_gap, 1))

        return {"avg_gap_days": round(avg_gap, 1), "days_since_last_post": days_since, "gap_history": history}

class DemoDataEngine:
    SAMPLE_CAFES = [
        ("Brewed Awakening", "brewedawakeningcafe", "Makati, Manila", 14, 2200, 0.8),
        ("The Roast Republic", "roastrepublic", "BGC, Taguig", 7, 5400, 2.1),
        ("Sip & Scribble", "sipandscribble", "Quezon City", 21, 980, 0.4),
        ("Dusk Espresso Bar", "duskespresso", "Cebu City", 4, 8900, 3.8),
        ("The Lazy Barista", "thelazybarista", "Davao City", 30, 430, 0.2),
        ("Fogged Lens Cafe", "foggedlenscafe", "Pasig", 9, 3100, 1.5),
        ("Grounds & Grains", "groundsandgrains", "Antipolo, Rizal", 45, 260, 0.1),
        ("Ember & Oak Coffee", "emberoakcoffee", "San Juan", 3, 12400, 5.2),
    ]

    @classmethod
    def generate(cls) -> dict:
        cafes = []
        for name, user, loc, avg_gap, fans, eng_mult in cls.SAMPLE_CAFES:
            # Generate dummy 5-point histories for the UI graphs
            gap_history = [max(1, avg_gap + random.randint(-3, 3)) for _ in range(5)]
            eng_history = [round(eng_mult * random.uniform(5, 15), 1) for _ in range(5)]
            foll_history = [random.randint(-5, 20) for _ in range(5)]
            
            avg_eng = sum(eng_history) / 5
            avg_foll = sum(foll_history) / 5

            cafes.append({
                "name": name,
                "location": loc,
                "fb_username": user,
                "ig_username": user,
                "fb_url": f"https://www.facebook.com/{user}",
                "ig_url": f"https://www.instagram.com/{user}",
                "map_url": f"https://www.google.com/maps/search/{name.replace(' ', '+')}+{loc.replace(' ', '+')}",
                "msg_url": f"https://m.me/{user}",
                "metrics": {
                    "avg_gap_days": sum(gap_history) / 5,
                    "gap_history": gap_history,
                    "avg_engagement": avg_eng,
                    "engagement_history": eng_history,
                    "avg_weekly_followers": avg_foll,
                    "follower_history": foll_history
                }
            })
        
        return {"cafes": cafes, "last_updated": datetime.now(timezone.utc).isoformat()}

def load_or_refresh_cache() -> dict:
    if DEMO_MODE: return DemoDataEngine.generate()
    # Live fetch logic goes here, utilizing the new history arrays format
    return DemoDataEngine.generate()

@app.route("/api/cafes")
def api_cafes():
    return jsonify(load_or_refresh_cache())

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
