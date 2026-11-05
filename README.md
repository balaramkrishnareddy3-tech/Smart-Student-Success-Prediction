# Smart Student Success Prediction & Analysis System

A Django-based student analytics application with academic record management, dashboard visualizations, transparent baseline risk indicators, and teacher-facing reporting tools.

## Included features
- Login, registration and logout using Django authentication.
- Executive dashboard: total students, average marks, average attendance and high-risk count.
- Risk distribution chart with low, medium and high categories and high-risk percentage.
- Academic comparison chart for marks, attendance and assignment scores.
- Early-warning list for low attendance, low internal marks and students with backlogs.
- Student directory with name, ID and department search plus risk filtering.
- Add, edit, view and delete student records.
- CSV import (minimum required headers: `student_id`, `name`) and CSV export.
- Individual student PDF reports and an overall dashboard PDF report.
- Prediction history, explanation and rule-based personalized recommendations.
- Initial database migration included.

## Important prediction transparency
The current in-app prediction action uses a deterministic, transparent heuristic in `core/ml.py`. It is **not a trained or validated machine-learning model**. The score should be treated as an educational decision-support signal only—not as a definitive prediction or a basis for penalizing students. The optional training script demonstrates a separate training workflow; meaningful evaluation requires an authorized, representative, correctly labeled dataset.

## Requirements
- Python 3.10+
- Windows PowerShell, macOS Terminal or Linux shell

## Setup (Windows PowerShell)
```powershell
cd smart_student_success
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## CSV import format
The CSV upload requires `student_id` and `name`. Other accepted column names match the Student model, for example:
`department`, `semester`, `course`, `attendance`, `internal_marks`, `assignment_score`, `previous_marks`, `practical_marks`, `project_score`, `study_hours`, `backlogs`, and `assignment_completion`.
Rows with duplicate IDs or invalid values are skipped and counted in the import result. Use UTF-8 CSV.

## First use
1. Register a Teacher account (or create a staff account through Django admin).
2. Add student records or import a CSV.
3. Open a student profile and select **Run analysis** to generate baseline indicators.
4. Review the dashboard risk distribution and early-warning list.
5. Export CSV or generate individual / overall PDF reports.

## Optional model training demonstration
A synthetic sample is included at `data/synthetic_students.csv`. It is explicitly synthetic and must not be used to claim real-world model accuracy.
```powershell
python ml_engine/train_model.py --input data/synthetic_students.csv
```
For meaningful evaluation, use an authorized, representative labeled dataset. See `data/README.md`.

## Security and deployment notes
Django authentication and password hashing are enabled. This project is a local academic prototype. Before public deployment, configure a production secret key, `DEBUG=False`, secure `ALLOWED_HOSTS`, HTTPS/security settings, backups, and institution-specific role/object-level access controls. Do not expose student personal data or publish a populated database.


## Role-based login setup

The login page has three separate role choices: Student, Teacher and Admin.

- **Admin:** Create the first administrator with `python manage.py createsuperuser`. Sign in by choosing Admin.
- **Teacher:** Sign in by choosing Teacher. For security, teacher accounts are not publicly self-registered. An administrator creates a user in `/admin/`, then adds that user to the `TEACHER` group. Keep `is_staff` disabled unless the person should also access Django administration.
- **Student:** Add/import the student's academic record first. The student then uses **Create account** and enters the exact existing Student ID. The account is securely linked to that one student record. A student can view only their own academic details and report.

Teacher and Admin accounts can access the institution-wide student workspace. Students cannot access the teacher/admin student directory, risk analysis, editing, importing or prediction controls.

### First-time setup

```powershell
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and choose the appropriate role on the sign-in page.

**Security note:** This project is configured for local development. Before public deployment, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=0`, configure `ALLOWED_HOSTS`, use HTTPS, and review the deployment security settings.
