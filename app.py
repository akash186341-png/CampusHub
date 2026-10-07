from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    db = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="NayaPassword123!",
        database="campushub"
    )

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


        db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="NayaPassword123!",
            database="campushub"
        )


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