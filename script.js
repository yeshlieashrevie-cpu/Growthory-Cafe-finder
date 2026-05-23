document.addEventListener("DOMContentLoaded", () => {

// =========================================================
// GLOBAL STATE
// =========================================================

let cafes = window.CAFE_DATA || []

let selectedIds = []

let currentView = "main"

let currentChart = null

// =========================================================
// ELEMENTS
// =========================================================

const cafeList =
    document.getElementById("cafe-list")

const mobileFrame =
    document.getElementById("mobile-frame")

const graphPopup =
    document.getElementById("graph-popup")

const graphCanvas =
    document.getElementById("graph-canvas")

const popupTitle =
    document.getElementById("popup-title")

const searchInput =
    document.getElementById("search-input")

// =========================================================
// TOAST
// =========================================================

function showToast(message){

    const toast =
        document.createElement("div")

    toast.className = "toast"

    toast.innerText = message

    document.body.appendChild(toast)

    setTimeout(() => {

        toast.style.opacity = "0"

        setTimeout(() => {

            toast.remove()

        }, 300)

    }, 2000)
}

// =========================================================
// LOADER
// =========================================================

function renderLoader(){

    cafeList.innerHTML = `
    
    <div class="loader">

        <div class="loader-spinner"></div>

    </div>
    
    `
}

// =========================================================
// EMPTY STATE
// =========================================================

function renderEmpty(message){

    cafeList.innerHTML = `
    
    <div class="empty-state">

        <h3>No cafes found</h3>

        <p>${message}</p>

    </div>
    
    `
}

// =========================================================
// LOAD DATA
// =========================================================

function loadCafeData(){

    renderLoader()

    try{

        cafes = window.CAFE_DATA || []

        renderCurrentView()

    }catch(error){

        console.error(error)

        renderEmpty(
            "Failed to load cafes."
        )
    }
}

// =========================================================
// FILTER CAFES
// =========================================================

function getFilteredCafes(){

    const query =
        searchInput.value.toLowerCase()

    return cafes.filter(cafe => {

        const matchesView =
            (cafe.status || "main") === currentView

        const matchesSearch =
            cafe.name
                .toLowerCase()
                .includes(query)

        return (
            matchesView &&
            matchesSearch
        )
    })
}

// =========================================================
// RENDER VIEW
// =========================================================

function renderCurrentView(){

    const filtered =
        getFilteredCafes()

    if(filtered.length === 0){

        renderEmpty(
            "Try another search."
        )

        return
    }

    cafeList.innerHTML = ""

    filtered.forEach(cafe => {

        renderCafeCard(cafe)

    })
}

// =========================================================
// METRIC COLORS
// =========================================================

function metricClass(type, value){

    if(type === "gap"){

        if(value <= 3)
            return "metric-good"

        if(value <= 6)
            return "metric-warning"

        return "metric-danger"
    }

    if(type === "engagement"){

        if(value >= 10)
            return "metric-good"

        if(value >= 5)
            return "metric-warning"

        return "metric-danger"
    }

    if(type === "followers"){

        if(value >= 5)
            return "metric-good"

        if(value >= 0)
            return "metric-warning"

        return "metric-danger"
    }

    return ""
}

// =========================================================
// RENDER CARD
// =========================================================

function renderCafeCard(cafe){

    const card =
        document.createElement("div")

    card.className = "cafe-card"

    const gapHistory =
        JSON.parse(cafe.posting_history)

    const engagementHistory =
        JSON.parse(cafe.engagement_history)

    const followersHistory =
        JSON.parse(cafe.followers_history)

    card.innerHTML = `

    <div class="card-top">

        <div class="checkbox-wrapper">

            <input
                type="checkbox"
                class="checkbox"
            >

            <div class="cafe-info">

                <h3>${cafe.name}</h3>

                <p>${cafe.location}</p>

            </div>

        </div>

        <div class="status-badge ${cafe.status}">
            ${cafe.status}
        </div>

    </div>

    <div class="metrics-grid">

        <div
            class="metric-card metric-hover"
            data-type="gap"
            data-history='${JSON.stringify(gapHistory)}'
        >

            <div class="metric-label">
                Posting Gap
            </div>

            <div class="metric-value ${metricClass("gap", cafe.avg_gap_days)}">
                ${cafe.avg_gap_days} D
            </div>

        </div>

        <div
            class="metric-card metric-hover"
            data-type="engagement"
            data-history='${JSON.stringify(engagementHistory)}'
        >

            <div class="metric-label">
                Engagement
            </div>

            <div class="metric-value ${metricClass("engagement", cafe.avg_engagement)}">
                ${cafe.avg_engagement}%
            </div>

        </div>

        <div
            class="metric-card metric-hover"
            data-type="followers"
            data-history='${JSON.stringify(followersHistory)}'
        >

            <div class="metric-label">
                Followers Gain
            </div>

            <div class="metric-value ${metricClass("followers", cafe.weekly_followers)}">
                ${cafe.weekly_followers > 0 ? "+" : ""}
                ${cafe.weekly_followers}
            </div>

        </div>

    </div>

    <div class="card-footer">

        <div class="social-actions">

            <button
                class="social-btn facebook"
                data-url="${cafe.facebook_url}"
            >
                f
            </button>

            <button
                class="social-btn instagram"
                data-url="${cafe.instagram_url}"
            >
                ◎
            </button>

            <button
                class="social-btn maps"
                data-url="${cafe.map_url}"
            >
                ⌖
            </button>

            <button
                class="social-btn message"
                data-url="${cafe.messenger_url}"
            >
                ✉
            </button>

        </div>

        <div class="segregation-actions">

            ${
                currentView !== "pending"
                ?
                `
                <button
                    class="segregation-btn pending"
                >
                    Move to Pending
                </button>
                `
                :
                `
                <button
                    class="segregation-btn pending"
                >
                    Restore
                </button>
                `
            }

            ${
                currentView !== "rejected"
                ?
                `
                <button
                    class="segregation-btn reject"
                >
                    Reject
                </button>
                `
                :
                `
                <button
                    class="segregation-btn reject"
                >
                    Reconsider
                </button>
                `
            }

        </div>

    </div>

    `

    cafeList.appendChild(card)

    setupCardEvents(card, cafe)
}

// =========================================================
// CARD EVENTS
// =========================================================

function setupCardEvents(card, cafe){

    // CHECKBOXES

    const checkbox =
        card.querySelector(".checkbox")

    checkbox.addEventListener("change", e => {

        if(e.target.checked){

            if(!selectedIds.includes(cafe.id)){

                selectedIds.push(cafe.id)
            }

        }else{

            selectedIds =
                selectedIds.filter(
                    x => x !== cafe.id
                )
        }
    })

    // SOCIAL BUTTONS

    const socialButtons =
        card.querySelectorAll(".social-btn")

    socialButtons.forEach(btn => {

        btn.addEventListener("click", () => {

            mobileFrame.src =
                btn.dataset.url
        })
    })

    // STATUS BUTTONS

    const segregationButtons =
        card.querySelectorAll(".segregation-btn")

    segregationButtons.forEach(btn => {

        btn.addEventListener("click", () => {

            let target = ""

            if(
                btn.classList.contains("pending")
            ){

                if(currentView === "pending"){

                    target =
                        `?restore=${cafe.id}`

                }else{

                    target =
                        `?move_to=${cafe.id}`
                }
            }

            if(
                btn.classList.contains("reject")
            ){

                if(currentView === "rejected"){

                    target =
                        `?restore=${cafe.id}`

                }else{

                    target =
                        `?reject=${cafe.id}`
                }
            }

showToast(
    "Updating lead..."
)

setTimeout(() => {

    window.location.href = target

}, 250)
        })
    })

    // HOVER CHARTS

    const metrics =
        card.querySelectorAll(".metric-hover")

    metrics.forEach(metric => {

        metric.addEventListener(
            "mouseenter",
            e => {

                const history =
                    JSON.parse(
                        metric.dataset.history
                    )

                const type =
                    metric.dataset.type

                showGraphPopup(
                    e,
                    type,
                    history
                )
            }
        )

        metric.addEventListener(
            "mouseleave",
            () => {

                hideGraphPopup()
            }
        )
    })
}

// =========================================================
// CHART POPUP
// =========================================================

function showGraphPopup(
    event,
    type,
    history
){

    graphPopup.style.display = "block"

    graphPopup.style.left =
        `${event.pageX + 20}px`

    graphPopup.style.top =
        `${event.pageY - 40}px`

    let title = ""

    if(type === "gap")
        title = "Posting Gap Trend"

    if(type === "engagement")
        title = "Engagement Trend"

    if(type === "followers")
        title = "Followers Trend"

    popupTitle.innerText = title

    if(currentChart){

        currentChart.destroy()
    }

    currentChart = new Chart(
        graphCanvas,
        {
            type:"line",

            data:{

                labels:[
                    "1","2","3","4","5"
                ],

                datasets:[{

                    data:history,

                    borderColor:"#8b5cf6",

                    backgroundColor:
                        "rgba(139,92,246,0.18)",

                    fill:true,

                    tension:0.4
                }]
            },

            options:{

                responsive:true,

                plugins:{
                    legend:{
                        display:false
                    }
                },

                scales:{

                    x:{
                        ticks:{
                            color:"#9ca3af"
                        },

                        grid:{
                            color:"rgba(255,255,255,0.05)"
                        }
                    },

                    y:{
                        ticks:{
                            color:"#9ca3af"
                        },

                        grid:{
                            color:"rgba(255,255,255,0.05)"
                        }
                    }
                }
            }
        }
    )
}

function hideGraphPopup(){

    graphPopup.style.display = "none"
}

// =========================================================
// VIEW SWITCHING
// =========================================================

document
.getElementById("main-list-btn")
.addEventListener("click", () => {

    currentView = "main"

    updateView()
})

document
.getElementById("pending-list-btn")
.addEventListener("click", () => {

    currentView = "pending"

    updateView()
})

document
.getElementById("rejected-list-btn")
.addEventListener("click", () => {

    currentView = "rejected"

    updateView()
})

// =========================================================
// UPDATE VIEW
// =========================================================

function updateView(){

    document
    .querySelectorAll(".sidebar-btn")
    .forEach(btn => {

        btn.classList.remove("active")
    })

    if(currentView === "main"){

        document
        .getElementById("main-list-btn")
        .classList.add("active")

        document
        .getElementById("view-title")
        .innerText = "Main Leads"
    }

    if(currentView === "pending"){

        document
        .getElementById("pending-list-btn")
        .classList.add("active")

        document
        .getElementById("view-title")
        .innerText = "Pending Leads"
    }

    if(currentView === "rejected"){

        document
        .getElementById("rejected-list-btn")
        .classList.add("active")

        document
        .getElementById("view-title")
        .innerText = "Rejected Leads"
    }

    renderCurrentView()
}

// =========================================================
// SEARCH
// =========================================================

searchInput.addEventListener(
    "input",
    renderCurrentView
)

// =========================================================
// DELETE
// =========================================================

// ======================================================
// DELETE SELECTED
// ======================================================

document
.getElementById("delete-selected-btn")
.addEventListener("click", () => {

    if (!selectedIds || selectedIds.length === 0){

        showToast(
            "No cafes selected."
        )

        return
    }

    const confirmed = confirm(
        `Delete ${selectedIds.length} cafe(s)?`
    )

    if(!confirmed){
        return
    }

    showToast(
        "Deleting..."
    )

    const deleteNext = (index)=>{

        if(index >= selectedIds.length){

            window.location.reload()

            return
        }

        const cafeId =
            selectedIds[index]

        window.location.href =
            `?delete=${cafeId}`

    }

    deleteNext(0)

})

// =========================================================
// REFRESH
// =========================================================

function refreshData(){

    showToast(
        "Refreshing metrics..."
    )

    loadCafeData()
}

document
.getElementById("refresh-btn")
.addEventListener("click", refreshData)

document
.getElementById("refresh-top-btn")
.addEventListener("click", refreshData)

// =========================================================
// EXPORT
// =========================================================

document
.getElementById("export-btn")
.addEventListener("click", () => {

    showToast(
        "CSV export coming soon."
    )
})

// =========================================================
// BATCH OUTREACH
// =========================================================

document
.getElementById("batch-outreach-btn")
.addEventListener("click", () => {

    if(selectedIds.length === 0){

        showToast(
            "Select cafes first."
        )

        return
    }

    showToast(
        "Opening outreach..."
    )

    const selectedCafes =
        cafes.filter(c =>
            selectedIds.includes(c.id)
        )

    selectedCafes.forEach(cafe => {

        window.open(
            cafe.messenger_url,
            "_blank"
        )
    })
})

// =========================================================
// INITIALIZE
// =========================================================

loadCafeData()

})
