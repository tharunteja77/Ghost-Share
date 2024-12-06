document.addEventListener("DOMContentLoaded", function() {
    var back2dash = document.getElementById("Dash");
     back2dash.onclick = function() {  
            window.location.href = "/dash";
    };
    var login2signup = document.getElementById("signup_redirect");
     login2signup.onclick = function() {  
            window.location.href = "/signup";

    };
});

async function Login(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const response = await fetch('/login', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    if (!result.exists) {     
        Swal.fire({
            icon: 'success',
            title: 'Login successful!',
            showConfirmButton: false,
            timer: 1500,
            willClose: () => {
                window.location.href = "/home";
            }
        });
    } else {
        document.getElementById('alert').style.display = 'block';
    }
}




