const messageContainer = document.querySelector(".flashContainer .messageList");

function createMessage(type, message) {
    let messageElement = document.createElement("div");
    messageElement.classList.add("messageContainer");
    messageElement.classList.add(type);
    let messageText = document.createElement("li");
    messageText.innerText = message;
    messageElement.appendChild(messageText);
    
    // Create the close button
    const closeButton = document.createElement("span");
    closeButton.innerText = "×";
    closeButton.classList.add("close-btn");
    closeButton.onclick = function() {
        messageElement.remove();
    };
    messageElement.appendChild(closeButton);
    messageContainer.appendChild(messageElement);

    setTimeout(() => {
        messageElement.remove();
    }, 6000);
}

function checkGSTIN(g){
    //Make sure g is 15 chars long
    let regTest = /\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}/.test(g)
     if(regTest){
        let a=65,b=55,c=36;
        return Array['from'](g).reduce((i,j,k,g)=>{ 
           p=(p=(j.charCodeAt(0)<a?parseInt(j):j.charCodeAt(0)-b)*(k%2+1))>c?1+(p-c):p;
           return k<14?i+p:j==((c=(c-(i%c)))<10?c:String.fromCharCode(c+b));
        },0); 
    }
    return regTest
}