/* ═══════════════════════════════════════════════════════════════════════
   CafePulse — script.js
   Handles: API fetching · Card rendering · Modal · Canvas BG · Toasts
═══════════════════════════════════════════════════════════════════════ */

"use strict";

// ─── State ────────────────────────────────────────────────────────────────────
let allCafes      = [];
let lastUpdated   = null;
let isDemoMode    = false;
let refreshTimer  = null;
let nextRefresh   = null;

// ─── DOM Refs ─────────────────────────────────────────────────────────────────
const $id  = id => document.getElementById(id);

const els = {
  statusPill:    $id("statusPill"),
  statusText:    $id("statusText"),
  demoBadge:     $id("demoBadge"),
  lastUpdated:   $id("lastUpdated"),
  refreshBtn:    $id("refreshBtn"),
  refreshIcon:   $id("refreshIcon"),
  skeletonGrid:  $id("skeletonGrid"),
  cardsGrid:     $id("cardsGrid"),
  modalBackdrop: $id("modalBackdrop"),
  modalPanel:    $id("modalPanel"),
  modalClose:    $id("modalClose"),
  modalBody:     $id("modalBody"),
  toastContainer:$id("toastContainer"),
  countdownTimer:$id("countdownTimer"),
  hstatCritical: $id("hstatCritical"),
  hstatAvgGap:   $id("hstatAvgGap"),
  hstatAvgEng:   $id("hstatAvgEng"),
  footerMode:    $id("footerMode"),
};

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initCanvas();
  startCountdown();
  loadCafes();

  els.refreshBtn.addEventListener("click", handleManualRefresh);
  els.modalClose.addEventListener("click", closeModal);
  els.modalBackdrop.addEventListener("click", e => {
    if (e.target === els.modalBackdrop) closeModal();
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeModal();
  });
});

// ─── API Calls ────────────────────────────────────────────────────────────────
async function loadCafes() {
  try {
    const data = await fetchJSON("/api/cafes");
    allCafes    = data.cafes || [];
    lastUpdated = data.last_updated;
    isDemoMode  = data.demo_mode || false;
    renderAll();
  } catch (err) {
    showSkeleton(false);
    renderError(err.message);
    showToast("Failed to load cafe data.", "error");
  }
}

async function handleManualRefresh() {
  if (els.refreshBtn.classList.contains("loading")) return;
  els.refreshBtn.classList.add("loading");
  showToast("Fetching fresh data from Meta…", "info");

  try {
    const res = await fetchJSON("/api/refresh", { method: "POST" });
    showToast(`Refreshed — ${res.count} cafes updated.`, "success");
    await loadCafes();
  } catch (err) {
    showToast("Refresh failed. Check API config.", "error");
  } finally {
    els.refreshBtn.classList.remove("loading");
  }
}

async function fetchJSON(url, opts = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...opts
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ─── Render All ───────────────────────────────────────────────────────────────
function renderAll() {
  updateStatus();
  updateHeroStats();
  showSkeleton(false);
  renderCards();
  els.footerMode.textContent = isDemoMode ? "Demo Mode — configure META_ACCESS_TOKEN for live data" : "Live Mode — Meta Graph API";
}

function updateStatus() {
  const ts = lastUpdated ? new Date(lastUpdated) : null;
  els.lastUpdated.textContent = ts
    ? ts.toLocaleString("en-PH", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
    : "—";

  if (isDemoMode) {
    els.demoBadge.style.display = "inline-flex";
    els.statusText.textContent  = "Demo Mode";
    els.statusPill.style.cssText = "background:rgba(245,200,66,0.08);border-color:rgba(245,200,66,0.25);color:#f5c842";
    els.statusPill.querySelector(".pulse-dot").style.background = "#f5c842";
  } else {
    els.demoBadge.style.display = "none";
    els.statusText.textContent  = "Live · Meta API";
    els.statusPill.style.cssText = "";
  }
}

function updateHeroStats() {
  const critCount = allCafes.filter(c => c.opportunity?.level === "CRITICAL").length;
  const avgGap    = allCafes.reduce((s, c) => s + (c.avg_gap_days || 0), 0) / Math.max(allCafes.length, 1);
  const avgEng    = allCafes.reduce((s, c) => s + (c.avg_engagement_rate || 0), 0) / Math.max(allCafes.length, 1);

  animateCount(els.hstatCritical, critCount, "", 800);
  animateCount(els.hstatAvgGap,   avgGap,   "", 900, 1);
  els.hstatAvgEng.textContent = avgEng.toFixed(2) + "%";
}

function animateCount(el, target, suffix = "", duration = 700, decimals = 0) {
  const start = performance.now();
  const from  = 0;
  const update = now => {
    const t   = Math.min((now - start) / duration, 1);
    const val = from + (target - from) * easeOut(t);
    el.textContent = val.toFixed(decimals) + suffix;
    if (t < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

// ─── Card Rendering ───────────────────────────────────────────────────────────
function renderCards() {
  els.cardsGrid.innerHTML = "";

  if (!allCafes.length) {
    els.cardsGrid.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">☕</div>
        <h3>No cafe data found</h3>
        <p>Add cafe page IDs to <code>cafes_config.json</code> and click Refresh, or check your <code>META_ACCESS_TOKEN</code> in <code>.env</code>.</p>
      </div>`;
  } else {
    allCafes.forEach((cafe, idx) => {
      const card = buildCard(cafe, idx);
      card.style.animationDelay = `${idx * 0.06}s`;
      els.cardsGrid.appendChild(card);
    });
  }

  els.cardsGrid.style.display = "flex";
}

function buildCard(cafe, idx) {
  const tier  = cafe.opportunity || {};
  const color = tier.color   || "#ff8c42";
  const glow  = tier.glow    || "rgba(255,140,66,0.3)";
  const level = tier.level   || "—";
  const emoji = tier.emoji   || "⚪";

  const fbCons = cafe.fb_consistency || {};
  const igCons = cafe.ig_consistency || {};
  const worstGap = Math.max(fbCons.avg_gap_days || 0, igCons.avg_gap_days || 0);
  const daysSince = cafe.days_since_last_post || 0;
  const engRate   = cafe.avg_engagement_rate || 0;

  // Determine value urgency colours
  const gapClass    = worstGap >= 14 ? "crit" : worstGap >= 7 ? "warn" : "good";
  const sinceClass  = daysSince >= 14 ? "crit" : daysSince >= 7 ? "warn" : "good";
  const engClass    = engRate < 0.5 ? "crit" : engRate < 2 ? "warn" : "good";

  const card = document.createElement("div");
  card.className = "cafe-card";
  card.style.setProperty("--tier-color", color);
  card.style.setProperty("--tier-glow",  glow);
  card.dataset.idx = idx;

  // Tier badge inline styles
  const tierStyles = {
    CRITICAL: "background:rgba(255,59,59,0.12);border-color:rgba(255,59,59,0.35);color:#ff3b3b",
    HIGH:     "background:rgba(255,140,66,0.12);border-color:rgba(255,140,66,0.35);color:#ff8c42",
    MEDIUM:   "background:rgba(245,200,66,0.10);border-color:rgba(245,200,66,0.3);color:#f5c842",
    LOW:      "background:rgba(66,214,140,0.10);border-color:rgba(66,214,140,0.3);color:#42d68c"
  };
  const tierStyle = tierStyles[level] || tierStyles.LOW;

  const fbUrl = cafe.fb_url || `https://facebook.com/${cafe.fb_username}`;
  const igUrl = cafe.ig_url || `https://instagram.com/${cafe.ig_username}`;

  card.innerHTML = `
    <div class="card-rank">
      <div class="rank-num">${String(idx + 1).padStart(2, "0")}</div>
      <div class="rank-tier-dot" style="background:${color};box-shadow:0 0 8px ${color}"></div>
    </div>

    <div class="card-main">
      <div class="card-info">
        <div class="card-name">${esc(cafe.name)}</div>
        <div class="card-meta">
          ${cafe.location ? `<span class="card-location"><svg width="10" height="10" viewBox="0 0 10 10" fill="none"><circle cx="5" cy="4" r="2.5" stroke="currentColor" stroke-width="1.2"/><path d="M5 9 C5 9 2 6.5 2 4a3 3 0 0 1 6 0C8 6.5 5 9 5 9z" stroke="currentColor" stroke-width="1.2" fill="none"/></svg>${esc(cafe.location)}</span>` : ""}
          <div class="card-platform-icons">
            ${cafe.fb_username ? `<span class="platform-icon fb" title="Facebook">FB</span>` : ""}
            ${cafe.ig_username ? `<span class="platform-icon ig" title="Instagram">IG</span>` : ""}
          </div>
          <span class="tier-badge" style="${tierStyle}">${emoji} ${level}</span>
        </div>
      </div>

      <div class="card-metrics">
        <div class="metric-chip">
          <span class="metric-chip-val ${gapClass}">${worstGap >= 100 ? "N/A" : worstGap.toFixed(1) + "d"}</span>
          <span class="metric-chip-label">Avg Post Gap</span>
        </div>
        <div class="metric-chip">
          <span class="metric-chip-val ${sinceClass}">${daysSince >= 999 ? "N/A" : daysSince + "d"}</span>
          <span class="metric-chip-label">Since Last Post</span>
        </div>
        <div class="metric-chip">
          <span class="metric-chip-val ${engClass}">${engRate.toFixed(2)}%</span>
          <span class="metric-chip-label">Engagement</span>
        </div>
      </div>

      <div class="score-chip" style="background:${color}18;border-color:${color}44;color:${color}">
        <span class="score-chip-val">${Math.round(cafe.priority_score || 0)}</span>
        <span class="score-chip-label">Score</span>
      </div>
    </div>

    <div class="card-arrow">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
  `;

  card.addEventListener("click", () => openModal(idx));
  return card;
}

function showSkeleton(show) {
  els.skeletonGrid.style.display = show ? "flex" : "none";
}

// ─── Modal ────────────────────────────────────────────────────────────────────
function openModal(idx) {
  const cafe = allCafes[idx];
  if (!cafe) return;
  els.modalBody.innerHTML = buildModalHTML(cafe, idx);
  els.modalBackdrop.classList.add("open");
  document.body.style.overflow = "hidden";

  // Trigger progress bar animations after mount
  requestAnimationFrame(() => {
    els.modalPanel.querySelectorAll(".progress-bar-fill[data-width]").forEach(bar => {
      bar.style.width = bar.dataset.width + "%";
    });
    animateGapBars(cafe);
  });
}

function closeModal() {
  els.modalBackdrop.classList.remove("open");
  document.body.style.overflow = "";
}

function buildModalHTML(cafe, idx) {
  const tier     = cafe.opportunity || {};
  const color    = tier.color  || "#ff8c42";
  const level    = tier.level  || "—";
  const score    = Math.round(cafe.priority_score || 0);
  const initials = cafe.name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
  const fbCons   = cafe.fb_consistency || {};
  const igCons   = cafe.ig_consistency || {};
  const fbEng    = cafe.fb_engagement  || {};
  const igEng    = cafe.ig_engagement  || {};
  const fbGrow   = cafe.fb_growth      || {};

  const worstGap    = Math.max(fbCons.avg_gap_days || 0, igCons.avg_gap_days || 0);
  const daysSince   = cafe.days_since_last_post || 0;
  const avgEng      = cafe.avg_engagement_rate || 0;
  const postsPerWk  = Math.max(fbCons.posts_per_week || 0, igCons.posts_per_week || 0);

  // Consistency score (0-100)
  const fbConsScore = fbCons.consistency_score || 0;
  const igConsScore = igCons.consistency_score || 0;
  const avgCons     = ((fbConsScore + igConsScore) / 2).toFixed(1);

  // Engagement benchmark: industry avg for cafes ≈ 1.5–3.5%
  const engBenchmark = 3.0;
  const engPct = Math.min((avgEng / engBenchmark) * 100, 100);

  // Tier badge inline styles
  const tierStyleMap = {
    CRITICAL: `background:rgba(255,59,59,0.12);border-color:rgba(255,59,59,0.4);color:#ff3b3b`,
    HIGH:     `background:rgba(255,140,66,0.12);border-color:rgba(255,140,66,0.4);color:#ff8c42`,
    MEDIUM:   `background:rgba(245,200,66,0.10);border-color:rgba(245,200,66,0.35);color:#f5c842`,
    LOW:      `background:rgba(66,214,140,0.10);border-color:rgba(66,214,140,0.35);color:#42d68c`
  };
  const tierStyle = tierStyleMap[level] || tierStyleMap.LOW;

  // KPI urgency class helpers
  const kpiClass = (val, low, med) => val <= low ? "urgent" : val <= med ? "warn" : "ok";

  const fbUrl = cafe.fb_url || `https://www.facebook.com/${cafe.fb_username}`;
  const igUrl = cafe.ig_url || `https://www.instagram.com/${cafe.ig_username}`;

  // Recent posts
  const fbPosts = cafe.recent_fb_posts || [];
  const igPosts = cafe.recent_ig_posts || [];

  const renderPostItem = (post, platform) => {
    const date = post.created_time || post.timestamp || "";
    const dateStr = date ? new Date(date).toLocaleDateString("en-PH", { month: "short", day: "numeric" }) : "—";
    const text = post.message || post.caption || "No caption";
    const likes = platform === "fb"
      ? (post.likes?.summary?.total_count ?? "—")
      : (post.like_count ?? "—");
    const comments = platform === "fb"
      ? (post.comments?.summary?.total_count ?? "—")
      : (post.comments_count ?? "—");
    return `
      <div class="post-item">
        <span class="post-date">${dateStr}</span>
        <span class="post-text">${esc(String(text).slice(0, 120))}${text.length > 120 ? "…" : ""}</span>
        <div class="post-stats">
          <span class="post-stat">❤️ ${fmt(likes)}</span>
          <span class="post-stat">💬 ${fmt(comments)}</span>
        </div>
      </div>`;
  };

  const gapData = [...(fbCons.gap_history || []), ...(igCons.gap_history || [])].slice(0, 10);
  const gapBarsHTML = gapData.length > 1
    ? gapData.map((g, i) => {
        const cls = g >= 14 ? "high-gap" : g >= 7 ? "med-gap" : "low-gap";
        return `<div class="gap-bar ${cls}" data-gap="${g}" data-i="${i}" title="${g} days gap" style="height:4px"></div>`;
      }).join("")
    : `<span style="color:var(--text-muted);font-size:12px;font-family:'DM Mono',monospace">Not enough data</span>`;

  return `
    <!-- Header -->
    <div class="modal-header">
      <div class="modal-cafe-avatar">${initials}</div>
      <div class="modal-cafe-title">
        <div class="modal-cafe-name" style="color:${color}">${esc(cafe.name)}</div>
        <div class="modal-cafe-meta">
          <span class="modal-rank-badge"># ${idx + 1} Priority</span>
          <span class="modal-score-badge" style="background:${color}18;border-color:${color}44;color:${color}">
            ${score} pts
          </span>
          <span class="tier-badge" style="${tierStyle}">${tier.emoji || ""} ${level}</span>
          ${cafe.demo ? `<span style="font-size:11px;color:var(--text-muted);font-family:'DM Mono',monospace">[demo data]</span>` : ""}
        </div>
        ${cafe.location ? `<div style="margin-top:8px;font-size:13px;color:var(--text-secondary)">📍 ${esc(cafe.location)}</div>` : ""}
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="modal-section">
      <div class="modal-section-title">🎯 Key Opportunity Signals</div>
      <div class="kpi-grid">

        <div class="kpi-card">
          <div class="kpi-top"><span class="kpi-icon">📅</span><span class="kpi-platform both">BOTH</span></div>
          <div class="kpi-val ${kpiClass(worstGap, 7, 14)}">${worstGap >= 999 ? "N/A" : worstGap.toFixed(1) + "d"}</div>
          <div class="kpi-label">Average posting gap</div>
          <div class="kpi-sub">${fbCons.cadence_label || "—"}</div>
          <div class="progress-wrap">
            <div class="progress-label"><span>Frequency</span><span>${Math.max(postsPerWk, 0).toFixed(1)}x/wk</span></div>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" data-width="${Math.min(postsPerWk / 7 * 100, 100)}" style="width:0;background:${color}"></div>
            </div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-top"><span class="kpi-icon">🕐</span><span class="kpi-platform both">BOTH</span></div>
          <div class="kpi-val ${kpiClass(daysSince, 7, 14)}">${daysSince >= 999 ? "N/A" : daysSince + "d"}</div>
          <div class="kpi-label">Days since last post</div>
          <div class="kpi-sub">Last seen: ${fbCons.last_post_date || igCons.last_post_date || "Unknown"}</div>
          <div class="progress-wrap">
            <div class="progress-label"><span>Recency</span><span>${daysSince >= 999 ? "?" : daysSince + " days ago"}</span></div>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" data-width="${Math.max(0, 100 - Math.min(daysSince / 30 * 100, 100))}" style="width:0;background:${daysSince >= 14 ? "var(--tier-critical)" : "var(--tier-high)"}"></div>
            </div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-top"><span class="kpi-icon">💓</span><span class="kpi-platform both">AVG</span></div>
          <div class="kpi-val ${avgEng < 0.5 ? "urgent" : avgEng < 2 ? "warn" : "ok"}">${avgEng.toFixed(2)}%</div>
          <div class="kpi-label">Avg engagement rate</div>
          <div class="kpi-sub">Benchmark: 1.5–3.5% for cafes</div>
          <div class="progress-wrap">
            <div class="progress-label"><span>vs. benchmark</span><span>${engPct.toFixed(0)}%</span></div>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" data-width="${engPct}" style="width:0;background:${avgEng < 1.5 ? "var(--tier-critical)" : "var(--tier-low)"}"></div>
            </div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-top"><span class="kpi-icon">📊</span><span class="kpi-platform both">BOTH</span></div>
          <div class="kpi-val">${avgCons}</div>
          <div class="kpi-label">Consistency score / 100</div>
          <div class="kpi-sub">σ = ${Math.max(fbCons.std_dev || 0, igCons.std_dev || 0).toFixed(1)} days variance</div>
          <div class="progress-wrap">
            <div class="progress-label"><span>Consistency</span><span>${avgCons}/100</span></div>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" data-width="${avgCons}" style="width:0;background:${avgCons < 40 ? "var(--tier-critical)" : avgCons < 70 ? "var(--tier-high)" : "var(--tier-low)"}"></div>
            </div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-top"><span class="kpi-icon">👥</span><span class="kpi-platform fb">FB</span></div>
          <div class="kpi-val">${fmt(cafe.fb_followers || 0)}</div>
          <div class="kpi-label">Facebook followers</div>
          <div class="kpi-sub">+${fmt(fbGrow.weekly_adds || 0)}/wk · ${(fbGrow.growth_rate_pct || 0).toFixed(3)}% growth</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-top"><span class="kpi-icon">👥</span><span class="kpi-platform ig">IG</span></div>
          <div class="kpi-val">${fmt(cafe.ig_followers || 0)}</div>
          <div class="kpi-label">Instagram followers</div>
          <div class="kpi-sub">${cafe.ig_posts_30d || 0} posts in last 30 days</div>
        </div>

      </div>
    </div>

    <!-- Platform comparison -->
    <div class="modal-section">
      <div class="modal-section-title">📱 Platform Breakdown</div>
      <div class="platform-compare">
        <div class="platform-block fb-block">
          <div class="platform-block-header fb-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="#4a9ff5"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
            Facebook
          </div>
          <div class="platform-stats">
            <div class="platform-stat-row"><span class="platform-stat-key">Followers</span><span class="platform-stat-val">${fmt(cafe.fb_followers || 0)}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Posts (30d)</span><span class="platform-stat-val">${cafe.fb_posts_30d || 0}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Avg Gap</span><span class="platform-stat-val">${fbCons.avg_gap_days >= 999 ? "N/A" : (fbCons.avg_gap_days || 0).toFixed(1) + "d"}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Engagement</span><span class="platform-stat-val">${(fbEng.rate || 0).toFixed(3)}%</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Avg Likes</span><span class="platform-stat-val">${fmt(Math.round(fbEng.avg_likes || 0))}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Avg Comments</span><span class="platform-stat-val">${fmt(Math.round(fbEng.avg_comments || 0))}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Weekly Adds</span><span class="platform-stat-val">+${fmt(fbGrow.weekly_adds || 0)}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Consistency</span><span class="platform-stat-val">${(fbCons.consistency_score || 0).toFixed(1)}/100</span></div>
          </div>
        </div>
        <div class="platform-block ig-block">
          <div class="platform-block-header ig-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="#e1306c"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
            Instagram
          </div>
          <div class="platform-stats">
            <div class="platform-stat-row"><span class="platform-stat-key">Followers</span><span class="platform-stat-val">${fmt(cafe.ig_followers || 0)}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Posts (30d)</span><span class="platform-stat-val">${cafe.ig_posts_30d || 0}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Avg Gap</span><span class="platform-stat-val">${igCons.avg_gap_days >= 999 ? "N/A" : (igCons.avg_gap_days || 0).toFixed(1) + "d"}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Engagement</span><span class="platform-stat-val">${(igEng.rate || 0).toFixed(3)}%</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Avg Likes</span><span class="platform-stat-val">${fmt(Math.round(igEng.avg_likes || 0))}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Avg Comments</span><span class="platform-stat-val">${fmt(Math.round(igEng.avg_comments || 0))}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Cadence</span><span class="platform-stat-val">${igCons.cadence_label || "—"}</span></div>
            <div class="platform-stat-row"><span class="platform-stat-key">Consistency</span><span class="platform-stat-val">${(igCons.consistency_score || 0).toFixed(1)}/100</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Posting Gap Timeline -->
    <div class="modal-section">
      <div class="modal-section-title">📈 Posting Gap History (days between posts)</div>
      <div class="gap-timeline" id="gapTimeline">${gapBarsHTML}</div>
      <div class="gap-timeline-label">← Older &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; More recent →</div>
    </div>

    <!-- Recent Posts -->
    ${(fbPosts.length || igPosts.length) ? `
    <div class="modal-section">
      <div class="modal-section-title">📝 Recent Posts</div>
      ${fbPosts.length ? `<div style="margin-bottom:8px"><span style="font-family:'DM Mono',monospace;font-size:10px;color:#4a9ff5;text-transform:uppercase;letter-spacing:1px">Facebook</span></div>
      <div class="recent-posts" style="margin-bottom:16px">${fbPosts.map(p => renderPostItem(p, "fb")).join("")}</div>` : ""}
      ${igPosts.length ? `<div style="margin-bottom:8px"><span style="font-family:'DM Mono',monospace;font-size:10px;color:#e1306c;text-transform:uppercase;letter-spacing:1px">Instagram</span></div>
      <div class="recent-posts">${igPosts.map(p => renderPostItem(p, "ig")).join("")}</div>` : ""}
    </div>` : ""}

    <!-- Action Buttons -->
    <div class="modal-actions">
      ${cafe.fb_username ? `<a href="${fbUrl}" target="_blank" rel="noopener noreferrer" class="action-btn fb-btn">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
        View on Facebook
      </a>` : ""}
      ${cafe.ig_username ? `<a href="${igUrl}" target="_blank" rel="noopener noreferrer" class="action-btn ig-btn">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
        View on Instagram
      </a>` : ""}
      <button class="action-btn report-btn" onclick="copyOpportunityReport(${idx})">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 2h10v10H2zM5 5h4M5 7h4M5 9h2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
        Copy Opportunity Report
      </button>
    </div>
  `;
}

function animateGapBars(cafe) {
  const fbGaps = (cafe.fb_consistency || {}).gap_history || [];
  const igGaps = (cafe.ig_consistency || {}).gap_history || [];
  const allGaps = [...fbGaps, ...igGaps].slice(0, 10);
  if (!allGaps.length) return;

  const maxGap = Math.max(...allGaps, 1);
  const bars = document.querySelectorAll(".gap-bar[data-i]");
  bars.forEach(bar => {
    const i   = parseInt(bar.dataset.i);
    const gap = allGaps[i] || 0;
    const h   = Math.max(4, (gap / maxGap) * 50);
    setTimeout(() => { bar.style.height = h + "px"; }, i * 60);
  });
}

// ─── Copy Report ──────────────────────────────────────────────────────────────
window.copyOpportunityReport = function(idx) {
  const cafe = allCafes[idx];
  if (!cafe) return;
  const fbCons = cafe.fb_consistency || {};
  const igCons = cafe.ig_consistency || {};
  const report = `
☕ CAFEPULSE OPPORTUNITY REPORT
═══════════════════════════════════════
Cafe:            ${cafe.name}
Location:        ${cafe.location || "—"}
Rank:            #${idx + 1} of 10
Priority Score:  ${Math.round(cafe.priority_score || 0)} pts (${cafe.opportunity?.level || "—"})
Generated:       ${new Date().toLocaleString("en-PH")}

📊 KEY METRICS
───────────────────────────────────────
Avg Posting Gap:     ${cafe.avg_gap_days?.toFixed(1) || "—"} days
Days Since Last Post: ${cafe.days_since_last_post >= 999 ? "Unknown" : cafe.days_since_last_post + " days"}
Avg Engagement Rate:  ${(cafe.avg_engagement_rate || 0).toFixed(3)}%
FB Consistency Score: ${(fbCons.consistency_score || 0).toFixed(1)}/100
IG Consistency Score: ${(igCons.consistency_score || 0).toFixed(1)}/100

📱 FACEBOOK
───────────────────────────────────────
Followers:     ${(cafe.fb_followers || 0).toLocaleString()}
Posts (30d):   ${cafe.fb_posts_30d || 0}
Engagement:    ${(cafe.fb_engagement?.rate || 0).toFixed(3)}%
Weekly Adds:   +${cafe.fb_growth?.weekly_adds || 0}
Profile:       ${cafe.fb_url || "—"}

📱 INSTAGRAM
───────────────────────────────────────
Followers:     ${(cafe.ig_followers || 0).toLocaleString()}
Posts (30d):   ${cafe.ig_posts_30d || 0}
Engagement:    ${(cafe.ig_engagement?.rate || 0).toFixed(3)}%
Profile:       ${cafe.ig_url || "—"}

🎯 OPPORTUNITY SUMMARY
───────────────────────────────────────
${generateOpportunitySummary(cafe)}

— CafePulse · Powered by Meta Graph API
`.trim();

  navigator.clipboard.writeText(report)
    .then(() => showToast("Opportunity report copied to clipboard!", "success"))
    .catch(() => showToast("Clipboard copy failed. Try again.", "error"));
};

function generateOpportunitySummary(cafe) {
  const lines = [];
  const daysSince = cafe.days_since_last_post || 0;
  const avgGap    = cafe.avg_gap_days || 0;
  const engRate   = cafe.avg_engagement_rate || 0;
  const fbFans    = cafe.fb_followers || 0;
  const igFans    = cafe.ig_followers || 0;
  const level     = cafe.opportunity?.level || "";

  if (daysSince >= 14) lines.push(`• Has not posted in ${daysSince} days — HIGH urgency for outreach.`);
  else if (daysSince >= 7) lines.push(`• Last post was ${daysSince} days ago — moderate posting gap.`);

  if (avgGap >= 14) lines.push(`• Posting frequency is very low (avg ${avgGap.toFixed(1)} day gap) — inconsistent content strategy.`);
  else if (avgGap >= 7) lines.push(`• Posting only weekly on average — room to improve consistency.`);

  if (engRate < 0.5) lines.push(`• Engagement rate (${engRate.toFixed(2)}%) is critically low — audience not responding.`);
  else if (engRate < 2) lines.push(`• Engagement rate (${engRate.toFixed(2)}%) is below the 2–3.5% cafe benchmark.`);

  if (fbFans < 1000) lines.push(`• Facebook page has fewer than 1,000 followers — early growth stage.`);
  if (igFans < 1000) lines.push(`• Instagram account has fewer than 1,000 followers — early growth stage.`);

  if (!lines.length) lines.push("• Account appears active. Consider a loyalty / repeat customer campaign.");

  lines.push("");
  lines.push(`📦 Recommended Package: ${level === "CRITICAL" || level === "HIGH" ? "Growth Starter + Roadmap Site" : "Engagement Booster PDF"}`);

  return lines.join("\n");
}

// ─── Countdown Timer ──────────────────────────────────────────────────────────
function startCountdown() {
  const tick = () => {
    const now  = new Date();
    const next = new Date();
    next.setHours(6, 0, 0, 0);
    if (next <= now) next.setDate(next.getDate() + 1);
    const diff    = next - now;
    const h       = Math.floor(diff / 3600000);
    const m       = Math.floor((diff % 3600000) / 60000);
    const s       = Math.floor((diff % 60000) / 1000);
    els.countdownTimer.textContent = `${pad(h)}h ${pad(m)}m ${pad(s)}s`;
  };
  tick();
  refreshTimer = setInterval(tick, 1000);
}

function pad(n) { return String(n).padStart(2, "0"); }

// ─── Toast Notifications ──────────────────────────────────────────────────────
function showToast(message, type = "info") {
  const icons = { success: "✅", error: "❌", info: "☕" };
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type] || "ℹ️"}</span><span>${esc(message)}</span>`;
  els.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.classList.add("exit");
    setTimeout(() => toast.remove(), 350);
  }, 3800);
}

// ─── Error State ──────────────────────────────────────────────────────────────
function renderError(msg) {
  els.cardsGrid.innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">⚠️</div>
      <h3>Could not load data</h3>
      <p>${esc(msg)}<br><br>Ensure the Flask server is running on port 5000 and your <code>.env</code> file is configured.</p>
    </div>`;
  els.cardsGrid.style.display = "flex";
  els.statusText.textContent = "Connection error";
  els.statusPill.classList.add("error");
}

// ─── Background Canvas (particle field + mesh gradient) ───────────────────────
function initCanvas() {
  const canvas = $id("bgCanvas");
  const ctx    = canvas.getContext("2d");
  let W, H, particles = [], mouseX = 0, mouseY = 0;

  const AMBER = [255, 140, 66];
  const CORAL = [255, 61, 110];
  const TEAL  = [0, 212, 170];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
    buildParticles();
  }

  function buildParticles() {
    const count = Math.min(Math.floor((W * H) / 14000), 80);
    particles = Array.from({ length: count }, () => newParticle());
  }

  function newParticle() {
    const palettes = [AMBER, CORAL, TEAL];
    const col = palettes[Math.floor(Math.random() * palettes.length)];
    return {
      x:    Math.random() * W,
      y:    Math.random() * H,
      r:    Math.random() * 1.4 + 0.3,
      vx:   (Math.random() - 0.5) * 0.25,
      vy:   (Math.random() - 0.5) * 0.25,
      col:  col,
      alpha: Math.random() * 0.35 + 0.05,
    };
  }

  function drawMeshGradient() {
    // Slow-moving ambient blobs
    const t = Date.now() / 12000;
    const blobs = [
      { x: W * (0.2 + Math.sin(t * 0.7) * 0.1), y: H * (0.3 + Math.cos(t) * 0.15), r: W * 0.35, col: [255, 140, 66], a: 0.035 },
      { x: W * (0.75 + Math.cos(t * 0.6) * 0.1), y: H * (0.6 + Math.sin(t * 0.8) * 0.12), r: W * 0.3, col: [255, 61, 110], a: 0.025 },
      { x: W * (0.5 + Math.sin(t * 0.5) * 0.15), y: H * (0.15 + Math.cos(t * 0.9) * 0.08), r: W * 0.25, col: [0, 212, 170], a: 0.02 },
    ];
    blobs.forEach(b => {
      const g = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
      g.addColorStop(0, `rgba(${b.col},${b.a})`);
      g.addColorStop(1, `rgba(${b.col},0)`);
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
    });
  }

  let connMaxDist = 130;

  function drawParticles() {
    particles.forEach(p => {
      // Subtle mouse attraction
      const dx = mouseX - p.x;
      const dy = mouseY - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 200) {
        p.vx += dx / dist * 0.004;
        p.vy += dy / dist * 0.004;
      }

      p.vx *= 0.98;
      p.vy *= 0.98;
      p.x  += p.vx;
      p.y  += p.vy;

      if (p.x < 0) p.x = W;
      if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H;
      if (p.y > H) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.col},${p.alpha})`;
      ctx.fill();
    });

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const a = particles[i], b = particles[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < connMaxDist) {
          const alpha = (1 - d / connMaxDist) * 0.08;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(255,140,66,${alpha})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function loop() {
    ctx.clearRect(0, 0, W, H);
    drawMeshGradient();
    drawParticles();
    requestAnimationFrame(loop);
  }

  window.addEventListener("resize", resize);
  window.addEventListener("mousemove", e => { mouseX = e.clientX; mouseY = e.clientY; });
  resize();
  loop();
}

// ─── Utilities ────────────────────────────────────────────────────────────────
function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function fmt(n) {
  const num = Number(n);
  if (isNaN(num)) return "—";
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
  if (num >= 1_000)     return (num / 1_000).toFixed(1) + "K";
  return String(num);
}