console.log("LOGIN JS LOADED");
document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm");
    if (!loginForm) return;

    const API = "http://127.0.0.1:5000";

    const loginUsername = document.getElementById("username");
    const loginPassword = document.getElementById("password");

    const startRecord = document.getElementById("startRecord");
    const stopRecord = document.getElementById("stopRecord");
    const recordStatus = document.getElementById("recordStatus");
    const statusMessage = document.getElementById("statusMessage");

    let mediaRecorder;
    let audioChunks = [];
    let audioBlob = null;
    let recordingDone = false;

    // ---------------- RECORD ----------------
    startRecord.addEventListener("click", async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);

            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                recordingDone = true;
                recordStatus.textContent = "Recorded ✔";
                stream.getTracks().forEach(t => t.stop());
            };

            mediaRecorder.start();
            startRecord.disabled = true;
            stopRecord.disabled = false;

            statusMessage.textContent = "Recording started...";
            statusMessage.style.color = "black";

        } catch (err) {
            console.error(err);
            statusMessage.textContent = "Mic permission denied ❌";
            statusMessage.style.color = "red";
        }
    });

    // ---------------- STOP ----------------
    stopRecord.addEventListener("click", () => {
        if (!mediaRecorder || mediaRecorder.state === "inactive") return;

        mediaRecorder.stop();
        startRecord.disabled = false;
        stopRecord.disabled = true;
    });

    // ---------------- LOGIN ----------------
    // ---------------- LOGIN ----------------
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    console.log("SUBMIT FIRED");

    statusMessage.style.display = "block";
    statusMessage.style.color = "black";
    statusMessage.textContent = "Logging in...";

    startRecord.disabled = true;
    stopRecord.disabled = true;

    if (!recordingDone || !audioBlob) {
        statusMessage.style.color = "red";
        statusMessage.textContent = "Please record your voice first 🎤";

        startRecord.disabled = false;
        stopRecord.disabled = false;
        return;
    }

    try {
        const formData = new FormData();
        formData.append("username", loginUsername.value);
        formData.append("password", loginPassword.value);
        formData.append("voice", audioBlob, "login.webm");

        const res = await fetch(`${API}/login`, {
            method: "POST",
            body: formData
        });

        const text = await res.text();
console.log("RAW:", text);

let data;
try {
    data = JSON.parse(text);
} catch (e) {
    statusMessage.style.color = "red";
    statusMessage.textContent = "Server response error";
    return;
}

        console.log("RESPONSE:", data);

       const success = data.success === true;

console.log("FINAL RESULT:", data);

statusMessage.style.display = "block";

if (success) {
    statusMessage.style.color = "green";
    statusMessage.innerHTML =
        `✅ <b>LOGIN SUCCESS</b><br>Score: ${data.score?.toFixed(2)}`;
} else {
    statusMessage.style.color = "red";
    statusMessage.innerHTML =
        `❌ <b>LOGIN FAILED</b><br>${data.message}<br>Score: ${data.score?.toFixed(2)}`;
}

    } catch (err) {
        console.error(err);

        statusMessage.style.color = "red";
        statusMessage.textContent = "Server error: " + err.message;
    } finally {
        // always re-enable buttons (VERY IMPORTANT for demo)
        startRecord.disabled = false;
        stopRecord.disabled = false;
    }
});
});