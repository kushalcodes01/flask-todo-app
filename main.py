import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from dbase import (
    create_table,
    create_users_table,
    get_all_tasks,
    add_task,
    update_task,
    search_task,
    delete_task,
    add_user,
    search_user,
    get_task,
    complete_task,
    migrate_sqlite_data
)


# --------------------------------------------------
# FLASK APP
# --------------------------------------------------

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:

    raise RuntimeError(
        "SECRET_KEY is not configured."
    )


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

create_table()
create_users_table()

# Import old SQLite data if list.db exists.
# Safe to run repeatedly because conflicts are handled.
migrate_sqlite_data()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    if "username" in session:

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "landing.html"
    )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:

        return redirect(
            url_for("login")
        )

    username = session["username"]
    user_id = session["user_id"]

    tasks = get_all_tasks(user_id)

    total_tasks = len(tasks)

    completed_tasks = 0
    pending_tasks = 0
    overdue_tasks = 0

    today = date.today().isoformat()

    for task in tasks:

        if task["status"] == "done":

            completed_tasks += 1

        elif task["status"] == "pending":

            pending_tasks += 1

            if task["due_date"] < today:

                overdue_tasks += 1

    if total_tasks == 0:

        completion_rate = 0

    else:

        completion_rate = round(
            (completed_tasks / total_tasks) * 100,
            2
        )

    return render_template(
        "dashboard.html",
        username=username,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completion_rate=completion_rate
    )


# --------------------------------------------------
# VIEW ALL TASKS
# --------------------------------------------------

@app.route("/show")
def view_tasks():

    if "username" not in session:
        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    tasks = get_all_tasks(user_id)

    today = date.today().isoformat()

    task_data = []

    for task in tasks:

        is_overdue = (
            task["status"] == "pending"
            and task["due_date"] < today
        )

        task_data.append(
            {
                "task": task,
                "overdue": is_overdue
            }
        )

    return render_template(
        "show.html",
        tasks=task_data
    )

# --------------------------------------------------
# ADD TASK
# --------------------------------------------------

@app.route(
    "/form",
    methods=["GET", "POST"]
)
def form():

    if "username" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        user_id = session["user_id"]

        task_name = request.form["name"]
        status = request.form["status"]
        due_date = request.form["due_date"]
        priority = request.form["priority"]

        add_task(
            user_id,
            task_name,
            status,
            due_date,
            priority
        )

        return redirect(
            url_for("view_tasks")
        )

    return render_template(
        "form.html"
    )


# --------------------------------------------------
# UPDATE TASK
# --------------------------------------------------

@app.route(
    "/update/<int:task_id>",
    methods=["GET", "POST"]
)
def edit_task(task_id):

    if "username" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    task = get_task(
        task_id,
        user_id
    )

    if task is None:

        return "Task Not Found", 404

    if request.method == "POST":

        task_name = request.form["name"]
        status = request.form["status"]
        due_date = request.form["due_date"]
        priority = request.form["priority"]

        update_task(
            task_id,
            user_id,
            task_name,
            status,
            due_date,
            priority
        )

        return redirect(
            url_for("view_tasks")
        )

    return render_template(
        "update.html",
        task=task
    )


# --------------------------------------------------
# SEARCH TASK
# --------------------------------------------------

@app.route(
    "/search",
    methods=["GET", "POST"]
)
def search():

    if "username" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        task_id = request.form["task_id"]

        try:

            task_id = int(task_id)

        except ValueError:

            return "Invalid Task ID", 400

        task = search_task(task_id)

        if task is None:

            return "Task Not Found", 404

        if task["user_id"] != session["user_id"]:

            return "Task Not Found", 404

        today = date.today().isoformat()

        is_overdue = (
            task["status"] == "pending"
            and task["due_date"] < today
        )

        return render_template(
            "search_result.html",
            task=task,
            is_overdue=is_overdue
        )

    return render_template(
        "search.html"
    )


# --------------------------------------------------
# DELETE TASK
# --------------------------------------------------

@app.route(
    "/delete/<int:task_id>"
)
def delete(task_id):

    if "username" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    task = get_task(
        task_id,
        user_id
    )

    if task is None:

        return "Task Not Found", 404

    delete_task(
        task_id,
        user_id
    )

    return redirect(
        url_for("view_tasks")
    )


# --------------------------------------------------
# COMPLETE TASK
# --------------------------------------------------

@app.route(
    "/complete/<int:task_id>"
)
def complete(task_id):

    if "username" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    task = get_task(
        task_id,
        user_id
    )

    if task is None:

        return "Task Not Found", 404

    complete_task(
        task_id,
        user_id
    )

    return redirect(
        url_for("view_tasks")
    )


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(
            password
        )

        try:

            add_user(
                username,
                email,
                hashed_password
            )

        except Exception:

            return (
                "Username or email already exists.",
                400
            )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = search_user(username)

        if user is None:

            return (
                "Invalid username or password.",
                401
            )

        if check_password_hash(
            user["password"],
            password
        ):
            session.clear()

            session["user_id"] = user["user_id"]
            session["username"] = user["username"]

            return redirect(
                url_for("dashboard")
            )

        return (
            "Invalid username or password.",
            401
        )

    return render_template(
        "login.html"
    )


# --------------------------------------------------
# PROFILE
# --------------------------------------------------

@app.route("/profile")
def profile():

    if "username" not in session:

        return redirect(
            url_for("login")
        )

    username = session["username"]
    user_id = session["user_id"]

    tasks = get_all_tasks(user_id)

    total_tasks = len(tasks)

    completed_tasks = 0
    pending_tasks = 0
    overdue_tasks = 0

    today = date.today().isoformat()

    for task in tasks:

        if task["status"] == "done":

            completed_tasks += 1

        elif task["status"] == "pending":

            pending_tasks += 1

            if task["due_date"] < today:

                overdue_tasks += 1

    if total_tasks == 0:

        completion_rate = 0

    else:

        completion_rate = round(
            (completed_tasks / total_tasks) * 100,
            2
        )

    return render_template(
        "profile.html",
        username=username,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completion_rate=completion_rate
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run()