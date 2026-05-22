// =========================================================
// GLOBAL STATE
// =========================================================

let cafes = []

let selectedIds = []

let currentView = "main"

let currentChart = null

// =========================================================
// ELEMENTS
// =========================================================

const cafeList = document.getElementById("cafe-list")

const mobileFrame = document.getElementById("mobile-frame")

const graphPopup = document.getElementById("graph-popup")

const graphCanvas = document.getElementById("graph-canvas")

const popupTitle = document.getElementById("popup-title")

const searchInput = document.getElementById("search-input")

// =========================================================
// TOAST
// =========================================================

function showToast(message){

    const toast = document.createElement("div")

    toast.className = "toast"

    toast.innerText = message

    document.body.appendChild(toast)

    toast.style.display = "block"

    setTimeout(() => {

        toast.style.opacity = "0"

        setTimeout(() => {

            toast.remove()

        }, 300)

    }, 2500)
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
// FETCH CAFES
// =========================================================

async function fetchCafes(){

    renderLoader()

    try{

        const response = await fetch(
            `${API_BASE}/api/cafes`
        )

        cafes = await response.json()

        renderCurrentView()

    }catch(error){

        console.error(error)

        renderEmpty("Backend connection failed.")
    }
}

// =========================================================
// FILTER VIEW
// =========================================================

function getFilteredCafes(){

    const query = searchInput.value
        .toLowerCase()

    return cafes.filter(cafe => {

        const matchesView =
            cafe.status === currentView

        const matchesSearch =
            cafe.name
                .toLowerCase()
                .includes(query)

        return matchesView && matchesSearch
    })
}

// =========================================================
// RENDER CURRENT VIEW
// =========================================================

function renderCurrentView(){

    const filtered = getFilteredCafes()

    if(filtered.length === 0){

        renderEmpty("Try another search or refresh.")
        return
    }

    cafeList.innerHTML = ""

    filtered.forEach(cafe => {

        renderCafeCard(cafe)

    })
}

// =========================================================
// METRIC CLASS
// =========================================================

function metricClass(type, value){

    if(type === "gap"){

       
