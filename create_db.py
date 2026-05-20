import sqlite3

# connect database
conn = sqlite3.connect("student.db")

# create cursor
cursor = conn.cursor()

# create Students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Students (
    student_id INTEGER PRIMARY KEY,
    name TEXT,
    dept TEXT
)
""")

# create Courses table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Courses (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT
)
""")

# create Enrollments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Enrollments (
    enroll_id INTEGER PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    grade INTEGER,

    FOREIGN KEY(student_id) REFERENCES Students(student_id),
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
)
""")

print("Tables created successfully!")

conn.commit()
conn.close()               
