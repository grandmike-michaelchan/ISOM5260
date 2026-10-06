import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Student Admission System", layout="wide")

def get_connection():
    conn = sqlite3.connect('admission_system.db', timeout=30)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    return conn

# Main Header
st.title("HKUST MSc Admission System v1")
portal_type = st.sidebar.selectbox("Select Portal View", ["Applicant Portal", "Staff Portal"])

# ---------------------------------------------------------
# APPLICANT PORTAL
# ---------------------------------------------------------
if portal_type == "Applicant Portal":
    st.sidebar.markdown("---")
    applicant_nav = st.sidebar.radio("Applicant Actions", ["1. Submit Application", "2. Check Progress"])
    
    # 1. Submit Application
    if applicant_nav == "1. Submit Application":
        st.header("New Application Form")
        conn = get_connection()
        programmes_df = pd.read_sql_query("SELECT Programme_ID, Title FROM Programmes", conn)
        conn.close()
        
        with st.form("applicant_submission_form", clear_on_submit=True):
            st.subheader("1. Personal Information")
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
            phone = st.text_input("Phone Number")
            dob = st.date_input("Date of Birth")
            
            st.subheader("2. Program Preferences")
            prog_options = programmes_df['Title'].tolist() if not programmes_df.empty else []
            p1 = st.selectbox("1st Preference Choice *", prog_options)
            p2 = st.selectbox("2nd Preference Choice (Optional)", ["None"] + prog_options)
            
            st.subheader("3. Academic & Background Details")
            institution = st.text_input("Degree Institution *")
            degree_name = st.text_input("Degree Title *")
            major = st.text_input("Major *")
            gpa = st.number_input("GPA (0.00 - 4.00) *", min_value=0.0, max_value=4.0, step=0.01)
            
            test_type = st.selectbox("Test Type", ["GMAT", "GRE", "TOEFL", "IELTS"])
            test_score = st.number_input("Test Total Score", min_value=0.0, max_value=800.0, step=1.0)
            
            company = st.text_input("Current Company")
            job_title = st.text_input("Job Title")
            years_exp = st.number_input("Years of Work Experience", min_value=0.0, max_value=40.0, step=0.5)
            
            submitted = st.form_submit_button("Submit Application ($300 Fee)")
            
            if submitted:
                if not full_name or not email or not institution or not degree_name or not major:
                    st.error("Please fill in all mandatory fields (*).")
                elif p1 == p2:
                    st.error("1st and 2nd choices must be different programs.")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("SELECT 1 FROM Applicants WHERE Email = ?", (email,))
                        if cursor.fetchone():
                            st.error("Submission Error: Email already exists in the system.")
                            conn.close()
                            st.stop()

                        cursor.execute("BEGIN IMMEDIATE")
                        cursor.execute("INSERT INTO Applicants (Full_Name, Email, Phone, Date_of_Birth) VALUES (?, ?, ?, ?)",
                                       (full_name, email, phone, str(dob)))
                        app_id_pk = cursor.lastrowid

                        cursor.execute("INSERT INTO Applications (Applicant_ID, Overall_Status) VALUES (?, 'Submitted')", (app_id_pk,))
                        application_id = cursor.lastrowid

                        p1_row = cursor.execute("SELECT Programme_ID FROM Programmes WHERE Title = ? LIMIT 1", (p1,)).fetchone()
                        if p1_row is None:
                            raise ValueError(f"Selected programme '{p1}' is no longer available.")
                        p1_id = p1_row[0]
                        cursor.execute("INSERT INTO Programme_Choices (Application_ID, Programme_ID, Preference_Rank) VALUES (?, ?, 1)",
                                       (application_id, p1_id))

                        if p2 != "None":
                            p2_row = cursor.execute("SELECT Programme_ID FROM Programmes WHERE Title = ? LIMIT 1", (p2,)).fetchone()
                            if p2_row is None:
                                raise ValueError(f"Selected programme '{p2}' is no longer available.")
                            p2_id = p2_row[0]
                            cursor.execute("INSERT INTO Programme_Choices (Application_ID, Programme_ID, Preference_Rank) VALUES (?, ?, 2)",
                                           (application_id, p2_id))

                        cursor.execute("INSERT INTO Academic_Qualifications (Applicant_ID, Institution, Degree_Name, Major, GPA) VALUES (?, ?, ?, ?, ?)",
                                       (app_id_pk, institution, degree_name, major, gpa))

                        if test_score > 0:
                            cursor.execute("INSERT INTO Test_Scores (Applicant_ID, Test_Type, Total_Score) VALUES (?, ?, ?)",
                                           (app_id_pk, test_type, test_score))

                        if company:
                            cursor.execute("INSERT INTO Work_Experiences (Applicant_ID, Company, Job_Title, Years_Exp) VALUES (?, ?, ?, ?)",
                                           (app_id_pk, company, job_title, years_exp))

                        cursor.execute("INSERT INTO Documents (Application_ID, Doc_Type, Verification_Status) VALUES (?, 'Transcript', 'Pending')", (application_id,))
                        cursor.execute("INSERT INTO Referees (Application_ID, Referee_Name, Status) VALUES (?, 'Academic Referee', 'Pending')", (application_id,))
                        cursor.execute("INSERT INTO Application_Fees (Application_ID, Amount, Payment_Status) VALUES (?, 300.0, 'Paid')", (application_id,))

                        conn.commit()
                        st.success(f"Application Submitted! Your Application ID is #{application_id}. Save this ID to track progress.")
                    except sqlite3.IntegrityError as e:
                        conn.rollback()
                        st.error(f"Submission Error: Database constraint failed. Please review all required details and try again. Details: {e}")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Submission Error: {e}")
                    finally:
                        conn.close()

    # 2. Check Progress
    elif applicant_nav == "2. Check Progress":
        st.header("Check Application Progress")
        search_email = st.text_input("Enter Registered Email Address")
        
        if st.button("Search Application Status"):
            if search_email:
                conn = get_connection()
                query = """
                SELECT a.Application_ID, app.Full_Name, a.Submission_Date, a.Overall_Status,
                       p.Title AS Programme_Name, pc.Preference_Rank, pc.Decision_Status
                FROM Applications a
                JOIN Applicants app ON a.Applicant_ID = app.Applicant_ID
                JOIN Programme_Choices pc ON a.Application_ID = pc.Application_ID
                JOIN Programmes p ON pc.Programme_ID = p.Programme_ID
                WHERE app.Email = ?
                ORDER BY pc.Preference_Rank ASC;
                """
                status_df = pd.read_sql_query(query, conn, params=(search_email,))
                conn.close()
                
                if not status_df.empty:
                    st.subheader(f"Applicant: {status_df['Full_Name'].iloc[0]}")
                    st.info(f"Overall Application Status: {status_df['Overall_Status'].iloc[0]}")
                    st.dataframe(status_df[['Programme_Name', 'Preference_Rank', 'Decision_Status']], use_container_width=True)
                else:
                    st.warning("No application found associated with that email address.")

# ---------------------------------------------------------
# STAFF PORTAL
# ---------------------------------------------------------
else:
    st.sidebar.markdown("---")
    staff_nav = st.sidebar.radio("Staff Views", ["1. Decisions Manager", "2. Managerial Analytics"])
    
    # 1. Decisions Manager
    if staff_nav == "1. Decisions Manager":
        st.header("Review & Decision Processing")
        conn = get_connection()
        
        apps_summary = pd.read_sql_query("""
            SELECT pc.Choice_ID, a.Application_ID, app.Full_Name, p.Title AS Programme, 
                   pc.Preference_Rank, q.GPA, pc.Decision_Status
            FROM Programme_Choices pc
            JOIN Applications a ON pc.Application_ID = a.Application_ID
            JOIN Applicants app ON a.Applicant_ID = app.Applicant_ID
            JOIN Programmes p ON pc.Programme_ID = p.Programme_ID
            LEFT JOIN Academic_Qualifications q ON app.Applicant_ID = q.Applicant_ID
        """, conn)
        
        st.dataframe(apps_summary, use_container_width=True)
        
        st.subheader("Update Programme Choice Decision")
        with st.form("decision_update_form"):
            choice_id_select = st.selectbox("Select Choice ID to Evaluate", apps_summary['Choice_ID'].tolist() if not apps_summary.empty else [])
            new_decision = st.selectbox("Render Decision", ["Pending", "Under Review", "Offered", "Rejected"])
            update_submit = st.form_submit_button("Update Decision")
            
            if update_submit and choice_id_select:
                cursor = conn.cursor()
                cursor.execute("UPDATE Programme_Choices SET Decision_Status = ? WHERE Choice_ID = ?", (new_decision, choice_id_select))
                
                # Fetch related application ID to sync Overall Status
                cursor.execute("SELECT Application_ID FROM Programme_Choices WHERE Choice_ID = ?", (choice_id_select,))
                app_id = cursor.fetchone()[0]
                
                cursor.execute("UPDATE Applications SET Overall_Status = 'Decision Rendered' WHERE Application_ID = ?", (app_id,))
                conn.commit()
                st.success(f"Choice #{choice_id_select} decision updated to '{new_decision}'. Applicant view updated.")
                st.rerun()
        conn.close()

    # 2. Managerial Analytics
    elif staff_nav == "2. Managerial Analytics":
        st.header("Managerial & Operational Dashboard")
        conn = get_connection()
        
        queries = {
            "Query 1: Programme Demand vs Capacity": """
                SELECT p.Programme_ID, p.Title, p.Capacity, 
                       COUNT(pc.Choice_ID) AS Total_Applications,
                       ROUND(CAST(COUNT(pc.Choice_ID) AS REAL) / p.Capacity, 2) AS Demand_Ratio
                FROM Programmes p
                LEFT JOIN Programme_Choices pc ON p.Programme_ID = pc.Programme_ID
                GROUP BY p.Programme_ID, p.Title, p.Capacity
                ORDER BY Total_Applications DESC;
            """,
            "Query 2: 1st Choice Preference Demand": """
                SELECT p.Title, COUNT(pc.Choice_ID) AS First_Choice_Count
                FROM Programme_Choices pc
                JOIN Programmes p ON pc.Programme_ID = p.Programme_ID
                WHERE pc.Preference_Rank = 1
                GROUP BY p.Title
                ORDER BY First_Choice_Count DESC;
            """,
            "Query 3: Average GPA by Admission Outcome": """
                SELECT pc.Decision_Status, 
                       COUNT(DISTINCT a.Application_ID) AS Candidate_Count,
                       ROUND(AVG(q.GPA), 2) AS Average_GPA
                FROM Programme_Choices pc
                JOIN Applications a ON pc.Application_ID = a.Application_ID
                JOIN Academic_Qualifications q ON a.Applicant_ID = q.Applicant_ID
                GROUP BY pc.Decision_Status
                HAVING pc.Decision_Status != 'Pending';
            """,
            "Query 4: Standardized Test Profiles": """
                SELECT t.Test_Type, 
                       COUNT(t.Score_ID) AS Total_Test_Takers,
                       ROUND(AVG(t.Total_Score), 1) AS Mean_Score,
                       MAX(t.Total_Score) AS Highest_Score
                FROM Test_Scores t
                GROUP BY t.Test_Type;
            """,
            "Query 5: Unverified Document Checklist": """
                SELECT d.Doc_ID, a.Application_ID, app.Full_Name, d.Doc_Type, d.Verification_Status
                FROM Documents d
                JOIN Applications a ON d.Application_ID = a.Application_ID
                JOIN Applicants app ON a.Applicant_ID = app.Applicant_ID
                WHERE d.Verification_Status = 'Pending';
            """,
            "Query 6: High-Performing Candidates Priority List": """
                SELECT app.Applicant_ID, app.Full_Name, app.Email, q.GPA, t.Total_Score AS Test_Score
                FROM Applicants app
                JOIN Academic_Qualifications q ON app.Applicant_ID = q.Applicant_ID
                JOIN Test_Scores t ON app.Applicant_ID = t.Applicant_ID
                WHERE q.GPA >= 3.50;
            """,
            "Query 7: Unpaid Application Fee Tracker": """
                SELECT f.Payment_ID, a.Application_ID, app.Full_Name, app.Email, f.Amount, f.Payment_Status
                FROM Application_Fees f
                JOIN Applications a ON f.Application_ID = a.Application_ID
                JOIN Applicants app ON a.Applicant_ID = app.Applicant_ID
                WHERE f.Payment_Status = 'Unpaid';
            """,
            "Query 8: Missing Reference Letters Checklist": """
                SELECT r.Ref_ID, a.Application_ID, app.Full_Name, r.Referee_Name, r.Status
                FROM Referees r
                JOIN Applications a ON r.Application_ID = a.Application_ID
                JOIN Applicants app ON a.Applicant_ID = app.Applicant_ID
                WHERE r.Status = 'Pending';
            """,
            "Query 9: Average Work Experience by Program": """
                SELECT p.Title, ROUND(AVG(w.Years_Exp), 1) AS Avg_Work_Exp_Years
                FROM Work_Experiences w
                JOIN Applications a ON w.Applicant_ID = a.Applicant_ID
                JOIN Programme_Choices pc ON a.Application_ID = pc.Application_ID
                JOIN Programmes p ON pc.Programme_ID = p.Programme_ID
                GROUP BY p.Title;
            """,
            "Query 10: Program Offer Yield & Decisions Breakdown": """
                SELECT p.Title,
                    SUM(CASE WHEN pc.Decision_Status = 'Offered' THEN 1 ELSE 0 END) AS Offers_Made,
                    SUM(CASE WHEN pc.Decision_Status = 'Rejected' THEN 1 ELSE 0 END) AS Rejections_Made,
                    COUNT(pc.Choice_ID) AS Total_Evaluated
                FROM Programme_Choices pc
                JOIN Programmes p ON pc.Programme_ID = p.Programme_ID
                GROUP BY p.Title;
            """,
            "Query 11: Total Application Fee Revenue by Department": """
                SELECT p.Department, SUM(f.Amount) AS Total_Revenue_Collected
                FROM Application_Fees f
                JOIN Applications a ON f.Application_ID = a.Application_ID
                JOIN Programme_Choices pc ON a.Application_ID = pc.Application_ID
                JOIN Programmes p ON pc.Programme_ID = p.Programme_ID
                WHERE f.Payment_Status = 'Paid'
                GROUP BY p.Department;
            """,
            "Query 12: Application Volume Timeline Summary": """
                SELECT a.Submission_Date, COUNT(a.Application_ID) AS Daily_Submissions
                FROM Applications a
                GROUP BY a.Submission_Date
                ORDER BY a.Submission_Date DESC;
            """
        }
        
        selected_query_name = st.selectbox("Select Managerial Report", list(queries.keys()))
        selected_sql = queries[selected_query_name]
        
        st.subheader("SQL Execution Query")
        st.code(selected_sql, language="sql")
        
        st.subheader("Report Output")
        report_df = pd.read_sql_query(selected_sql, conn)
        st.dataframe(report_df, use_container_width=True)
        conn.close()