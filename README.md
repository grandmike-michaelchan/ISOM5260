# ISOM5260 Student Admission System

A Streamlit application for managing student admission applications, programme
choices, qualifications, test scores, work experience, documents, referees, and
application fees. Data is stored locally in SQLite.

## Requirements

- Python 3.9 or newer

## Run locally

1. Create and activate a virtual environment.
2. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create the local database schema:

   ```bash
   python init_db.py
   ```

4. Start the application:

   ```bash
   python -m streamlit run app.py
   ```

The application creates `admission_system.db` in the project directory. The
database is intentionally excluded from Git because it can contain applicant
personal information.

## Optional sample data

After initializing the database, load the sample SQL data with:

```bash
python -c "import sqlite3; db = sqlite3.connect('admission_system.db'); db.executescript(open('seed_data.sql', encoding='utf-8').read()); db.close()"
```

Run this only once per fresh database to avoid duplicate sample rows.
