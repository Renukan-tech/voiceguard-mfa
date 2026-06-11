document.addEventListener("DOMContentLoaded", () => {

    const registerForm = document.getElementById("registerForm");
    if (!registerForm) return;

    const API = "http://127.0.0.1:5000";

    const regUsername = document.getElementById("username");
    const regPassword = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");

    const startRecord = document.getElementById("startRecord");
    const stopRecord = document.getElementById("stopRecord");
    const recordStatus = document.getElementById("recordStatus");
    const statusMessage = document.getElementById("statusMessage");

    let mediaRecorder;
    let audioChunks = [];
    let audioBlob = null;

    // ---------- RECORD ----------
    startRecord.addEventListener("click", async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);

        mediaRecorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            recordStatus.textContent = "Recorded ✔";
            stream.getTracks().forEach(t => t.stop());
        };

        mediaRecorder.start();
        startRecord.disabled = true;
        stopRecord.disabled = false;
        recordStatus.textContent = "Recording...";
    });

    // ---------- STOP ----------
    stopRecord.addEventListener("click", () => {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
        startRecord.disabled = false;
        stopRecord.disabled = true;
    });

    // ---------- SUBMIT ----------
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        recordStatus.textContent = "Recording...";

        statusMessage.style.color = "black";
        statusMessage.textContent = "Registering...";

        if (regPassword.value !== confirmPassword.value) {
            statusMessage.style.color = "red";
            statusMessage.textContent = "Passwords do not match";
            return;
        }

        if (!audioBlob) {
            statusMessage.style.color = "red";
            statusMessage.textContent = "Record voice first";
            return;
        }

        const formData = new FormData();
        formData.append("username", regUsername.value);
        formData.append("password", regPassword.value);
        formData.append("voice", audioBlob, "voice.webm");

        try {
            const res = await fetch(`${API}/register`, {
    method: "POST",
    body: formData
});

const data = await res.json();

console.log("REGISTER RESPONSE:", data); // 👈 HERE



            if (data.success === true) {
                statusMessage.style.color = "green";
                statusMessage.textContent = "REGISTERED ✔ Redirecting...";

                setTimeout(() => {
                    window.location.href = "login.html";
                }, 4000);

            } else {
                statusMessage.style.color = "red";
                statusMessage.textContent = "ERROR: " + (data.message || "Something went wrong");
            }

        } catch (err) {
            console.error(err);
            statusMessage.style.color = "red";
            statusMessage.textContent = "Server error: " + err.message;
        }
    });

});