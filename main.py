from flask import Flask, render_template, request, redirect, url_for

from dbase import create_table,get_all_tasks,add_task,update_task,search_task, delete_task

app = Flask(__name__)

create_table()

@app.route("/")
def Home():

    return render_template("home.html")

@app.route("/show")
def view_tasks():

    tasks = get_all_tasks()

    return render_template("show.html",tasks=tasks)

@app.route("/form", methods=["GET", "POST"])
def form():

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

    if request.method == "POST":

        task_id = request.form["task_id"]
        task = search_task(task_id)

        return render_template("search_result.html", task=task)

    return render_template("search.html")

@app.route("/delete/<task_id>")
def delete(task_id):

    delete_task(task_id)

    return redirect(url_for("view_tasks"))

app.run(debug=True)