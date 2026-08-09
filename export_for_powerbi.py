"""
export_for_powerbi.py
---------------------
This script connects to your local SQLite database ('student_simple.db') 
and exports the tables into clean CSV files inside the 'powerbi_data/' folder.
These CSV files can be imported directly into Power BI Desktop for analysis.
"""

import sqlite3
import csv
import os

DB_NAME = "student_simple.db"
EXPORT_DIR = "powerbi_data"

def export_table_to_csv(cursor, table_name, csv_filename):
    """Utility function to query a table and export it to a CSV file."""
    # Query all columns from the table
    cursor.execute(f"SELECT * FROM {table_name};")
    
    # Get column headers
    headers = [description[0] for description in cursor.description]
    
    # Fetch all data rows
    rows = cursor.fetchall()
    
    # Full path to the CSV file
    file_path = os.path.join(EXPORT_DIR, csv_filename)
    
    # Write to CSV
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)  # Write headers
        writer.writerows(rows)    # Write data rows
        
    print(f"Exported table '{table_name}' -> '{file_path}' ({len(rows)} rows)")

def main():
    # 1. Check if database file exists
    if not os.path.exists(DB_NAME):
        print(f"❌ Error: Database file '{DB_NAME}' not found!")
        print("💡 Solution: Please run 'python simple_project.py' first to create and seed the database.")
        return

    # 2. Create the export folder if it doesn't exist
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        print(f"Folder '{EXPORT_DIR}/' created successfully.")

    # 3. Connect to SQLite database
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        print("\nStarting data extraction from SQLite...")
        print("-" * 50)
        
        # Export 'students' table
        export_table_to_csv(cursor, "students", "students.csv")
        
        # Export 'grades' table
        export_table_to_csv(cursor, "grades", "grades.csv")
        
        print("-" * 50)
        print("SUCCESS! Your CSV files are ready for Power BI.")
        print(f"Files are located in: {os.path.abspath(EXPORT_DIR)}")
        print("Next Step: Open Power BI Desktop and follow the steps in 'PowerBI_Guide.md'!")
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    main()
