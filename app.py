from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student")

    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("index.html", students=students)


# =========================
# REGISTRATION PAGE
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]
        semester = request.form["semester"]
        age = request.form["age"]

        db = get_db_connection()

        cursor = db.cursor()

        sql = """
        INSERT INTO student
        (name, email, course, semester, age)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            course,
            semester,
            age
        )

        cursor.execute(sql, values)

        db.commit()

        cursor.close()
        db.close()

        return redirect(url_for("home"))

    return render_template("register.html")


# =========================
# START SERVER
# =========================

if __name__ == "__main__":
    app.run(debug=True)