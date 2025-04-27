import sqlite3
from datetime import datetime

conn = sqlite3.connect("black_hacker_bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    progress TEXT DEFAULT '',
    rank TEXT DEFAULT 'Новичок',
    bio TEXT DEFAULT '',
    psych_profile TEXT DEFAULT ''
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    timestamp TEXT
)
""")
conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def insert_user(user_id, username):
    cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

def update_user_analysis(user_id: int):
    cursor.execute("SELECT username, level, xp FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        username, level, xp = user
        new_bio = f"Псевдоним: {username}. Присоединился к Ордену. Уровень: {level}. Опыт: {xp}."
        psych = "Активность высокая. Потенциал для роста в хакерстве."
        cursor.execute("UPDATE users SET bio = ?, psych_profile = ? WHERE user_id = ?", (new_bio, psych, user_id))
        conn.commit()

def log_message(user_id, message):
    cursor.execute("INSERT INTO messages_log (user_id, message, timestamp) VALUES (?, ?, ?)",
                   (user_id, message, datetime.now().isoformat()))
    conn.commit()

def get_user_stats(user_id):
    cursor.execute("SELECT username, level, xp FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def get_user_profile(user_id):
    cursor.execute("SELECT username, level, progress, rank, bio, psych_profile FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def update_user_progress(user_id, progress):
    cursor.execute("UPDATE users SET progress = ? WHERE user_id = ?", (progress, user_id))
    conn.commit()

def update_user_level(user_id, xp, level, rank):
    cursor.execute("UPDATE users SET xp = ?, level = ?, rank = ? WHERE user_id = ?", (xp, level, rank, user_id))
    conn.commit()

def get_user_progress(user_id):
    cursor.execute("SELECT progress FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else ""

def get_rank(level: int) -> str:
    if level < 3:
        return "Новичок"
    elif level < 6:
        return "Ученик"
    elif level < 10:
        return "Ассасин"
    elif level < 15:
        return "Элитный хакер"
    else:
        return "Легенда BLACKCORE"


