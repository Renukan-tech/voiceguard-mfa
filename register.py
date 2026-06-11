import sqlite3
from record import record_voice

def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")

    conn = sqlite3.connect("authentication.db")
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    if cursor.fetchone():
        print("❌ User already exists")
        conn.close()
        return

    # Record voice
    voice_file = f"{username}.wav"
    record_voice(voice_file)

    # Save user
    cursor.execute(
        "INSERT INTO users(username,password,voice_file) VALUES(?,?,?)",
        (username, password, voice_file)
    )

    conn.commit()
    conn.close()

    print("✅ User registered successfully!")