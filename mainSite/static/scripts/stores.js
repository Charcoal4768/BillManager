function fetch_token(type) {
    if (type == "admin") {
        fetch('/api/request_admin_token', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(tokenData => {
            if (tokenData.publish_token) {
                return tokenData.publish_token;
            } else{
                return "error";
            }
        });
    } else {
        fetch('/api/request_token', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(tokenData => {
            if (tokenData.publish_token) {
                return tokenData.publish_token;
            } else{
                return "error";
            }
        });
    }
}

const storesGrid = document.querySelector(".storesGrid");

function displayNewStore(storeData){
    if (storeData){
        let newStore = document.createElement("div");
        let storeTitle = document.createElement("div");
        let storeBody = document.createElement("div");
        newStore.classList.add("store")
        storeTitle.classList.add("title");
        storeBody.classList.add("body");
        storeBody.innerText = "Total Products" + storeData.total_products;
        storeTitle.innerText = storeData.name;
        return true
    } else {
        return false
    }
}

function validateFields(OwnerName, StoreName, PhoneNum, AddressLine1, AddressLine2, GSTNo) {
    // Check if any field is empty
    if (!OwnerName || !StoreName || !PhoneNum || !AddressLine1 || !GSTNo) {
        createMessage("danger", "Please enter all required information.");
        return false;
    }
    if (OwnerName.length < 2 || OwnerName.length > 50) {
        createMessage("danger", "Owner's name must be between 2 and 50 characters long.");
        return false;
    }
    if (StoreName.length < 2 || StoreName.length > 100) {
        createMessage("danger", "Store name must be between 2 and 100 characters long.");
        return false;
    }
    if (PhoneNum.length !== 10) {
        createMessage("danger", "Phone number must be exactly 10 digits.");
        return false;
    }
    if (AddressLine1.length < 5 || AddressLine1.length > 150) {
        createMessage("danger", "Address Line 1 must be between 5 and 150 characters long.");
        return false;
    }
    if (AddressLine2 && (AddressLine2.length < 5 || AddressLine2.length > 150)) {
        createMessage("warning", "Address Line 2 is unusually long. Please check the information.");
    }
    
    if (GSTNo.length !== 15) {
        createMessage("danger", "GST number must be exactly 15 characters long.");
        return false;
    }
    if (!checkGSTIN(GSTNo)){
        createMessage("warning", `GST number ${GSTNo} is invalid.`);
        return false;
    }
    return true;
}

const form = document.querySelector('form');
form.addEventListener("submit", (event) => {
    event.preventDefault();
    event.stopImmediatePropagation();
})
const submitButton = document.querySelector('#new-store')
submitButton.addEventListener('click', (event) => {
    event.preventDefault();

    const OwnerName = form.querySelector('[name="name"]').value;
    const StoreName = form.querySelector('[name="store-name"]').value;
    const TelCode = form.querySelector('[name="tel-code"]').value;
    const PhoneNum = form.querySelector('[name="phone"]').value;
    const AddressLine1 = form.querySelector('[name="address-line1"]').value;
    const AddressLine2 = form.querySelector('[name="address-line2"]').value;
    const GSTNo = form.querySelector('[name="gstno"]').value;

    if (validateFields(OwnerName, StoreName, PhoneNum, AddressLine1, AddressLine2, GSTNo)) {
        // Fetch the token and then proceed with the form submission
        fetch('/api/request_token', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(tokenData => {
            if (tokenData.publish_token) {
                const token = tokenData.publish_token;
                
                const formData = new FormData();
                formData.append("storeName", StoreName);
                formData.append("ownerName", OwnerName);
                formData.append("phoneNum", PhoneNum);
                formData.append("address1", AddressLine1);
                formData.append("address2", AddressLine2);
                formData.append("gstNo", GSTNo);
                formData.append("telCode", TelCode);
                formData.append("publish_token", token); // Add the token to the form data

                fetch('/api/new_store', {
                    method: 'POST',
                    credentials: "include",
                    body: formData
                })
                .then(response => response.json())
                .then(responseDict => {
                    if (responseDict.status === "ok") {
                        if (displayNewStore(responseDict.store)) {
                            createMessage("ok", "Store Added Successfully!");
                        }
                    } else {
                        createMessage("danger", responseDict.message);
                        console.error(responseDict.message);
                    }
                })
                .catch(error => {
                    createMessage("danger", "An error occurred while adding the store.");
                    console.error("Fetch error:", error);
                });
            } else {
                createMessage("danger", "Error fetching API Token.");
                console.error("Error fetching token.");
            }
        })
        .catch(error => {
            createMessage("danger", "An error occurred while requesting the token.");
            console.error("Token fetch error:", error);
        });
    }
});