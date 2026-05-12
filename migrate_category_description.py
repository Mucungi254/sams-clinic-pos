import sqlite3
from datetime import datetime

def migrate_category_description():
    """Add description column to categories table"""
    conn = sqlite3.connect('instance/sams_clinic_pos.db')
    cursor = conn.cursor()
    
    try:
        # Check if description column already exists
        cursor.execute("PRAGMA table_info(categories)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'description' not in columns:
            print("Adding description column to categories table...")
            cursor.execute("ALTER TABLE categories ADD COLUMN description TEXT")
            conn.commit()
            print("Description column added successfully!")
        else:
            print("Description column already exists.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_category_description()
