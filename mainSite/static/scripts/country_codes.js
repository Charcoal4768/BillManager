/**
 * Fetches country calling codes from a public API and populates a select dropdown.
 * API Source: REST Countries (https://restcountries.com)
 */
document.addEventListener('DOMContentLoaded', () => {
    const countryCodeSelect = document.getElementById('country-code');

    if (countryCodeSelect) {
        const apiUrl = 'https://restcountries.com/v3.1/all?fields=name,idd';

        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.statusText}`);
                }
                return response.json();
            })
            .then(countries => {
                // ✅ FIX: Create a simple list to hold all countries, allowing duplicates for shared codes.
                const countryList = [];

                countries.forEach(country => {
                    if (country.idd && country.idd.root) {
                        const dialCode = (country.idd.suffixes && country.idd.suffixes.length === 1)
                            ? `${country.idd.root}${country.idd.suffixes[0]}`
                            : country.idd.root;
                        
                        if (dialCode && dialCode !== "N/A") {
                           // Add an object with the name and code to our list
                           countryList.push({ name: country.name.common, code: dialCode });
                        }
                    }
                });
                
                // Sort the final list alphabetically by country name
                countryList.sort((a, b) => a.name.localeCompare(b.name));

                const placeholder = countryCodeSelect.querySelector('option[disabled]');
                countryCodeSelect.innerHTML = ''; 
                if (placeholder) {
                    countryCodeSelect.appendChild(placeholder);
                }

                // Loop through the complete, sorted list and create an <option> for each country
                countryList.forEach(country => {
                    const option = document.createElement('option');
                    option.value = country.code;
                    option.textContent = `${country.name} (${country.code})`;
                    countryCodeSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Failed to fetch country codes:', error);
            });
    }
});