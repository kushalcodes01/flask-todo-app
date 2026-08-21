import sqlite3
import os
import psycopg2


SQLITE_DB = "list.db"


def get_postgres_connection():

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    return psycopg2.connect(database_url)


def migrate():

    print("Connecting to SQLite...")

    sqlite_conn = sqlite3.connect(
        SQLITE_DB
    )

    sqlite_cursor = sqlite_conn.cursor()

    print("Connecting to PostgreSQL...")

    postgres_conn = get_postgres_connection()

    postgres_cursor = postgres_conn.cursor()

    # -----------------------------------------
    # CREATE TABLES
    # -----------------------------------------

    postgres_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            user_id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    postgres_cursor.execute(
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

    postgres_conn.commit()

    # -----------------------------------------
    # MIGRATE USERS
    # -----------------------------------------

    print("Reading users from SQLite...")

    sqlite_cursor.execute(
        "SELECT * FROM users"
    )

    users = sqlite_cursor.fetchall()

    print(
        f"Found {len(users)} users."
    )

    for user in users:

        postgres_cursor.execute(
            """
            INSERT INTO users
            (user_id, username, email, password)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id)
            DO NOTHING
            """,
            (
                user[0],
                user[1],
                user[2],
                user[3]
            )
        )

    postgres_conn.commit()

    # -----------------------------------------
    # MIGRATE TASKS
    # -----------------------------------------

    print("Reading tasks from SQLite...")

    sqlite_cursor.execute(
        "SELECT * FROM tasks"
    )

    tasks = sqlite_cursor.fetchall()

    print(
        f"Found {len(tasks)} tasks."
    )

    for task in tasks:

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
            DO NOTHING
            """,
            (
                task[0],
                task[1],
                task[2],
                task[3],
                task[4],
                task[5]
            )
        )

    postgres_conn.commit()

    # -----------------------------------------
    # FIX ID SEQUENCES
    # -----------------------------------------

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

    # -----------------------------------------
    # CLOSE CONNECTIONS
    # -----------------------------------------

    sqlite_cursor.close()
    sqlite_conn.close()

    postgres_cursor.close()
    postgres_conn.close()

    print()
    print("Migration completed successfully.")
    print(
        f"Users migrated: {len(users)}"
    )
    print(
        f"Tasks migrated: {len(tasks)}"
    )


if __name__ == "__main__":
    migrate()