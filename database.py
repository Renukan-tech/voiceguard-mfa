import sqlite3

# Connect to database
conn = sqlite3.connect("authentication.db")

# Create cursor
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    voice_file TEXT NOT NULL
)
""")

# Create logs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    login_time TEXT,
    status TEXT
)
""")

# Save changes
conn.commit()

# Close connection
conn.close()

print("✅ Database and tables created successfully")