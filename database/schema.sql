-- Student Course Management System - Schema
-- Run this to initialize the database

CREATE TABLE IF NOT EXISTS Admins (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

INSERT OR IGNORE INTO Admins VALUES ('admin', '1234');

CREATE TABLE IF NOT EXISTS Students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    dept TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Courses (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT NOT NULL
);

INSERT OR IGNORE INTO Courses VALUES (1, 'DBMS');
INSERT OR IGNORE INTO Courses VALUES (2, 'Python');
INSERT OR IGNORE INTO Courses VALUES (3, 'AI');
INSERT OR IGNORE INTO Courses VALUES (4, 'Machine Learning');

CREATE TABLE IF NOT EXISTS Enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    grade TEXT DEFAULT 'Not Assigned',
    UNIQUE(student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE IF NOT EXISTS Attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);
