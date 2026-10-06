import sqlite3

def setup_database():
    conn = sqlite3.connect('admission_system.db', timeout=30)
    cursor = conn.cursor()

    # Enforce foreign key constraints in SQLite and reduce lock contention for concurrent app sessions
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA busy_timeout = 30000;")

    # 1. Applicants
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Applicants (
        Applicant_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Full_Name TEXT NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        Phone TEXT,
        Date_of_Birth DATE NOT NULL
    )''')

    # 2. Programmes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Programmes (
        Programme_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Title TEXT NOT NULL,
        Department TEXT NOT NULL,
        Capacity INTEGER NOT NULL CHECK (Capacity > 0),
        Tuition_Fee REAL NOT NULL CHECK (Tuition_Fee >= 0)
    )''')

    # 3. Applications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Applications (
        Application_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Applicant_ID INTEGER NOT NULL,
        Submission_Date DATE DEFAULT CURRENT_DATE,
        Overall_Status TEXT CHECK(Overall_Status IN ('Submitted', 'Under Review', 'Decision Rendered')) DEFAULT 'Submitted',
        FOREIGN KEY (Applicant_ID) REFERENCES Applicants(Applicant_ID) ON DELETE CASCADE
    )''')

    # 4. Programme Choices
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Programme_Choices (
        Choice_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Application_ID INTEGER NOT NULL,
        Programme_ID INTEGER NOT NULL,
        Preference_Rank INTEGER CHECK (Preference_Rank BETWEEN 1 AND 3),
        Decision_Status TEXT CHECK(Decision_Status IN ('Pending', 'Under Review', 'Offered', 'Rejected')) DEFAULT 'Pending',
        FOREIGN KEY (Application_ID) REFERENCES Applications(Application_ID) ON DELETE CASCADE,
        FOREIGN KEY (Programme_ID) REFERENCES Programmes(Programme_ID)
    )''')

    # 5. Academic Qualifications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Academic_Qualifications (
        Qual_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Applicant_ID INTEGER NOT NULL,
        Institution TEXT NOT NULL,
        Degree_Name TEXT NOT NULL,
        Major TEXT NOT NULL,
        GPA REAL CHECK (GPA BETWEEN 0.0 AND 4.0),
        FOREIGN KEY (Applicant_ID) REFERENCES Applicants(Applicant_ID) ON DELETE CASCADE
    )''')

    # 6. Test Scores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Test_Scores (
        Score_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Applicant_ID INTEGER NOT NULL,
        Test_Type TEXT CHECK(Test_Type IN ('TOEFL', 'IELTS', 'GMAT', 'GRE')),
        Total_Score REAL NOT NULL,
        FOREIGN KEY (Applicant_ID) REFERENCES Applicants(Applicant_ID) ON DELETE CASCADE
    )''')

    # 7. Work Experiences
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Work_Experiences (
        Exp_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Applicant_ID INTEGER NOT NULL,
        Company TEXT NOT NULL,
        Job_Title TEXT NOT NULL,
        Years_Exp REAL CHECK (Years_Exp >= 0),
        FOREIGN KEY (Applicant_ID) REFERENCES Applicants(Applicant_ID) ON DELETE CASCADE
    )''')

    # 8. Documents
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Documents (
        Doc_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Application_ID INTEGER NOT NULL,
        Doc_Type TEXT NOT NULL,
        Verification_Status TEXT CHECK(Verification_Status IN ('Pending', 'Verified', 'Rejected')) DEFAULT 'Pending',
        FOREIGN KEY (Application_ID) REFERENCES Applications(Application_ID) ON DELETE CASCADE
    )''')

    # 9. Referees
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Referees (
        Ref_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Application_ID INTEGER NOT NULL,
        Referee_Name TEXT NOT NULL,
        Status TEXT CHECK(Status IN ('Pending', 'Received')) DEFAULT 'Pending',
        FOREIGN KEY (Application_ID) REFERENCES Applications(Application_ID) ON DELETE CASCADE
    )''')

    # 10. Application Fees
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Application_Fees (
        Payment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Application_ID INTEGER NOT NULL,
        Amount REAL CHECK (Amount >= 0),
        Payment_Status TEXT CHECK(Payment_Status IN ('Unpaid', 'Paid')) DEFAULT 'Unpaid',
        FOREIGN KEY (Application_ID) REFERENCES Applications(Application_ID) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    setup_database()