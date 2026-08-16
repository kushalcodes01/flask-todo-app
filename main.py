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
                   search_user)

app = Flask(__name__)
app.secret_key = "mysecretkey"

create_table() #task table
create_users_table() #users table

@app.route("/")
def Home():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("home.html")

@app.route("/show")
def view_tasks():

    if "username" not in session:
        return redirect(url_for("login"))

    tasks = get_all_tasks()

    return render_template(
        "show.html",
        tasks=tasks
    )

@app.route("/form", methods=["GET", "POST"])
def form():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        task_id = request.form["task_id"]
        task_name = request.form["name"]
        status = request.form["status"]

        add_task(
            task_id,
            task_name,
            status
        )
        return redirect(url_for("view_tasks"))

    return render_template("form.html")

@app.route("/update/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):

    if request.method == "POST":

        task_name = request.form["name"]
        status = request.form["status"]

        update_task(
            task_id,
            task_name,
            status
        )
        return redirect(url_for("view_tasks"))

    task = search_task(task_id)
    
    return render_template("update.html", 
                           task=task)

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

    delete_task(task_id)

    return redirect(url_for("view_tasks"))

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        add_user(
            username,
            email,
            password
        )
        return "Registration Successfully"
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

        if password == user[3]:
            session["username"] = username
            return "Login Successful"

        return "Wrong Password"

    return render_template("login.html")

@app.route("/profile")
def profile():

    return f"Session Data: {dict(session)}"

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

app.run(debug=True)