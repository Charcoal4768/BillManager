const addStoreDiv = document.querySelector(".addStore");
const loadingIndicator = document.getElementById('loading');

let currentPage = 1;
let isLoading = false;
let hasMore = true;

function displayStore(storeData){
    // Create the anchor tag to wrap the store content
    const storeLink = document.createElement("a");
    storeLink.href = `/stores/${storeData.id}`;
    storeLink.classList.add("store-link");
    
    // Create the store content div
    const storeDiv = document.createElement("div");
    storeDiv.classList.add("store");
    
    // Create the title div
    const titleDiv = document.createElement("div");
    titleDiv.classList.add("title");
    titleDiv.innerHTML = `<h3>${storeData.name}</h3>`;
    
    // Create the body div and its child elements
    const bodyDiv = document.createElement("div");
    bodyDiv.classList.add("body");
    
    // Create and append the individual text elements for the body
    const ownerParagraph = document.createElement("p");
    ownerParagraph.innerHTML = `<strong>Owner:</strong> ${storeData.owner}`;
    
    const productsParagraph = document.createElement("p");
    productsParagraph.innerHTML = `<strong>Total Products:</strong> ${storeData.total_products}`;
    
    const addressParagraph = document.createElement("p");
    addressParagraph.innerHTML = `<strong>Address:</strong> ${storeData.addr.slice(0, 25) + '...'}`;
    
    bodyDiv.appendChild(ownerParagraph);
    bodyDiv.appendChild(productsParagraph);
    bodyDiv.appendChild(addressParagraph);

    storeDiv.appendChild(titleDiv);
    storeDiv.appendChild(bodyDiv);
    
    // Append the store content to the anchor tag
    storeLink.appendChild(storeDiv);
    
    // Add the new anchor tag before the "Add Store" button
    storesGrid.insertBefore(storeLink, addStoreDiv.parentNode);

    if (window.observeAnimateElements) {
        window.observeAnimateElements();
    }
}

const fetchStores = async (page) => {
    if (isLoading || !hasMore) return;
    isLoading = true;
    loadingIndicator.style.display = 'block';

    try {
        const response = await fetch(`/api/stores_paginated?page=${page}`);
        const data = await response.json();
        
        if (data.status === "ok") {
            data.stores.forEach(store => {
                displayStore(store);
            });
            currentPage++;
            hasMore = data.has_next;
        } else {
            console.error("Error fetching stores:", data.message);
            createMessage("danger", "Failed to load stores: " + data.message);
        }

    } catch (error) {
        console.error('Error fetching stores:', error);
        createMessage("danger", "Failed to connect to the server.");
    } finally {
        isLoading = false;
        loadingIndicator.style.display = 'none';
    }
};

// Throttle the scroll event listener
let throttleTimeout = null;
window.addEventListener('scroll', () => {
    if (throttleTimeout) return;
    throttleTimeout = setTimeout(() => {
        throttleTimeout = null;
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 800) {
            console.log('Fetching more stores...');
            fetchStores(currentPage);
        }
    }, 200); // Throttle interval
});

// Initial load of stores
document.addEventListener('DOMContentLoaded', () => {
    fetchStores(currentPage);
});