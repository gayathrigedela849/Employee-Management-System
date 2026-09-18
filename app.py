from flask import Flask, request, redirect, render_template, session
import sqlite3

app = Flask(__name__)
app.secret_key = "employee_management_secret"


# ==========================================
# DATABASE CREATION
# ==========================================

def create_database():

    connection = sqlite3.connect("employees.db")
    cursor = connection.cursor()

    # Employee table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            fullname TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            joining_date TEXT NOT NULL,
            salary REAL NOT NULL,
            qualification TEXT NOT NULL,
            experience TEXT NOT NULL,
            skills TEXT NOT NULL
        )
    """)

    # User table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# ADD EMPLOYEE PAGE
# ==========================================

@app.route("/add_employee")
def add_employee():

    return render_template("add_employee.html")


# ==========================================
# SAVE EMPLOYEE
# ==========================================

@app.route("/save_employee", methods=["POST"])
def save_employee():

    employee_id = request.form["employee_id"]
    fullname = request.form["fullname"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]
    department = request.form["department"]
    designation = request.form["designation"]
    joining_date = request.form["joining_date"]
    salary = request.form["salary"]
    qualification = request.form["qualification"]
    experience = request.form["experience"]
    skills = request.form["skills"]

    connection = sqlite3.connect("employees.db")
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO employees
            (
                employee_id,
                fullname,
                dob,
                gender,
                email,
                phone,
                address,
                department,
                designation,
                joining_date,
                salary,
                qualification,
                experience,
                skills
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_id,
            fullname,
            dob,
            gender,
            email,
            phone,
            address,
            department,
            designation,
            joining_date,
            salary,
            qualification,
            experience,
            skills
        ))

        connection.commit()
        connection.close()

        return redirect("/view_employee")

    except sqlite3.IntegrityError:

        connection.close()

        return """
        <h2>Employee ID already exists!</h2>
        <a href="/add_employee">Go Back</a>
        """


# ==========================================
# VIEW EMPLOYEES
# ==========================================

@app.route("/view_employee")
def view_employee():

    connection = sqlite3.connect("employees.db")

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM employees
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()

    connection.close()

    return render_template(
        "view_employee.html",
        employees=employees
    )


# ==========================================
# SEARCH EMPLOYEE
# ==========================================

@app.route("/search_employee", methods=["GET", "POST"])
def search_employee():

    employees = []

    if request.method == "POST":

        search = request.form["search"]

        connection = sqlite3.connect("employees.db")

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM employees
            WHERE employee_id LIKE ?
            OR fullname LIKE ?
            OR department LIKE ?
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

        employees = cursor.fetchall()

        connection.close()

    return render_template(
        "search_employee.html",
        employees=employees
    )


# ==========================================
# EDIT EMPLOYEE
# ==========================================

@app.route("/edit/<int:id>")
def edit_employee(id):

    connection = sqlite3.connect("employees.db")

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM employees WHERE id = ?",
        (id,)
    )

    employee = cursor.fetchone()

    connection.close()

    return render_template(
        "add_employee.html",
        employee=employee
    )


# ==========================================
# UPDATE EMPLOYEE
# ==========================================

@app.route("/update/<int:id>", methods=["POST"])
def update_employee(id):

    employee_id = request.form["employee_id"]
    fullname = request.form["fullname"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]
    department = request.form["department"]
    designation = request.form["designation"]
    joining_date = request.form["joining_date"]
    salary = request.form["salary"]
    qualification = request.form["qualification"]
    experience = request.form["experience"]
    skills = request.form["skills"]

    connection = sqlite3.connect("employees.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE employees SET
            employee_id = ?,
            fullname = ?,
            dob = ?,
            gender = ?,
            email = ?,
            phone = ?,
            address = ?,
            department = ?,
            designation = ?,
            joining_date = ?,
            salary = ?,
            qualification = ?,
            experience = ?,
            skills = ?
        WHERE id = ?
    """, (
        employee_id,
        fullname,
        dob,
        gender,
        email,
        phone,
        address,
        department,
        designation,
        joining_date,
        salary,
        qualification,
        experience,
        skills,
        id
    ))

    connection.commit()
    connection.close()

    return redirect("/view_employee")


# ==========================================
# DELETE EMPLOYEE
# ==========================================

@app.route("/delete/<int:id>")
def delete_employee(id):

    connection = sqlite3.connect("employees.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM employees WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/view_employee")


# ==========================================
# REGISTER PAGE
# ==========================================

@app.route("/register")
def register_page():

    return render_template("register.html")


# ==========================================
# REGISTER USER
# ==========================================

@app.route("/register_user", methods=["POST"])
def register_user():

    fullname = request.form["fullname"]
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    connection = sqlite3.connect("employees.db")
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users
            (fullname, username, email, password)
            VALUES (?, ?, ?, ?)
        """, (
            fullname,
            username,
            email,
            password
        ))

        connection.commit()
        connection.close()

        return redirect("/login")

    except sqlite3.IntegrityError:

        connection.close()

        return """
        <h2>Username or Email already exists!</h2>
        <a href="/register">Go Back</a>
        """


# ==========================================
# LOGIN PAGE
# ==========================================

@app.route("/login")
def login_page():

    return render_template("login.html")


# ==========================================
# LOGIN USER
# ==========================================

@app.route("/login_user", methods=["POST"])
def login_user():

    username = request.form["username"]
    password = request.form["password"]

    connection = sqlite3.connect("employees.db")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
        AND password = ?
    """, (
        username,
        password
    ))

    user = cursor.fetchone()

    connection.close()

    if user:

        session["username"] = username

        return redirect("/")

    else:

        return """
        <h2>Invalid username or password!</h2>
        <a href="/login">Try Again</a>
        """


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)