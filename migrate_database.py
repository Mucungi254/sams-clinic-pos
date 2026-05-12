import sqlite3
import os

# Connect to the database
db_path = os.path.join('instance', 'sams_clinic_pos.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add new columns to sales table
new_columns = [
    "ALTER TABLE sales ADD COLUMN cash_amount REAL DEFAULT 0.0",
    "ALTER TABLE sales ADD COLUMN mpesa_amount REAL DEFAULT 0.0", 
    "ALTER TABLE sales ADD COLUMN amount_received REAL DEFAULT 0.0",
    "ALTER TABLE sales ADD COLUMN balance_given REAL DEFAULT 0.0",
    "ALTER TABLE sales ADD COLUMN mpesa_code TEXT"
]

for column_sql in new_columns:
    try:
        cursor.execute(column_sql)
        print("Added column successfully")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column already exists")
        else:
            print(f"Error: {e}")

conn.commit()
conn.close()
print("Database migration completed!")
