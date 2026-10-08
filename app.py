from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from functools import wraps
import mysql.connector
import os
import secrets

app = Flask(__name__)

# Set SECRET_KEY in Render Environment Variables.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("home"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        admin_username = os.environ.get("ADMIN_USERNAME", "")
        password_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")

        if (
            admin_username
            and password_hash
            and secrets.compare_digest(username, admin_username)
            and check_password_hash(password_hash, password)
        ):
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("home"))

        error = "Invalid username or password."

    response = app.make_response(render_template("login.html", error=error))
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@admin_required
def home():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
    finally:
        cursor.close()
        db.close()

    response = app.make_response(
        render_template("index.html", students=students)
    )
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/register", methods=["GET", "POST"])
@admin_required
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        course = request.form["course"].strip()
        semester = int(request.form["semester"])
        age = int(request.form["age"])

        db = get_db_connection()
        cursor = db.cursor()
        try:
            sql = """
                INSERT INTO student
                (name, email, course, semester, age)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, email, course, semester, age))
            db.commit()
        finally:
            cursor.close()
            db.close()

        return redirect(url_for("home"))

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
