# Library Management System

A simple full-stack web app built with **Python, Flask, and SQL (SQLite)**.
Comes preloaded with a dataset of 50 real books so you can test it immediately.

## Features
- View & search the book catalog (search by title or author)
- Add new books
- Register new members
- Issue a book to a member (14-day due date, blocks issuing if no copies left)
- Mark books as returned
- View all borrow records with overdue highlighting

## Project Structure
```
library_management/
├── app.py                # Flask app (all routes/logic)
├── schema.sql             # Database table definitions
├── init_db.py              # One-time script: creates DB + loads dataset
├── books_dataset.csv       # Sample dataset of 50 books
├── requirements.txt
├── templates/               # HTML pages (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── add_book.html
│   ├── members.html
│   ├── add_member.html
│   ├── issue.html
│   └── records.html
└── library.db               # SQLite database (auto-created)
```

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create the database (only needed once)
```bash
python init_db.py
```
This creates `library.db`, loads all 50 books from `books_dataset.csv`,
and adds 2 sample members so you can test right away.

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
Go to: **http://127.0.0.1:5000**

## How to Reset the Data
If you want to start fresh (e.g. after testing):
```bash
rm library.db
python init_db.py
```

## Concepts This Project Demonstrates (good for interviews)
- **SQL**: table design, foreign keys, JOINs (see `/records` route), 
  aggregation-ready schema, parameterized queries (prevents SQL injection)
- **Flask**: routing, GET vs POST, Jinja2 templating, form handling, flash messages
- **Business logic**: preventing overbooking (can't issue a book with 0 copies),
  automatic due-date calculation, overdue detection

## Ideas to Extend This (for your resume/portfolio)
- Add login/authentication so only staff can add books
- Add fine calculation for overdue books
- Add pagination for large catalogs
- Deploy it live on Render or PythonAnywhere and share the link
- Switch SQLite → PostgreSQL/MySQL to show you know a "production" database
