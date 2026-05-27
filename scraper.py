# scraper.py
# Apify Facebook Pages Scraper integration
# To activate: set APIFY_API_TOKEN in your .env file
# Apify actor used: apify/facebook-pages-scraper

import os
import json
import time
import requests
from datetime import datetime, timedelta
from dummy_data import compute_metrics

# ── Config ───────────────────────────────────────────────────────
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "")
ACTOR_ID = "apify~facebook-pages-scraper"
APIFY_BASE = "https://api.apify.com/v2"

# Search keywords — Apify will search Facebook for these
SEARCH_QUERIES = [
    "cafe Philippines",
    "coffee shop Philippines",
    "kape Philippines",
    "coffee house Manila",
    "cafe Cebu",
    "coffee shop Davao",
    "cafe Quezon City",
    "coffee shop Iloilo",
    "cafe Baguio",
    "kape shop Visayas",
]

MAX_RESULTS = 30  # Fetch more, then filter to top 10 worst performers


# ── Main scrape function ─────────────────────────────────────────
def scrape_cafes(max_results=MAX_RESULTS):
    """
    Scrape Philippine café Facebook pages via Apify.
    Returns list of café dicts with metrics computed.
    Falls back to dummy data if token not set.
    """
    if not APIFY_TOKEN:
        print("[scraper] No APIFY_API_TOKEN found — using dummy data.")
        from dummy_data import get_dummy_cafes
        return get_dummy_cafes()

    print("[scraper] Starting Apify scrape...")
    raw_pages = []

    for query in SEARCH_QUERIES[:3]:  # Limit queries per run to save credits
        results = _run_actor(query, limit=10)
        raw_pages.extend(results)
        time.sleep(1)  # Be gentle with the API

    if not raw_pages:
        print("[scraper] No results from Apify — falling back to dummy data.")
        from dummy_data import get_dummy_cafes
        return get_dummy_cafes()

    cafes = _parse_pages(raw_pages)
    scored = [compute_metrics(c) for c in cafes]

    # Filter: only show cafés that fail at least 2 of 3 metrics
    flagged = [c for c in scored if sum([c["gap_bad"], c["engagement_bad"], c["gain_bad"]]) >= 2]

    # Sort by worst performers first (most metrics failing + highest gap)
    flagged.sort(key=lambda x: (
        -(x["gap_bad"] + x["engagement_bad"] + x["gain_bad"]),
        -x["avg_gap_days"]
    ))

    return flagged[:10]


# ── Apify actor runner ───────────────────────────────────────────
def _run_actor(search_query: str, limit: int = 10):
    """Run Apify Facebook Pages Scraper and return results."""
    run_input = {
        "startUrls": [],
        "searchTerms": [search_query],
        "resultsLimit": limit,
        "scrapePosts": True,
        "postsLimit": 5,
        "scrapeAbout": True,
        "proxy": {"useApifyProxy": True},
    }

    # Start actor run
    run_url = f"{APIFY_BASE}/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"
    resp = requests.post(run_url, json=run_input, timeout=30)
    if resp.status_code != 201:
        print(f"[scraper] Actor start failed: {resp.status_code} {resp.text}")
        return []

    run_id = resp.json()["data"]["id"]
    print(f"[scraper] Actor run started: {run_id}")

    # Poll for completion
    for _ in range(60):  # Max 5 minutes
        time.sleep(5)
        status_url = f"{APIFY_BASE}/actor-runs/{run_id}?token={APIFY_TOKEN}"
        status_resp = requests.get(status_url, timeout=10)
        status = status_resp.json()["data"]["status"]
        if status == "SUCCEEDED":
            break
        elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
            print(f"[scraper] Actor run {status}")
            return []

    # Fetch dataset results
    dataset_id = status_resp.json()["data"]["defaultDatasetId"]
    data_url = f"{APIFY_BASE}/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json"
    data_resp = requests.get(data_url, timeout=30)
    return data_resp.json() if data_resp.status_code == 200 else []


# ── Parser: Apify raw → our café dict ───────────────────────────
def _parse_pages(raw_pages: list):
    cafes = []
    seen_ids = set()

    for page in raw_pages:
        page_id = page.get("pageId") or page.get("id", "")
        if not page_id or page_id in seen_ids:
            continue
        seen_ids.add(page_id)

        name = page.get("title") or page.get("name", "Unknown Cafe")
        username = page.get("username") or page.get("pageUrl", "").split("/")[-1]
        location = _extract_location(page)
        fb_url = page.get("url") or f"https://www.facebook.com/{username}"
        followers = page.get("likes") or page.get("followers") or 0

        # Extract post timestamps to compute gaps
        posts = page.get("posts") or []
        posting_gaps = _compute_gaps_from_posts(posts)
        if len(posting_gaps) < 5:
            posting_gaps = posting_gaps + [120] * (5 - len(posting_gaps))  # Fill with 5h default

        # Extract engagement from posts
        engagement_rates = _compute_engagement(posts, followers)
        if len(engagement_rates) < 5:
            engagement_rates = engagement_rates + [1.5] * (5 - len(engagement_rates))

        # Weekly follower gains not available via scraping — use estimated variance
        weekly_gains = _estimate_weekly_gains(page)

        cafe = {
            "id": f"apify_{page_id}",
            "name": name,
            "location": location,
            "facebook_url": fb_url,
            "instagram_url": _extract_instagram(page),
            "messenger_url": f"https://m.me/{username}",
            "maps_url": f"https://maps.google.com/?q={name.replace(' ', '+')}+{location.replace(' ', '+')}",
            "facebook_username": username,
            "instagram_handle": _extract_instagram_handle(page),
            "follower_count": followers,
            "profile_photo": "☕",
            "posting_gaps": posting_gaps[:5],
            "engagement_rates": engagement_rates[:5],
            "weekly_follower_gains": weekly_gains,
        }
        cafes.append(cafe)

    return cafes


# ── Helper parsers ───────────────────────────────────────────────
def _extract_location(page):
    addr = page.get("address") or {}
    if isinstance(addr, dict):
        parts = [addr.get("city", ""), addr.get("region", ""), addr.get("country", "")]
        loc = ", ".join(p for p in parts if p)
        return loc or "Philippines"
    return page.get("location", "Philippines")


def _extract_instagram(page):
    for key in ["instagramUrl", "instagram_url", "instagramProfile"]:
        val = page.get(key, "")
        if val:
            return val if val.startswith("http") else f"https://www.instagram.com/{val}"
    return ""


def _extract_instagram_handle(page):
    ig = _extract_instagram(page)
    if ig:
        handle = ig.rstrip("/").split("/")[-1]
        return f"@{handle}"
    return ""


def _compute_gaps_from_posts(posts):
    """Compute hour gaps between consecutive posts."""
    if len(posts) < 2:
        return []
    timestamps = []
    for p in posts:
        ts = p.get("time") or p.get("created_time") or p.get("timestamp")
        if ts:
            try:
                if isinstance(ts, (int, float)):
                    timestamps.append(datetime.fromtimestamp(ts))
                else:
                    timestamps.append(datetime.fromisoformat(str(ts).replace("Z", "")))
            except Exception:
                pass
    timestamps.sort(reverse=True)
    gaps = []
    for i in range(len(timestamps) - 1):
        diff = (timestamps[i] - timestamps[i+1]).total_seconds() / 3600
        gaps.append(round(diff, 1))
    return gaps[:5]


def _compute_engagement(posts, followers):
    """Compute engagement rate per post."""
    if not posts or not followers:
        return []
    rates = []
    for p in posts:
        likes = p.get("likes", 0) or 0
        comments = p.get("comments", 0) or 0
        shares = p.get("shares", 0) or 0
        total = likes + comments + shares
        rate = (total / followers * 100) if followers > 0 else 0
        rates.append(round(rate, 2))
    return rates[:5]


def _estimate_weekly_gains(page):
    """
    Weekly follower gain not available without Page Insights API.
    Use a conservative low estimate to flag for outreach.
    """
    followers = page.get("likes") or page.get("followers") or 0
    # Estimate: low-follower pages typically have low organic growth
    base = max(0, int(followers * 0.001))  # ~0.1% weekly growth estimate
    return [base, base - 1, base + 1, base, base - 1]
