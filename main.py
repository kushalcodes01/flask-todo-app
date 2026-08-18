from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session

from dbase import (create_table,
                   get_all_tasks,
                   add_task,
                   update_task,
                   search_task, 
                   delete_task,
                   create_users_table,
                   get_all_users,
                   add_user,
                   search_user,
                   get_task,
                   add_due_date_column)

app = Flask(__name__)
app.secret_key = "mysecretkey"

create_table() #task table
create_users_table() #users table
#add_due_date_column() #table for deadline 

@app.route("/")
def home():

    if "username" in session:
        return redirect(url_for("view_tasks"))

    return render_template("landing.html")

@app.route("/show")
def view_tasks():

    if "username" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    tasks = get_all_tasks(user_id)

    return render_template(
        "show.html",
        tasks=tasks
    )
@app.route("/form", methods=["GET", "POST"])
def form():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        user_id = session["user_id"]
        task_name = request.form["name"]
        status = request.form["status"]
        due_date = request.form["due_date"]

        add_task(
            user_id,
            task_name,
            status,
            due_date
        )
        return redirect(url_for("view_tasks"))

    return render_template("form.html")

@app.route("/update/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):

    task = get_task(task_id)

    if task is None:
        return "Task Not Found"

    if task[1] != session["user_id"]:
        return "Access Denied"

    if request.method == "POST":

        task_name = request.form["name"]
        status = request.form["status"]
        due_date = request.form["due_date"]

        update_task(
            task_id,
            task_name,
            status,
            due_date
        )

        return redirect(url_for("view_tasks"))

    return render_template(
        "update.html",
        task=task
    )

@app.route("/search", methods=["GET", "POST"])
def search():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        task_id = request.form["task_id"]
        task = search_task(task_id)

        return render_template("search_result.html", task=task)

    return render_template("search.html")

@app.route("/delete/<task_id>")
def delete(task_id):

    task = get_task(task_id)

    if task is None:
        return "Task Not Found"

    if task[1] != session["user_id"]:
        return "Access Denied"

    delete_task(task_id)

    return redirect(url_for("view_tasks"))

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        add_user(
            username,
            email,
            hashed_password
        )
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/users")
def users():

    return str(get_all_users())

@app.route("/testuser")
def testuser():

    return str(search_user("kushal"))

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = search_user(username)

        if user is None:
            return "User Not Found"

        if check_password_hash(user[3], password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect(url_for("dashboard"))

        return "Wrong Password"

    return render_template("login.html")

@app.route("/profile")
def profile():

    return str(dict(session))

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_id = session["user_id"]

    tasks = get_all_tasks(user_id)

    total_tasks = len(tasks)

    completed_tasks = 0
    pending_tasks = 0

    for task in tasks:

        if task[3] == "done":
            completed_tasks += 1

        elif task[3] == "pending":
            pending_tasks += 1

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
        completion_rate=completion_rate
    )

app.run(debug=True)