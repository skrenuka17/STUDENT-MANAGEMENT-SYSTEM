# EduTrack — Student Course Management System (Web)
A professional web-based Student Management System built with Flask + SQLite.

---

## Folder Structure
```
student_mgmt/
├── app.py                  # Flask backend — all routes
├── requirements.txt
├── database/
│   ├── schema.sql          # SQL schema (auto-applied on first run)
│   └── student.db          # SQLite DB (auto-created on first run)
├── templates/
│   ├── base.html           # Shared layout + navbar
│   ├── login.html
│   ├── dashboard.html
│   ├── students.html
│   ├── courses.html
│   ├── enrollments.html
│   ├── attendance.html
│   └── reports.html
└── static/
    ├── css/main.css
    └── js/main.js
```

---

## Setup & Run

### 1. Install Python (3.8+)
https://www.python.org/downloads/

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

### 6. Default login
- Username: `admin`
- Password: `1234`

---

## Features

| Feature | Description |
|---|---|
| Login / Logout | Session-based authentication |
| Dashboard | Live stats + recent students + quick actions |
| Students | Add, Edit, Delete, Search, Auto-generate ID |
| Courses | View and manage available courses |
| Enrollments | Enroll/unenroll students, update grades |
| Attendance | Mark Present/Absent per student per date |
| Reports | GPA calculator, Attendance %, Toppers, Report Card |
| CSV Export | Export students and enrollments as CSV |
| CSV Import | Bulk import students via CSV upload |

---

## Grade Scale (GPA)
| Grade | Points |
|---|---|
| O   | 10 |
| A+  | 9  |
| A   | 8  |
| B+  | 7  |
| B   | 6  |
| C   | 5  |

---

## Default Courses
1. DBMS  
2. Python  
3. AI  
4. Machine Learning  

You can add more courses from the Courses page.
THIS IS MY FIRST AND FOREMOST.
