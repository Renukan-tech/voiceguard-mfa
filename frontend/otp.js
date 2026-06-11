const savedOtp = sessionStorage.getItem("otp");

if (savedOtp) {
    document.getElementById("otpDisplay").innerText = savedOtp;
}
const otpForm = document.getElementById("otpForm");

function showOtp(otp) {
    document.getElementById("otpDisplay").innerText = otp;
}

// VERIFY OTP
otpForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const otp = document.getElementById("otp").value;
    const username = sessionStorage.getItem("username");

    const res = await fetch("http://127.0.0.1:5000/verify-otp", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, otp })
    });

    const data = await res.json();

    if (data.success) {
        alert("Login Successful!");
        window.location.href = "./index.html";
    } else {
        alert(data.message || "Invalid OTP");
    }
});

// RESEND OTP
document.getElementById("resendOTP").addEventListener("click", async (e) => {
    e.preventDefault();

    const username = sessionStorage.getItem("username");

    const res = await fetch("http://127.0.0.1:5000/resend-otp", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username })
    });

    const data = await res.json();

    if (data.success) {
        alert("OTP regenerated!");
        if (data.otp) showOtp(data.otp);
    }
});