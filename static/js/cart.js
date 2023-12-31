// adding an event handler to each button
var updateBtns = document.getElementsByClassName('update_cart')
for(let i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        let productId = this.dataset.product
        let action = this.dataset.action
        console.log('productId:', productId, 'action:', action)

        // note user is defined in the head section of the main.html
        console.log('user:', user)
        if(user === 'AnonymousUser'){
            updateUserOrderCookie(productId, action)
        }
        else{
            // call updateUserOrder
            updateUserOrder(productId, action)
        }
    })
}


function getCookie(name) {
    // split string and get all individual name:value pairs in the array
    let cookieArr = document.cookie.split(";");

    // Loop through the array elements
    for (let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");

        // Remove white space at the beginning of the cookie name
        // and compare it with the given string
        if (name == cookiePair[0].trim()) {
            // Decode the cookie value and return
            return decodeURIComponent(cookiePair[1]);
        }
    }
    // return null if not found
    return null;
}

function setCookie(cookieName) {
    // create cookies dynamically for the cookie name set as parameter
    let cookieValue = getCookie(cookieName);
    console.log(`get cookie ${cookieName}:`, cookieValue);

    if (cookieValue === null) {
        let newCookieValue = {};
        console.log(`New cookie '${cookieName}' created!`, newCookieValue);

        // Calculate the expiration date as one month from the current date
        const expirationDate = new Date();
        expirationDate.setMonth(expirationDate.getMonth() + 1);

        // Format the expiration date as a string
        const expires = expirationDate.toUTCString();

        // Set the cookie with the "expires", "SameSite", and "Secure" attributes
        document.cookie = `${cookieName}=` + JSON.stringify(newCookieValue) +
            `; expires=${expires}; domain=; path=/; SameSite=None; Secure`;
    } else {
        let parsedCookieValue = JSON.parse(cookieValue);
        console.log(`existing ${cookieName}:`, parsedCookieValue);
    }
}
setCookie('cart');

function updateCookie(cookieName, newValue) {
    let existingValue = getCookie(cookieName);

    // Calculate the expiration date as one month from the current date
    const expirationDate = new Date();
    expirationDate.setMonth(expirationDate.getMonth() + 1);

    // Format the expiration date as a string
    const expires = expirationDate.toUTCString();

    if (existingValue !== null) {
        let updatedValue = JSON.stringify(newValue);

        // Set the cookie with the updated value, "expires", "SameSite", and "Secure" attributes
        document.cookie = `${cookieName}=${updatedValue}; expires=${expires}; domain=; path=/; SameSite=None; Secure`;

        console.log(`Cookie ${cookieName} updated! New value:`, newValue);
    } else {
        // If the cookie doesn't exist, create a new one with the provided value
        document.cookie = `${cookieName}=${JSON.stringify(newValue)}; expires=${expires}; domain=; path=/; SameSite=None; Secure`;

        console.log(`New cookie '${cookieName}' created!`, newValue);
    }
}
// // Example usage 1:
// updateCookie('cart', valueObject);
// // Example usage 2:
// updateCookie('cart', { shoes: 'example', quantity: 2 });


function updateUserOrderCookie(productId, action){
    console.log('user not logged in ...')
    // create cookies dynamically for the cookie name set as parameter
    let cookieValue = getCookie('cart');
    let cart = JSON.parse(cookieValue);
    console.log('cart ...', cart)

    if(action == "add"){
        if(cart[productId] == undefined){
            cart[productId] = {'quantity':1}
        }
        else{
            cart[productId]['quantity'] += 1
        }
    }

    if(action == "remove"){
        cart[productId]['quantity'] -= 1
        if(cart[productId]['quantity'] <= 0){
            delete cart[productId];
            console.log(`item ${cart[productId]} deleted`)
        }
    }
    updateCookie('cart', cart);
    location.reload()
}



function updateUserOrder(productId, action){
    console.log('user is logged in, sending data')
    // using fetch api
    let url = '/update_item/'
    fetch(url, {
        method:'POST',
        headers:{
            'content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId': productId, 'action':action})
        })

        .then((response) =>{
            return response.json()
        })
        .then((data) => {
            console.log('data:',data)

            // to reload the page for now
            location.reload()
        })
    
}

