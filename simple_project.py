"""
simple_project.py
-----------------
A super simple, beginner-level Student Performance Analysis project for freshers.
This script is completely self-contained and uses ONLY Python's built-in libraries:
- sqlite3: For creating and querying the relational database.
- csv: For parsing the Kaggle CSV dataset.
- urllib.request: For downloading the Kaggle dataset directly.
- math: For standard square root calculations.

How it works:
1. It automatically downloads the UCI/Kaggle 'student-mat.csv' dataset if not present.
2. It sets up a local SQLite database 'student_simple.db'.
3. It imports 395 real student records and their grades for Math, Physics, and Chemistry.
4. It provides a text menu to:
   - View complete reports using SQL INNER JOINs.
   - View course standings and student rankings using SQL Window Functions.
   - Calculate basic stats (Mean, Median, Mode, Range, Std Dev) manually.
   - Calculate Pearson Correlation Coefficient to see study habit relationships.
   - Run a Machine Learning Linear Regression model manually to predict grades.
"""

import sqlite3
import urllib.request
import csv
import math
import os
import random

DB_NAME = "student_simple.db"
CSV_FILE = "student-mat.csv"
DATA_URL = "https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/04_Apply/Students_Alcohol_Consumption/student-mat.csv"

# Lists for generating realistic student names based on gender
FIRST_NAMES_MALE = ["Aarav", "Kabir", "Vihaan", "Aditya", "Sai", "Arjun", "Reyansh", "Krishna", "Atharv", "Ishaan", "Rohan", "Dev", "Rahul", "Samir", "Amit", "Ravi", "Aniket", "Pankaj", "Deepak", "Sanjay"]
FIRST_NAMES_FEMALE = ["Diya", "Aanya", "Pari", "Ananya", "Sanya", "Prisha", "Riya", "Ira", "Avani", "Myra", "Sneha", "Tanya", "Pooja", "Neha", "Kriti", "Shreya", "Kavya", "Aditi", "Meera", "Ritu"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Patel", "Mehta", "Singh", "Joshi", "Rao", "Nair", "Iyer", "Choudhury", "Das", "Sen", "Bose", "Mishra", "Pandey", "Reddy", "Menon", "Trivedi", "Kulkarni"]

# =====================================================================
# 1. DATABASE SETUP & DATA IMPORT FROM KAGGLE CSV
# =====================================================================
def download_kaggle_dataset():
    """Downloads the popular Kaggle Student Performance CSV if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        print(f"Downloading Kaggle Student Performance dataset from: {DATA_URL}...")
        try:
            urllib.request.urlretrieve(DATA_URL, CSV_FILE)
            print("Download completed successfully!")
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            print("Please check your internet connection or download it manually.")
            raise

def setup_database():
    """Creates SQLite tables and populates them using the downloaded Kaggle CSV."""
    download_kaggle_dataset()

    # Restart database
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create Students Table
    cursor.execute("""
        CREATE TABLE students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            study_hours REAL
        );
    """)

    # Create Grades Table
    cursor.execute("""
        CREATE TABLE grades (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_name TEXT,
            score INTEGER,
            attendance REAL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
    """)

    # Read and parse Kaggle CSV file
    # Semicolon is the default delimiter for Paulo Cortez's student-mat.csv dataset
    random.seed(42)  # For reproducible name mapping
    students_count = 0
    grades_count = 0

    with open(CSV_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        
        for row in reader:
            # Map gender and generate realistic names
            sex = row['sex']
            gender = 'Female' if sex == 'F' else 'Male'
            if gender == 'Male':
                name = f"{random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}"
            else:
                name = f"{random.choice(FIRST_NAMES_FEMALE)} {random.choice(LAST_NAMES)}"
                
            age = int(row['age'])
            
            # Map studytime (categories 1 to 4) into study hours per week
            # 1: <2 hours -> 3.5h, 2: 2-5 hours -> 7.0h, 3: 5-10 hours -> 10.5h, 4: >10 hours -> 14.0h
            study_time_category = float(row['studytime'])
            study_hours = study_time_category * 3.5
            
            # Insert student records into database
            cursor.execute(
                "INSERT INTO students (name, gender, age, study_hours) VALUES (?, ?, ?, ?);",
                (name, gender, age, study_hours)
            )
            student_id = cursor.lastrowid
            students_count += 1
            
            # Converted class absences (0 to 93) into attendance rate percentage
            # Converted absences: 0 absences = 100% attendance, each absence subtracts 1.5%
            absences = float(row['absences'])
            attendance = max(35.0, 100.0 - (absences * 1.5))
            
            # Scale grade scores (G1, G2, G3 scores are 0-20. Scale them to 0-100 by multiplying by 5)
            # G1 = Chemistry, G2 = Physics, G3 = Mathematics
            math_score = int(row['G3']) * 5
            physics_score = int(row['G2']) * 5
            chemistry_score = int(row['G1']) * 5
            
            # Insert grade rows
            grades_to_insert = [
                (student_id, "Mathematics", math_score, attendance),
                (student_id, "Physics", physics_score, attendance),
                (student_id, "Chemistry", chemistry_score, attendance)
            ]
            for s_id, course, score, att in grades_to_insert:
                cursor.execute(
                    "INSERT INTO grades (student_id, course_name, score, attendance) VALUES (?, ?, ?, ?);",
                    (s_id, course, score, att)
                )
                grades_count += 1

    conn.commit()
    conn.close()
    print(f"Data migration successfully completed!")
    print(f" - Loaded {students_count} unique students from Kaggle.")
    print(f" - Populated {grades_count} grade records (Math, Physics, Chemistry).")

# =====================================================================
# 2. SQL QUERY RUNNERS
# =====================================================================
def view_student_report():
    """Executes a SQL INNER JOIN to print first 30 report card rows."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
        SELECT s.student_id, s.name, s.study_hours, g.course_name, g.score, g.attendance
        FROM grades g
        INNER JOIN students s ON g.student_id = s.student_id
        ORDER BY s.student_id, g.course_name
        LIMIT 90;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    print("\n" + "="*85)
    print(f"{'ID':<4} | {'Student Name':<18} | {'Study Hours':<12} | {'Course':<15} | {'Score':<6} | {'Attendance (%)':<10}")
    print("="*85)
    for row in rows:
        print(f"{row[0]:<4} | {row[1]:<18} | {row[2]:<12.1f} | {row[3]:<15} | {row[4]:<6} | {row[5]:<10.1f}")
    print("="*85)
    print("Note: Showing first 30 student profiles (90 grade rows) of 395 total students.\n")

def view_course_standings():
    """Demonstrates intermediate SQL: Window Functions (RANK() OVER) to rank students."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Query uses RANK() over course grouping partitioned by course_name, sorted by score desc
    query = """
        SELECT 
            g.course_name,
            s.name,
            g.score,
            RANK() OVER (PARTITION BY g.course_name ORDER BY g.score DESC) as subject_rank
        FROM grades g
        INNER JOIN students s ON g.student_id = s.student_id
        ORDER BY g.course_name, subject_rank
        LIMIT 60;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    print("\n" + "="*55)
    print("      STUDENT RANKINGS BY SUBJECT (SQL Window Function)")
    print("="*55)
    print(f"{'Course':<15} | {'Student Name':<18} | {'Score':<6} | {'Rank':<4}")
    print("-"*55)
    for row in rows:
        print(f"{row[0]:<15} | {row[1]:<18} | {row[2]:<6} | {row[3]:<4}")
    print("="*55)
    print("Note: Showing top 20 rankings for each subject (60 total rows).\n")

# =====================================================================
# 3. MANUAL STATISTICAL ALGORITHMS
# Calculated using simple loops so beginners can explain it easily!
# =====================================================================
def get_all_scores():
    """Fetches all exam scores from the database as a simple Python list."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM grades;")
    scores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return scores

def calculate_mean(numbers):
    """Mean = sum of all numbers / count of numbers"""
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def calculate_median(numbers):
    """Median = Middle value in a sorted list."""
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
    else:
        return sorted_numbers[mid]

def calculate_mode(numbers):
    """Mode = Most frequently occurring number in the list."""
    frequency = {}
    for num in numbers:
        if num in frequency:
            frequency[num] += 1
        else:
            frequency[num] = 1
            
    max_count = 0
    mode_value = None
    for num, count in frequency.items():
        if count > max_count:
            max_count = count
            mode_value = num
    return mode_value

def calculate_range(numbers):
    """Range = Maximum value - Minimum value"""
    max_val = numbers[0]
    min_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
        if num < min_val:
            min_val = num
    return max_val - min_val

def calculate_std_dev(numbers, mean_val):
    """Calculates sample standard deviation manually."""
    if len(numbers) <= 1:
        return 0.0
    squared_diffs = sum((x - mean_val) ** 2 for x in numbers)
    variance = squared_diffs / (len(numbers) - 1)
    return math.sqrt(variance)

def display_statistics():
    """Computes and prints descriptive stats in the console."""
    scores = get_all_scores()
    if not scores:
        print("No grade data available.")
        return

    mean_val = calculate_mean(scores)
    median_val = calculate_median(scores)
    mode_val = calculate_mode(scores)
    range_val = calculate_range(scores)
    std_dev_val = calculate_std_dev(scores, mean_val)

    print("\n" + "-"*40)
    print("      BASIC EXAM GRADE STATISTICS")
    print("-"*40)
    print(f"Total Grades Evaluated : {len(scores)}")
    print(f"Mean (Average Score)   : {mean_val:.2f}%")
    print(f"Median (Middle Score)  : {median_val:.2f}%")
    print(f"Mode (Most Common)     : {mode_val}%")
    print(f"Range (Max - Min Score): {range_val}%")
    print(f"Standard Deviation     : {std_dev_val:.3f}")
    print("-"*40 + "\n")

# =====================================================================
# 4. CORRELATION & PREDICTIVE MODEL (Manual Linear Regression)
# =====================================================================
def get_habit_lists():
    """Returns lists of study hours, attendance, and scores for analysis."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = """
        SELECT s.study_hours, g.attendance, g.score 
        FROM grades g
        INNER JOIN students s ON g.student_id = s.student_id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    study_hours = [row[0] for row in rows]
    attendance = [row[1] for row in rows]
    scores = [row[2] for row in rows]
    
    return study_hours, attendance, scores

def calculate_pearson_r(x, y):
    """
    Calculates Pearson Correlation Coefficient (r) manually.
    r = sum((x - mean_x) * (y - mean_y)) / sqrt(sum((x - mean_x)^2) * sum((y - mean_y)^2))
    """
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)

    numerator = 0
    sum_sq_x = 0
    sum_sq_y = 0

    for i in range(len(x)):
        diff_x = x[i] - mean_x
        diff_y = y[i] - mean_y
        numerator += diff_x * diff_y
        sum_sq_x += diff_x ** 2
        sum_sq_y += diff_y ** 2

    denominator = math.sqrt(sum_sq_x * sum_sq_y)
    if denominator == 0:
        return 0.0
    return numerator / denominator

def display_insights():
    """Prints Pearson r correlation coefficients and explains what they mean."""
    study_hours, attendance, scores = get_habit_lists()
    
    r_study = calculate_pearson_r(study_hours, scores)
    r_attendance = calculate_pearson_r(attendance, scores)

    print("\n" + "-"*55)
    print("      CORRELATION ANALYSIS & STUDY INSIGHTS (KAGGLE DATA)")
    print("-"*55)
    print(f"1. Study Hours vs. Exam Grade (r)   : {r_study:.4f}")
    print(f"2. Class Attendance vs. Exam Grade (r): {r_attendance:.4f}")
    print("-"*55)
    print("EXPLANATION OF RESULTS (For Your Project Viva):")
    print("- A correlation close to +1.0 represents a strong positive relation.")
    print(f"- Since Study Hours vs Score has a correlation of {r_study:.2f}, it proves")
    print("  that students who study more get higher exam marks.")
    print(f"- Class Attendance correlation is {r_attendance:.2f}, proving that")
    print("  attending classes regularly strongly impacts performance.")
    print("-"*55 + "\n")

def predict_grade():
    """
    Manual Linear Regression: y = mx + c to predict exam scores.
    m = r * (std_dev_y / std_dev_x)
    c = mean_y - m * mean_x
    """
    study_hours, _, scores = get_habit_lists()

    mean_x = calculate_mean(study_hours)
    mean_y = calculate_mean(scores)

    std_x = calculate_std_dev(study_hours, mean_x)
    std_y = calculate_std_dev(scores, mean_y)

    r = calculate_pearson_r(study_hours, scores)

    if std_x == 0:
        print("Cannot calculate regression. Standard deviation of X is 0.")
        return

    # Calculate slope (m) and intercept (c)
    m = r * (std_y / std_x)
    c = mean_y - (m * mean_x)

    print("\n" + "-"*55)
    print("      PREDICTIVE MODEL: LINEAR REGRESSION (y = mx + c)")
    print("-"*55)
    print(f"Equation: Exam Score = ({m:.3f} * Study Hours) + {c:.3f}")
    print(f"Pearson Correlation (r): {r:.4f}")
    print("-"*55)

    try:
        user_input = input("Enter weekly study hours (0 to 24): ").strip()
        hours = float(user_input)
        if hours < 0 or hours > 24:
            print("Please enter a valid study duration between 0 and 24 hours.")
            return

        # Linear Equation prediction
        predicted_score = (m * hours) + c
        # Clamp score between 0% and 100%
        predicted_score = min(100.0, max(0.0, predicted_score))

        print(f"\nPREDICTED EXAM SCORE: {predicted_score:.2f}%")
        
        # Advisory insights based on predicted score
        if predicted_score >= 85:
            print("Study Recommendation: Excellent! You are on track for an A Grade.")
        elif predicted_score >= 60:
            print("Study Recommendation: Satisfactory. Increase study time to secure a B Grade.")
        else:
            print("Study Recommendation: Critical warning! Increase study time to avoid failing grades.")
        print("-" * 55 + "\n")

    except ValueError:
        print("Error: Please enter a valid decimal number.")
        print("-" * 55 + "\n")

# =====================================================================
# 5. USER INTERACTIVE MENU
# =====================================================================
def main():
    print("Setting up student database from Kaggle...")
    try:
        setup_database()
        print("Database successfully initialized with Kaggle dataset!")
    except Exception as e:
        print(f"Fatal error initializing database: {e}")
        return

    while True:
        print("=========================================")
        print("     STUDENT PERFORMANCE ANALYSIS        ")
        print("=========================================")
        print("1. View Student Grade Sheets (SQL Join)")
        print("2. View Course Standings & Rankings (SQL RANK)")
        print("3. Calculate Basic Stats (Mean, Median, Mode)")
        print("4. View Habits vs Grades Insights (Correlation)")
        print("5. Predict Student Grade (Linear Regression Model)")
        print("6. Exit")
        print("=========================================")
        
        choice = input("Enter option (1-6): ").strip()
        
        if choice == "1":
            view_student_report()
        elif choice == "2":
            view_course_standings()
        elif choice == "3":
            display_statistics()
        elif choice == "4":
            display_insights()
        elif choice == "5":
            predict_grade()
        elif choice == "6":
            print("\nExiting project. Thank you!")
            break
        else:
            print("\nInvalid choice! Please select an option between 1 and 6.\n")

if __name__ == "__main__":
    main()
