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
    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("employees.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Total employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    # Total departments
    cursor.execute("""
        SELECT COUNT(DISTINCT department)
        FROM employees
    """)
    total_departments = cursor.fetchone()[0]

    # Total designations
    cursor.execute("""
        SELECT COUNT(DISTINCT designation)
        FROM employees
    """)
    total_designations = cursor.fetchone()[0]

    # Salary Analytics

    # Average salary
    cursor.execute("""
        SELECT AVG(salary)
        FROM employees
    """)
    average_salary = cursor.fetchone()[0] or 0

    # Total payroll
    cursor.execute("""
        SELECT SUM(salary)
        FROM employees
    """)
    total_payroll = cursor.fetchone()[0] or 0

    # Highest salary
    cursor.execute("""
        SELECT MAX(salary)
        FROM employees
    """)
    highest_salary = cursor.fetchone()[0] or 0

    # Lowest salary
    cursor.execute("""
        SELECT MIN(salary)
        FROM employees
    """)
    lowest_salary = cursor.fetchone()[0] or 0

    # Department Analytics
    cursor.execute("""
        SELECT department,
            COUNT(*) AS employee_count
        FROM employees
        WHERE department IS NOT NULL
          AND TRIM(department) != ''
        GROUP BY department
        ORDER BY employee_count DESC
    """)

    department_data = cursor.fetchall()

    department_colors = [
    "#2563eb",
    "#8b5cf6",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#06b6d4"
 ]

    department_data = [
    {
        "department": row["department"],
        "employee_count": row["employee_count"],
        "percentage": round(
            (row["employee_count"] / total_employees) * 100, 1
        ) if total_employees else 0,
        "color": department_colors[index % len(department_colors)]
    }
    for index, row in enumerate(department_data)
    ]

    # Recently added employees
    cursor.execute("""
        SELECT employee_id,
               fullname,
               department,
               designation,
               joining_date
        FROM employees
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_employees = cursor.fetchall()

    # Number of employees added recently
    cursor.execute("""
        SELECT COUNT(*)
        FROM employees
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_count = cursor.fetchone()[0]

    connection.close()

    return render_template(
      "index.html",
     total_employees=total_employees,
     total_departments=total_departments,
     total_designations=total_designations,

     average_salary=average_salary,
     total_payroll=total_payroll,
     highest_salary=highest_salary,
     lowest_salary=lowest_salary,

     department_data=department_data,
     recent_employees=recent_employees,
     recent_count=recent_count
    ) 
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
    if not phone.isdigit() or len(phone) != 10:
     return "Phone number must contain exactly 10 digits!"
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

        return redirect("/")

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
    
@app.route("/view_employee/<employee_id>")
def employee_details(employee_id):
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM employees
        WHERE employee_id = ?
    """, (employee_id,))

    employee = cursor.fetchone()
    conn.close()

    if employee:
        return render_template("employee_details.html", employee=employee)

    return "Employee not found"

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
    if not phone.isdigit() or len(phone) != 10:
     return "Phone number must contain exactly 10 digits!"
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

    connection = sqlite3.connect("users.db")
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

    connection = sqlite3.connect("users.db")

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

    return redirect("/login")
# ==========================================
# DEPARTMENT OVERVIEW
# ==========================================

@app.route("/departments")
def departments():

    connection = sqlite3.connect("employees.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT department, COUNT(*) AS employee_count
        FROM employees
        GROUP BY department
        ORDER BY employee_count DESC
    """)

    departments = cursor.fetchall()

    connection.close()

    return render_template(
        "departments.html",
        departments=departments
    )


# ==========================================
# DESIGNATION OVERVIEW
# ==========================================

@app.route("/designations")
def designations():

    connection = sqlite3.connect("employees.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT designation, COUNT(*) AS employee_count
        FROM employees
        GROUP BY designation
        ORDER BY employee_count DESC
    """)

    designations = cursor.fetchall()

    connection.close()

    return render_template(
        "designations.html",
        designations=designations
    )


# ==========================================
# RECENT EMPLOYEES
# ==========================================

@app.route("/recent_employees")
def recent_employees():

    connection = sqlite3.connect("employees.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT employee_id,
               fullname,
               department,
               designation,
               joining_date
        FROM employees
        ORDER BY id DESC
        LIMIT 5
    """)

    employees = cursor.fetchall()

    connection.close()

    return render_template(
        "recent_employees.html",
        employees=employees
    )

# ==========================================
# EXPORT EMPLOYEE REPORT
# ==========================================

@app.route("/export_employees")
def export_employees():

    connection = sqlite3.connect("employees.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT employee_id,
               fullname,
               dob,
               gender,
               email,
               phone,
               address,
               department,
               designation,
               joining_date,
               salary
        FROM employees
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()

    connection.close()

    import csv
    from io import StringIO

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Employee ID",
        "Full Name",
        "Date of Birth",
        "Gender",
        "Email",
        "Phone",
        "Address",
        "Department",
        "Designation",
        "Joining Date",
        "Salary"
    ])

    for employee in employees:
        writer.writerow([
            employee["employee_id"],
            employee["fullname"],
            employee["dob"],
            employee["gender"],
            employee["email"],
            employee["phone"],
            employee["address"],
            employee["department"],
            employee["designation"],
            employee["joining_date"],
            employee["salary"]
        ])

    from flask import Response

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=employee_report.csv"
        }
    )

# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)