document.addEventListener("DOMContentLoaded", () => {
    // Select all elements with the class '.material-input'
    const materialInputDivs = document.querySelectorAll(".material-input");

    // Loop through each material-input div
    materialInputDivs.forEach(materialInputDiv => {
        const inputElement = materialInputDiv.querySelector("input");

        if (inputElement) { // Ensure an input element exists within the div
            // Function to update the filled class
            const updateFilledState = () => {
                const isFilled = inputElement.value.trim() !== "";
                if (isFilled) {
                    materialInputDiv.classList.add("filled");
                } else {
                    materialInputDiv.classList.remove("filled");
                }
            };

            // Listen for input events to update the filled state
            inputElement.addEventListener("input", updateFilledState);

            // Handle the case where the browser auto-fills on page load
            // A slight delay ensures the browser's auto-fill has completed
            setTimeout(updateFilledState, 100);
        }
    });
});