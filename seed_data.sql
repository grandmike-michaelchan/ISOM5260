-- Programmes
INSERT INTO Programmes (Title, Department, Capacity, Tuition_Fee) VALUES 
('MSc in Information Systems Management', 'ISOM', 60, 280000),
('MSc in Business Analytics', 'ISOM', 50, 300000),
('MSc in Finance', 'FINA', 80, 350000);

-- Applicants
INSERT INTO Applicants (Full_Name, Email, Phone, Date_of_Birth) VALUES 
('Alex Wong', 'alex.wong@example.com', '91234567', '2001-05-14'),
('Sarah Lee', 'sarah.lee@example.com', '98765432', '2000-11-20'),
('David Chen', 'david.chen@example.com', '61112222', '1999-08-03');

-- Applications
INSERT INTO Applications (Applicant_ID, Submission_Date, Overall_Status) VALUES 
(1, '2026-09-01', 'Under Review'),
(2, '2026-09-02', 'Decision Rendered'),
(3, '2026-09-03', 'Submitted');

-- Programme Choices
INSERT INTO Programme_Choices (Application_ID, Programme_ID, Preference_Rank, Decision_Status) VALUES 
(1, 1, 1, 'Under Review'),
(1, 2, 2, 'Pending'),
(2, 2, 1, 'Offered'),
(2, 3, 2, 'Rejected'),
(3, 1, 1, 'Pending');

-- Academic Qualifications
INSERT INTO Academic_Qualifications (Applicant_ID, Institution, Degree_Name, Major, GPA) VALUES 
(1, 'HKUST', 'Bachelor of Science', 'Computer Science', 3.65),
(2, 'CUHK', 'Bachelor of Business Administration', 'Finance', 3.82),
(3, 'PolyU', 'Bachelor of Engineering', 'Electronic Engineering', 3.20);

-- Test Scores
INSERT INTO Test_Scores (Applicant_ID, Test_Type, Total_Score) VALUES 
(1, 'TOEFL', 105),
(2, 'GMAT', 720),
(3, 'IELTS', 7.5);

-- Work Experiences
INSERT INTO Work_Experiences (Applicant_ID, Company, Job_Title, Years_Exp) VALUES 
(1, 'TechCorp HK', 'Software Engineer', 2.0),
(2, 'Global Bank', 'Financial Analyst', 3.5),
(3, 'Innovate Ltd', 'Assistant Engineer', 1.0);

-- Documents
INSERT INTO Documents (Application_ID, Doc_Type, Verification_Status) VALUES 
(1, 'Transcript', 'Verified'),
(2, 'Transcript', 'Verified'),
(3, 'Transcript', 'Pending');

-- Referees
INSERT INTO Referees (Application_ID, Referee_Name, Status) VALUES 
(1, 'Dr. John Smith', 'Received'),
(2, 'Prof. Mary Johnson', 'Received'),
(3, 'Manager Wang', 'Pending');

-- Application Fees
INSERT INTO Application_Fees (Application_ID, Amount, Payment_Status) VALUES 
(1, 300.0, 'Paid'),
(2, 300.0, 'Paid'),
(3, 300.0, 'Paid');