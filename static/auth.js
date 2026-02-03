function togglePassword(id, icon) {
    const input = document.getElementById(id);
    if (input.type === "password") {
        input.type = "text";
        icon.innerText = "🙈";
    } else {
        input.type = "password";
        icon.innerText = "👁️";
    }
}

function validateLogin() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const error = document.getElementById("error");

    if (username === "" || password === "") {
        error.innerText = "All fields are required";
        return false;
    }

    if (password.length < 6) {
        error.innerText = "Password must be at least 6 characters";
        return false;
    }

    error.innerText = "";
    return true;
}

function validateSignup() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const error = document.getElementById("error");

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
        error.innerText = "Enter a valid email address";
        return false;
    }

    if (password.length < 6) {
        error.innerText = "Password must be at least 6 characters";
        return false;
    }

    error.innerText = "";
    return true;
}
