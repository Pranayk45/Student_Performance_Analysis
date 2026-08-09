# Student Performance Analysis using Python, SQL, and Statistics

This is a comprehensive, educational, and end-to-end beginner-level project designed for fresher computer science or data science students. It demonstrates how to integrate **SQL databases (SQLite)**, **Python data engineering & analysis**, and **Core Statistics** to solve a real-world problem: analyzing how class attendance and weekly study hours affect students' exam scores.

---

## 🚀 Project Overview

In this project, we:
1. **Set up a SQLite Database:** Create a local schema (`students`, `courses`, and `grades`) using SQLite and populate it with 60 realistic students taking 5 different subjects.
2. **Write SQL Queries:** Study queries for table joins, demographic aggregations, and performance-based filtering.
3. **Write Python Analysis:** Fetch the data, perform central tendency, dispersion, and correlation analysis programmatically.
4. **Compare Methods:** Implement statistical equations manually in Python (so you can explain the mathematics to your teachers) and compare them with standard Python data libraries like **Pandas** and **NumPy**.
5. **Generate Visualizations:** Build beautiful, modern charts using **Matplotlib** and **Seaborn** to show performance distributions, averages per course, and correlation trends.

---

## 📁 Project Structure

```text
student_performance_analysis/
├── setup_database.py       # Initializes the SQLite DB and inserts synthetic data
├── analyze_performance.py  # Performs statistical analysis and generates plots
├── app.py                  # Interactive Streamlit Web Dashboard application
├── queries.sql             # SQL query workbook for study/practice
├── requirements.txt        # Third-party Python libraries
├── README.md               # Complete documentation (This file!)
├── student_records.db      # The generated database file (created by setup)
└── plots/                  # Visual charts output folder (created by analysis)
    ├── score_distribution.png
    ├── course_performance.png
    └── study_hours_vs_score.png
```

---

## 🛠️ Installation & Execution

### 1. Prerequisites
Make sure you have **Python 3.8+** installed. You can check your version in the terminal/command prompt:
```bash
python --version
```

### 2. Set Up the Project
Clone or copy these files into a folder of your choice (e.g. `student_performance_analysis/`), navigate to that directory, and run the following commands:

```bash
# Install the required data science packages
pip install -r requirements.txt
```

### 3. Initialize the Database
Run the setup script to create your SQLite database and generate the records:
```bash
python setup_database.py
```
*Expected Output:*
> Creating tables...  
> Tables created successfully!  
> Generating and inserting sample data...  
> Data insertion complete! SQLite database saved as 'student_records.db' with:  
>  - 5 Courses  
>  - 60 Students  
>  - 240 Grade Records  

### 4. Run the Statistical Analysis & Visualization
Run the analysis script to print the dashboard and save the plots:
```bash
python analyze_performance.py
```
*Expected Output:*  
A beautifully formatted console report listing Mean, Median, Mode, Standard Deviation, and Pearson Correlation Coefficients, followed by confirmation that charts are saved in the `plots/` folder.

### 5. Launch the Streamlit Web Dashboard
To view your data, statistics, and charts interactively inside your web browser, execute:
```bash
streamlit run app.py
```
*Expected Output:*  
Streamlit starts a local web server (usually at `http://localhost:8501`) and **automatically opens your web browser** directly to a simple, clean, and interactive performance dashboard!

---

## 🗄️ Database Architecture (SQL)

The SQLite database structure represents a standard relational database with Foreign Keys:

```text
┌─────────────────┐        ┌──────────────┐        ┌─────────────────┐
│    students     │        │    grades    │        │     courses     │
├─────────────────┤        ├──────────────┤        ├─────────────────┤
│ student_id (PK) │◄───────│ student_id   │───────►│ course_id (PK)  │
│ name            │        │ course_id    │        │ course_name     │
│ age             │        │ score        │        │ credits         │
│ gender          │        │ attendance   │        └─────────────────┘
│ study_hours     │        └──────────────┘
└─────────────────┘
```

- **`students`**: Keeps demographic details and the independent variable `study_hours_per_week`.
- **`courses`**: Details subjects and academic weights (`credits`).
- **`grades`**: A bridge table containing the dependent variables `score` (exam grade out of 100) and class `attendance_rate`.

---

## 🔍 SQL Queries Explained (from `queries.sql`)

Inside `queries.sql`, you will find key queries grouped by concept:

### 1. INNER JOIN (Linking Tables)
Combines data across multiple tables to display a complete report:
```sql
SELECT s.name, c.course_name, g.score, g.attendance_rate
FROM grades g
INNER JOIN students s ON g.student_id = s.student_id
INNER JOIN courses c ON g.course_id = c.course_id;
```

### 2. Aggregations & GROUP BY (Descriptive Stats in SQL)
Calculates averages and counts per course directly in the database:
```sql
SELECT 
    c.course_name,
    COUNT(g.student_id) AS enrolled_students,
    ROUND(AVG(g.score), 2) AS average_score,
    MAX(g.score) AS highest_score
FROM grades g
INNER JOIN courses c ON g.course_id = c.course_id
GROUP BY c.course_name;
```

### 3. Conditional Classification (CASE statements)
Converts raw numerical scores into letter grades:
```sql
SELECT s.name, g.score,
    CASE 
        WHEN g.score >= 90 THEN 'A'
        WHEN g.score >= 80 THEN 'B'
        WHEN g.score >= 70 THEN 'C'
        ELSE 'F'
    END AS grade_letter
FROM grades g
INNER JOIN students s ON g.student_id = s.student_id;
```

---

## 📈 Statistical Analysis Formulas & Python Implementation

To impress your project evaluators, this project computes statistics using **both** native Python logic (manually applying mathematical formulas) and the **Pandas** package.

### 1. Measures of Central Tendency
These metrics help pinpoint the center point of our academic data.

*   **Mean (Average):** The sum of all scores divided by the number of scores.
    $$\mu = \frac{\sum_{i=1}^{N} x_i}{N}$$
    *Manual Python implementation:* `sum(scores) / len(scores)`
*   **Median:** The middle value when the scores are sorted in order. If the count is even, it's the average of the two middle values.
    *Manual Python implementation:* Sorting the list and retrieving the middle index/indices.
*   **Mode:** The score that appears most frequently in our dataset.
    *Manual Python implementation:* Occurrences are counted using a hash map (dictionary).

### 2. Measures of Dispersion
These metrics describe how much the students' scores vary or are spread out from the average.

*   **Variance ($s^2$):** The average of the squared differences from the Mean.
    $$s^2 = \frac{\sum_{i=1}^{N} (x_i - \mu)^2}{N - 1}$$
*   **Standard Deviation ($s$):** The square root of the variance. It represents the standard spread of exam scores.
    $$s = \sqrt{\frac{\sum_{i=1}^{N} (x_i - \mu)^2}{N - 1}}$$

### 3. Correlation (Pearson's Correlation Coefficient - $r$)
Determines whether two variables (like study hours and test scores) move together. It ranges from **-1.0** (perfect negative correlation) to **+1.0** (perfect positive correlation), with **0.0** representing no relationship.

$$r = \frac{\sum (x - \bar{x})(y - \bar{y})}{\sqrt{\sum (x - \bar{x})^2 \sum (y - \bar{y})^2}}$$

*   **Positive Correlation:** As a student's study hours or class attendance increases, their exam score also increases.
*   **Negative Correlation:** If increasing one variable led to a decrease in the other.

---

## 📊 Visualizations Generated

The project produces three modern, stylish diagrams:
1.  **`score_distribution.png`**: Displays a bell-curve histogram outlining how grades spread across the student body, featuring dashed markers indicating the exact Mean and Median scores.
2.  **`course_performance.png`**: A clean, colorful bar chart showing which courses are producing the highest average performance.
3.  **`study_hours_vs_score.png`**: A scatter plot mapping individual students' study habits against their final exam scores. It features a **regression trendline** showing the exact positive correlation mathematically.

---

## 🎯 Key Learning Takeaways for Freshers

1.  **Relational Database Design:** Understand Primary Keys, Foreign Keys, table constraints, and relational normalization.
2.  **SQL-Python Interoperability:** Learn how Python programs connect to SQL databases using standard libraries like `sqlite3`.
3.  **Data Manipulation using Pandas:** Clean, filter, load, and compute metrics from data.
4.  **Math Translation:** Learn how to translate algebraic statistical formulas into readable Python functions.
5.  **Visual Storytelling:** Understand axes scaling, labels, grids, and trendlines in data visualization.
