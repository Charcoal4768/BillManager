document.addEventListener("DOMContentLoaded", () => {
    const inputs = document.querySelectorAll(".material-input input, .material-input select");

    // Function to update the filled class
    const updateFilledState = (element) => {
        const materialInputDiv = element.closest(".material-input");
        const isFilled = element.value.trim() !== "";
        if (isFilled) {
            materialInputDiv.classList.add("filled");
        } else {
            materialInputDiv.classList.remove("filled");
        }
    };

    // Loop through all inputs and selectors
    inputs.forEach(element => {
        // Listen for change/input events to update the filled state
        element.addEventListener("input", () => updateFilledState(element));
        element.addEventListener("change", () => updateFilledState(element));

        // Handle the case where the browser auto-fills on page load
        // A slight delay ensures the browser's auto-fill has completed
        setTimeout(() => updateFilledState(element), 100);
    });
});