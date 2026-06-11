from flask import Flask, request, jsonify
import sqlite3
import os
import random
import subprocess
import time

from comparison import compare_audio

app = Flask(__name__)
from flask_cors import CORS

CORS(app)

VOICE_FOLDER = "voices"
os.makedirs(VOICE_FOLDER, exist_ok=True)

otp_store = {}
login_attempts = {}

FFMPEG = r"C:\Users\Dell\Downloads\ffmpeg-8.1.1-essentials_build\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe"


# ---------------- CONVERT WEBM -> WAV ----------------
def convert_to_wav(input_file, output_file):

    result = subprocess.run(
        [
            FFMPEG,
            "-y",
            "-i",
            input_file,
            output_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("FFMPEG RETURN CODE:", result.returncode)

    if result.returncode != 0:
        print("FFMPEG FAILED")
        return None

    return output_file


# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():

    if "voice" not in request.files:
        return jsonify({
            "success": False,
            "message": "No voice file received"
        })

    username = request.form["username"].strip().lower()
    password = request.form["password"]
    voice = request.files["voice"]

    conn = sqlite3.connect("authentication.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "User exists"
        })

    webm_path = os.path.join(VOICE_FOLDER, f"{username}_reg.webm")
    wav_path = os.path.join(VOICE_FOLDER, f"{username}_reg.wav")

    voice.save(webm_path)

    convert_to_wav(webm_path, wav_path)

    cursor.execute(
        "INSERT INTO users(username,password,voice_file) VALUES(?,?,?)",
        (username, password, f"{username}_reg.wav")
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Registered"
    })


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():

    if "voice" not in request.files:
        return jsonify({
            "success": False,
            "message": "No voice file received"
        })

    username = request.form["username"].strip().lower()
    password = request.form["password"]
    voice = request.files["voice"]

    conn = sqlite3.connect("authentication.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password, voice_file FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({
    "success": False,
    "otp_required": False,
    "message": "User not found",
    "score": None
})

    if password != user[0]:
        return jsonify({
    "success": False,
    "otp_required": False,
    "message": "Wrong password",
    "score": None
})

    login_webm = os.path.join(VOICE_FOLDER, f"login_{username}.webm")
    login_wav = os.path.join(VOICE_FOLDER, f"login_{username}.wav")

    voice.save(login_webm)

    wav_result = convert_to_wav(login_webm, login_wav)

    if wav_result is None:
        return jsonify({
    "success": False,
    "otp_required": False,
    "message": "Audio conversion failed",
    "score": None
})

    reg_voice = os.path.join(VOICE_FOLDER, user[1])

    if not os.path.exists(reg_voice):
        return jsonify({
    "success": False,
    "otp_required": False,
    "message": "Registered voice missing",
    "score": None
})

    print("Comparing voices...")

    start = time.time()
    score = compare_audio(reg_voice, login_wav)
    print("Voice Score =", score)
    print("COMPARE TIME:", time.time() - start)

    # ---------------- SUCCESS ----------------
    if score < 3.5:
        print("LOGIN RESULT: SUCCESS ✔")
    else:
        print("LOGIN RESULT: FAIL ❌")

        login_attempts[username] = 0

        return jsonify({
    "success": True,
    "otp_required": False,
    "message": "Voice matched. Login successful.",
    "score": score
})

    # ---------------- FAIL ----------------
    login_attempts[username] = login_attempts.get(username, 0) + 1

    print(f"{username} failed attempt {login_attempts[username]}/3")

    # ---------------- OTP TRIGGER ----------------
    if login_attempts[username] >= 3:

        otp = str(random.randint(100000, 999999))
        otp_store[username] = otp
        login_attempts[username] = 0

        print("OTP GENERATED:", otp)

        return jsonify({
    "success": False,
    "otp_required": True,
    "otp": otp,
    "message": "3 failed attempts. OTP required.",
    "score": score
})

    return jsonify({
    "success": False,
    "otp_required": False,
    "message": f"Voice mismatch ({login_attempts[username]}/3)",
    "score": score
})


# ---------------- VERIFY OTP ----------------
@app.route("/verify-otp", methods=["POST"])
def verify():

    data = request.json
    username = data.get("username", "").lower()
    otp = data.get("otp")

    if otp_store.get(username) == otp:

        otp_store.pop(username, None)

        return jsonify({
    "success": True,
    "otp_required": False,
    "message": "Login successful",
    "score": None
})
    return jsonify({
        "success": False,
        "message": "Invalid OTP",
        "score": None
    })


# ---------------- RESEND OTP ----------------
@app.route("/resend-otp", methods=["POST"])
def resend():

    data = request.json
    username = data.get("username", "").lower()

    otp = str(random.randint(100000, 999999))
    otp_store[username] = otp

    print("OTP RESENT:", otp)

    return jsonify({
    "success": True,
    "otp_required": True,
    "otp": otp,
    "message": "OTP resent"
})


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)