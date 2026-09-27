# Student Job & Internship Portal — Complete 3 Role Version

A Flask + SQLite professional portal with **Student, Company/Recruiter and Admin** accounts.

## Features
### Student
- Register/Login
- Detailed profile: phone, location, education, skills, bio, LinkedIn, GitHub
- Resume upload: PDF/DOC/DOCX, max 5 MB
- Resume view
- Jobs/internships search and mode filter
- Apply only after resume upload
- Application tracking: Applied, Under Review, Shortlisted, Interview, Selected, Rejected
- Interview date/time/type/link/message visible in My Applications

### Company / Recruiter
- Separate registration/login
- Company profile
- Company dashboard
- Post jobs/internships
- View applicants for own jobs
- See applicant education, skills, email
- View applicant resume
- Update status: Under Review, Shortlisted, Rejected, Selected
- Schedule interview with date, time, Online/Offline, meeting link and message
- Interview automatically changes application status to Interview

### Admin
- Admin dashboard
- View users, jobs and applications
- Add jobs
- Update application status

## Demo Accounts
- Student: `student@example.com` / `student123`
- Company: `company@example.com` / `company123`
- Admin: `admin@example.com` / `admin123`

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`

If upgrading from an older version, delete the old `instance/portal.db` once before first run so the new schema can be created.


### Admin Settings
Admin can open **Admin Settings** from the sidebar and change the Admin login email/username and password. The current password is required for every credential update.
