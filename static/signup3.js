async function checkUsername(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const response = await fetch('/signup', {
        method: 'POST',
        body: formData      
    });
    alert("Sign Up successful !!!, You can now log in into GHOST SHARE...");
    const result = await response.json();
    if (result.exists) {
        alert("Username already exists!");
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var back2dash = document.getElementById("Dash");
     back2dash.onclick = function() {  
            window.location.href = "/dash";
    };

    var signup2login = document.getElementById("login_redirect");
        signup2login.onclick = function(){
            window.location.href = "/login";
        };
});
