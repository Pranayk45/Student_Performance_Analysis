# Power BI Dashboard Setup Guide

This guide walks you through building a professional, interactive **Student Performance Dashboard** in Power BI Desktop using the CSV data exported from your SQLite database.

---

## 🛠️ Step 1: Export Your Database to CSV
Before opening Power BI, you need to extract the data from SQLite into clean CSV files.

1. Open your Command Prompt/PowerShell.
2. Go to the project folder:
   ```cmd
   cd C:\Users\HP\.gemini\antigravity\scratch\student_performance_analysis
   ```
3. Run the exporter script:
   ```cmd
   python export_for_powerbi.py
   ```
   *This will create a new folder named `powerbi_data/` containing two files: `students.csv` and `grades.csv`.*

---

## 📊 Step 2: Import the Data into Power BI Desktop
1. Open **Power BI Desktop** (free to download from the Microsoft Store).
2. On the Home ribbon, click **Get Data** -> select **Text/CSV**.
3. Navigate to your project folder, open `powerbi_data/`, select **`students.csv`**, and click **Open**.
4. In the preview window, click **Load**.
5. Repeat the process: Click **Get Data** -> **Text/CSV** -> select **`grades.csv`** -> click **Load**.

---

## 🔗 Step 3: Link the Tables (Data Modeling)
To ensure filters work across both tables, we must define the relationship.

1. On the far-left sidebar of Power BI, click the **Model View** icon (the third icon, which looks like three boxes connected by lines).
2. You will see two boxes representing your tables: `students` and `grades`.
3. Click and hold the **`student_id`** column in the `students` table, drag it, and drop it directly onto the **`student_id`** column in the `grades` table.
4. Power BI will automatically create a **1-to-Many (1:*) relationship** (represented by a line with a `1` on the student side and a `*` on the grades side).

---

## 🎨 Step 4: Build Your Dashboard Visuals
Click the **Report View** icon (the first icon on the left sidebar) to open your blank canvas.

### 1. Header (Project Title)
*   On the Home ribbon, click **Text Box**.
*   Type: `"Student Performance Analysis Dashboard"`.
*   Style: Font size **24**, **Bold**, centered.

### 2. KPI Cards (Quick Statistics)
*   **Total Students Card:**
    *   Click the **Card** visual (in the Visualizations pane, it looks like a box with `123`).
    *   Drag **`student_id`** from the `students` table into the "Fields" bucket.
    *   Click the down-arrow next to `student_id` in the bucket and select **Count (Distinct)**.
    *   Rename the visual title or label to `Total Students`.
*   **Average Score Card:**
    *   Create another **Card** visual.
    *   Drag **`score`** from the `grades` table into the Fields bucket.
    *   Click the down-arrow next to `score` and change the aggregation to **Average**.
    *   Format as percentage (decimal place = 1).
*   **Average Attendance Card:**
    *   Create a third **Card** visual.
    *   Drag **`attendance`** from the `grades` table into the Fields bucket and set aggregation to **Average**.

### 3. Slicer Filter (Interactive Controls)
*   Click the **Slicer** visual (looks like a funnel on a sheet of paper).
*   Drag **`gender`** from the `students` table into the Field bucket.
*   *Now, clicking "Male" or "Female" on the slicer will instantly filter all cards and charts on the page!*

### 4. Bar Chart (Course Performance)
*   Click the **Clustered Column Chart** visual (vertical bar chart).
*   Drag **`course_name`** from the `grades` table into the **X-axis** bucket.
*   Drag **`score`** from the `grades` table into the **Y-axis** bucket, and set it to **Average**.
*   *This will display a bar chart comparing the average score of each subject.*

### 5. Scatter Plot with Trendline (Study Hours Correlation)
*   Click the **Scatter Chart** visual.
*   Drag **`study_hours`** from the `students` table into the **X-axis** bucket.
*   Drag **`score`** from the `grades` table into the **Y-axis** bucket, and set it to **Average**.
*   Drag **`name`** from the `students` table into the **Values** or **Details** bucket.
*   **Add Trendline (The Magic Step):**
    *   With the Scatter Chart selected, click the **Format visual** paint-roller icon, then switch to the **Analytics** pane (icon looks like a magnifying glass with a line).
    *   Expand the **Trend line** section and click **Add**.
    *   Set the color to dark blue or red.
    *   *This shows your evaluators the clear mathematical positive correlation between study habits and exam marks!*

---

## 🎯 Tips for an A+ Student Project Presentation
*   **Theme Selection:** Go to the **View** ribbon and choose a modern, professional theme (like "Innovate" or "Executive" dark theme).
*   **Interactivity:** During your presentation, show your teachers how clicking a course name or a gender slicer dynamically recalculates the scatter trendline and averages.
