import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3


def get_connection():

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor
    )


# --------------------------------------------------
# CREATE TASK TABLE
# --------------------------------------------------

def create_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks(
            task_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'medium'
        )
        """
    )

    conn.commit()
    cursor.close()
    conn.close()


# --------------------------------------------------
# CREATE USERS TABLE
# --------------------------------------------------

def create_users_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            user_id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    conn.commit()
    cursor.close()
    conn.close()


# --------------------------------------------------
# ADD USER
# --------------------------------------------------

def add_user(username, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (username, email, password)
        VALUES (%s, %s, %s)
        """,
        (username, email, password)
    )

    conn.commit()

    cursor.close()
    conn.close()


# --------------------------------------------------
# SEARCH USER
# --------------------------------------------------

def search_user(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username = %s
        """,
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


# --------------------------------------------------
# ADD TASK
# --------------------------------------------------

def add_task(
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
        INSERT INTO tasks
        (user_id, task_name, status, due_date, priority)
        VALUES (%s, %s, %s, %s, %s)
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

    cursor.close()
    conn.close()


# --------------------------------------------------
# GET ALL TASKS
# --------------------------------------------------

def get_all_tasks(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE user_id = %s
        ORDER BY task_id ASC
        """,
        (user_id,)
    )

    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    return tasks


# --------------------------------------------------
# GET ONE TASK
# --------------------------------------------------

def get_task(task_id, user_id=None):

    conn = get_connection()
    cursor = conn.cursor()

    if user_id is None:

        cursor.execute(
            """
            SELECT *
            FROM tasks
            WHERE task_id = %s
            """,
            (task_id,)
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM tasks
            WHERE task_id = %s
            AND user_id = %s
            """,
            (task_id, user_id)
        )

    task = cursor.fetchone()

    cursor.close()
    conn.close()

    return task


# --------------------------------------------------
# SEARCH TASK
# --------------------------------------------------

def search_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE task_id = %s
        """,
        (task_id,)
    )

    task = cursor.fetchone()

    cursor.close()
    conn.close()

    return task


# --------------------------------------------------
# UPDATE TASK
# --------------------------------------------------

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
        SET task_name = %s,
            status = %s,
            due_date = %s,
            priority = %s
        WHERE task_id = %s
        AND user_id = %s
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

    cursor.close()
    conn.close()

    return rows_updated


# --------------------------------------------------
# DELETE TASK
# --------------------------------------------------

def delete_task(task_id, user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE task_id = %s
        AND user_id = %s
        """,
        (
            task_id,
            user_id
        )
    )

    conn.commit()

    rows_deleted = cursor.rowcount

    cursor.close()
    conn.close()

    return rows_deleted


# --------------------------------------------------
# COMPLETE TASK
# --------------------------------------------------

def complete_task(task_id, user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = 'done'
        WHERE task_id = %s
        AND user_id = %s
        """,
        (
            task_id,
            user_id
        )
    )

    conn.commit()

    rows_updated = cursor.rowcount

    cursor.close()
    conn.close()

    return rows_updated


# --------------------------------------------------
# MIGRATE OLD SQLITE DATABASE
# --------------------------------------------------

def migrate_sqlite_data():

    sqlite_file = "list.db"

    if not os.path.exists(sqlite_file):
        return

    sqlite_conn = sqlite3.connect(sqlite_file)
    sqlite_cursor = sqlite_conn.cursor()

    postgres_conn = get_connection()
    postgres_cursor = postgres_conn.cursor()

    # ----------------------------------------------
    # USERS
    # ----------------------------------------------

    try:

        sqlite_cursor.execute(
            "SELECT * FROM users"
        )

        users = sqlite_cursor.fetchall()

    except sqlite3.Error:

        users = []

    for user in users:

        postgres_cursor.execute(
            """
            INSERT INTO users
            (
                user_id,
                username,
                email,
                password
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (username)
            DO UPDATE SET
                email = EXCLUDED.email,
                password = EXCLUDED.password
            """,
            (
                user[0],
                user[1],
                user[2],
                user[3]
            )
        )

    # ----------------------------------------------
    # TASKS
    # ----------------------------------------------

    try:

        sqlite_cursor.execute(
            "PRAGMA table_info(tasks)"
        )

        columns = sqlite_cursor.fetchall()

        column_names = [
            column[1]
            for column in columns
        ]

        sqlite_cursor.execute(
            "SELECT * FROM tasks"
        )

        tasks = sqlite_cursor.fetchall()

    except sqlite3.Error:

        tasks = []
        column_names = []

    for task in tasks:

        task_id = task[0]
        user_id = task[1]
        task_name = task[2]
        status = task[3]

        if "due_date" in column_names:

            due_date_index = column_names.index(
                "due_date"
            )

            due_date = task[due_date_index]

        else:

            due_date = "2099-12-31"

        if "priority" in column_names:

            priority_index = column_names.index(
                "priority"
            )

            priority = task[priority_index]

        else:

            priority = "medium"

        if not due_date:
            due_date = "2099-12-31"

        if not priority:
            priority = "medium"

        postgres_cursor.execute(
            """
            INSERT INTO tasks
            (
                task_id,
                user_id,
                task_name,
                status,
                due_date,
                priority
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (task_id)
            DO UPDATE SET
                user_id = EXCLUDED.user_id,
                task_name = EXCLUDED.task_name,
                status = EXCLUDED.status,
                due_date = EXCLUDED.due_date,
                priority = EXCLUDED.priority
            """,
            (
                task_id,
                user_id,
                task_name,
                status,
                due_date,
                priority
            )
        )

    # ----------------------------------------------
    # FIX POSTGRES SEQUENCES
    # ----------------------------------------------

    postgres_cursor.execute(
        """
        SELECT setval(
            'users_user_id_seq',
            COALESCE(
                (SELECT MAX(user_id) FROM users),
                1
            )
        )
        """
    )

    postgres_cursor.execute(
        """
        SELECT setval(
            'tasks_task_id_seq',
            COALESCE(
                (SELECT MAX(task_id) FROM tasks),
                1
            )
        )
        """
    )

    postgres_conn.commit()

    sqlite_cursor.close()
    sqlite_conn.close()

    postgres_cursor.close()
    postgres_conn.close()