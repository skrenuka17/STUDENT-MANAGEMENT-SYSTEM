import sqlite3
import csv 
from tkinter import ttk
from tkinter import *
from tkinter import messagebox

login = Tk()

login.title("Login")
login.geometry("300x200")


# ---------------- DATABASE ----------------
conn = sqlite3.connect("student.db",timeout=10)

cursor = conn.cursor()

# insert courses
cursor.execute("""
CREATE TABLE IF NOT EXISTS Admins(
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO Admins
VALUES ('admin', '1234')
""")

conn.commit()


cursor.execute("""
CREATE TABLE IF NOT EXISTS Courses(
    course_id INTEGER PRIMARY KEY,
    course_name TEXT
)
""")



courses = [
    (1, "DBMS"),
    (2, "Python"),
    (3, "AI"),
    (4, "Machine Learning")
]

for course in courses:

    cursor.execute(
        "INSERT OR IGNORE INTO Courses VALUES (?, ?)",
        course
    )
cursor.execute("""
CREATE TABLE IF NOT EXISTS Attendance(
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT
)
""")

conn.commit()

# ---------------- MAIN WINDOW ----------------
root = Toplevel(login)
root.withdraw()
root.title("Student Course Management System")
root.geometry("1400x750")

root.configure(bg="#dfe6e9")

notebook = ttk.Notebook(root)

students_tab = Frame(notebook, bg="#1e272e")
academic_tab = Frame(notebook, bg="#1e272e")
attendance_tab = Frame(notebook, bg="#1e272e")
reports_tab = Frame(notebook, bg="#1e272e")

notebook.add(students_tab, text="Students")
notebook.add(academic_tab, text="Academic")
notebook.add(attendance_tab, text="Attendance")
notebook.add(reports_tab, text="Reports")

notebook.pack(expand=True, fill="both")

Label(
    root,
    text="STUDENT COURSE MANAGEMENT SYSTEM",
    bg="#2d3436",
    fg="white",
    font=("Segoe UI", 22, "bold"),
    pady=15
    ).pack(fill="x")

# ---------------- FUNCTIONS ----------------
def check_login():

    username = user_entry.get()
    password = pass_entry.get()

    cursor.execute(
        """
        SELECT * FROM Admins
        WHERE username = ? AND password = ?
        """,
        (username, password)
    )

    admin = cursor.fetchone()

    if admin:

        login.withdraw()
        root.deiconify()

    else:

        messagebox.showerror(
            "Login Failed",
            "Invalid username or password"
        )


def add_student():

    sid = entry_id.get().strip()
    name = entry_name.get().strip()
    dept = entry_dept.get().strip()

    # empty validation
    if sid == "" or name == "" or dept == "":

        messagebox.showerror(
            "Error",
            "All fields are required"
        )

        return

    # check duplicate student
    cursor.execute(
        "SELECT * FROM Students WHERE student_id = ?",
        (sid,)
    )

    existing = cursor.fetchone()

    if existing:

        messagebox.showerror(
            "Duplicate Error",
            f"Student ID {sid} already exists"
        )

        return

    try:

        cursor.execute(
            """
            INSERT INTO Students
            (student_id, name, dept)
            VALUES (?, ?, ?)
            """,
            (sid, name, dept)
        )

        conn.commit()
        # auto enrollment

        course_text = entry_course.get().strip()

        if course_text != "":

           cid = course_text.split(" - ")[0]

           grade = entry_grade.get().strip()

           if grade == "":
               grade = "Not Assigned"

           cursor.execute(
                """
                INSERT INTO Enrollments

                (student_id, course_id, grade)
                VALUES (?, ?, ?)
                """,
                (sid, cid, grade)
        )

        conn.commit()
        update_dashboard()
        messagebox.showinfo(
            "Success",
            f"Student {sid} added successfully"
        )

    except Exception as e:

        messagebox.showerror(
            "Database Error",
            str(e)
        )


def search_student():

    sid = entry_id.get().strip()
    name = entry_name.get().strip()

    # clear old rows
    for item in result_box.get_children():
        result_box.delete(item)

    # validation
    if sid == "" and name == "":

        messagebox.showerror(
            "Error",
            "Enter Student ID or Name"
        )

        return

    # search by ID
    if sid != "":

        query = """
        SELECT
            student_id,
            name,
            dept
        FROM Students
        WHERE student_id = ?
        """

        cursor.execute(query, (sid,))

    # search by Name
    else:

        query = """
        SELECT
            student_id,
            name,
            dept
        FROM Students
        WHERE name LIKE ?
        """

        cursor.execute(
            query,
            (f"%{name}%",)
        )

    rows = cursor.fetchall()

    if len(rows) == 0:

        messagebox.showerror(
            "Not Found",
            "No student found"
        )

    else:

        result_box["columns"] = (
            "ID",
            "Name",
            "Dept"
        )

        result_box.heading("ID", text="Student ID")
        result_box.heading("Name", text="Name")
        result_box.heading("Dept", text="Department")

        for row in rows:

            result_box.insert(
                "",
                END,
                values=row
            )
            
def update_student():

    sid = entry_id.get()
    name = entry_name.get()
    dept = entry_dept.get()

    if sid.strip() == "" or name.strip() == "" or dept.strip() == "":

        messagebox.showerror(
            "Error",
            "All fields are required"
        )

        return

    cursor.execute(
        "SELECT * FROM Students WHERE student_id = ?",
        (sid,)
    )

    student = cursor.fetchone()

    if student is None:

        messagebox.showerror(
            "Invalid ID",
            "Student does not exist"
        )

        return

    cursor.execute("""
        UPDATE Students
        SET name = ?, dept = ?
        WHERE student_id = ?
    """, (name, dept, sid))

    conn.commit()

    messagebox.showinfo(
        "Updated",
        f"Student {sid} updated successfully"
    )

def delete_student():

    sid = entry_id.get().strip()

    if sid == "":

        messagebox.showerror(
            "Error",
            "Enter Student ID"
        )

        return

    cursor.execute(
        "SELECT * FROM Students WHERE student_id = ?",
        (sid,)
    )

    student = cursor.fetchone()

    if student is None:

        messagebox.showerror(
            "Invalid ID",
            "Student does not exist"
        )

        return

    # confirmation popup
    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Delete student and all related records?"
    )

    if not confirm:
        return

    # delete enrollments
    cursor.execute(
        """
        DELETE FROM Enrollments
        WHERE student_id = ?
        """,
        (sid,)
    )

    # delete attendance
    cursor.execute(
        """
        DELETE FROM Attendance
        WHERE student_id = ?
        """,
        (sid,)
    )

    # delete student
    cursor.execute(
        """
        DELETE FROM Students
        WHERE student_id = ?
        """,
        (sid,)
    )

    conn.commit()

    update_dashboard()

    messagebox.showinfo(
        "Deleted",
        f"Student {sid} and related records deleted successfully"
    )

    show_students()

def enroll_student():

    sid = entry_id.get().strip()
    course_text = entry_course.get()
    cid = course_text.split(" - ")[0]
    grade = entry_grade.get().strip()

    # validation
    if sid == "":
        messagebox.showerror("Error", "Enter Student ID")
        return

    if cid == "":
        messagebox.showerror("Error", "Enter Course ID")
        return

    # optional grade
    if grade == "":
        grade = "Not Assigned"

    # check student exists
    cursor.execute(
        "SELECT * FROM Students WHERE student_id = ?",
        (sid,)
    )

    student = cursor.fetchone()

    if student is None:
        messagebox.showerror(
            "Invalid Student",
            f"Student ID {sid} does not exist"
        )
        return

    # check course exists
    cursor.execute(
        "SELECT * FROM Courses WHERE course_id = ?",
        (cid,)
    )

    course = cursor.fetchone()

    if course is None:
        messagebox.showerror(
            "Invalid Course",
            f"Course ID {cid} does not exist"
        )
        return

    # prevent duplicate enrollment
    cursor.execute(
        """
        SELECT * FROM Enrollments
        WHERE student_id = ? AND course_id = ?
        """,
        (sid, cid)
    )

    existing = cursor.fetchone()

    if existing:
        messagebox.showerror(
            "Duplicate Enrollment",
            "Student already enrolled in this course"
        )
        return

    try:

        cursor.execute(
            """
            INSERT INTO Enrollments
            (student_id, course_id, grade)
            VALUES (?, ?, ?)
            """,
            (sid, cid, grade)
        )

        conn.commit()
        update_dashboard()
        messagebox.showinfo(
            "Success",
            f"Student {sid} enrolled successfully"
        )
    
    except Exception as e:

        messagebox.showerror(
            "Database Error",
            str(e)
        )


def show_students():

    # clear old data
    for item in result_box.get_children():
        result_box.delete(item)

    # change columns
    result_box["columns"] = (
        "ID",
        "Name",
        "Dept"
    )

    # headings
    result_box.heading("ID", text="Student ID")
    result_box.heading("Name", text="Name")
    result_box.heading("Dept", text="Department")

    # widths
    result_box.column("ID", width=120)
    result_box.column("Name", width=220)
    result_box.column("Dept", width=180)

    cursor.execute(
        "SELECT * FROM Students"
    )

    rows = cursor.fetchall()

    for row in rows:

        result_box.insert(
            "",
            END,
            values=row
        )

def show_enrollments():

    # clear old data
    for item in result_box.get_children():
        result_box.delete(item)

    query = """
    SELECT
        Students.student_id,
        Students.name,
        Students.dept,
        Courses.course_id,
        Courses.course_name

    FROM Enrollments

    JOIN Students
        ON Students.student_id = Enrollments.student_id

    JOIN Courses
        ON Courses.course_id = Enrollments.course_id
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    if len(rows) == 0:

        messagebox.showinfo(
            "No Data",
            "No enrollments found"
        )

    else:

        for row in rows:

            result_box.insert(
                "",
                END,
                values=row
            )

def remove_enrollment():

    sid = entry_id.get().strip()

    # get only course id from combobox
    cid = entry_course.get().split(" - ")[0].strip()

    # validation
    if sid == "":
        messagebox.showerror(
            "Error",
            "Enter Student ID"
        )
        return

    if cid == "":
        messagebox.showerror(
            "Error",
            "Enter Course ID"
        )
        return

    # check enrollment exists
    cursor.execute(
        """
        SELECT * FROM Enrollments
        WHERE student_id = ? AND course_id = ?
        """,
        (sid, cid)
    )

    enrollment = cursor.fetchone()

    if enrollment is None:

        messagebox.showerror(
            "Not Found",
            "Enrollment does not exist"
        )

        return

    # delete enrollment
    cursor.execute(
        """
        DELETE FROM Enrollments
        WHERE student_id = ? AND course_id = ?
        """,
        (sid, cid)
    )

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Enrollment removed successfully"
    )

    show_enrollments()

def update_grade():

    sid = entry_id.get().strip()
    cid = entry_course.get().split(" - ")[0]
    grade = entry_grade.get().strip()

    if sid == "" or cid == "" or grade == "":

        messagebox.showerror(
            "Error",
            "Enter all fields"
        )

        return

    cursor.execute(
        """
        UPDATE Enrollments
        SET grade = ?
        WHERE student_id = ? AND course_id = ?
        """,
        (grade, sid, cid)
    )

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Grade updated"
    )

def mark_attendance():

    sid = entry_id.get().strip()
    date = entry_date.get().strip()
    status = entry_status.get().strip()

    if sid == "" or date == "" or status == "":

        messagebox.showerror(
            "Error",
            "Fill all attendance fields"
        )

        return

    cursor.execute(
        """
        INSERT INTO Attendance
        (student_id, date, status)
        VALUES (?, ?, ?)
        """,
        (sid, date, status)
    )

    conn.commit()
    update_dashboard()
    messagebox.showinfo(
        "Success",
        "Attendance marked"
    )

def export_students():

    cursor.execute("SELECT * FROM Students")

    rows = cursor.fetchall()

    with open(
        "students.csv",
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            ["Student ID", "Name", "Department"]
        )

        writer.writerows(rows)

    messagebox.showinfo(
        "Exported",
        "students.csv created successfully"
    )

def show_course_students():

    # clear old rows
    for item in result_box.get_children():
        result_box.delete(item)

    course_text = entry_course.get().strip()

    if course_text == "":

        messagebox.showerror(
            "Error",
            "Select a course"
        )

        return

    cid = course_text.split(" - ")[0]

    query = """
    SELECT
        Students.student_id,
        Students.name,
        Students.dept

    FROM Enrollments

    JOIN Students
        ON Students.student_id = Enrollments.student_id

    WHERE Enrollments.course_id = ?
    """

    cursor.execute(query, (cid,))

    rows = cursor.fetchall()

    if len(rows) == 0:

        messagebox.showinfo(
            "No Data",
            "No students enrolled in this course"
        )

        return

    result_box["columns"] = (
        "ID",
        "Name",
        "Dept"
    )

    result_box.heading("ID", text="Student ID")
    result_box.heading("Name", text="Name")
    result_box.heading("Dept", text="Department")

    result_box.column("ID", width=120)
    result_box.column("Name", width=220)
    result_box.column("Dept", width=180)

    for row in rows:

        result_box.insert(
            "",
            END,
            values=row
        )

def update_dashboard():

    # total students
    cursor.execute(
        "SELECT COUNT(*) FROM Students"
    )

    students = cursor.fetchone()[0]

    # total courses
    cursor.execute(
        "SELECT COUNT(*) FROM Courses"
    )

    courses = cursor.fetchone()[0]

    # total enrollments
    cursor.execute(
        "SELECT COUNT(*) FROM Enrollments"
    )

    enrollments = cursor.fetchone()[0]

    # total attendance
    cursor.execute(
        "SELECT COUNT(*) FROM Attendance"
    )

    attendance = cursor.fetchone()[0]

    # update labels
    student_count_label.config(
        text=f"Students: {students}"
    )

    course_count_label.config(
        text=f"Courses: {courses}"
    )

    enrollment_count_label.config(
        text=f"Enrollments: {enrollments}"
    )

    attendance_count_label.config(
        text=f"Attendance: {attendance}"
    )

def show_toppers():

    # clear old rows
    for item in result_box.get_children():
        result_box.delete(item)

    query = """
    SELECT
        Students.student_id,
        Students.name,
        Courses.course_name,
        Enrollments.grade

    FROM Enrollments

    JOIN Students
        ON Students.student_id = Enrollments.student_id

    JOIN Courses
        ON Courses.course_id = Enrollments.course_id

    WHERE Enrollments.grade != 'Not Assigned'

    ORDER BY Enrollments.grade DESC
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    if len(rows) == 0:

        messagebox.showinfo(
            "No Data",
            "No toppers found"
        )

        return

    # set columns
    result_box["columns"] = (
        "ID",
        "Name",
        "Course",
        "Grade"
    )

    result_box.heading("ID", text="Student ID")
    result_box.heading("Name", text="Name")
    result_box.heading("Course", text="Course")
    result_box.heading("Grade", text="Grade")

    result_box.column("ID", width=100)
    result_box.column("Name", width=180)
    result_box.column("Course", width=180)
    result_box.column("Grade", width=100)

    # insert data
    for row in rows:

        result_box.insert(
            "",
            END,
            values=row
        )

def view_attendance():

    # clear old rows
    for item in result_box.get_children():
        result_box.delete(item)

    query = """
    SELECT
        Students.student_id,
        Students.name,
        Attendance.date,
        Attendance.status

    FROM Attendance

    JOIN Students
        ON Students.student_id = Attendance.student_id
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    if len(rows) == 0:

        messagebox.showinfo(
            "No Data",
            "No attendance records found"
        )

        return

    # set columns
    result_box["columns"] = (
        "ID",
        "Name",
        "Date",
        "Status"
    )

    result_box.heading("ID", text="Student ID")
    result_box.heading("Name", text="Name")
    result_box.heading("Date", text="Date")
    result_box.heading("Status", text="Status")

    result_box.column("ID", width=100)
    result_box.column("Name", width=180)
    result_box.column("Date", width=150)
    result_box.column("Status", width=120)

    # insert data
    for row in rows:

        result_box.insert(
            "",
            END,
            values=row
        )

def show_report_card():

    # clear old rows
    for item in result_box.get_children():
        result_box.delete(item)

    sid = entry_id.get().strip()

    if sid == "":

        messagebox.showerror(
            "Error",
            "Enter Student ID"
        )

        return

    query = """
    SELECT
        Students.student_id,
        Students.name,
        Courses.course_name,
        Enrollments.grade

    FROM Enrollments

    JOIN Students
        ON Students.student_id = Enrollments.student_id

    JOIN Courses
        ON Courses.course_id = Enrollments.course_id

    WHERE Students.student_id = ?
    """

    cursor.execute(query, (sid,))

    rows = cursor.fetchall()

    if len(rows) == 0:

        messagebox.showinfo(
            "No Data",
            "No report card found"
        )

        return

    # set columns
    result_box["columns"] = (
        "ID",
        "Name",
        "Course",
        "Grade"
    )

    result_box.heading("ID", text="Student ID")
    result_box.heading("Name", text="Name")
    result_box.heading("Course", text="Course")
    result_box.heading("Grade", text="Grade")

    result_box.column("ID", width=100)
    result_box.column("Name", width=180)
    result_box.column("Course", width=180)
    result_box.column("Grade", width=100)

    # insert rows
    for row in rows:

        result_box.insert(
            "",
            END,
            values=row
        )

def calculate_gpa():

    sid = entry_id.get().strip()

    if sid == "":

        messagebox.showerror(
            "Error",
            "Enter Student ID"
        )

        return

    query = """
    SELECT grade
    FROM Enrollments
    WHERE student_id = ?
    """

    cursor.execute(query, (sid,))

    rows = cursor.fetchall()

    if len(rows) == 0:

        messagebox.showinfo(
            "No Data",
            "No grades found"
        )

        return

    # grade mapping
    grade_points = {
        "O": 10,
        "A+": 9,
        "A": 8,
        "B+": 7,
        "B": 6,
        "C": 5
    }

    total = 0
    count = 0

    for row in rows:

        grade = row[0]

        if grade in grade_points:

            total += grade_points[grade]
            count += 1

    if count == 0:

        messagebox.showinfo(
            "No GPA",
            "No valid grades found"
        )

        return

    gpa = total / count

    messagebox.showinfo(
        "GPA Result",
        f"Student GPA = {round(gpa, 2)}"
    )

def attendance_percentage():

    sid = entry_id.get().strip()

    if sid == "":

        messagebox.showerror(
            "Error",
            "Enter Student ID"
        )

        return

    # total attendance
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM Attendance
        WHERE student_id = ?
        """,
        (sid,)
    )

    total = cursor.fetchone()[0]

    if total == 0:

        messagebox.showinfo(
            "No Data",
            "No attendance records found"
        )

        return

    # present count
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM Attendance
        WHERE student_id = ?
        AND status = 'Present'
        """,
        (sid,)
    )

    present = cursor.fetchone()[0]

    percentage = (present / total) * 100

    messagebox.showinfo(
        "Attendance Percentage",
        f"Attendance = {round(percentage, 2)}%"
    )

def generate_student_id():

    cursor.execute(
        """
        SELECT MAX(student_id)
        FROM Students
        """
    )

    result = cursor.fetchone()[0]

    if result is None:

        new_id = 1001

    else:

        new_id = result + 1

    entry_id.delete(0, END)

    entry_id.insert(
        0,
        str(new_id)
    )



# ---------------- INPUT FRAME ----------------
input_frame = LabelFrame(
    students_tab,
    text="Student Details",
    bg="#2f3640",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    padx=20,
    pady=20,
    bd=2
)
input_frame.pack()
academic_frame = LabelFrame(
    academic_tab,
    text="Academic Details",
    bg="#2f3640",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    padx=20,
    pady=20,
    bd=2
)

academic_frame.pack(pady=20)
attendance_frame = LabelFrame(
    attendance_tab,
    text="Attendance Details",
    bg="#2f3640",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    padx=20,
    pady=20,
    bd=2
)

attendance_frame.pack(pady=20)



Label(login, text="Username").pack(pady=5)
user_entry = Entry(login)
user_entry.pack()

Label(login, text="Password").pack(pady=5)
pass_entry = Entry(login, show="*")
pass_entry.pack()


Label(input_frame, text="Student ID", width=15, anchor="w", fg="white", bg="#2f3640").grid(row=0, column=0)
entry_id = Entry(input_frame,font=("Segoe Ui",11), width=30)
entry_id.grid(row=0, column=1, padx=10, pady=8)

Label(input_frame, text="Name", width=15, anchor="w", bg="#2f3640",
fg="white").grid(row=1, column=0)
entry_name = Entry(input_frame, width=30, font=("Segoe UI", 11))
entry_name.grid(row=1, column=1, padx=10, pady=8)

Label(input_frame, text="Department", width=15, anchor="w", bg="#2f3640",
fg="white").grid(row=2, column=0)
entry_dept = Entry(input_frame, width=30, font=("Segoe UI", 11) )
entry_dept.grid(row=2, column=1, padx=10, pady=8)

Label(academic_frame, text="Course ID", width=15, anchor="w", bg="#2f3640",
fg="white").grid(row=0, column=0)
course_var = StringVar()

entry_course = ttk.Combobox(
    academic_frame,
    textvariable=course_var,
    width=27,
    state="readonly",
    font=("Segoe UI", 11)
)

entry_course["values"] = (
    "1 - DBMS",
    "2 - Python",
    "3 - AI",
    "4 - Machine Learning"      
)
entry_course.grid(row=0, column=1, padx=10, pady=8)

Label(academic_frame, text="Grade", width=15, anchor="w", bg="#2f3640",
fg="white").grid(row=1, column=0)
entry_grade = Entry(academic_frame, width=30, font=("Segoe UI", 11))
entry_grade.grid(row=1, column=1, padx=10, pady=8)
 
Label(attendance_frame, text="Date", width=15, anchor="w", bg="#2f3640",
fg="white").grid(row=5, column=0)
entry_date = Entry(input_frame, width=30, font=("Segoe UI", 11))
entry_date.grid(row=5, column=1, padx=10, pady=8)

Label(attendance_frame, text="Status", width=15, anchor="w", bg="#2f3640",
fg="white").grid(row=6, column=0)

status_var = StringVar()

entry_status = ttk.Combobox(
    input_frame,
    textvariable=status_var,
    width=27,
    state="readonly"
)

entry_status["values"] = (
    "Present",
    "Absent"
)

entry_status.grid(row=6, column=1, padx=10, pady=8)




entry_id.bind("<Return>", lambda event: entry_name.focus_set())

entry_name.bind("<Return>", lambda event: entry_dept.focus_set())

entry_dept.bind("<Return>", lambda event: entry_course.focus_set())

entry_course.bind("<Return>", lambda event: entry_grade.focus_set())





# ---------------- BUTTON FRAME ----------------
btn_frame = LabelFrame(
    academic_tab,
    text="Academic Operations",
    bg="#2f3640",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    padx=15,
    pady=15
)

btn_frame.pack()

# ---------------- DASHBOARD ----------------

dashboard_frame = LabelFrame(
    reports_tab,
    text="Dashboard",
    bg="#2f3640",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    pady=10
)

dashboard_frame.pack(fill="x", padx=20, pady=10)

student_count_label = Label(
    dashboard_frame,
    text="Students: 0",
    font=("Segoe UI", 12, "bold"),
    bg="#353b48",
    fg="white"
)

student_count_label.grid(row=0, column=0, padx=20)

course_count_label = Label(
    dashboard_frame,
    text="Courses: 0",
    font=("Arial", 11, "bold"),
    bg="#353b48",
    fg="white"

)

course_count_label.grid(row=0, column=1, padx=20)

enrollment_count_label = Label(
    dashboard_frame,
    text="Enrollments: 0",
    font=("Arial", 11, "bold"),
    bg="#353b48",
    fg="white"
)

enrollment_count_label.grid(row=0, column=2, padx=20)

attendance_count_label = Label(
    dashboard_frame,
    text="Attendance: 0",
    font=("Arial", 11, "bold"),
    bg="#353b48",
    fg="white"
)

attendance_count_label.grid(row=0, column=3, padx=20)

Button(
    btn_frame,
    text="Add",
    width=10,
    bg="#0984e3", 
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=add_student
).grid(row=0, column=0, padx=5, pady=5)

Button(
    btn_frame,
    text="Search",
    width=10,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=search_student
).grid(row=0, column=1, padx=5)

Button(
    btn_frame,
    text="Update",
    width=10,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=update_student
).grid(row=0, column=2, padx=5)

Button(
    btn_frame,
    text="Delete",
    width=10,
    bg="#d63031",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=delete_student
).grid(row=0, column=3, padx=5)

Button(
    btn_frame,
    text="Students",
    bg="#0984e3",
    width=10,
    command=show_students
).grid(row=1, column=0, padx=5, pady=5)

Button(
    btn_frame,
    text="Enroll",
    width=10,
    bg="#0984e3",
    command=enroll_student
).grid(row=1, column=1, padx=5)

Button(
    btn_frame,
    text="Enrollments",
    width=10,
    bg="#0984e3",
    command=show_enrollments
).grid(row=1, column=2, padx=5)

Button(
    btn_frame,
    text="Remove Enrollment",
    width=18,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=remove_enrollment
).grid(row=1, column=3, padx=5)

Button(
    btn_frame,
    text="Update Grade",
    width=14,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=update_grade
).grid(row=2, column=0, padx=5)

Button(
    btn_frame,
    text="Export CSV",
    width=12,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=export_students
).grid(row=2, column=1, padx=5)

Button(
    btn_frame,
    text="Course Students",
    width=15,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=show_course_students
).grid(row=2, column=2, padx=5)

Button(
    btn_frame,
    text="Topper List",
    width=14,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=show_toppers
).grid(row=2, column=3, padx=5)

Button(
    btn_frame,
    text="View Attendance",
    width=16,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=view_attendance
).grid(row=3, column=0, padx=5)

Button(
    btn_frame,
    text="Report Card",
    width=14,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=show_report_card
).grid(row=3, column=1, padx=5)

Button(
    btn_frame,
    text="Calculate GPA",
    width=15,
    bg="#0984e3",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=calculate_gpa
).grid(row=3, column=2, padx=5)

Button(
    btn_frame,
    text="Attendance %",
    width=15,
    bg="#0984e3",
    fg="black",
    font=("Arial",10,"bold"),
    relief="flat",
    command=attendance_percentage
).grid(row=3, column=3, padx=5)

Button(
    btn_frame,
    text="Generate ID",
    width=14,
    bg="#00b894",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=generate_student_id
).grid(row=0, column=6, padx=5, pady=5)

root.resizable(True,True)


# ---------------- OUTPUT ----------------
# ---------------- OUTPUT ----------------
output_frame = Frame(
    reports_tab,
    bg="#1e272e"
)
output_frame.pack(pady=10)

result_box = ttk.Treeview(
    output_frame,
    columns=(
        "ID",
        "Name",
        "Dept",
        "CourseID",
        "CourseName"
    ),
    show="headings"
)

Button(
    btn_frame,
    text="Attendance",
    width=12,
    bg="#795548",
    fg="white",
    font=("Arial",10,"bold"),
    relief="flat",
    command=mark_attendance
).grid(row=1, column=4, padx=5)


Button(
    login,
    text="Login",
    command=check_login
).pack(pady=20)


# headings
result_box.heading("ID", text="Student ID")
result_box.heading("Dept", text="Department")
result_box.heading("CourseID", text="Course ID")
result_box.heading("CourseName", text="Course Name")

# column widths
result_box.column("ID", width=100)
result_box.column("Name", width=180)
result_box.column("Dept", width=150)
result_box.column("CourseID", width=100)
result_box.column("CourseName", width=180)

result_box.pack(pady=20)

style = ttk.Style()

style.theme_use("clam")

style.configure(
    "Treeview",
    background="#2f3640",
    foreground="white",
    fieldbackground="#2f3640",
    rowheight=32,
    font=("Segoe UI", 10)
)

style.map(
    "Treeview",
    background=[("selected", "#0984e3")]
)

style.configure(
    "Treeview.Heading",
    background="#0984e3",
    foreground="white",
    font=("Segoe UI", 11, "bold")
)

# ---------------- RUN ----------------
update_dashboard()
login.mainloop()
conn.close()