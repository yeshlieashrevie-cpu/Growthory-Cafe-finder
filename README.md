# ☕ CAFE ORBIT CAFE FINDER

A daily lead generation dashboard for finding and targeting underperforming café Facebook pages in the Philippines for social media agency outreach.

---

## 🗂 File Structure

```
cafe-orbit/
├── dashboard.py          # Main Streamlit app
├── dummy_data.py         # 10 sample PH cafés (used until Apify is activated)
├── data_store.py         # CSV read/write for all 3 lists
├── scraper.py            # Apify integration (activate with API token)
├── requirements.txt
├── .env.example          # Copy to .env and fill in your Apify token
└── data/                 # Auto-created on first run
    ├── main_list.csv
    ├── pending_list.csv
    └── rejected_list.csv
```

---

## 🚀 Local Setup

```bash
# 1. Clone your repo
git clone https://github.com/yourusername/cafe-orbit.git
cd cafe-orbit

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file
cp .env.example .env
# Edit .env and add your Apify token when ready

# 4. Run the app
streamlit run dashboard.py
```

---

## 🌐 Deploy to Streamlit Cloud (Free)

1. Push all files to your GitHub repo
2. Go to https://share.streamlit.io
3. Click **New app** → select your repo → set main file to `dashboard.py`
4. Under **Advanced settings → Secrets**, add:
   ```
   APIFY_API_TOKEN = "your_token_here"
   ```
5. Click **Deploy** — live in ~2 minutes!

---

## 📊 Metric Thresholds

| Metric | Threshold | Color |
|---|---|---|
| Average Posting Gap | > 5 days | 🔴 Red |
| Average Engagement Rate | < 3% | 🔴 Red |
| Average Weekly Follower Gain | < 3 followers | 🔴 Red |

---

## 🔌 Activating Apify (Real Data)

1. Create account at https://apify.com (free trial available)
2. Get your API token at https://console.apify.com/account/integrations
3. Add to `.env`: `APIFY_API_TOKEN=your_token`
4. The app automatically switches from dummy data to real scraped data
5. Estimated cost: ~$0.10–0.50 per daily run of 10 cafés

---

## 🧩 Meta Developer Setup (For Future Messenger API)

To upgrade Batch Outreach to real automated DMs, you'll need these in Meta Developers:
1. **Facebook App** — create at https://developers.facebook.com
2. **Messenger API** — add the Messenger product
3. **pages_messaging** permission
4. **Business Verification** (required for sending to non-test users)

For now, Batch Outreach opens `m.me/` links in new tabs — functional for manual outreach.

---

## 🎨 Color Palette

| Role | Hex |
|---|---|
| Background | `#000000` Black |
| Primary | `#7D39EB` Violet |
| Accent | `#C6FF33` Lime |
| Text | `#FFFFFF` White |
| Danger | `#FF2222` Red |
