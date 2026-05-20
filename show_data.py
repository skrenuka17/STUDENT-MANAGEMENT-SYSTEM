import sqlite3

conn = sqlite3.connect("student.db")
cursor = conn.cursor()

query = """
SELECT Students.name, Courses.course_name, Enrollments.grade
FROM Enrollments
JOIN Students
ON Enrollments.student_id = Students.student_id
JOIN Courses
ON Enrollments.course_id = Courses.course_id
"""

cursor.execute(query)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
