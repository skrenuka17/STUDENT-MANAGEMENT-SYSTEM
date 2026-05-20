import sqlite3

conn = sqlite3.connect("student.db")
cursor = conn.cursor()

# insert students
cursor.execute("INSERT INTO Students VALUES (1, 'Renuka', 'AIML')")
cursor.execute("INSERT INTO Students VALUES (2, 'Ravi', 'CSE')")
cursor.execute("INSERT INTO Students VALUES (3, 'Meena', 'ECE')")

# insert courses
cursor.execute("INSERT INTO Courses VALUES (101, 'DBMS')")
cursor.execute("INSERT INTO Courses VALUES (102, 'Python')")
cursor.execute("INSERT INTO Courses VALUES (103, 'Machine Learning')")

# insert enrollments
cursor.execute("INSERT INTO Enrollments VALUES (1, 1, 101, 85)")
cursor.execute("INSERT INTO Enrollments VALUES (2, 1, 102, 90)")
cursor.execute("INSERT INTO Enrollments VALUES (3, 2, 101, 78)")
cursor.execute("INSERT INTO Enrollments VALUES (4, 3, 103, 88)")

conn.commit()

print("Data inserted successfully!")

conn.close()
