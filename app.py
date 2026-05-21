from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import sqlite3
import csv
import io
import os

app = Flask(__name__)
app.secret_key = "scms_secret_key_2025"

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "student.db")


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    schema_path = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
    with open(schema_path, "r") as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM Admins WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()
        if admin:
            session["user"] = username
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    stats = {
        "students": conn.execute("SELECT COUNT(*) FROM Students").fetchone()[0],
        "courses":  conn.execute("SELECT COUNT(*) FROM Courses").fetchone()[0],
        "enrollments": conn.execute("SELECT COUNT(*) FROM Enrollments").fetchone()[0],
        "attendance": conn.execute("SELECT COUNT(*) FROM Attendance").fetchone()[0],
    }
    recent = conn.execute(
        "SELECT student_id, name, dept FROM Students ORDER BY student_id DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", stats=stats, recent=recent)


# ── STUDENTS ──────────────────────────────────────────────────────────────────

@app.route("/students")
@login_required
def students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM Students ORDER BY student_id").fetchall()
    courses = conn.execute("SELECT * FROM Courses").fetchall()
    conn.close()
    return render_template("students.html", students=rows, courses=courses)


@app.route("/students/add", methods=["POST"])
@login_required
def add_student():
    sid   = request.form.get("student_id", "").strip()
    name  = request.form.get("name", "").strip()
    dept  = request.form.get("dept", "").strip()
    cid   = request.form.get("course_id", "").strip()
    grade = request.form.get("grade", "Not Assigned").strip() or "Not Assigned"

    if not sid or not name or not dept:
        return jsonify(success=False, message="All fields are required.")

    conn = get_db()
    try:
        conn.execute("INSERT INTO Students (student_id, name, dept) VALUES (?,?,?)", (sid, name, dept))
        if cid:
            conn.execute(
                "INSERT OR IGNORE INTO Enrollments (student_id, course_id, grade) VALUES (?,?,?)",
                (sid, cid, grade)
            )
        conn.commit()
        return jsonify(success=True, message=f"Student {sid} added successfully.")
    except sqlite3.IntegrityError:
        return jsonify(success=False, message=f"Student ID {sid} already exists.")
    except Exception as e:
        return jsonify(success=False, message=str(e))
    finally:
        conn.close()


@app.route("/students/update", methods=["POST"])
@login_required
def update_student():
    sid  = request.form.get("student_id", "").strip()
    name = request.form.get("name", "").strip()
    dept = request.form.get("dept", "").strip()

    if not sid or not name or not dept:
        return jsonify(success=False, message="All fields are required.")

    conn = get_db()
    existing = conn.execute("SELECT * FROM Students WHERE student_id=?", (sid,)).fetchone()
    if not existing:
        conn.close()
        return jsonify(success=False, message="Student not found.")

    conn.execute("UPDATE Students SET name=?, dept=? WHERE student_id=?", (name, dept, sid))
    conn.commit()
    conn.close()
    return jsonify(success=True, message=f"Student {sid} updated.")


@app.route("/students/delete", methods=["POST"])
@login_required
def delete_student():
    sid = request.form.get("student_id", "").strip()
    if not sid:
        return jsonify(success=False, message="Student ID required.")

    conn = get_db()
    existing = conn.execute("SELECT * FROM Students WHERE student_id=?", (sid,)).fetchone()
    if not existing:
        conn.close()
        return jsonify(success=False, message="Student not found.")

    conn.execute("DELETE FROM Enrollments WHERE student_id=?", (sid,))
    conn.execute("DELETE FROM Attendance WHERE student_id=?", (sid,))
    conn.execute("DELETE FROM Students WHERE student_id=?", (sid,))
    conn.commit()
    conn.close()
    return jsonify(success=True, message=f"Student {sid} and all related records deleted.")


@app.route("/students/search")
@login_required
def search_student():
    sid  = request.args.get("student_id", "").strip()
    name = request.args.get("name", "").strip()

    conn = get_db()
    if sid:
        rows = conn.execute("SELECT * FROM Students WHERE student_id=?", (sid,)).fetchall()
    elif name:
        rows = conn.execute("SELECT * FROM Students WHERE name LIKE ?", (f"%{name}%",)).fetchall()
    else:
        rows = []
    conn.close()
    return jsonify(students=[dict(r) for r in rows])


@app.route("/students/generate_id")
@login_required
def generate_id():
    conn = get_db()
    result = conn.execute("SELECT MAX(student_id) FROM Students").fetchone()[0]
    conn.close()
    new_id = 1001 if result is None else result + 1
    return jsonify(new_id=new_id)


# ── COURSES ───────────────────────────────────────────────────────────────────

@app.route("/courses")
@login_required
def courses():
    conn = get_db()
    rows = conn.execute("SELECT * FROM Courses ORDER BY course_id").fetchall()
    conn.close()
    return render_template("courses.html", courses=rows)


@app.route("/courses/add", methods=["POST"])
@login_required
def add_course():
    cid  = request.form.get("course_id", "").strip()
    name = request.form.get("course_name", "").strip()
    if not cid or not name:
        return jsonify(success=False, message="All fields required.")
    conn = get_db()
    try:
        conn.execute("INSERT INTO Courses (course_id, course_name) VALUES (?,?)", (cid, name))
        conn.commit()
        return jsonify(success=True, message="Course added.")
    except sqlite3.IntegrityError:
        return jsonify(success=False, message="Course ID already exists.")
    finally:
        conn.close()


@app.route("/courses/delete", methods=["POST"])
@login_required
def delete_course():
    cid = request.form.get("course_id", "").strip()
    conn = get_db()
    conn.execute("DELETE FROM Enrollments WHERE course_id=?", (cid,))
    conn.execute("DELETE FROM Courses WHERE course_id=?", (cid,))
    conn.commit()
    conn.close()
    return jsonify(success=True, message="Course deleted.")


# ── ENROLLMENTS ───────────────────────────────────────────────────────────────

@app.route("/enrollments")
@login_required
def enrollments():
    conn = get_db()
    rows = conn.execute("""
        SELECT s.student_id, s.name, s.dept, c.course_id, c.course_name, e.grade
        FROM Enrollments e
        JOIN Students s ON s.student_id = e.student_id
        JOIN Courses c  ON c.course_id  = e.course_id
        ORDER BY s.student_id
    """).fetchall()
    students = conn.execute("SELECT student_id, name FROM Students ORDER BY student_id").fetchall()
    courses  = conn.execute("SELECT * FROM Courses").fetchall()
    conn.close()
    return render_template("enrollments.html", enrollments=rows, students=students, courses=courses)


@app.route("/enrollments/add", methods=["POST"])
@login_required
def enroll_student():
    sid   = request.form.get("student_id", "").strip()
    cid   = request.form.get("course_id", "").strip()
    grade = request.form.get("grade", "Not Assigned").strip() or "Not Assigned"

    if not sid or not cid:
        return jsonify(success=False, message="Student ID and Course ID required.")

    conn = get_db()
    if not conn.execute("SELECT 1 FROM Students WHERE student_id=?", (sid,)).fetchone():
        conn.close()
        return jsonify(success=False, message="Student not found.")
    if not conn.execute("SELECT 1 FROM Courses WHERE course_id=?", (cid,)).fetchone():
        conn.close()
        return jsonify(success=False, message="Course not found.")
    if conn.execute("SELECT 1 FROM Enrollments WHERE student_id=? AND course_id=?", (sid, cid)).fetchone():
        conn.close()
        return jsonify(success=False, message="Student already enrolled in this course.")

    conn.execute("INSERT INTO Enrollments (student_id, course_id, grade) VALUES (?,?,?)", (sid, cid, grade))
    conn.commit()
    conn.close()
    return jsonify(success=True, message="Student enrolled successfully.")


@app.route("/enrollments/remove", methods=["POST"])
@login_required
def remove_enrollment():
    sid = request.form.get("student_id", "").strip()
    cid = request.form.get("course_id", "").strip()
    conn = get_db()
    conn.execute("DELETE FROM Enrollments WHERE student_id=? AND course_id=?", (sid, cid))
    conn.commit()
    conn.close()
    return jsonify(success=True, message="Enrollment removed.")


@app.route("/enrollments/update_grade", methods=["POST"])
@login_required
def update_grade():
    sid   = request.form.get("student_id", "").strip()
    cid   = request.form.get("course_id", "").strip()
    grade = request.form.get("grade", "").strip()
    if not sid or not cid or not grade:
        return jsonify(success=False, message="All fields required.")
    conn = get_db()
    conn.execute("UPDATE Enrollments SET grade=? WHERE student_id=? AND course_id=?", (grade, sid, cid))
    conn.commit()
    conn.close()
    return jsonify(success=True, message="Grade updated.")


# ── ATTENDANCE ────────────────────────────────────────────────────────────────

@app.route("/attendance")
@login_required
def attendance():
    conn = get_db()
    rows = conn.execute("""
        SELECT s.student_id, s.name, a.date, a.status
        FROM Attendance a
        JOIN Students s ON s.student_id = a.student_id
        ORDER BY a.date DESC
    """).fetchall()
    students = conn.execute("SELECT student_id, name FROM Students ORDER BY student_id").fetchall()
    conn.close()
    return render_template("attendance.html", attendance=rows, students=students)


@app.route("/attendance/mark", methods=["POST"])
@login_required
def mark_attendance():
    sid    = request.form.get("student_id", "").strip()
    date   = request.form.get("date", "").strip()
    status = request.form.get("status", "").strip()

    if not sid or not date or not status:
        return jsonify(success=False, message="All fields required.")

    conn = get_db()
    if not conn.execute("SELECT 1 FROM Students WHERE student_id=?", (sid,)).fetchone():
        conn.close()
        return jsonify(success=False, message="Student not found.")

    conn.execute("INSERT INTO Attendance (student_id, date, status) VALUES (?,?,?)", (sid, date, status))
    conn.commit()
    conn.close()
    return jsonify(success=True, message="Attendance marked.")


# ── REPORTS ───────────────────────────────────────────────────────────────────

@app.route("/reports")
@login_required
def reports():
    conn = get_db()
    # GPA data
    enrollments = conn.execute("""
        SELECT s.student_id, s.name, s.dept, c.course_name, e.grade
        FROM Enrollments e
        JOIN Students s ON s.student_id = e.student_id
        JOIN Courses c  ON c.course_id  = e.course_id
        ORDER BY s.student_id
    """).fetchall()

    toppers = conn.execute("""
        SELECT s.student_id, s.name, c.course_name, e.grade
        FROM Enrollments e
        JOIN Students s ON s.student_id = e.student_id
        JOIN Courses c  ON c.course_id  = e.course_id
        WHERE e.grade != 'Not Assigned'
        ORDER BY e.grade DESC
        LIMIT 10
    """).fetchall()

    students = conn.execute("SELECT student_id, name FROM Students ORDER BY student_id").fetchall()
    conn.close()
    return render_template("reports.html", enrollments=enrollments, toppers=toppers, students=students)


@app.route("/reports/gpa")
@login_required
def get_gpa():
    sid = request.args.get("student_id", "").strip()
    if not sid:
        return jsonify(success=False, message="Student ID required.")

    conn = get_db()
    grades = conn.execute(
        "SELECT grade FROM Enrollments WHERE student_id=?", (sid,)
    ).fetchall()
    conn.close()

    grade_points = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5}
    total, count = 0, 0
    for row in grades:
        g = row["grade"]
        if g in grade_points:
            total += grade_points[g]
            count += 1

    if count == 0:
        return jsonify(success=False, message="No valid grades found.")
    gpa = round(total / count, 2)
    return jsonify(success=True, gpa=gpa)


@app.route("/reports/attendance_pct")
@login_required
def attendance_pct():
    sid = request.args.get("student_id", "").strip()
    if not sid:
        return jsonify(success=False, message="Student ID required.")

    conn = get_db()
    total   = conn.execute("SELECT COUNT(*) FROM Attendance WHERE student_id=?", (sid,)).fetchone()[0]
    present = conn.execute("SELECT COUNT(*) FROM Attendance WHERE student_id=? AND status='Present'", (sid,)).fetchone()[0]
    conn.close()

    if total == 0:
        return jsonify(success=False, message="No attendance records found.")
    pct = round((present / total) * 100, 2)
    return jsonify(success=True, percentage=pct, present=present, total=total)


# ── CSV IMPORT / EXPORT ───────────────────────────────────────────────────────

@app.route("/export/students")
@login_required
def export_students():
    conn = get_db()
    rows = conn.execute("SELECT student_id, name, dept FROM Students").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Name", "Department"])
    for row in rows:
        writer.writerow([row["student_id"], row["name"], row["dept"]])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="students.csv"
    )


@app.route("/export/enrollments")
@login_required
def export_enrollments():
    conn = get_db()
    rows = conn.execute("""
        SELECT s.student_id, s.name, c.course_name, e.grade
        FROM Enrollments e
        JOIN Students s ON s.student_id = e.student_id
        JOIN Courses c  ON c.course_id  = e.course_id
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Name", "Course", "Grade"])
    for row in rows:
        writer.writerow([row["student_id"], row["name"], row["course_name"], row["grade"]])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="enrollments.csv"
    )


@app.route("/import/students", methods=["POST"])
@login_required
def import_students():
    file = request.files.get("csv_file")
    if not file:
        return jsonify(success=False, message="No file uploaded.")

    stream = io.StringIO(file.stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)
    conn = get_db()
    added, skipped = 0, 0
    for row in reader:
        try:
            conn.execute(
                "INSERT INTO Students (student_id, name, dept) VALUES (?,?,?)",
                (row.get("Student ID"), row.get("Name"), row.get("Department"))
            )
            added += 1
        except Exception:
            skipped += 1
    conn.commit()
    conn.close()
    return jsonify(success=True, message=f"Imported {added} students. Skipped {skipped} duplicates.")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT",5000))
)
