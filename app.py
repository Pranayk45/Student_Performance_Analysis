"""
app.py
------
This is the Streamlit-based web dashboard for the Student Performance Analysis project.
It provides a simple, clean, and highly interactive graphical interface where users can:
1. Filter students dynamically by gender and weekly study hours.
2. View real-time metric cards for student counts, average scores, and class attendance.
3. See live, interactive charts that update instantly based on sidebar filters.
4. Compare key statistical metrics.
5. Write and execute custom SQL queries directly from the web browser!
"""

import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set webpage browser tab title and favicon
st.set_page_config(page_title="Student Performance Dashboard", page_icon="🎓", layout="wide")

DB_NAME = "student_records.db"

# Helper function to connect to SQLite
def get_db_connection():
    if not os.path.exists(DB_NAME):
        st.error(f"Error: '{DB_NAME}' not found! Please run 'setup_database.py' first to generate your data.")
        st.stop()
    conn = sqlite3.connect(DB_NAME)
    return conn

# =====================================================================
# HEADER SECTION
# =====================================================================
st.title("🎓 Student Performance Analytics Dashboard")
st.write("An interactive web dashboard analyzing the correlation between class attendance, weekly study hours, and exam scores.")
st.markdown("---")

# =====================================================================
# SIDEBAR FILTERS (Interactive controls)
# =====================================================================
st.sidebar.header("🔍 Filter Options")
st.sidebar.write("Adjust filters to update all stats, data, and charts in real-time.")

# 1. Gender Filter
gender_opt = st.sidebar.selectbox("Select Gender:", ["All", "Male", "Female"])

# 2. Study Hours Filter
min_study_hours = st.sidebar.slider(
    "Minimum Weekly Study Hours:", 
    min_value=0.0, 
    max_value=22.0, 
    value=0.0, 
    step=0.5
)

# =====================================================================
# LOAD FILTERED DATA USING SQL
# =====================================================================
conn = get_db_connection()

# Construct standard SQL query based on user's sidebar filters
query = """
    SELECT 
        s.student_id,
        s.name,
        s.age,
        s.gender,
        s.study_hours_per_week,
        c.course_name,
        g.score,
        g.attendance_rate
    FROM grades g
    INNER JOIN students s ON g.student_id = s.student_id
    INNER JOIN courses c ON g.course_id = c.course_id
    WHERE s.study_hours_per_week >= ?
"""
params = [min_study_hours]

if gender_opt != "All":
    query += " AND s.gender = ?"
    params.append(gender_opt)

df_filtered = pd.read_sql_query(query, conn, params=params)
conn.close()

# =====================================================================
# KPI METRIC CARDS
# =====================================================================
if df_filtered.empty:
    st.warning("No student records match the selected filters. Try loosening your sidebar controls.")
else:
    # Compute quick stats
    total_records = len(df_filtered)
    unique_students = df_filtered["student_id"].nunique()
    avg_score = df_filtered["score"].mean()
    avg_attendance = df_filtered["attendance_rate"].mean()

    # Render metric cards side-by-side
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Unique Students", unique_students)
    col2.metric("Total Grade Records", total_records)
    col3.metric("Average Exam Score", f"{avg_score:.2f}%")
    col4.metric("Average Attendance", f"{avg_attendance:.2f}%")
    st.markdown("---")

    # =====================================================================
    # LAYOUT TABS (Keeps the page clean and simple!)
    # =====================================================================
    tab1, tab2, tab3 = st.tabs(["📊 Interactive Analysis & Charts", "📋 Statistical Laboratory", "💻 SQL Playground"])

    # -----------------------------------------------------------------
    # TAB 1: INTERACTIVE CHARTS
    # -----------------------------------------------------------------
    with tab1:
        st.subheader("Visual Data Insights")
        st.write("These charts adjust dynamically based on the filters in your sidebar.")

        col_left, col_right = st.columns(2)

        # Chart 1: Average score per course
        with col_left:
            st.write("##### Average Score per Course")
            # Group by course name in pandas
            course_avg = df_filtered.groupby("course_name")["score"].mean().reset_index().sort_values(by="score", ascending=False)
            
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(x="course_name", y="score", data=course_avg, palette="viridis", hue="course_name", legend=False, ax=ax)
            ax.set_xlabel("Course")
            ax.set_ylabel("Average Score (%)")
            ax.set_ylim(0, 100)
            plt.xticks(rotation=20, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

        # Chart 2: Study Hours vs. Score Scatter Plot
        with col_right:
            st.write("##### Study Hours vs. Exam Score (Trendline)")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.scatterplot(x="study_hours_per_week", y="score", hue="gender", data=df_filtered, palette={"Male": "#3498db", "Female": "#e74c3c"}, s=40, alpha=0.8, ax=ax)
            
            # Draw a simple linear fit line if we have enough points
            if len(df_filtered) > 1:
                x_vals = df_filtered["study_hours_per_week"]
                y_vals = df_filtered["score"]
                m, b = np.polyfit(x_vals, y_vals, 1)
                ax.plot(x_vals, m*x_vals + b, color='#2c3e50', linestyle='-', linewidth=2, label="Trendline")
            
            ax.set_xlabel("Weekly Study Hours")
            ax.set_ylabel("Exam Score (%)")
            ax.set_ylim(0, 105)
            plt.tight_layout()
            st.pyplot(fig)

        st.subheader("Raw Data Preview")
        st.write("Showing records loaded from SQLite database matching your sidebar selections:")
        st.dataframe(df_filtered[["name", "age", "gender", "study_hours_per_week", "course_name", "score", "attendance_rate"]], use_container_width=True)

    # -----------------------------------------------------------------
    # TAB 2: STATISTICAL LABORATORY
    # -----------------------------------------------------------------
    with tab2:
        st.subheader("Descriptive Statistics Dashboard")
        st.write("A summary of mathematical indicators derived from the current filtered student list.")

        # Calculate statistics
        scores = df_filtered["score"]
        
        stat_data = {
            "Statistical Metric": [
                "Mean (Average Grade)",
                "Median (Middle Grade)",
                "Minimum Grade Score",
                "Maximum Grade Score",
                "Standard Deviation (Grade Spread)",
                "Variance",
                "Study Hours vs. Score Correlation (Pearson's r)"
            ],
            "Current Value": [
                f"{scores.mean():.3f}%",
                f"{scores.median():.3f}%",
                f"{scores.min():.1f}%",
                f"{scores.max():.1f}%",
                f"{scores.std():.3f}",
                f"{scores.var():.3f}",
                f"{df_filtered['study_hours_per_week'].corr(scores):.4f}"
            ],
            "What this means for a Fresher Project": [
                "The typical score obtained by this group of students.",
                "The score that splits the class exactly in half.",
                "The lowest recorded grade in this filtered group.",
                "The highest recorded grade in this filtered group.",
                "How much the scores deviate or spread out from the average score.",
                "The average of the squared differences from the Mean.",
                "Shows relation (close to +1.0 = positive impact; close to 0.0 = no impact)."
            ]
        }
        
        st.table(pd.DataFrame(stat_data))
        
        # Educational explanation box
        st.info(
            "💡 **Statistical Tip for your Project Viva:** Pearson's $r$ is a measurement of relation. "
            "Our data shows that **Study Hours** and **Class Attendance** have a strong positive correlation with final grades. "
            "This mathematically proves that students who attend classes and study more are statistically highly likely to score better marks!"
        )

    # -----------------------------------------------------------------
    # TAB 3: SQL PLAYGROUND (Teacher / Student interactive query runner)
    # -----------------------------------------------------------------
    with tab3:
        st.subheader("💻 Interactive SQL Query Playground")
        st.write(
            "Test and run any SQL command directly against your `student_records.db` database. "
            "Type a query in the box below and click **Execute Query**."
        )
        
        # Default starter SQL query
        default_query = (
            "-- Find the top 10 students by their study hours\n"
            "SELECT name, age, gender, study_hours_per_week\n"
            "FROM students\n"
            "ORDER BY study_hours_per_week DESC\n"
            "LIMIT 10;"
        )
        
        sql_input = st.text_area("Write your SQL Query here:", value=default_query, height=150)
        
        if st.button("🚀 Execute Query", type="primary"):
            try:
                # Run query
                conn = get_db_connection()
                query_result_df = pd.read_sql_query(sql_input, conn)
                conn.close()
                
                # Check for empty results
                if query_result_df.empty:
                    st.info("Query executed successfully, but returned 0 rows.")
                else:
                    st.success(f"Successfully retrieved {len(query_result_df)} rows!")
                    st.dataframe(query_result_df, use_container_width=True)
                    
            except Exception as e:
                st.error(f"SQL Error: {e}")
                st.info("💡 Hint: Ensure you are referencing existing tables: `students`, `courses`, or `grades`.")
