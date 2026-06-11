import sqlite3
import datetime
import os
import random

from record import record_voice
from comparison import compare_audio

def login_user():

    username = input("Enter username: ")
    password = input("Enter password: ")

    conn = sqlite3.connect("authentication.db")
    cursor = conn.cursor()

    # Get user data
    cursor.execute(
        "SELECT password, voice_file FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        print("❌ User not found")
        conn.close()
        return

    stored_password = user[0]
    voice_file = user[1]

    if password != stored_password:
        print("❌ Incorrect password")

        cursor.execute(
            "INSERT INTO logs(username, login_time, status) VALUES(?,?,?)",
            (
                username,
                str(datetime.datetime.now()),
                "Failed"
            )
        )

        conn.commit()
        conn.close()
        return

    print("🔐 Password verified")

    file1 = os.path.join("voices", voice_file)

    attempts = 0
    success = False

    while attempts < 3:

        print(f"\n🎤 Voice Attempt {attempts + 1}/3")

        temp_file = "temp.wav"
        record_voice(temp_file)

        file2 = os.path.join("voices", temp_file)

        score = compare_audio(file1, file2)

        print(f"Distance Score: {score:.2f}")

        if score < 10:
            print("✅ Voice Match - Access Granted")
            success = True
            break

        else:
            print("❌ Voice not matched")
            attempts += 1

    # OTP fallback
    if not success:

        print("\n⚠️ Voice verification failed 3 times")
        print("🔢 OTP verification required")

        otp = random.randint(100000, 999999)

        print(f"Your OTP is: {otp}")

        user_otp = input("Enter OTP: ")

        if str(otp) == user_otp:
            print("✅ OTP Verified - Access Granted")
            success = True
        else:
            print("❌ OTP Incorrect - Access Denied")

    # Save log
    cursor.execute(
        "INSERT INTO logs(username, login_time, status) VALUES(?,?,?)",
        (
            username,
            str(datetime.datetime.now()),
            "Success" if success else "Failed"
        )
    )

    conn.commit()
    conn.close()