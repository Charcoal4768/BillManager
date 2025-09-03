import { fetch_token } from "./request_token";
function createMessage(type,message){
    return "not implimented"
}

function validateFields(){
    if (!OwnerName || !StoreName || !PhoneNum || !AddressLine1 || !AddressLine2 || !GSTNo) {
        // Since you are using a form, you may also need to get the store name and GST number.
        // I have added a hypothetical `[name="store-name"]` and `[name="gst-no"]`.
        // You should check the actual `name` attributes of your input fields.
        createMessage(type="error", message="Please enter all the Requested Information");
        return "error";
    }
}
const form = document.querySelector('form');
form.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevents the form from submitting normally

    const OwnerName = form.querySelector('[name="name"]').value;
    const StoreName = form.querySelector('[name="store-name"]').value;
    const PhoneNum = form.querySelector('[name="phone"]').value;
    const AddressLine1 = form.querySelector('[name="address-line1"]').value;
    const AddressLine2 = form.querySelector('[name="address-line2"]').value;
    const GSTNo = form.querySelector('[name="gst-no"]').value;

    validateFields();
    // Rest of your form submission logic
});