import streamlit as st
import streamlit.components.v1 as components
import json
import os
import random
from datetime import datetime, timedelta, timezone

# ─── 1. STREAMLIT PAGE CONFIGURATION ─────────────────────────────────────────
st.set_page_config(page_title="Growthory Cafe Finder", layout="wide", initial_sidebar_state="collapsed")

CACHE_FILE = "daily_cache.json"

# ─── 2. PYTHON BACKEND LOGIC (DATA ENGINE) ───────────────────────────────────
# We generate the data using standard Python, exactly as your old backend did.

class DemoDataEngine:
    SAMPLE_CAFES = [
        ("Brewed Awakening", "brewedawakeningcafe", "Makati, Manila", 3, 2200, 0.8),
        ("The Roast Republic", "roastrepublic", "BGC, Taguig", 7, 5400, 2.1),
        ("Sip & Scribble", "sipandscribble", "Quezon City", 1, 980, 0.4),
        ("Dusk Espresso Bar", "duskespresso", "Cebu City", 14, 8900, 3.8),
        ("The Lazy Barista", "thelazybarista", "Davao City", 20, 430, 0.2),
        ("Fogged Lens Cafe", "foggedlenscafe", "Pasig", 4, 3100, 1.5),
        ("Grounds & Grains", "groundsandgrains", "Antipolo, Rizal", 35, 260, 0.1),
        ("Ember & Oak Coffee", "emberoakcoffee", "San Juan", 2, 12400, 5.2),
    ]

    @classmethod
    def generate(cls) -> dict:
        cafes = []
        for name, user, loc, avg_gap, fans, eng_mult in cls.SAMPLE_CAFES:
            # Generate 5-point histories for the UI graphs
            gap_hist = [max(1, avg_gap + random.randint(-3, 3)) for _ in range(5)]
            eng_hist = [round(eng_mult * random.uniform(5, 15), 1) for _ in range(5)]
            foll_hist = [random.randint(-5, 20) for _ in range(5)]
            
            avg_eng = round(sum(eng_hist) / 5, 1)
            avg_foll = round(sum(foll_hist) / 5, 1)
            
            # Opportunity tier logic
            score = (avg_gap * 2) + max(0, 5 - avg_eng)
            if score >= 30: tier = {"level": "CRITICAL", "color": "#ff3366", "glow": "rgba(255,51,102,0.2)"}
            elif score >= 15: tier = {"level": "HIGH", "color": "#ff9900", "glow": "rgba(255,153,0,0.2)"}
            else: tier = {"level": "OPTIMAL", "color": "#00ff66", "glow": "rgba(0,255,102,0.2)"}

            cafes.append({
                "name": name,
                "location": loc,
                "fb_username": user,
                "ig_username": user,
                "fb_url": f"https://www.facebook.com/{user}",
                "ig_url": f"https://www.instagram.com/{user}",
                "metrics": {
                    "avg_gap_days": sum(gap_hist) / 5,
                    "gap_history": gap_hist,
                    "avg_engagement": avg_eng,
                    "engagement_history": eng_hist,
                    "avg_weekly_followers": avg_foll,
                    "follower_history": foll_hist
                },
                "priority_score": round(score, 1),
                "opportunity": tier
            })
        
        # Sort by priority score (highest needs most help)
        cafes.sort(key=lambda x: x["priority_score"], reverse=True)
        return {"cafes": cafes, "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), "demo_mode": True}

def load_or_refresh_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    # If no cache, generate and save
    data = DemoDataEngine.generate()
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)
    return data

# Streamlit native refresh trigger
c1, c2 = st.columns([8, 2])
with c2:
    if st.button("🔄 Pull Live API Data", use_container_width=True):
        new_data = DemoDataEngine.generate() # Replace this line with your actual Meta API fetch function when ready
        with open(CACHE_FILE, "w") as f:
            json.dump(new_data, f)
        st.rerun()

# ─── 3. FRONTEND UI BUNDLE (HTML/CSS/JS) ─────────────────────────────────────
# We use a raw string literal to avoid Streamlit/Python curly-brace conflicts.

frontend_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0b071a; --bg-surface: #130e29; --bg-surface-elevated: #1e173d;
            --border-color: rgba(255, 255, 255, 0.08); --border-color-hover: rgba(255, 255, 255, 0.16);
            --accent-purple: #7c4dff; --accent-purple-glow: rgba(124, 77, 255, 0.25);
            --neon-green: #00ff66; --neon-green-dim: rgba(0, 255, 102, 0.15);
            --neon-red: #ff3366; --neon-red-dim: rgba(255, 51, 102, 0.15);
            --text-primary: #f5f4f8; --text-muted: #928da7;
            --font-stack: 'Inter', sans-serif;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: var(--bg-main); color: var(--text-primary); font-family: var(--font-stack); display: flex; height: 100vh; overflow: hidden; padding: 15px; }
        
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: var(--bg-surface-elevated); border-radius: 10px; }

        .dashboard-container { display: flex; width: 100%; height: 100%; gap: 20px; }
        .preview-panel { flex: 0 0 350px; display: flex; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 20px; padding: 15px; }
        .main-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

        .device-mockup { width: 100%; height: 100%; background: #000; border: 10px solid #252131; border-radius: 36px; display: flex; flex-direction: column; overflow: hidden; }
        .device-screen { flex: 1; background: #fff; }
        .device-screen iframe { width: 100%; height: 100%; border: none; }

        .dashboard-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 15px; border-bottom: 1px solid var(--border-color); }
        .brand-identity h1 { font-size: 22px; font-weight: 800; }
        .brand-identity .accent-text { color: var(--accent-purple); }

        .action-bar { display: flex; gap: 8px; }
        .btn { font-family: var(--font-stack); font-weight: 600; font-size: 12px; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-surface); color: white; cursor: pointer; transition: 0.2s; }
        .btn:hover { background: var(--bg-surface-elevated); }
        .btn-primary { background: var(--accent-purple); border-color: var(--accent-purple); }

        .workspace-viewport { flex: 1; overflow-y: auto; margin-top: 15px; padding-right: 5px; }
        .workspace-card { background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 12px; }

        .table-header-row { display: flex; padding: 12px 20px; background: rgba(255, 255, 255, 0.02); border-bottom: 1px solid var(--border-color); font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }
        .col-check { flex: 0 0 30px; } .col-social { flex: 0 0 130px; display: flex; gap: 4px; }
        .col-identity { flex: 1; } .col-metric { flex: 0 0 100px; text-align: center; }
        .col-score { flex: 0 0 120px; text-align: center; } .col-actions { flex: 0 0 90px; display: flex; justify-content: flex-end; }

        .cafe-row-item { display: flex; align-items: center; padding: 14px 20px; border-bottom: 1px solid var(--border-color); }
        .social-link-icon { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 6px; text-decoration: none; font-size: 11px; font-weight: bold; color: white !important; }
        .lnk-fb { background: #1877f2; } .lnk-ig { background: #e1306c; } .lnk-map { background: #24292e; border: 1px solid #444; } .lnk-msg { background: #0084ff; }

        .entity-title { font-weight: 600; font-size: 14px; } .entity-geo { font-size: 12px; color: var(--text-muted); }

        .metric-capsule { position: relative; display: inline-flex; width: 75px; height: 36px; border-radius: 6px; font-weight: 700; font-size: 12px; align-items: center; justify-content: center; cursor: pointer; }
        .status-optimal { background-color: var(--neon-green-dim); color: var(--neon-green); border: 1px solid rgba(0, 255, 102, 0.2); }
        .status-warning { background-color: var(--neon-red-dim); color: var(--neon-red); border: 1px solid rgba(255, 51, 102, 0.2); }

        /* SVG Tooltip Popovers */
        .tooltip-popover { visibility: hidden; opacity: 0; position: absolute; bottom: 130%; left: 50%; transform: translateX(-50%); background-color: #120d2b; border: 1px solid var(--border-color-hover); padding: 12px; border-radius: 10px; z-index: 100; box-shadow: 0 10px 25px rgba(0,0,0,0.5); pointer-events: none; transition: 0.2s; }
        .metric-capsule:hover .tooltip-popover { visibility: visible; opacity: 1; }
        .chart-title { font-size: 9px; text-transform: uppercase; color: var(--text-muted); text-align: center; margin-bottom: 8px; }

        .routing-controls { display: flex; background: var(--bg-main); border: 1px solid var(--border-color); border-radius: 6px; overflow: hidden; }
        .route-btn { width: 32px; height: 30px; border: none; background: transparent; color: var(--text-muted); font-size: 16px; cursor: pointer; transition: 0.15s; }
        .route-to-pending:hover { background-color: var(--neon-green-dim); color: var(--neon-green); }
        .route-to-rejected:hover { background-color: var(--neon-red-dim); color: var(--neon-red); }

        /* Segregated Lists */
        .segregated-columns-grid { display: flex; gap: 20px; height: 100%; }
        .pipeline-column { flex: 1; display: flex; flex-direction: column; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; }
        .column-header { display: flex; justify-content: space-between; padding: 14px 18px; background: rgba(255, 255, 255, 0.02); border-bottom: 1px solid var(--border-color); font-size: 12px; font-weight: bold; }
        .pipeline-scroll-area { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .pipeline-lead-card { background: var(--bg-surface-elevated); border: 1px solid var(--border-color); padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        .pipeline-btn { font-size: 10px; padding: 6px 10px; border-radius: 4px; border: none; background: var(--neon-green); color: black; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <aside class="preview-panel">
            <div class="device-mockup">
                <div class="device-screen">
                    <iframe name="mobile_frame" src="https://m.facebook.com/"></iframe>
                </div>
            </div>
        </aside>

        <main class="main-panel">
            <header class="dashboard-header">
                <div class="brand-identity">
                    <h1>Growthory <span class="accent-text">Cafe Finder</span></h1>
                    <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">Node Sync: <span id="sync-time"></span></div>
                </div>
                <div class="action-bar">
                    <button class="btn" onclick="alert('Batch Outreach Initialized.')">✉ Batch Outreach</button>
                    <button class="btn btn-primary" id="toggle-view-btn" onclick="toggleView()">🔀 View Segregated List</button>
                    <button class="btn" onclick="alert('Downloading CSV Data...')">📥 Download CSV</button>
                </div>
            </header>

            <div id="main-workspace-view" class="workspace-viewport">
                <div class="workspace-card">
                    <div class="table-header-row">
                        <div class="col-check"><input type="checkbox" id="master-check" onclick="toggleAll()"></div>
                        <div class="col-social">Channels</div>
                        <div class="col-identity">Business Entity</div>
                        <div class="col-metric">Post Gap</div>
                        <div class="col-metric">Engagement</div>
                        <div class="col-metric">Growth</div>
                        <div class="col-score">Opportunity</div>
                        <div class="col-actions">Route</div>
                    </div>
                    <div id="main-cafe-list-container"></div>
                </div>
            </div>

            <div id="segregated-workspace-view" class="workspace-viewport" style="display: none;">
                <div class="segregated-columns-grid">
                    <div class="pipeline-column">
                        <div class="column-header" style="color:var(--neon-green)">● PENDING LEAD ROUTE (<span id="pending-count">0</span>)</div>
                        <div id="pending-list-container" class="pipeline-scroll-area"></div>
                    </div>
                    <div class="pipeline-column">
                        <div class="column-header" style="color:var(--neon-red)">● REJECTED / ARCHIVED (<span id="rejected-count">0</span>)</div>
                        <div id="rejected-list-container" class="pipeline-scroll-area"></div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Data injected safely from Python Engine
        const AppData = __PYTHON_DATA_PAYLOAD__;
        
        const AppState = {
            collections: { main: AppData.cafes || [], pending: [], rejected: [] },
            activeView: 'main'
        };

        document.getElementById('sync-time').innerText = AppData.last_updated || 'Live';

        // Dynamic SVG Sparkline Generator
        function buildSparkline(dataArray, metricType) {
            const w = 220, h = 50;
            if(!dataArray || dataArray.length < 2) return `<svg width="${w}" height="${h}"></svg>`;
            
            const maxVal = Math.max(...dataArray.map(Math.abs)) || 1;
            const pts = dataArray.map((val, i) => {
                const x = 10 + i * ((w - 20) / (dataArray.length - 1));
                const y = h - 15 - (Math.abs(val) / maxVal) * (h - 20);
                return {x, y, val};
            });

            let color = '#7c4dff';
            const lastVal = pts[pts.length-1].val;
            if (metricType === 'gap') color = lastVal > 5 ? '#ff3366' : '#00ff66';
            if (metricType === 'eng') color = lastVal < 10 ? '#ff3366' : '#00ff66';
            if (metricType === 'fol') color = lastVal < 5 ? '#ff3366' : '#00ff66';

            const poly = `<polyline points="${pts.map(p=>`${p.x},${p.y}`).join(' ')}" fill="none" stroke="${color}" stroke-width="2"/>`;
            const nodes = pts.map(p => `
                <circle cx="${p.x}" cy="${p.y}" r="3" fill="#fff"/>
                <text x="${p.x}" y="${h-2}" fill="#928da7" font-size="9" text-anchor="middle">${metricType==='eng'?p.val+'%':p.val}</text>
            `).join('');

            return `<svg width="${w}" height="${h}">${poly}${nodes}</svg>`;
        }

        // Main Render Function
        function renderInterface() {
            const listCont = document.getElementById('main-cafe-list-container');
            listCont.innerHTML = '';
            
            AppState.collections.main.forEach(cafe => {
                const m = cafe.metrics;
                const gapCls = m.avg_gap_days > 5 ? 'status-warning' : 'status-optimal';
                const engCls = m.avg_engagement < 10 ? 'status-warning' : 'status-optimal';
                const folCls = m.avg_weekly_followers < 5 ? 'status-warning' : 'status-optimal';
                
                const gapTxt = m.avg_gap_days < 1 ? Math.round(m.avg_gap_days*24)+'H' : Math.round(m.avg_gap_days)+'D';
                const folTxt = m.avg_weekly_followers > 0 ? '+'+Math.round(m.avg_weekly_followers) : Math.round(m.avg_weekly_followers);
                
                // Proper Google Maps URL encoding
                const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(cafe.name + ' ' + cafe.location)}`;

                const row = document.createElement('div');
                row.className = 'cafe-row-item';
                row.innerHTML = `
                    <div class="col-check"><input type="checkbox" class="row-chk"></div>
                    <div class="col-social">
                        <a href="${cafe.fb_url}" target="mobile_frame" class="social-link-icon lnk-fb">f</a>
                        <a href="${cafe.ig_url}" target="mobile_frame" class="social-link-icon lnk-ig">ig</a>
                        <a href="${mapUrl}" target="mobile_frame" class="social-link-icon lnk-map">📍</a>
                        <a href="https://m.me/${cafe.fb_username}" target="mobile_frame" class="social-link-icon lnk-msg">💬</a>
                    </div>
                    <div class="col-identity">
                        <div class="entity-title">[${cafe.name}]</div>
                        <div class="entity-geo">[${cafe.location}]</div>
                    </div>
                    <div class="col-metric">
                        <div class="metric-capsule ${gapCls}">${gapTxt}
                            <div class="tooltip-popover"><div class="chart-title">Gap Pattern</div>${buildSparkline(m.gap_history, 'gap')}</div>
                        </div>
                    </div>
                    <div class="col-metric">
                        <div class="metric-capsule ${engCls}">${Math.round(m.avg_engagement)}%
                            <div class="tooltip-popover"><div class="chart-title">Engagement</div>${buildSparkline(m.engagement_history, 'eng')}</div>
                        </div>
                    </div>
                    <div class="col-metric">
                        <div class="metric-capsule ${folCls}">${folTxt}
                            <div class="tooltip-popover"><div class="chart-title">Followers</div>${buildSparkline(m.follower_history, 'fol')}</div>
                        </div>
                    </div>
                    <div class="col-score">
                        <span style="font-size:11px; font-weight:bold; background:${cafe.opportunity.glow}; color:${cafe.opportunity.color}; padding:4px 8px; border-radius:12px; border:1px solid ${cafe.opportunity.color}">
                            ${cafe.opportunity.level}
                        </span>
                    </div>
                    <div class="col-actions">
                        <div class="routing-controls">
                            <button class="route-btn route-to-pending" onclick="transfer('${cafe.name}', 'main', 'pending')">←</button>
                            <button class="route-btn route-to-rejected" onclick="transfer('${cafe.name}', 'main', 'rejected')">→</button>
                        </div>
                    </div>
                `;
                listCont.appendChild(row);
            });

            // Render Segregated Lists
            renderLane('pending', 'pending-list-container', 'ADD', 'main', 'var(--neon-green)', 'black');
            renderLane('rejected', 'rejected-list-container', 'RECON', 'pending', 'var(--neon-red)', 'white');
        }

        function renderLane(laneId, containerId, btnTxt, targetLane, btnColor, textColor) {
            const cont = document.getElementById(containerId);
            cont.innerHTML = '';
            document.getElementById(laneId + '-count').innerText = AppState.collections[laneId].length;
            
            AppState.collections[laneId].forEach(cafe => {
                const card = document.createElement('div');
                card.className = 'pipeline-lead-card';
                card.innerHTML = `
                    <div>
                        <div class="entity-title">[${cafe.name}]</div>
                        <div class="entity-geo">[${cafe.location}]</div>
                    </div>
                    <div style="display:flex; gap:5px;">
                        <button class="pipeline-btn" style="background:${btnColor}; color:${textColor}" onclick="transfer('${cafe.name}', '${laneId}', '${targetLane}')">${btnTxt}</button>
                        <button class="pipeline-btn" style="background:transparent; color:var(--neon-red); border:1px solid var(--neon-red);" onclick="deleteItem('${cafe.name}', '${laneId}')">DEL</button>
                    </div>
                `;
                cont.appendChild(card);
            });
        }

        // Logic Actions
        function transfer(name, from, to) {
            const idx = AppState.collections[from].findIndex(c => c.name === name);
            if(idx > -1) {
                AppState.collections[to].push(AppState.collections[from].splice(idx, 1)[0]);
                renderInterface();
            }
        }

        function deleteItem(name, from) {
            AppState.collections[from] = AppState.collections[from].filter(c => c.name !== name);
            renderInterface();
        }

        function toggleAll() {
            const master = document.getElementById('master-check').checked;
            document.querySelectorAll('.row-chk').forEach(c => c.checked = master);
        }

        function toggleView() {
            const main = document.getElementById('main-workspace-view');
            const seg = document.getElementById('segregated-workspace-view');
            const btn = document.getElementById('toggle-view-btn');
            
            if (AppState.activeView === 'main') {
                main.style.display = 'none'; seg.style.display = 'block';
                btn.innerHTML = '📋 View Main Grid'; AppState.activeView = 'segregated';
            } else {
                main.style.display = 'block'; seg.style.display = 'none';
                btn.innerHTML = '🔀 View Segregated List'; AppState.activeView = 'main';
            }
        }

        // Init
        window.onload = renderInterface;
    </script>
</body>
</html>
"""

# ─── 4. DATA INJECTION & COMPONENT RENDER ────────────────────────────────────

# Load backend data
data_payload = load_or_refresh_cache()
json_string = json.dumps(data_payload)

# Safely inject the Python data string into our JavaScript block
final_html = frontend_html.replace("__PYTHON_DATA_PAYLOAD__", json_string)

# Render the massive component inside Streamlit spanning the full height
components.html(final_html, height=850, scrolling=False)
