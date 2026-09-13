"""
app.py
Library Management System - Flask + SQLite

Routes:
  /                     -> Home: list all books (with search)
  /add_book             -> Add a new book (GET form, POST save)
  /members              -> List all members
  /add_member           -> Add a new member (GET form, POST save)
  /issue                -> Issue a book to a member (GET form, POST save)
  /return/<record_id>   -> Return a borrowed book
  /records              -> View all borrow records (who has what)
"""
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # needed for flash messages

# Always resolve the database next to this file, regardless of the
# folder you run "python app.py" from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "library.db")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, like a dict
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    conn = get_db_connection()

    if query:
        # Search by title OR author using SQL LIKE
        books = conn.execute("""
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ?
            ORDER BY title
        """, (f"%{query}%", f"%{query}%")).fetchall()
    else:
        books = conn.execute("SELECT * FROM books ORDER BY title").fetchall()

    conn.close()
    return render_template("index.html", books=books, query=query)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        genre = request.form.get("genre", "").strip()
        isbn = request.form.get("isbn", "").strip()
        copies = int(request.form.get("total_copies", 1))

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO books (title, author, genre, isbn, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, author, genre, isbn, copies, copies))
            conn.commit()
            flash(f'Book "{title}" added successfully!', "success")
        except sqlite3.IntegrityError:
            flash("A book with this ISBN already exists.", "error")
        finally:
            conn.close()
        return redirect(url_for("index"))

    return render_template("add_book.html")


@app.route("/members")
def members():
    conn = get_db_connection()
    all_members = conn.execute("SELECT * FROM members ORDER BY name").fetchall()
    conn.close()
    return render_template("members.html", members=all_members)


@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form.get("phone", "").strip()

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO members (name, email, phone) VALUES (?, ?, ?)
            """, (name, email, phone))
            conn.commit()
            flash(f'Member "{name}" registered successfully!', "success")
        except sqlite3.IntegrityError:
            flash("A member with this email already exists.", "error")
        finally:
            conn.close()
        return redirect(url_for("members"))

    return render_template("add_member.html")


@app.route("/issue", methods=["GET", "POST"])
def issue_book():
    conn = get_db_connection()

    if request.method == "POST":
        book_id = int(request.form["book_id"])
        member_id = int(request.form["member_id"])

        book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()

        if book is None:
            flash("Book not found.", "error")
        elif book["available_copies"] <= 0:
            # This check is the core business rule: can't issue a book with 0 copies left
            flash(f'No available copies of "{book["title"]}" right now.', "error")
        else:
            due_date = (date.today() + timedelta(days=14)).isoformat()
            conn.execute("""
                INSERT INTO borrow_records (book_id, member_id, due_date)
                VALUES (?, ?, ?)
            """, (book_id, member_id, due_date))
            conn.execute("""
                UPDATE books SET available_copies = available_copies - 1 WHERE id = ?
            """, (book_id,))
            conn.commit()
            flash(f'"{book["title"]}" issued successfully. Due back {due_date}.', "success")

        conn.close()
        return redirect(url_for("records"))

    # GET: show the issue form with dropdowns of books & members
    books = conn.execute("SELECT * FROM books WHERE available_copies > 0 ORDER BY title").fetchall()
    all_members = conn.execute("SELECT * FROM members ORDER BY name").fetchall()
    conn.close()
    return render_template("issue.html", books=books, members=all_members)


@app.route("/return/<int:record_id>", methods=["POST"])
def return_book(record_id):
    conn = get_db_connection()
    record = conn.execute("SELECT * FROM borrow_records WHERE id = ?", (record_id,)).fetchone()

    if record is None:
        flash("Borrow record not found.", "error")
    elif record["return_date"] is not None:
        flash("This book was already returned.", "error")
    else:
        conn.execute("""
            UPDATE borrow_records SET return_date = ? WHERE id = ?
        """, (date.today().isoformat(), record_id))
        conn.execute("""
            UPDATE books SET available_copies = available_copies + 1 WHERE id = ?
        """, (record["book_id"],))
        conn.commit()
        flash("Book marked as returned.", "success")

    conn.close()
    return redirect(url_for("records"))


@app.route("/records")
def records():
    conn = get_db_connection()
    # JOIN across 3 tables to show readable info instead of raw IDs
    all_records = conn.execute("""
        SELECT br.id, b.title, m.name AS member_name,
               br.borrow_date, br.due_date, br.return_date
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        JOIN members m ON br.member_id = m.id
        ORDER BY br.return_date IS NOT NULL, br.due_date
    """).fetchall()
    conn.close()
    return render_template("records.html", records=all_records, today=date.today().isoformat())


if __name__ == "__main__":
    app.run(debug=True)
