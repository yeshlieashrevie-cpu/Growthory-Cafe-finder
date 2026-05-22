/**
 * Growthory Cafe Finder — Core Orchestration Architecture
 * Runtime application state container & UI layout rendering engine
 */

const AppState = {
    collections: {
        main: [],
        pending: [],
        rejected: []
    },
    activeView: 'main' // Allowed values: 'main' | 'segregated'
};

// ─── TOOLTIP VECTOR SVG GENERATION ENGINE ───
/**
 * Synthesizes dynamic, styled structural inline SVGs representing trends inside item popovers.
 */
function buildSparklineSvg(dataPoints, metricType) {
    const width = 260;
    const height = 60;
    const paddingLeftRight = 15;
    const paddingTopBottom = 10;
    
    if (!dataPoints || dataPoints.length < 2) {
        return `<svg width="${width}" height="${height}"><text x="50%" y="50%" fill="#928da7" text-anchor="middle" font-size="11">Data pipeline sizing...</text></svg>`;
    }

    const absoluteValues = dataPoints.map(Math.abs);
    const maxVal = Math.max(...absoluteValues) || 1;
    
    // Create localized geometry plot coordinates
    const coordinates = dataPoints.map((val, index) => {
        const xPosition = paddingLeftRight + index * ((width - (paddingLeftRight * 2)) / (dataPoints.length - 1));
        // Inverse calculation matching standard vector coordinate models
        const normalizedHeight = (Math.abs(val) / maxVal) * (height - (paddingTopBottom * 2));
        const yPosition = height - paddingTopBottom - normalizedHeight;
        return { x: xPosition, y: yPosition, value: val };
    });

    // Build vector drawing configurations
    const polylinePointsAttr = coordinates.map(pt => `${pt.x},${pt.y}`).join(' ');
    
    let pathColor = '#7c4dff'; // Default application theme color 
    if (metricType === 'gap') {
        pathColor = dataPoints[dataPoints.length - 1] > 5 ? '#ff3366' : '#00ff66';
    } else if (metricType === 'engagement') {
        pathColor = dataPoints[dataPoints.length - 1] < 2 ? '#ff3366' : '#00ff66';
    } else if (metricType === 'growth') {
        pathColor = dataPoints[dataPoints.length - 1] < 0 ? '#ff3366' : '#00ff66';
    }

    const pathElement = `<polyline points="${polylinePointsAttr}" fill="none" stroke="${pathColor}" stroke-width="2.5" />`;
    
    const vertexPointsElements = coordinates.map((pt, i) => {
        let labelDisplay = pt.value;
        if (metricType === 'engagement') labelDisplay = pt.value + '%';
        if (metricType === 'gap') labelDisplay = pt.value + 'd';
        if (metricType === 'growth' && pt.value > 0) labelDisplay = '+' + pt.value;

        // Render alternating offsets for point labels to avoid horizontal text overlaps
        const textOffsetDirection = (i % 2 === 0) ? -8 : 12;

        return `
            <circle cx="${pt.x}" cy="${pt.y}" r="3.5" fill="#f5f4f8" stroke="${pathColor}" stroke-width="1.5" />
            <text x="${pt.x}" y="${pt.y + textOffsetDirection}" fill="#928da7" font-weight="600" font-size="8" text-anchor="middle">${labelDisplay}</text>
        `;
    }).join('');

    return `<svg width="${width}px" height="${height}px" style="overflow: visible;">${pathElement}${vertexPointsElements}</svg>`;
}

// ─── RENDERING ACTIONS & BINDINGS ───
/**
 * Renders the master tabular workspace grid.
 */
function renderMainWorkspace() {
    const listContainer = document.getElementById('main-cafe-list-container');
    if (!listContainer) return;

    if (AppState.collections.main.length === 0) {
        listContainer.innerHTML = `<div class="loading-state">Zero operational entries assigned to main workspace.</div>`;
        return;
    }

    listContainer.innerHTML = '';

    AppState.collections.main.forEach(cafe => {
        const row = document.createElement('div');
        row.className = 'cafe-row-item';
        row.dataset.id = cafe.name;

        // Normalize parsing data patterns directly from Flask schema model types
        const gapDays = cafe.avg_gap_days || 0;
        const gapClass = gapDays > 5 ? 'status-warning' : 'status-optimal';
        const gapLabel = gapDays < 1 ? Math.round(gapDays * 24) + ' hrs' : gapDays + ' days';

        const engRate = cafe.avg_engagement_rate || 0;
        const engClass = engRate < 2.0 ? 'status-warning' : 'status-optimal';
        const engLabel = engRate + '%';

        const weeklyGrowth = cafe.fb_growth?.weekly_adds || 0;
        const growthClass = weeklyGrowth < 1 ? 'status-warning' : 'status-optimal';
        const growthLabel = (weeklyGrowth > 0 ? '+' : '') + weeklyGrowth;

        // Source individual configuration arrays
        const gapHistoryArray = cafe.fb_consistency?.gap_history || [gapDays, gapDays];
        const engHistoryArray = [
            cafe.fb_engagement?.rate || 0,
            cafe.ig_engagement?.rate || 0,
            engRate
        ];
        const growthHistoryArray = [0, weeklyGrowth];

        row.innerHTML = `
            <div class="col-check">
                <input type="checkbox" class="row-selector" value="${cafe.name}">
            </div>
            <div class="col-social">
                <a href="${cafe.fb_url || '#'}" target="mobile_frame" class="social-link-icon lnk-fb">f</a>
                <a href="${cafe.ig_url || '#'}" target="mobile_frame" class="social-link-icon lnk-ig">ig</a>
                <a href="https://maps.google.com/?q=${encodeURIComponent(cafe.name + ' ' + cafe.location)}" target="mobile_frame" class="social-link-icon lnk-map">📍</a>
                <a href="https://m.me/${cafe.fb_username || ''}" target="mobile_frame" class="social-link-icon lnk-msg">💬</a>
            </div>
            <div class="col-identity">
                <div class="entity-meta">
                    <div class="entity-title">${cafe.name}</div>
                    <div class="entity-geo">${cafe.location || 'Unknown Venue'}</div>
                </div>
            </div>
            <div class="col-metric">
                <div class="metric-capsule ${gapClass}">
                    ${gapLabel}
                    <div class="tooltip-popover">
                        <div class="chart-title">Historical Posting Intervals</div>
                        ${buildSparklineSvg(gapHistoryArray, 'gap')}
                    </div>
                </div>
            </div>
            <div class="col-metric">
                <div class="metric-capsule ${engClass}">
                    ${engLabel}
                    <div class="tooltip-popover">
                        <div class="chart-title">Engagement Variations</div>
                        ${buildSparklineSvg(engHistoryArray, 'engagement')}
                    </div>
                </div>
            </div>
            <div class="col-metric">
                <div class="metric-capsule ${growthClass}">
                    ${growthLabel}
                    <div class="tooltip-popover">
                        <div class="chart-title">Net Follower Growth Changes</div>
                        ${buildSparklineSvg(growthHistoryArray, 'growth')}
                    </div>
                </div>
            </div>
            <div class="col-score">
                <span class="tier-capsule" style="background: ${cafe.opportunity?.glow || 'rgba(255,255,255,0.05)'}; color: ${cafe.opportunity?.color || '#fff'}; border-color: ${cafe.opportunity?.color || 'transparent'}">
                    ${cafe.opportunity?.emoji || '●'} ${cafe.opportunity?.level || 'UNKNOWN'} (${cafe.priority_score || 0})
                </span>
            </div>
            <div class="col-actions">
                <div class="routing-controls">
                    <button class="route-btn route-to-pending" title="Route to Pending" onclick="pipelineTransfer('${cafe.name}', 'main', 'pending')">←</button>
                    <button class="route-btn route-to-rejected" title="Route to Rejected" onclick="pipelineTransfer('${cafe.name}', 'main', 'rejected')">→</button>
                </div>
            </div>
        `;
        listContainer.appendChild(row);
    });
}

/**
 * Renders pipeline swimlanes mapped inside the segregated workspace viewport.
 */
function renderPipelineSwimlane(laneName, targetElementId, actionText, actionTargetLane, isRecon = false) {
    const laneContainer = document.getElementById(targetElementId);
    if (!laneContainer) return;

    laneContainer.innerHTML = '';
    
    // Track localized length indicators
    document.getElementById(`${laneName}-count-badge`).innerText = AppState.collections[laneName].length;

    if (AppState.collections[laneName].length === 0) {
        laneContainer.innerHTML = `<div class="loading-state" style="padding: 20px; font-size:12px;">Pipeline channel empty.</div>`;
        return;
    }

    AppState.collections[laneName].forEach(cafe => {
        const leadCard = document.createElement('div');
        leadCard.className = 'pipeline-lead-card';
        
        leadCard.innerHTML = `
            <div class="card-meta">
                <h3>${cafe.name}</h3>
                <p>${cafe.location || 'Undefined Region'}</p>
            </div>
            <div class="pipeline-actions-group">
                <button class="pipeline-btn" onclick="pipelineTransfer('${cafe.name}', '${laneName}', '${actionTargetLane}')">${actionText}</button>
                <button class="pipeline-btn pipeline-btn-danger" onclick="pipelinePermanentDelete('${cafe.name}', '${laneName}')">Delete</button>
            </div>
        `;
        laneContainer.appendChild(leadCard);
    });
}

/**
 * Evaluates state updates and runs UI re-renders across all dashboard view components.
 */
function refreshInterfaceViews() {
    renderMainWorkspace();
    renderPipelineSwimlane('pending', 'pending-list-container', 'Promote', 'main');
    renderPipelineSwimlane('rejected', 'rejected-list-container', 'Reconsider', 'pending', true);
}

// ─── DATA ROUTING OPERATIONS ───
/**
 * Safely moves structural objects across state arrays by matching key identifiers.
 */
function pipelineTransfer(cafeId, originCollection, destinationCollection) {
    const itemIndex = AppState.collections[originCollection].findIndex(item => item.name === cafeId);
    if (itemIndex > -1) {
        const capturedObject = AppState.collections[originCollection].splice(itemIndex, 1)[0];
        AppState.collections[destinationCollection].push(capturedObject);
        refreshInterfaceViews();
    }
}

/**
 * Drops an item directly from a designated pipeline track.
 */
function pipelinePermanentDelete(cafeId, targetCollection) {
    if (confirm(`Confirm permanent removal of ${cafeId} from tracking state?`)) {
        AppState.collections[targetCollection] = AppState.collections[targetCollection].filter(item => item.name !== cafeId);
        refreshInterfaceViews();
    }
}

// ─── DESKTOP HUD NAV EVENTS ───
/**
 * Toggles visibility variables between the tabular viewport and pipeline split viewport.
 */
function toggleView() {
    const mainWorkspace = document.getElementById('main-workspace-view');
    const segregatedWorkspace = document.getElementById('segregated-workspace-view');
    const toggleButton = document.getElementById('toggle-view-btn');

    if (AppState.activeView === 'main') {
        mainWorkspace.style.display = 'none';
        segregatedWorkspace.style.display = 'block';
        toggleButton.innerHTML = '<span class="btn-icon">📋</span> View Main Grid';
        AppState.activeView = 'segregated';
    } else {
        mainWorkspace.style.display = 'block';
        segregatedWorkspace.style.display = 'none';
        toggleButton.innerHTML = '<span class="btn-icon">🔀</span> View Segregated List';
        AppState.activeView = 'main';
    }
}

/**
 * Handles master checkbox selectors.
 */
function toggleSelectAll(masterCheckbox) {
    const checkBoxes = document.querySelectorAll('.row-selector');
    checkBoxes.forEach(cb => cb.checked = masterCheckbox.checked);
}

function getSelectedCafeNames() {
    const selectedBoxes = document.querySelectorAll('.row-selector:checked');
    return Array.from(selectedBoxes).map(cb => cb.value);
}

// Placeholder interactions for batch events
function triggerBatchOutreach() {
    const targets = getSelectedCafeNames();
    if(targets.length === 0) return alert('Select target row vectors first via the checkbox system.');
    alert(`Initializing batch programmatic communication routing to: \n${targets.join(',\n')}`);
}

function triggerBatchDelete() {
    const targets = getSelectedCafeNames();
    if(targets.length === 0) return alert('Select target row vectors to clear.');
    if (confirm(`Purge ${targets.length} selected elements?`)) {
        AppState.collections.main = AppState.collections.main.filter(item => !targets.includes(item.name));
        document.getElementById('master-checkbox').checked = false;
        refreshInterfaceViews();
    }
}

function exportCSV() {
    alert('Synthesizing CSV data structures for current data matrix... Downloader triggered.');
}

// ─── BACKEND ASYNC DATA FETCH PILLARS ───
/**
 * Requests data from the core Flask route `/api/cafes`.
 */
async function initializeDashboardPayload() {
    try {
        const response = await fetch('/api/cafes');
        if (!response.ok) throw new Error(`HTTP network fault code: ${response.status}`);
        
        const payload = await response.json();
        
        // Load data into state container
        AppState.collections.main = payload.cafes || [];
        
        // Sync operational header elements
        document.getElementById('sync-timestamp').innerText = payload.last_updated ? new Date(payload.last_updated).toLocaleString() : 'Live Stream';
        
        const modeDot = document.getElementById('system-mode-dot');
        const modeText = document.getElementById('system-mode-text');
        if (payload.demo_mode) {
            modeDot.className = 'status-dot demo';
            modeText.innerText = 'Demo Engine Operational (No Meta Token)';
        } else {
            modeDot.className = 'status-dot live';
            modeText.innerText = 'Graph Node Synchronized';
        }

        refreshInterfaceViews();
    } catch (error) {
        console.error('Critical initialization failure parsing Flask backend API stream:', error);
        document.getElementById('main-cafe-list-container').innerHTML = `
            <div class="loading-state" style="color: #ff3366;">
                Failed to communicate with Flask microservice. Validate server runtime connectivity.<br>
                <small>${error.message}</small>
            </div>
        `;
    }
}

/**
 * Triggers a refresh job execution sequence across target pipeline endpoints.
 */
async function forceRefreshData() {
    const refreshBtn = document.getElementById('refresh-btn');
    const originalContent = refreshBtn.innerHTML;
    
    try {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<span class="btn-icon">⚡</span> Processing Re-fetch...';
        
        const response = await fetch('/api/refresh', { method: 'POST' });
        if (!response.ok) throw new Error('API processing failure.');
        
        // Clear old pipeline allocations to cleanly accept incoming payload changes
        AppState.collections.pending = [];
        AppState.collections.rejected = [];
        
        await initializeDashboardPayload();
        alert('Meta Graph network endpoints synchronized.');
    } catch (e) {
        alert(`Core background process thread execution error: ${e.message}`);
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = originalContent;
    }
}

// Bind initialization routine directly to document readiness hooks
window.addEventListener('DOMContentLoaded', initializeDashboardPayload);
