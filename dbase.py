import sqlite3

def create_table():

    conn = sqlite3.connect("list.db")

    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks(
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        status TEXT)
        """)

    conn.commit()
    conn.close()

def add_task(task_id, task_name, status):

    conn = sqlite3.connect("list.db")

    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO tasks
        VALUES (?, ?, ?)""",
        (task_id, task_name, status)
    )

    conn.commit()
    conn.close()

def get_all_tasks():

    conn = sqlite3.connect("list.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks"
    )

    tasks = cursor.fetchall()

    conn.close()
    return tasks

def delete_task(task_id):

    conn = sqlite3.connect("list.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE task_id= ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

def update_task(task_id, task_name, status):

    conn = sqlite3.connect("list.db")

    cursor = conn.cursor()

    cursor.execute(
        """UPDATE tasks
        SET task_name = ?, status = ?
        WHERE task_id= ?""",
        (task_name, status, task_id)
    )
    conn.commit()
    conn.close()

def search_task(task_id):

    conn = sqlite3.connect("list.db")

    cursor = conn.cursor()

    cursor.execute(
        """SELECT * FROM tasks
        WHERE task_id =?""",
        (task_id,)
    )
    task = cursor.fetchone()
    conn.close()
    return task
