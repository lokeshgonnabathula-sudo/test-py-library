"""
init_db.py
Run this ONCE to create library.db and load the sample dataset.
Usage: python init_db.py
"""
import sqlite3
import csv
import os

# BASE_DIR = the folder this script lives in, no matter where you run it FROM
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "library.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
CSV_PATH = os.path.join(BASE_DIR, "books_dataset.csv")

def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create tables from schema.sql
    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())

    # Load books from CSV dataset
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total = int(row["total_copies"])
            cursor.execute("""
                INSERT INTO books (title, author, genre, isbn, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (row["title"], row["author"], row["genre"], row["isbn"], total, total))

    # Add a couple of sample members so you can test borrowing right away
    sample_members = [
        ("Ravi Kumar", "ravi.kumar@example.com", "9876543210"),
        ("Priya Sharma", "priya.sharma@example.com", "9123456780"),
    ]
    cursor.executemany("""
        INSERT INTO members (name, email, phone) VALUES (?, ?, ?)
    """, sample_members)

    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' created and loaded with sample data successfully.")

if __name__ == "__main__":
    init_database()
