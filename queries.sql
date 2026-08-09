-- =====================================================================
-- SQL Query Reference Sheet - Student Performance Analysis
-- =====================================================================
-- This file contains SQL queries that are highly relevant to student
-- projects, showing how to query, join, filter, and aggregate student records.
--
-- You can run these queries directly using SQLite.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Querying Basic Student Demographics
-- Shows basic selection, filtering, and ordering.
-- ---------------------------------------------------------------------

-- View the list of all students sorted by their study hours (highest first)
SELECT student_id, name, gender, age, study_hours_per_week 
FROM students 
ORDER BY study_hours_per_week DESC;

-- Filter students who are older than 20 and study more than 10 hours a week
SELECT name, age, study_hours_per_week 
FROM students 
WHERE age > 20 AND study_hours_per_week > 10.0;


-- ---------------------------------------------------------------------
-- 2. Inner Joins to Combine Student, Course, and Grade Information
-- Links records across all three tables using Foreign Key relationships.
-- ---------------------------------------------------------------------

-- Get a complete academic report card showing students, their courses, credits, scores, and attendance
SELECT 
    s.name AS student_name, 
    c.course_name, 
    c.credits, 
    g.score, 
    g.attendance_rate
FROM grades g
INNER JOIN students s ON g.student_id = s.student_id
INNER JOIN courses c ON g.course_id = c.course_id
ORDER BY s.name, c.course_name;


-- ---------------------------------------------------------------------
-- 3. Grouping and Aggregation (GROUP BY)
-- Derives statistical summaries directly inside the database.
-- ---------------------------------------------------------------------

-- Query: Average, Maximum, and Minimum score for each Course
SELECT 
    c.course_name,
    COUNT(g.student_id) AS enrolled_students,
    ROUND(AVG(g.score), 2) AS average_score,
    MAX(g.score) AS highest_score,
    MIN(g.score) AS lowest_score
FROM grades g
INNER JOIN courses c ON g.course_id = c.course_id
GROUP BY c.course_name
ORDER BY average_score DESC;

-- Query: Gender-wise performance summary (Average Study Hours, Score, and Attendance)
-- Helps analyze if gender correlates with study patterns or grades.
SELECT 
    s.gender,
    COUNT(DISTINCT s.student_id) AS total_students,
    ROUND(AVG(s.study_hours_per_week), 2) AS average_study_hours,
    ROUND(AVG(g.score), 2) AS average_score,
    ROUND(AVG(g.attendance_rate), 2) AS average_attendance
FROM grades g
INNER JOIN students s ON g.student_id = s.student_id
GROUP BY s.gender;


-- ---------------------------------------------------------------------
-- 4. Analytical Filtering (HAVING, Subqueries & CASE)
-- Handles complex queries for warning systems and performance evaluation.
-- ---------------------------------------------------------------------

-- Query: List students with poor class attendance (< 75%) and their average score
-- This is useful for identifying students at risk.
SELECT 
    s.name AS student_name,
    ROUND(AVG(g.attendance_rate), 1) AS overall_attendance,
    ROUND(AVG(g.score), 1) AS overall_average_score,
    COUNT(g.course_id) AS courses_taken
FROM grades g
INNER JOIN students s ON g.student_id = s.student_id
GROUP BY s.student_id
HAVING overall_attendance < 75.0
ORDER BY overall_attendance ASC;

-- Query: Top 5 performing students across all courses by their overall average grade
SELECT 
    s.name AS student_name,
    s.study_hours_per_week,
    ROUND(AVG(g.attendance_rate), 1) AS average_attendance,
    ROUND(AVG(g.score), 2) AS average_score
FROM grades g
INNER JOIN students s ON g.student_id = s.student_id
GROUP BY s.student_id
ORDER BY average_score DESC
LIMIT 5;

-- Query: Classify students into Grade Categories based on their scores
SELECT 
    s.name AS student_name,
    c.course_name,
    g.score,
    CASE 
        WHEN g.score >= 90 THEN 'A (Outstanding)'
        WHEN g.score >= 80 THEN 'B (Very Good)'
        WHEN g.score >= 70 THEN 'C (Good)'
        WHEN g.score >= 60 THEN 'D (Satisfactory)'
        WHEN g.score >= 50 THEN 'E (Pass)'
        ELSE 'F (Fail)'
    END AS grade_letter
FROM grades g
INNER JOIN students s ON g.student_id = s.student_id
INNER JOIN courses c ON g.course_id = c.course_id
LIMIT 20;

-- ---------------------------------------------------------------------
-- 5. Intermediate SQL: Window Functions (RANK() OVER)
-- Ranks students within each course group based on their scores.
-- ---------------------------------------------------------------------

-- Query: Rank students in each course group by score (highest first)
SELECT 
    g.course_name,
    s.name AS student_name,
    g.score,
    RANK() OVER (PARTITION BY g.course_name ORDER BY g.score DESC) as subject_rank
FROM grades g
INNER JOIN students s ON g.student_id = s.student_id
ORDER BY g.course_name, subject_rank;
