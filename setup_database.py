"""
setup_database.py
-----------------
This script sets up a SQLite database for the Student Performance Analysis project.
It creates three tables:
1. students: Information about students (id, name, age, gender, study hours).
2. courses: Details of courses offered (id, name, credits).
3. grades: Exam scores and attendance rates for students in specific courses.

It generates realistic, synthetic sample data where study hours and class attendance
are positively correlated with exam scores, allowing for meaningful statistical analysis.
"""

import sqlite3
import random
import os

# Define the database file name
DB_NAME = "student_records.db"

# Sample lists for generating realistic student names
FIRST_NAMES_MALE = ["Aarav", "Kabir", "Vihaan", "Aditya", "Sai", "Arjun", "Reyansh", "Krishna", "Atharv", "Ishaan", "Rohan", "Dev"]
FIRST_NAMES_FEMALE = ["Diya", "Aanya", "Pari", "Ananya", "Sanya", "Prisha", "Riya", "Ira", "Avani", "Myra", "Sneha", "Tanya"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Patel", "Mehta", "Singh", "Joshi", "Rao", "Nair", "Iyer", "Choudhury", "Das"]

COURSES_DATA = [
    ("Mathematics", 4),
    ("Physics", 4),
    ("Computer Science", 3),
    ("Statistics", 3),
    ("English Literature", 2)
]

def create_database():
    # Remove the database if it already exists to ensure a clean setup
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Removed existing database: {DB_NAME}")

    # Connect to SQLite Database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Enable Foreign Key support in SQLite (disabled by default)
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("Creating tables...")

    # 1. Create 'students' table
    cursor.execute("""
        CREATE TABLE students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER CHECK(age >= 17 AND age <= 25),
            gender TEXT CHECK(gender IN ('Male', 'Female')),
            study_hours_per_week REAL CHECK(study_hours_per_week >= 0)
        );
    """)

    # 2. Create 'courses' table
    cursor.execute("""
        CREATE TABLE courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT UNIQUE NOT NULL,
            credits INTEGER CHECK(credits > 0)
        );
    """)

    # 3. Create 'grades' table
    cursor.execute("""
        CREATE TABLE grades (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            score REAL CHECK(score >= 0 AND score <= 100),
            attendance_rate REAL CHECK(attendance_rate >= 0 AND attendance_rate <= 100),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    print("Tables created successfully!")
    return conn, cursor

def populate_data(conn, cursor):
    print("Generating and inserting sample data...")

    # Insert Courses
    course_ids = []
    for course_name, credits in COURSES_DATA:
        cursor.execute("INSERT INTO courses (course_name, credits) VALUES (?, ?);", (course_name, credits))
        course_ids.append(cursor.lastrowid)

    # Generate 60 Students
    random.seed(42)  # Set seed for reproducible results
    
    students_list = []
    for _ in range(60):
        gender = random.choice(["Male", "Female"])
        if gender == "Male":
            name = f"{random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}"
        else:
            name = f"{random.choice(FIRST_NAMES_FEMALE)} {random.choice(LAST_NAMES)}"
        
        age = random.randint(18, 22)
        # Study hours: range from 3 to 22 hours, bell-curved
        study_hours = round(random.triangular(3, 22, 10), 1)
        
        cursor.execute(
            "INSERT INTO students (name, age, gender, study_hours_per_week) VALUES (?, ?, ?, ?);",
            (name, age, gender, study_hours)
        )
        student_id = cursor.lastrowid
        students_list.append((student_id, study_hours))

    # Generate Grades and Attendance
    # We want a positive correlation between study_hours, attendance, and exam scores!
    for student_id, study_hours in students_list:
        # Every student takes a random selection of 4 courses (out of 5)
        enrolled_courses = random.sample(course_ids, 4)
        
        for course_id in enrolled_courses:
            # Attendance rate: correlated with study hours (active students attend more)
            # Base attendance is 60% + influence of study hours + some random noise
            attendance_noise = random.uniform(-10, 10)
            attendance = 60 + (study_hours * 1.5) + attendance_noise
            attendance = min(100.0, max(45.0, round(attendance, 1)))  # Clamp between 45% and 100%
            
            # Score formula: 35 base + study hour impact + attendance impact + exam day noise
            # Standard random exam day noise
            exam_noise = random.uniform(-8, 8)
            score = 35 + (study_hours * 1.8) + ((attendance - 50) * 0.4) + exam_noise
            score = min(100.0, max(0.0, round(score, 1)))  # Clamp between 0 and 100
            
            cursor.execute(
                "INSERT INTO grades (student_id, course_id, score, attendance_rate) VALUES (?, ?, ?, ?);",
                (student_id, course_id, score, attendance)
            )

    conn.commit()
    print(f"Data insertion complete! SQLite database saved as '{DB_NAME}' with:")
    print(" - 5 Courses")
    print(" - 60 Students")
    print(" - 240 Grade Records")

def main():
    try:
        conn, cursor = create_database()
        populate_data(conn, cursor)
    except sqlite3.Error as e:
        print(f"An error occurred with SQLite: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
