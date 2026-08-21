# To-Do App

A web-based To-Do application built with Python, Flask, Jinja2, and SQLite.

The application allows users to create accounts, manage their personal tasks, set priorities and due dates, search tasks, and track completed or overdue tasks.

## Features

- User Registration and Login
- Session-based Authentication
- Personal User Dashboard
- Add Tasks
- View Tasks
- Update Tasks
- Delete Tasks
- Mark Tasks as Completed
- Search Tasks
- Task Details
- Task Priorities
- Task Due Dates
- Overdue Task Detection
- User Profile
- SQLite Database
- Jinja2 Templates
- Protected Routes for Logged-in Users

## Tech Stack

- **Python**
- **Flask**
- **Jinja2**
- **SQLite**
- **HTML**
- **CSS**
- **Git & GitHub**

## Project Structure

```text
To-Do-App/
│
├── main.py
├── dbase.py
├── list.db
├── requirements.txt
├── .gitignore
├── .env
│
├── templates/
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── navbar.html
│   ├── dashboard.html
│   ├── form.html
│   ├── show.html
│   ├── update.html
│   ├── search.html
│   ├── search_result.html
│   └── profile.html
│
└── static/
    └── ...