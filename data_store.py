# data_store.py
# Handles all CSV read/write operations for the 3 lists

import os
import json
import pandas as pd
from datetime import datetime

DATA_DIR = "data"
MAIN_CSV = os.path.join(DATA_DIR, "main_list.csv")
PENDING_CSV = os.path.join(DATA_DIR, "pending_list.csv")
REJECTED_CSV = os.path.join(DATA_DIR, "rejected_list.csv")

COLUMNS = [
    "id", "name", "location", "facebook_url", "instagram_url",
    "messenger_url", "maps_url", "facebook_username", "instagram_handle",
    "follower_count", "profile_photo",
    "posting_gaps", "engagement_rates", "weekly_follower_gains",
    "avg_gap_hours", "avg_gap_days", "gap_display", "gap_labels",
    "avg_engagement", "avg_gain",
    "gap_bad", "engagement_bad", "gain_bad",
    "added_date"
]


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _empty_df():
    return pd.DataFrame(columns=COLUMNS)


def _load_csv(path):
    ensure_data_dir()
    if not os.path.exists(path):
        return _empty_df()
    try:
        df = pd.read_csv(path)
        # Parse JSON list columns
        for col in ["posting_gaps", "engagement_rates", "weekly_follower_gains", "gap_labels"]:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: json.loads(x) if isinstance(x, str) else x
                )
        return df
    except Exception:
        return _empty_df()


def _save_csv(df, path):
    ensure_data_dir()
    save_df = df.copy()
    for col in ["posting_gaps", "engagement_rates", "weekly_follower_gains", "gap_labels"]:
        if col in save_df.columns:
            save_df[col] = save_df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, list) else x
            )
    save_df.to_csv(path, index=False)


# ── Load functions ──────────────────────────────────────────────
def load_main():
    return _load_csv(MAIN_CSV)

def load_pending():
    return _load_csv(PENDING_CSV)

def load_rejected():
    return _load_csv(REJECTED_CSV)


# ── Save full list ───────────────────────────────────────────────
def save_main(df):
    _save_csv(df, MAIN_CSV)

def save_pending(df):
    _save_csv(df, PENDING_CSV)

def save_rejected(df):
    _save_csv(df, REJECTED_CSV)


# ── Seed main list from dummy/scraped data ───────────────────────
def seed_main_list(cafes: list):
    """Populate main list from a list of cafe dicts (dummy or scraped)."""
    for c in cafes:
        c.setdefault("added_date", datetime.now().strftime("%Y-%m-%d"))
    df = pd.DataFrame(cafes, columns=COLUMNS)
    save_main(df)
    return df


# ── Move operations ──────────────────────────────────────────────
def move_to_pending(cafe_ids: list):
    main = load_main()
    pending = load_pending()
    rows = main[main["id"].isin(cafe_ids)].copy()
    main = main[~main["id"].isin(cafe_ids)]
    pending = pd.concat([pending, rows], ignore_index=True)
    save_main(main)
    save_pending(pending)


def move_to_rejected(cafe_ids: list):
    main = load_main()
    rejected = load_rejected()
    rows = main[main["id"].isin(cafe_ids)].copy()
    main = main[~main["id"].isin(cafe_ids)]
    rejected = pd.concat([rejected, rows], ignore_index=True)
    save_main(main)
    save_rejected(rejected)


def move_pending_to_main(cafe_ids: list):
    pending = load_pending()
    main = load_main()
    rows = pending[pending["id"].isin(cafe_ids)].copy()
    pending = pending[~pending["id"].isin(cafe_ids)]
    main = pd.concat([main, rows], ignore_index=True)
    save_pending(pending)
    save_main(main)


def move_rejected_to_pending(cafe_ids: list):
    rejected = load_rejected()
    pending = load_pending()
    rows = rejected[rejected["id"].isin(cafe_ids)].copy()
    rejected = rejected[~rejected["id"].isin(cafe_ids)]
    pending = pd.concat([pending, rows], ignore_index=True)
    save_rejected(rejected)
    save_pending(pending)


def delete_from_main(cafe_ids: list):
    main = load_main()
    main = main[~main["id"].isin(cafe_ids)]
    save_main(main)


def delete_from_pending(cafe_ids: list):
    pending = load_pending()
    pending = pending[~pending["id"].isin(cafe_ids)]
    save_pending(pending)


def delete_from_rejected(cafe_ids: list):
    rejected = load_rejected()
    rejected = rejected[~rejected["id"].isin(cafe_ids)]
    save_rejected(rejected)


def get_main_as_csv_string():
    main = load_main()
    return main.to_csv(index=False)
