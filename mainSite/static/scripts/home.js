document.addEventListener("DOMContentLoaded", () => {
    addButton = window.document.querySelector(".add");
    closeButton = window.document.querySelector(".back");
    mainPage = window.document.querySelector(".pageLander");
    storeForm = window.document.querySelector(".standardLander");

    addButton.addEventListener("click", ()=>{
        storeForm.style.display = "flex";
        mainPage.style.display = "none";
    });
    closeButton.addEventListener("click", ()=>{
        storeForm.style.display = "none";
        mainPage.style.display = "flex";
    });
})