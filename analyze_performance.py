"""
analyze_performance.py
----------------------
This is the core analysis script for the Student Performance Analysis project.
It accomplishes the following:
1. Connects to the SQLite database 'student_records.db'.
2. Queries the tables using SQL to load data into Pandas DataFrames.
3. Computes descriptive statistics (Mean, Median, Mode, Variance, Std Dev) using
   both standard Pandas methods and custom manual algorithms to highlight the math.
4. Computes Pearson Correlation Coefficients (both manually and using Pandas).
5. Generates three highly-polished charts inside the 'plots' folder:
   - Score Distribution (Histogram + Kernel Density Estimate)
   - Average Score per Course (Bar Chart)
   - Study Hours vs. Score (Scatter Plot with linear regression fit line)
6. Outputs a comprehensive, beautifully styled report dashboard directly in the console.
"""

import sqlite3
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure modern, clean plots using Seaborn style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16
})

DB_NAME = "student_records.db"
PLOTS_DIR = "plots"

# Create plots directory if it does not exist
if not os.path.exists(PLOTS_DIR):
    os.makedirs(PLOTS_DIR)

# =====================================================================
# 1. CUSTOM STATISTICAL FUNCTIONS (Manual Calculations)
# Perfect for a student project to demonstrate understanding of formulas!
# =====================================================================

def calculate_mean(values):
    """Formula: sum(x) / N"""
    return sum(values) / len(values) if values else 0.0

def calculate_median(values):
    """Formula: Middle value when sorted. If even, average of middle two."""
    if not values:
        return 0.0
    sorted_val = sorted(values)
    n = len(sorted_val)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_val[mid - 1] + sorted_val[mid]) / 2.0
    return sorted_val[mid]

def calculate_mode(values):
    """Formula: Most frequently occurring value(s)."""
    if not values:
        return None
    counts = {}
    for v in values:
        # Round to integers for scores to make a meaningful mode
        rounded_v = round(v)
        counts[rounded_v] = counts.get(rounded_v, 0) + 1
    
    max_count = max(counts.values())
    modes = [val for val, count in counts.items() if count == max_count]
    # Return the first mode or a string of modes if multiple
    return modes[0] if len(modes) == 1 else modes

def calculate_variance(values, mean_val, is_sample=True):
    """Formula: sum((x - mean)^2) / (N - 1) for sample"""
    if len(values) <= 1:
        return 0.0
    squared_diff_sum = sum((x - mean_val) ** 2 for x in values)
    denominator = len(values) - 1 if is_sample else len(values)
    return squared_diff_sum / denominator

def calculate_std_deviation(variance_val):
    """Formula: sqrt(variance)"""
    return math.sqrt(variance_val)

def calculate_pearson_correlation(x, y):
    """
    Formula: Covariance(x,y) / (StdDev(x) * StdDev(y))
    Which translates to: sum((x - x_mean)*(y - y_mean)) / sqrt(sum((x - x_mean)^2) * sum((y - y_mean)^2))
    """
    if len(x) != len(y) or len(x) == 0:
        return 0.0
    
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)
    
    num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
    den_x = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
    den_y = sum((y[i] - mean_y) ** 2 for i in range(len(y)))
    
    denominator = math.sqrt(den_x * den_y)
    if denominator == 0:
        return 0.0
    return num / denominator

# =====================================================================
# 2. DATA EXTRACTION & ANALYSIS
# =====================================================================

def fetch_data():
    """Connects to SQL database and extracts data using SQL queries."""
    if not os.path.exists(DB_NAME):
        raise FileNotFoundError(f"Database '{DB_NAME}' not found! Please run setup_database.py first.")

    conn = sqlite3.connect(DB_NAME)
    
    # Query 1: Extract all grades alongside student demographics
    grades_query = """
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
        INNER JOIN courses c ON g.course_id = c.course_id;
    """
    df_grades = pd.read_sql_query(grades_query, conn)
    
    # Query 2: Extract course-wise performance stats from SQL to compare with Python stats
    course_summary_query = """
        SELECT 
            c.course_name,
            COUNT(g.student_id) AS enrolled_students,
            AVG(g.score) AS avg_score,
            MAX(g.score) AS max_score,
            MIN(g.score) AS min_score
        FROM grades g
        INNER JOIN courses c ON g.course_id = c.course_id
        GROUP BY c.course_name;
    """
    df_course_summary = pd.read_sql_query(course_summary_query, conn)
    
    conn.close()
    return df_grades, df_course_summary

def generate_plots(df_grades, df_course_summary):
    """Generates three publication-quality visualizations for the project."""
    print("Generating statistical plots...")

    # Plot 1: Grade/Score Distribution
    plt.figure(figsize=(8, 5))
    # Custom colored histogram with a clean KDE line
    sns.histplot(df_grades['score'], kde=True, bins=15, color="#4a90e2", edgecolor="white", alpha=0.8)
    
    mean_val = df_grades['score'].mean()
    median_val = df_grades['score'].median()
    
    # Add vertical indicator lines for Mean and Median
    plt.axvline(mean_val, color="red", linestyle="--", linewidth=1.5, label=f"Mean: {mean_val:.1f}")
    plt.axvline(median_val, color="green", linestyle="-.", linewidth=1.5, label=f"Median: {median_val:.1f}")
    
    plt.title("Distribution of Student Exam Scores", pad=15)
    plt.xlabel("Exam Score (0 - 100)")
    plt.ylabel("Number of Grade Records")
    plt.legend(frameon=True, facecolor="white", edgecolor="none")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "score_distribution.png"), dpi=150)
    plt.close()

    # Plot 2: Average Scores by Course
    plt.figure(figsize=(9, 5.5))
    # Order by average score
    df_sorted = df_course_summary.sort_values(by="avg_score", ascending=False)
    # Using a elegant palette
    barplot = sns.barplot(
        x="course_name", 
        y="avg_score", 
        data=df_sorted, 
        palette="viridis",
        hue="course_name",
        legend=False
    )
    
    # Add values on top of the bars
    for p in barplot.patches:
        barplot.annotate(
            format(p.get_height(), '.1f'), 
            (p.get_x() + p.get_width() / 2., p.get_height() - 6), 
            ha='center', va='center', 
            xytext=(0, 9), 
            textcoords='offset points', 
            color='white', fontweight='bold', fontsize=11
        )
        
    plt.title("Average Scores Across Courses", pad=15)
    plt.xlabel("Course Name")
    plt.ylabel("Average Score (out of 100)")
    plt.ylim(0, 110)  # Expand slightly to fit labels nicely
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "course_performance.png"), dpi=150)
    plt.close()

    # Plot 3: Scatter Plot of Study Hours vs. Score (with Trendline)
    plt.figure(figsize=(8, 5.5))
    # Calculate Pearson Correlation for visual legend
    r_corr = df_grades['study_hours_per_week'].corr(df_grades['score'])
    
    # Plot scatter points with transparency to handle overlaps
    sns.scatterplot(
        x="study_hours_per_week", 
        y="score", 
        hue="gender", 
        style="gender",
        data=df_grades, 
        palette={"Male": "#3498db", "Female": "#e74c3c"},
        s=60, 
        alpha=0.85
    )
    
    # Add Trendline using polyfit
    x = df_grades['study_hours_per_week']
    y = df_grades['score']
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b, color='#2c3e50', linestyle='-', linewidth=2, label=f"Trendline (r = {r_corr:.2f})")
    
    plt.title("Correlation: Weekly Study Hours vs. Exam Scores", pad=15)
    plt.xlabel("Weekly Study Hours")
    plt.ylabel("Exam Score")
    plt.legend(frameon=True, facecolor="white", loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "study_hours_vs_score.png"), dpi=150)
    plt.close()

    print(f"All plots successfully generated and saved to the '{PLOTS_DIR}/' directory!")

# =====================================================================
# 3. REPORT GENERATION AND DASHBOARD PRINTING
# =====================================================================

def display_dashboard(df_grades, df_course_summary):
    # Perform standard pandas statistics
    scores_series = df_grades['score']
    
    # Extract native Python lists for manual calculations
    scores_list = scores_series.tolist()
    study_hours_list = df_grades['study_hours_per_week'].tolist()
    attendance_list = df_grades['attendance_rate'].tolist()

    # Calculate statistics manually
    m_mean = calculate_mean(scores_list)
    m_median = calculate_median(scores_list)
    m_mode = calculate_mode(scores_list)
    m_variance = calculate_variance(scores_list, m_mean, is_sample=True)
    m_std = calculate_std_deviation(m_variance)
    
    # Correlation coefficients
    corr_study = calculate_pearson_correlation(study_hours_list, scores_list)
    corr_attend = calculate_pearson_correlation(attendance_list, scores_list)

    # Let's verify with pandas to show matching values
    pd_mean = scores_series.mean()
    pd_std = scores_series.std()
    pd_corr_study = df_grades['study_hours_per_week'].corr(df_grades['score'])

    print("\n" + "="*80)
    print("                    STUDENT PERFORMANCE ANALYSIS DASHBOARD                     ")
    print("="*80)
    
    # Print general database counts
    print(f"Dataset Size: {len(df_grades)} Grade Sheets from {df_grades['student_id'].nunique()} unique Students")
    print(f"Evaluated Courses: {', '.join(df_course_summary['course_name'].tolist())}")
    print("-"*80)
    
    # SECTION A: Central Tendency
    print("   SECTION A: MEASURES OF CENTRAL TENDENCY (EXAM SCORES)")
    print("-"*80)
    print(f"   Metric            | Manual Calculation  | Python Pandas Method")
    print(f"   ------------------+---------------------+---------------------")
    print(f"   Mean (Average)    | {m_mean:<19.3f} | {pd_mean:<19.3f}")
    print(f"   Median (Middle)   | {m_median:<19.3f} | {scores_series.median():<19.3f}")
    print(f"   Mode (Most Common)| {str(m_mode):<19} | {scores_series.round().mode()[0]:<19.3f} (rounded)")
    print("-"*80)

    # SECTION B: Dispersion
    print("   SECTION B: MEASURES OF DISPERSION (EXAM SCORES)")
    print("-"*80)
    print(f"   Metric            | Manual Calculation  | Python Pandas Method")
    print(f"   ------------------+---------------------+---------------------")
    print(f"   Range (Max - Min) | {max(scores_list) - min(scores_list):<19.1f} | {(scores_series.max() - scores_series.min()):<19.1f}")
    print(f"   Variance          | {m_variance:<19.3f} | {scores_series.var():<19.3f}")
    print(f"   Standard Deviation| {m_std:<19.3f} | {pd_std:<19.3f}")
    print("-"*80)

    # SECTION C: Correlation Analysis
    print("   SECTION C: CORRELATION ANALYSIS (PEARSON'S r)")
    print("-"*80)
    print("   Analyzing relations between habits and grades (Range: -1.0 to +1.0):")
    print(f"   - Study Hours vs. Exam Score  : {corr_study:.4f} (Pandas: {pd_corr_study:.4f})")
    print(f"   - Attendance Rate vs. Exam Score: {corr_attend:.4f} (Pandas: {df_grades['attendance_rate'].corr(df_grades['score']):.4f})")
    
    # Interpretations
    print("\n   INSIGHTS & STATISTICAL INTERPRETATIONS:")
    
    if corr_study > 0.7:
        print("   -> [STUDY HABITS] Study Hours show a VERY STRONG positive correlation with student scores.")
        print("      Students who allocate more weekly study time score consistently higher.")
    elif corr_study > 0.4:
        print("   -> [STUDY HABITS] Study Hours show a MODERATE positive correlation with student scores.")
    else:
        print("   -> [STUDY HABITS] Study Hours show weak correlation with student scores.")
        
    if corr_attend > 0.5:
        print("   -> [ATTENDANCE] Regular Class Attendance is also STRONGLY correlated with academic success.")
        print("      Higher attendance rates strongly predict stronger grades.")

    # SECTION D: SQL Aggregated Course Summary
    print("\n" + "-"*80)
    print("   SECTION D: COURSE-WISE SUMMARY STATISTICS (EXTRACTED VIA SQL)")
    print("-"*80)
    print(f"   Course Name          | Enrolled Students | Avg Score | Max Score | Min Score")
    print(f"   ---------------------+-------------------+-----------+-----------+-----------")
    for _, row in df_course_summary.iterrows():
        print(f"   {row['course_name']:<20} | {int(row['enrolled_students']):<17} | {row['avg_score']:<9.2f} | {row['max_score']:<9.1f} | {row['min_score']:<9.1f}")
    print("="*80 + "\n")

def main():
    print("Starting Student Performance Analysis...")
    try:
        # 1. Fetch data from SQLite using SQL queries
        df_grades, df_course_summary = fetch_data()
        
        # 2. Print beautiful ASCII stats report in the console
        display_dashboard(df_grades, df_course_summary)
        
        # 3. Generate high-quality visual plots
        generate_plots(df_grades, df_course_summary)
        
    except FileNotFoundError as e:
        print(f"[ERROR] Error: {e}")
        print("Please ensure that you have run 'setup_database.py' first to create the dataset.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
