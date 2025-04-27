import sqlite3
from database import get_rank

conn = sqlite3.connect("black_hacker_bot.db")
cursor = conn.cursor()

def add_xp(user_id: int, xp_amount: int):
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        current_xp, current_level = result
        new_xp = current_xp + xp_amount
        level_up = False
        if new_xp >= current_level * 100:
            current_level += 1
            new_xp = 0
            level_up = True
        new_rank = get_rank(current_level)
        cursor.execute("UPDATE users SET xp = ?, level = ?, rank = ? WHERE user_id = ?", (new_xp, current_level, new_rank, user_id))
        conn.commit()
        return level_up
    return False

def is_task_completed(user_id: int, task_name: str) -> bool:
    cursor.execute("SELECT progress FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        progress = result[0] or ""
        completed_tasks = progress.split(",") if progress else []
        return task_name in completed_tasks
    return False

def mark_task_completed(user_id: int, task_name: str):
    cursor.execute("SELECT progress FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        progress = result[0] or ""
        completed_tasks = progress.split(",") if progress else []
        if task_name not in completed_tasks:
            completed_tasks.append(task_name)
            new_progress = ",".join(completed_tasks)
            cursor.execute("UPDATE users SET progress = ? WHERE user_id = ?", (new_progress, user_id))
            conn.commit()
