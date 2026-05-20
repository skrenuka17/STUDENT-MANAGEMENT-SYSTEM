import sqlite3

conn = sqlite3.connect("student.db")
cursor = conn.cursor()

query = """
SELECT Students.name,

COUNT(Enrollments.course_id) as total_courses,

AVG(Enrollments.grade) as average_grade,

MAX(Enrollments.grade) as highest_grade

FROM Enrollments

JOIN Students
ON Enrollments.student_id = Students.student_id

GROUP BY Students.name

ORDER BY average_grade DESC
"""

cursor.execute(query)

rows = cursor.fetchall()

print("Top Performing Students:\n")

for row in rows:
    print(row)

conn.close()
