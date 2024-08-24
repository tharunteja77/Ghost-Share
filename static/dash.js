document.addEventListener("DOMContentLoaded", function() {
    //For SIGNUP Redirect..
    var signupButton = document.getElementById("Signup");
     signupButton.onclick = function() {
        window.location.href = "/signup";
    };

    // For LOGIN Redirect..
    var loginButton = document.getElementById("Login");
     loginButton.onclick = function() {  
            window.location.href = "/login";
    };
});
