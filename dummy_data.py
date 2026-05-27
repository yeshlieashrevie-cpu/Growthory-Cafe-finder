# dummy_data.py
# Realistic Philippine café dummy data for development/testing
# Replace with live Apify data by calling scraper.py

DUMMY_CAFES = [
    {
        "id": "cafe_001",
        "name": "Brewed Awakening Cafe",
        "location": "Quezon City, Metro Manila",
        "facebook_url": "https://www.facebook.com/BrewedAwakeningCafe",
        "instagram_url": "https://www.instagram.com/brewedawakeningcafe",
        "messenger_url": "https://m.me/BrewedAwakeningCafe",
        "maps_url": "https://maps.google.com/?q=Brewed+Awakening+Cafe+Quezon+City",
        "facebook_username": "BrewedAwakeningCafe",
        "instagram_handle": "@brewedawakeningcafe",
        "follower_count": 1240,
        "profile_photo": "☕",
        # Last 5 post gaps in hours
        "posting_gaps": [96, 48, 120, 72, 168],   # avg ~100.8h = ~4.2 days
        # Last 5 post engagement rates (%)
        "engagement_rates": [1.2, 0.8, 1.5, 0.9, 1.1],  # avg 1.1% — BAD
        # Last 5 weeks follower gain
        "weekly_follower_gains": [2, -1, 3, 1, 0],       # avg 1 — BAD
    },
    {
        "id": "cafe_002",
        "name": "The Lazy Bean",
        "location": "Cebu City, Cebu",
        "facebook_url": "https://www.facebook.com/TheLazyBeanCebu",
        "instagram_url": "https://www.instagram.com/thelazybeancebu",
        "messenger_url": "https://m.me/TheLazyBeanCebu",
        "maps_url": "https://maps.google.com/?q=The+Lazy+Bean+Cebu+City",
        "facebook_username": "TheLazyBeanCebu",
        "instagram_handle": "@thelazybeancebu",
        "follower_count": 876,
        "profile_photo": "🫘",
        "posting_gaps": [144, 200, 168, 192, 120],  # avg ~164.8h = ~6.9 days — BAD
        "engagement_rates": [0.5, 0.7, 0.4, 0.6, 0.8],  # avg 0.6% — BAD
        "weekly_follower_gains": [1, 0, 2, -1, 1],       # avg 0.6 — BAD
    },
    {
        "id": "cafe_003",
        "name": "Kape Kesho",
        "location": "Davao City, Davao del Sur",
        "facebook_url": "https://www.facebook.com/KapeKeshoDavao",
        "instagram_url": "",
        "messenger_url": "https://m.me/KapeKeshoDavao",
        "maps_url": "https://maps.google.com/?q=Kape+Kesho+Davao+City",
        "facebook_username": "KapeKeshoDavao",
        "instagram_handle": "",
        "follower_count": 2100,
        "profile_photo": "🌿",
        "posting_gaps": [240, 312, 288, 168, 360],  # avg ~273.6h = ~11.4 days — BAD
        "engagement_rates": [2.1, 1.8, 2.4, 1.6, 2.0],  # avg 1.98% — BAD
        "weekly_follower_gains": [4, 2, 1, 3, 2],         # avg 2.4 — BAD
    },
    {
        "id": "cafe_004",
        "name": "Sinagtala Coffee",
        "location": "Iloilo City, Iloilo",
        "facebook_url": "https://www.facebook.com/SinagtalaCoffe",
        "instagram_url": "https://www.instagram.com/sinagtalacoffee",
        "messenger_url": "https://m.me/SinagtalaCoffe",
        "maps_url": "https://maps.google.com/?q=Sinagtala+Coffee+Iloilo+City",
        "facebook_username": "SinagtalaCoffe",
        "instagram_handle": "@sinagtalacoffee",
        "follower_count": 540,
        "profile_photo": "⭐",
        "posting_gaps": [120, 144, 96, 168, 192],   # avg ~144h = ~6 days — BAD
        "engagement_rates": [1.0, 0.8, 1.2, 0.6, 0.9],  # avg 0.9% — BAD
        "weekly_follower_gains": [0, 1, 0, 2, 1],         # avg 0.8 — BAD
    },
    {
        "id": "cafe_005",
        "name": "Higante Brew Co.",
        "location": "Angeles City, Pampanga",
        "facebook_url": "https://www.facebook.com/HiganteBrew",
        "instagram_url": "https://www.instagram.com/higantebrew",
        "messenger_url": "https://m.me/HiganteBrew",
        "maps_url": "https://maps.google.com/?q=Higante+Brew+Co+Angeles+City",
        "facebook_username": "HiganteBrew",
        "instagram_handle": "@higantebrew",
        "follower_count": 3200,
        "profile_photo": "🍺",
        "posting_gaps": [72, 96, 120, 144, 96],     # avg ~105.6h = ~4.4 days — BORDERLINE
        "engagement_rates": [2.5, 2.1, 2.8, 1.9, 2.3],  # avg 2.32% — BAD
        "weekly_follower_gains": [2, 3, 1, 2, 1],         # avg 1.8 — BAD
    },
    {
        "id": "cafe_006",
        "name": "Haligi ng Kape",
        "location": "Baguio City, Benguet",
        "facebook_url": "https://www.facebook.com/HaligiNgKape",
        "instagram_url": "https://www.instagram.com/haliginakape",
        "messenger_url": "https://m.me/HaligiNgKape",
        "maps_url": "https://maps.google.com/?q=Haligi+ng+Kape+Baguio+City",
        "facebook_username": "HaligiNgKape",
        "instagram_handle": "@haliginakape",
        "follower_count": 1890,
        "profile_photo": "🏔️",
        "posting_gaps": [168, 192, 216, 144, 288],  # avg ~201.6h = ~8.4 days — BAD
        "engagement_rates": [1.4, 1.1, 1.6, 0.9, 1.3],  # avg 1.26% — BAD
        "weekly_follower_gains": [1, 2, 0, 1, 2],         # avg 1.2 — BAD
    },
    {
        "id": "cafe_007",
        "name": "Tambay Grounds",
        "location": "Cagayan de Oro, Misamis Oriental",
        "facebook_url": "https://www.facebook.com/TambayGrounds",
        "instagram_url": "",
        "messenger_url": "https://m.me/TambayGrounds",
        "maps_url": "https://maps.google.com/?q=Tambay+Grounds+Cagayan+de+Oro",
        "facebook_username": "TambayGrounds",
        "instagram_handle": "",
        "follower_count": 720,
        "profile_photo": "☁️",
        "posting_gaps": [336, 288, 408, 264, 312],  # avg ~321.6h = ~13.4 days — BAD
        "engagement_rates": [0.4, 0.3, 0.5, 0.2, 0.4],  # avg 0.36% — BAD
        "weekly_follower_gains": [-2, 0, 1, -1, 0],       # avg -0.4 — BAD
    },
    {
        "id": "cafe_008",
        "name": "Daloy Coffee House",
        "location": "Tagaytay City, Cavite",
        "facebook_url": "https://www.facebook.com/DaloyCoffeeHouse",
        "instagram_url": "https://www.instagram.com/daloycoffeehouse",
        "messenger_url": "https://m.me/DaloyCoffeeHouse",
        "maps_url": "https://maps.google.com/?q=Daloy+Coffee+House+Tagaytay",
        "facebook_username": "DaloyCoffeeHouse",
        "instagram_handle": "@daloycoffeehouse",
        "follower_count": 4500,
        "profile_photo": "🌊",
        "posting_gaps": [96, 120, 144, 168, 96],    # avg ~124.8h = ~5.2 days — BAD
        "engagement_rates": [2.8, 2.3, 2.6, 2.1, 2.9],  # avg 2.54% — BAD
        "weekly_follower_gains": [2, 1, 3, 2, 1],         # avg 1.8 — BAD
    },
    {
        "id": "cafe_009",
        "name": "Pulang Lupa Roasters",
        "location": "Lipa City, Batangas",
        "facebook_url": "https://www.facebook.com/PulangLupaRoasters",
        "instagram_url": "https://www.instagram.com/pulanglupa",
        "messenger_url": "https://m.me/PulangLupaRoasters",
        "maps_url": "https://maps.google.com/?q=Pulang+Lupa+Roasters+Lipa+City",
        "facebook_username": "PulangLupaRoasters",
        "instagram_handle": "@pulanglupa",
        "follower_count": 980,
        "profile_photo": "🔴",
        "posting_gaps": [192, 264, 216, 288, 192],  # avg ~230.4h = ~9.6 days — BAD
        "engagement_rates": [1.8, 1.4, 2.0, 1.6, 1.7],  # avg 1.7% — BAD
        "weekly_follower_gains": [1, 0, 2, 1, 0],         # avg 0.8 — BAD
    },
    {
        "id": "cafe_010",
        "name": "Tindahan ni Lola Brew",
        "location": "Vigan City, Ilocos Sur",
        "facebook_url": "https://www.facebook.com/TindahanNiLolaBrew",
        "instagram_url": "https://www.instagram.com/lolabrew",
        "messenger_url": "https://m.me/TindahanNiLolaBrew",
        "maps_url": "https://maps.google.com/?q=Tindahan+ni+Lola+Brew+Vigan",
        "facebook_username": "TindahanNiLolaBrew",
        "instagram_handle": "@lolabrew",
        "follower_count": 620,
        "profile_photo": "👵",
        "posting_gaps": [288, 360, 240, 312, 408],  # avg ~321.6h = ~13.4 days — BAD
        "engagement_rates": [0.6, 0.5, 0.7, 0.4, 0.6],  # avg 0.56% — BAD
        "weekly_follower_gains": [0, 1, -1, 0, 1],        # avg 0.2 — BAD
    },
]


def compute_metrics(cafe):
    """Compute summary metrics from raw data."""
    gaps = cafe["posting_gaps"]
    eng = cafe["engagement_rates"]
    gains = cafe["weekly_follower_gains"]

    avg_gap_hours = sum(gaps) / len(gaps)
    avg_gap_days = avg_gap_hours / 24
    avg_engagement = sum(eng) / len(eng)
    avg_gain = sum(gains) / len(gains)

    # Format gap display
    if avg_gap_days >= 1:
        gap_display = f"{avg_gap_days:.1f}D"
    else:
        gap_display = f"{avg_gap_hours:.0f}H"

    # Format individual gaps
    gap_labels = []
    for h in gaps:
        if h >= 24:
            gap_labels.append(f"{h/24:.0f}D")
        else:
            gap_labels.append(f"{h:.0f}H")

    return {
        **cafe,
        "avg_gap_hours": avg_gap_hours,
        "avg_gap_days": avg_gap_days,
        "gap_display": gap_display,
        "gap_labels": gap_labels,
        "avg_engagement": avg_engagement,
        "avg_gain": avg_gain,
        # Threshold flags
        "gap_bad": avg_gap_days > 5,
        "engagement_bad": avg_engagement < 3.0,
        "gain_bad": avg_gain < 3,
    }


def get_dummy_cafes():
    return [compute_metrics(c) for c in DUMMY_CAFES]
