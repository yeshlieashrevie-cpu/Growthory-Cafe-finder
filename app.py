"""
Cafe Intelligence Tracker — Powered by Meta Graph API
Tracks 10 cafe business accounts daily for engagement, posting consistency,
and follower growth. Ranks by opportunity (lowest posting frequency first).
"""

import os
import json
import math
import logging
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, render_template, request, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from functools import wraps
import atexit

# ─── Initialization ──────────────────────────────────────────────────────────

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")

GRAPH_API_VERSION = "v19.0"
GRAPH_API_BASE    = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
DEMO_MODE         = not bool(META_ACCESS_TOKEN)
CACHE_FILE        = "daily_cache.json"
CONFIG_FILE       = "cafes_config.json"
CACHE_TTL_HOURS   = 24

# ─── Default Cafe List ────────────────────────────────────────────────────────
# Replace fb_page_id / ig_business_id with real values from Meta Business Suite.
# fb_username / ig_username are used to build direct profile links.

DEFAULT_CAFES = [
    {
        "name": "Brewed Awakening",
        "fb_page_id": "111111111111111",
        "ig_business_id": "111111111111111",
        "fb_username": "brewedawakeningcafe",
        "ig_username": "brewedawakeningcafe",
        "location": "Makati, Manila"
    },
    {
        "name": "The Roast Republic",
        "fb_page_id": "222222222222222",
        "ig_business_id": "222222222222222",
        "fb_username": "roastrepublic",
        "ig_username": "roastrepublic",
        "location": "BGC, Taguig"
    },
    {
        "name": "Sip & Scribble",
        "fb_page_id": "333333333333333",
        "ig_business_id": "333333333333333",
        "fb_username": "sipandscribble",
        "ig_username": "sipandscribble",
        "location": "Quezon City"
    },
    {
        "name": "Dusk Espresso Bar",
        "fb_page_id": "444444444444444",
        "ig_business_id": "444444444444444",
        "fb_username": "duskespresso",
        "ig_username": "duskespresso",
        "location": "Cebu City"
    },
    {
        "name": "The Lazy Barista",
        "fb_page_id": "555555555555555",
        "ig_business_id": "555555555555555",
        "fb_username": "thelazybarista",
        "ig_username": "thelazybarista",
        "location": "Davao City"
    },
    {
        "name": "Fogged Lens Cafe",
        "fb_page_id": "666666666666666",
        "ig_business_id": "666666666666666",
        "fb_username": "foggedlenscafe",
        "ig_username": "foggedlenscafe",
        "location": "Pasig, Metro Manila"
    },
    {
        "name": "Grounds & Grains",
        "fb_page_id": "777777777777777",
        "ig_business_id": "777777777777777",
        "fb_username": "groundsandgrains",
        "ig_username": "groundsandgrains",
        "location": "Antipolo, Rizal"
    },
    {
        "name": "Ember & Oak Coffee",
        "fb_page_id": "888888888888888",
        "ig_business_id": "888888888888888",
        "fb_username": "emberoakcoffee",
        "ig_username": "emberoakcoffee",
        "location": "San Juan, Metro Manila"
    },
    {
        "name": "The Velvet Cup",
        "fb_page_id": "999999999999999",
        "ig_business_id": "999999999999999",
        "fb_username": "thevelvetcup",
        "ig_username": "thevelvetcup",
        "location": "Mandaluyong"
    },
    {
        "name": "Steeped & Still",
        "fb_page_id": "101010101010101",
        "ig_business_id": "101010101010101",
        "fb_username": "steepedandstill",
        "ig_username": "steepedandstill",
        "location": "Alabang, Muntinlupa"
    }
]

# ─── Meta API Client ──────────────────────────────────────────────────────────

class MetaAPIClient:
    """Thin wrapper around Meta Graph API endpoints."""

    def __init__(self, access_token: str):
        self.token = access_token
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _get(self, endpoint: str, params: dict) -> dict:
        params["access_token"] = self.token
        url = f"{GRAPH_API_BASE}/{endpoint}"
        try:
            resp = self.session.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                log.warning("Meta API error on %s: %s", endpoint, data["error"].get("message"))
            return data
        except requests.RequestException as e:
            log.error("Request failed for %s: %s", endpoint, e)
            return {}

    # ── Facebook ──────────────────────────────────────────────────────────────

    def get_page_info(self, page_id: str) -> dict:
        return self._get(page_id, {
            "fields": (
                "name,fan_count,category,description,cover,about,"
                "website,phone,location,verification_status"
            )
        })

    def get_page_posts(self, page_id: str, days: int = 30) -> list:
        since = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
        data = self._get(f"{page_id}/posts", {
            "fields": (
                "created_time,message,full_picture,"
                "likes.summary(true),comments.summary(true),shares"
            ),
            "since": since,
            "limit": 100
        })
        posts = data.get("data", [])
        # Handle pagination (up to 3 pages)
        cursor = data.get("paging", {}).get("cursors", {}).get("after")
        for _ in range(2):
            if not cursor:
                break
            next_data = self._get(f"{page_id}/posts", {
                "fields": "created_time,likes.summary(true),comments.summary(true),shares",
                "since": since,
                "limit": 100,
                "after": cursor
            })
            posts.extend(next_data.get("data", []))
            cursor = next_data.get("paging", {}).get("cursors", {}).get("after")
        return posts

    def get_page_insights(self, page_id: str) -> dict:
        """Weekly fan and engagement insights."""
        return self._get(f"{page_id}/insights", {
            "metric": "page_fans,page_fan_adds_unique,page_engaged_users,page_post_engagements",
            "period": "week",
            "date_preset": "last_28d"
        })

    # ── Instagram ─────────────────────────────────────────────────────────────

    def get_ig_account(self, ig_id: str) -> dict:
        return self._get(ig_id, {
            "fields": (
                "followers_count,media_count,name,biography,"
                "profile_picture_url,username,website"
            )
        })

    def get_ig_media(self, ig_id: str, days: int = 30) -> list:
        data = self._get(f"{ig_id}/media", {
            "fields": "timestamp,like_count,comments_count,media_type,caption,permalink,media_url",
            "limit": 100
        })
        media = data.get("data", [])
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return [
            m for m in media
            if _parse_ts(m.get("timestamp", "")) and _parse_ts(m["timestamp"]) > cutoff
        ]

    def get_ig_insights(self, ig_id: str) -> dict:
        since = int((datetime.now(timezone.utc) - timedelta(days=14)).timestamp())
        until = int(datetime.now(timezone.utc).timestamp())
        return self._get(f"{ig_id}/insights", {
            "metric": "follower_count,impressions,reach",
            "period": "day",
            "since": since,
            "until": until
        })

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _parse_ts(ts_str: str):
    """Parse ISO8601 timestamp, return UTC-aware datetime or None."""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None

# ─── Metrics Engine ───────────────────────────────────────────────────────────

class MetricsEngine:
    """Calculates engagement rate, posting consistency, and follower trends."""

    @staticmethod
    def posting_consistency(post_dates: list) -> dict:
        """
        Returns avg_gap_days, std_dev, consistency_score (0-100),
        days_since_last_post, and posting cadence label.
        """
        if not post_dates:
            return {
                "avg_gap_days": 999,
                "std_dev": 0,
                "consistency_score": 0,
                "days_since_last_post": 999,
                "total_posts": 0,
                "posts_per_week": 0,
                "cadence_label": "No posts found",
                "last_post_date": None,
                "gap_history": []
            }

        parsed = sorted(
            [d for d in [_parse_ts(ts) for ts in post_dates] if d],
            reverse=False
        )

        if len(parsed) == 1:
            now = datetime.now(timezone.utc)
            days_since = (now - parsed[-1]).days
            return {
                "avg_gap_days": days_since,
                "std_dev": 0,
                "consistency_score": max(0, 100 - days_since * 5),
                "days_since_last_post": days_since,
                "total_posts": 1,
                "posts_per_week": round(7 / max(days_since, 1), 2),
                "cadence_label": MetricsEngine._cadence_label(days_since),
                "last_post_date": parsed[-1].strftime("%b %d, %Y"),
                "gap_history": []
            }

        gaps_days = [(parsed[i + 1] - parsed[i]).total_seconds() / 86400
                     for i in range(len(parsed) - 1)]

        avg_gap = sum(gaps_days) / len(gaps_days)
        variance = sum((g - avg_gap) ** 2 for g in gaps_days) / len(gaps_days)
        std_dev = math.sqrt(variance)

        now = datetime.now(timezone.utc)
        days_since = (now - parsed[-1]).days

        # Consistency score: max 100, penalise for large gaps and high variance
        consistency = max(0, min(100, 100 - (avg_gap * 8) - (std_dev * 4)))
        posts_per_week = round(7 / max(avg_gap, 0.1), 2)

        return {
            "avg_gap_days": round(avg_gap, 1),
            "std_dev": round(std_dev, 1),
            "consistency_score": round(consistency, 1),
            "days_since_last_post": days_since,
            "total_posts": len(parsed),
            "posts_per_week": min(posts_per_week, 21),
            "cadence_label": MetricsEngine._cadence_label(avg_gap),
            "last_post_date": parsed[-1].strftime("%b %d, %Y"),
            "gap_history": [round(g, 1) for g in gaps_days[-10:]]
        }

    @staticmethod
    def _cadence_label(avg_gap_days: float) -> str:
        if avg_gap_days <= 1:   return "Daily poster"
        if avg_gap_days <= 3:   return "Every few days"
        if avg_gap_days <= 7:   return "Weekly"
        if avg_gap_days <= 14:  return "Bi-weekly"
        if avg_gap_days <= 30:  return "Monthly"
        return "Rarely posts"

    @staticmethod
    def fb_engagement_rate(posts: list, followers: int) -> dict:
        if not posts or followers < 1:
            return {"rate": 0, "avg_likes": 0, "avg_comments": 0, "avg_shares": 0}

        total_likes    = sum(p.get("likes", {}).get("summary", {}).get("total_count", 0) for p in posts)
        total_comments = sum(p.get("comments", {}).get("summary", {}).get("total_count", 0) for p in posts)
        total_shares   = sum(p.get("shares", {}).get("count", 0) for p in posts if "shares" in p)
        n = len(posts)

        avg_likes    = total_likes    / n
        avg_comments = total_comments / n
        avg_shares   = total_shares   / n
        rate = ((avg_likes + avg_comments + avg_shares) / followers) * 100

        return {
            "rate": round(min(rate, 100), 3),
            "avg_likes": round(avg_likes, 1),
            "avg_comments": round(avg_comments, 1),
            "avg_shares": round(avg_shares, 1)
        }

    @staticmethod
    def ig_engagement_rate(media: list, followers: int) -> dict:
        if not media or followers < 1:
            return {"rate": 0, "avg_likes": 0, "avg_comments": 0}

        total_likes    = sum(m.get("like_count", 0) for m in media)
        total_comments = sum(m.get("comments_count", 0) for m in media)
        n = len(media)

        avg_likes    = total_likes    / n
        avg_comments = total_comments / n
        rate = ((avg_likes + avg_comments) / followers) * 100

        return {
            "rate": round(min(rate, 100), 3),
            "avg_likes": round(avg_likes, 1),
            "avg_comments": round(avg_comments, 1)
        }

    @staticmethod
    def follower_growth_score(insights_data: dict) -> dict:
        """Extract weekly follower adds from page insights."""
        metrics = {}
        for item in insights_data.get("data", []):
            name = item.get("name", "")
            values = item.get("values", [])
            if values:
                metrics[name] = values[-1].get("value", 0)

        weekly_adds = metrics.get("page_fan_adds_unique", 0)
        total_fans  = metrics.get("page_fans", 0)

        growth_rate = (weekly_adds / max(total_fans, 1)) * 100 if total_fans else 0

        return {
            "weekly_adds": weekly_adds,
            "growth_rate_pct": round(growth_rate, 3)
        }

    @staticmethod
    def priority_score(
        fb_consistency: dict,
        ig_consistency: dict,
        fb_engagement: dict,
        ig_engagement: dict,
        fb_growth: dict
    ) -> float:
        """
        Composite priority score — higher means the cafe needs MORE help.
        Weighted: posting gap (40%), days since last post (30%),
                  low engagement (20%), low growth (10%)
        """
        avg_gap = max(
            fb_consistency.get("avg_gap_days", 0),
            ig_consistency.get("avg_gap_days", 0)
        )
        days_since = max(
            fb_consistency.get("days_since_last_post", 0),
            ig_consistency.get("days_since_last_post", 0)
        )
        avg_eng = (
            fb_engagement.get("rate", 0) +
            ig_engagement.get("rate", 0)
        ) / 2

        # Penalise low engagement (benchmark: 2% is "okay", 5%+ is good)
        eng_penalty = max(0, 5 - avg_eng) * 3

        # Penalise stagnant growth
        growth_penalty = max(0, 1 - fb_growth.get("growth_rate_pct", 0)) * 4

        score = (avg_gap * 3.5) + (days_since * 2.0) + eng_penalty + growth_penalty
        return round(score, 2)

    @staticmethod
    def opportunity_tier(score: float) -> dict:
        if score >= 40:
            return {"level": "CRITICAL", "color": "#ff3b3b", "emoji": "🔴", "glow": "rgba(255,59,59,0.4)"}
        if score >= 20:
            return {"level": "HIGH", "color": "#ff8c42", "emoji": "🟠", "glow": "rgba(255,140,66,0.4)"}
        if score >= 10:
            return {"level": "MEDIUM", "color": "#f5c842", "emoji": "🟡", "glow": "rgba(245,200,66,0.35)"}
        return {"level": "LOW", "color": "#42d68c", "emoji": "🟢", "glow": "rgba(66,214,140,0.3)"}

# ─── Demo Data Generator ──────────────────────────────────────────────────────

class DemoDataEngine:
    """
    Generates realistic mock data when META_ACCESS_TOKEN is not set.
    Perfect for UI development and demonstration.
    """

    SAMPLE_CAFES = [
        ("Brewed Awakening",      "brewedawakeningcafe", "brewedawakening",    "Makati, Manila",     14, 2200, 1800, 0.8),
        ("The Roast Republic",    "roastrepublic",       "roastrepublic",      "BGC, Taguig",        7,  5400, 4200, 2.1),
        ("Sip & Scribble",        "sipandscribble",      "sipandscribble",     "Quezon City",        21, 980,  1200, 0.4),
        ("Dusk Espresso Bar",     "duskespresso",        "duskespresso",       "Cebu City",          4,  8900, 7600, 3.8),
        ("The Lazy Barista",      "thelazybarista",      "thelazybarista",     "Davao City",         30, 430,  610,  0.2),
        ("Fogged Lens Cafe",      "foggedlenscafe",      "foggedlenscafe",     "Pasig",              9,  3100, 2700, 1.5),
        ("Grounds & Grains",      "groundsandgrains",    "groundsandgrains",   "Antipolo, Rizal",    45, 260,  340,  0.1),
        ("Ember & Oak Coffee",    "emberoakcoffee",      "emberoakcoffee",     "San Juan",           3,  12400,9800, 5.2),
        ("The Velvet Cup",        "thevelvetcup",        "thevelvetcup",       "Mandaluyong",        18, 1600, 1400, 0.6),
        ("Steeped & Still",       "steepedandstill",     "steepedandstill",    "Alabang",            60, 120,  90,   0.05),
    ]

    @classmethod
    def build_post_dates(cls, avg_gap: int, num_posts: int = 15) -> list:
        """Generate synthetic post timestamps for consistency calculations."""
        import random
        now = datetime.now(timezone.utc)
        dates = []
        current = now - timedelta(days=avg_gap)
        for _ in range(num_posts):
            jitter = random.uniform(-avg_gap * 0.4, avg_gap * 0.4)
            current = current - timedelta(days=max(0.5, avg_gap + jitter))
            dates.append(current.strftime("%Y-%m-%dT%H:%M:%S+00:00"))
        # most recent post is avg_gap days ago
        return dates

    @classmethod
    def generate(cls) -> dict:
        import random
        cafes = []
        for (
            name, fb_user, ig_user, location,
            avg_gap, fb_fans, ig_followers, eng_mult
        ) in cls.SAMPLE_CAFES:

            fb_posts_dates = cls.build_post_dates(avg_gap, num_posts=12)
            ig_posts_dates = cls.build_post_dates(avg_gap + random.randint(-2, 3), num_posts=10)

            fb_consistency = MetricsEngine.posting_consistency(fb_posts_dates)
            ig_consistency = MetricsEngine.posting_consistency(ig_posts_dates)

            base_eng = eng_mult * random.uniform(0.85, 1.15)
            fb_eng = {"rate": round(base_eng, 3), "avg_likes": round(fb_fans * base_eng / 100), "avg_comments": round(fb_fans * base_eng / 300), "avg_shares": round(fb_fans * base_eng / 600)}
            ig_eng = {"rate": round(base_eng * 1.3, 3), "avg_likes": round(ig_followers * base_eng / 80), "avg_comments": round(ig_followers * base_eng / 250)}
            fb_growth = {"weekly_adds": random.randint(2, max(3, int(fb_fans * 0.005))), "growth_rate_pct": round(random.uniform(0.01, 0.5) * (1 / avg_gap), 3)}

            score = MetricsEngine.priority_score(fb_consistency, ig_consistency, fb_eng, ig_eng, fb_growth)
            tier  = MetricsEngine.opportunity_tier(score)

            # Build recent post previews
            sample_captions = [
                "Morning vibes ☕ Start your day with our signature flat white.",
                "Weekend special: Buy 2 get 1 FREE on all cold brews! 🧊",
                "Thank you for 1,000 followers! You make this community special 💛",
                "New menu drop — introducing our Ube Latte! 💜 Limited slots.",
                "Cozy corners and good coffee. Come find your spot with us.",
                "Holiday hours: We'll be open 7am–8pm this Saturday!",
                "Behind the brew ☕ Meet our head barista, Miko!",
            ]
            recent_fb = [{"created_time": fb_posts_dates[i], "message": random.choice(sample_captions), "likes": {"summary": {"total_count": fb_eng["avg_likes"] + random.randint(-20, 50)}}, "comments": {"summary": {"total_count": fb_eng["avg_comments"] + random.randint(-3, 10)}}} for i in range(min(3, len(fb_posts_dates)))]
            recent_ig = [{"timestamp": ig_posts_dates[i], "like_count": ig_eng["avg_likes"] + random.randint(-15, 40), "comments_count": ig_eng["avg_comments"] + random.randint(-2, 8), "media_type": random.choice(["IMAGE", "CAROUSEL_ALBUM", "VIDEO"]), "permalink": f"https://instagram.com/{ig_user}"} for i in range(min(3, len(ig_posts_dates)))]

            cafes.append({
                "name": name,
                "location": location,
                "fb_username": fb_user,
                "ig_username": ig_user,
                "fb_url": f"https://www.facebook.com/{fb_user}",
                "ig_url": f"https://www.instagram.com/{ig_user}",
                "fb_followers": fb_fans,
                "ig_followers": ig_followers,
                "fb_posts_30d": len([d for d in fb_posts_dates if _parse_ts(d) and (datetime.now(timezone.utc) - _parse_ts(d)).days <= 30]),
                "ig_posts_30d": len([d for d in ig_posts_dates if _parse_ts(d) and (datetime.now(timezone.utc) - _parse_ts(d)).days <= 30]),
                "fb_engagement": fb_eng,
                "ig_engagement": ig_eng,
                "fb_consistency": fb_consistency,
                "ig_consistency": ig_consistency,
                "fb_growth": fb_growth,
                "priority_score": score,
                "opportunity": tier,
                "avg_gap_days": max(fb_consistency["avg_gap_days"], ig_consistency["avg_gap_days"]),
                "days_since_last_post": max(fb_consistency["days_since_last_post"], ig_consistency["days_since_last_post"]),
                "avg_engagement_rate": round((fb_eng["rate"] + ig_eng["rate"]) / 2, 3),
                "recent_fb_posts": recent_fb,
                "recent_ig_posts": recent_ig,
                "demo": True
            })

        cafes.sort(key=lambda x: x["priority_score"], reverse=True)
        return {
            "cafes": cafes[:10],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "demo_mode": True
        }

# ─── Data Fetcher ─────────────────────────────────────────────────────────────

def load_cafes_config() -> list:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_CAFES


def fetch_live_cafe_data() -> dict:
    """Fetch real data from Meta API for all configured cafes."""
    if DEMO_MODE:
        log.info("META_ACCESS_TOKEN not set — running in demo mode.")
        return DemoDataEngine.generate()

    client  = MetaAPIClient(META_ACCESS_TOKEN)
    engine  = MetricsEngine()
    cafes   = load_cafes_config()
    results = []

    for cfg in cafes:
        try:
            log.info("Fetching data for: %s", cfg["name"])
            cafe = {
                "name":        cfg["name"],
                "location":    cfg.get("location", ""),
                "fb_username": cfg.get("fb_username", ""),
                "ig_username": cfg.get("ig_username", ""),
                "fb_url":      f"https://www.facebook.com/{cfg.get('fb_username', cfg.get('fb_page_id', ''))}",
                "ig_url":      f"https://www.instagram.com/{cfg.get('ig_username', '')}",
                "demo":        False
            }

            # ── Facebook ──────────────────────────────────────────────────────
            if cfg.get("fb_page_id"):
                fb_info    = client.get_page_info(cfg["fb_page_id"])
                fb_posts   = client.get_page_posts(cfg["fb_page_id"])
                fb_insight = client.get_page_insights(cfg["fb_page_id"])

                fb_fans = fb_info.get("fan_count", 0)
                fb_dates = [p["created_time"] for p in fb_posts if "created_time" in p]
                fb_consistency = engine.posting_consistency(fb_dates)
                fb_engagement  = engine.fb_engagement_rate(fb_posts, fb_fans)
                fb_growth      = engine.follower_growth_score(fb_insight)

                cafe.update({
                    "fb_followers":  fb_fans,
                    "fb_posts_30d":  len(fb_posts),
                    "fb_engagement": fb_engagement,
                    "fb_consistency": fb_consistency,
                    "fb_growth":     fb_growth,
                    "fb_page_name":  fb_info.get("name", cfg["name"]),
                    "fb_category":   fb_info.get("category", "Cafe / Coffee Shop"),
                    "recent_fb_posts": fb_posts[:4]
                })
            else:
                cafe.update({
                    "fb_followers": 0, "fb_posts_30d": 0,
                    "fb_engagement": {"rate": 0}, "fb_consistency": engine.posting_consistency([]),
                    "fb_growth": {"weekly_adds": 0, "growth_rate_pct": 0}
                })

            # ── Instagram ─────────────────────────────────────────────────────
            if cfg.get("ig_business_id"):
                ig_info  = client.get_ig_account(cfg["ig_business_id"])
                ig_media = client.get_ig_media(cfg["ig_business_id"])

                ig_followers = ig_info.get("followers_count", 0)
                ig_dates     = [m["timestamp"] for m in ig_media]
                ig_consistency = engine.posting_consistency(ig_dates)
                ig_engagement  = engine.ig_engagement_rate(ig_media, ig_followers)

                cafe.update({
                    "ig_followers":  ig_followers,
                    "ig_posts_30d":  len(ig_media),
                    "ig_engagement": ig_engagement,
                    "ig_consistency": ig_consistency,
                    "ig_bio":        ig_info.get("biography", ""),
                    "ig_profile_pic": ig_info.get("profile_picture_url", ""),
                    "recent_ig_posts": ig_media[:4]
                })
            else:
                cafe.update({
                    "ig_followers": 0, "ig_posts_30d": 0,
                    "ig_engagement": {"rate": 0}, "ig_consistency": engine.posting_consistency([])
                })

            # ── Composite metrics ─────────────────────────────────────────────
            score = engine.priority_score(
                cafe["fb_consistency"], cafe["ig_consistency"],
                cafe["fb_engagement"], cafe["ig_engagement"],
                cafe.get("fb_growth", {"weekly_adds": 0, "growth_rate_pct": 0})
            )
            tier = engine.opportunity_tier(score)

            cafe.update({
                "priority_score": score,
                "opportunity":    tier,
                "avg_gap_days": max(
                    cafe["fb_consistency"]["avg_gap_days"],
                    cafe["ig_consistency"]["avg_gap_days"]
                ),
                "days_since_last_post": max(
                    cafe["fb_consistency"]["days_since_last_post"],
                    cafe["ig_consistency"]["days_since_last_post"]
                ),
                "avg_engagement_rate": round(
                    (cafe["fb_engagement"].get("rate", 0) +
                     cafe["ig_engagement"].get("rate", 0)) / 2, 3
                )
            })

            results.append(cafe)
            log.info("  ✓ %s — score: %.1f (%s)", cfg["name"], score, tier["level"])

        except Exception as exc:
            log.error("Failed to process %s: %s", cfg.get("name", "unknown"), exc)

    results.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

    payload = {
        "cafes": results[:10],
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "demo_mode": False
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(payload, f, default=str)

    return payload


def load_or_refresh_cache() -> dict:
    """Return cached data if fresh (<24 h), otherwise re-fetch."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        updated = _parse_ts(cache.get("last_updated", ""))
        if updated and (datetime.now(timezone.utc) - updated).total_seconds() < CACHE_TTL_HOURS * 3600:
            return cache
    return fetch_live_cafe_data()

# ─── Scheduler ────────────────────────────────────────────────────────────────

scheduler = BackgroundScheduler(timezone="Asia/Manila")
scheduler.add_job(fetch_live_cafe_data, "cron", hour=6, minute=0, id="daily_refresh")
scheduler.start()
atexit.register(scheduler.shutdown)

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/cafes")
def api_cafes():
    data = load_or_refresh_cache()
    return jsonify(data)


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    data = fetch_live_cafe_data()
    return jsonify({
        "success": True,
        "message": "Data refreshed successfully.",
        "last_updated": data["last_updated"],
        "count": len(data["cafes"])
    })


@app.route("/api/cafe/<int:rank>")
def api_cafe_detail(rank):
    """Return full detail for one cafe by its rank (0-indexed)."""
    data = load_or_refresh_cache()
    cafes = data.get("cafes", [])
    if 0 <= rank < len(cafes):
        return jsonify(cafes[rank])
    return jsonify({"error": "Not found"}), 404


@app.route("/api/status")
def api_status():
    cache_exists = os.path.exists(CACHE_FILE)
    last_updated = None
    if cache_exists:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        last_updated = cache.get("last_updated")
    return jsonify({
        "api_configured": not DEMO_MODE,
        "demo_mode": DEMO_MODE,
        "cache_exists": cache_exists,
        "last_updated": last_updated,
        "next_refresh": "06:00 Asia/Manila daily",
        "tracked_cafes": len(load_cafes_config())
    })


@app.route("/api/config", methods=["GET"])
def api_config_get():
    return jsonify(load_cafes_config())


@app.route("/api/config", methods=["POST"])
def api_config_post():
    data = request.get_json(force=True)
    if not isinstance(data, list):
        return jsonify({"error": "Expected a JSON array of cafe configs"}), 400
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return jsonify({"success": True, "count": len(data)})


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("=" * 60)
    log.info("  Cafe Intelligence Tracker")
    log.info("  Mode    : %s", "DEMO (no META_ACCESS_TOKEN)" if DEMO_MODE else "LIVE")
    log.info("  Port    : http://localhost:5000")
    log.info("=" * 60)
    app.run(debug=True, port=5000, use_reloader=False)