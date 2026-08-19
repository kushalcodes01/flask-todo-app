import sqlite3


DATABASE = "list.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks(
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'medium'
        )
        """
    )

    conn.commit()
    conn.close()


def create_users_table():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def add_user(username, email, password):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (username, email, password)
        VALUES (?, ?, ?)
        """,
        (username, email, password)
    )

    conn.commit()
    conn.close()


def search_user(username):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def add_task(user_id, task_name, status, due_date, priority):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks
        (user_id, task_name, status, due_date, priority)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            task_name,
            status,
            due_date,
            priority
        )
    )

    conn.commit()
    conn.close()


def get_all_tasks(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE user_id = ?
        ORDER BY due_date ASC
        """,
        (user_id,)
    )

    tasks = cursor.fetchall()

    conn.close()

    return tasks


def get_task(task_id, user_id=None):

    conn = get_connection()

    cursor = conn.cursor()

    if user_id is None:

        cursor.execute(
            """
            SELECT *
            FROM tasks
            WHERE task_id = ?
            """,
            (task_id,)
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM tasks
            WHERE task_id = ?
            AND user_id = ?
            """,
            (task_id, user_id)
        )

    task = cursor.fetchone()

    conn.close()

    return task


def search_task(task_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE task_id = ?
        """,
        (task_id,)
    )

    task = cursor.fetchone()

    conn.close()

    return task


def update_task(
    task_id,
    user_id,
    task_name,
    status,
    due_date,
    priority
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET task_name = ?,
            status = ?,
            due_date = ?,
            priority = ?
        WHERE task_id = ?
        AND user_id = ?
        """,
        (
            task_name,
            status,
            due_date,
            priority,
            task_id,
            user_id
        )
    )

    conn.commit()

    rows_updated = cursor.rowcount

    conn.close()

    return rows_updated


def delete_task(task_id, user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE task_id = ?
        AND user_id = ?
        """,
        (
            task_id,
            user_id
        )
    )

    conn.commit()

    rows_deleted = cursor.rowcount

    conn.close()

    return rows_deleted


def complete_task(task_id, user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = 'done'
        WHERE task_id = ?
        AND user_id = ?
        """,
        (
            task_id,
            user_id
        )
    )

    conn.commit()

    rows_updated = cursor.rowcount

    conn.close()

    return rows_updated