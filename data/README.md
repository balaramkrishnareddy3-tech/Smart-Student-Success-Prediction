# Labeled dataset format for ML training

Place a CSV named `students_labeled.csv` in this folder. Required target column: `performance_category`.

Recommended input columns:
- previous_marks
- internal_marks
- assignment_score
- attendance
- practical_marks
- project_score
- study_hours
- participation
- backlogs
- assignment_completion
- department (optional categorical)

Target labels can be categories such as `High Performance`, `Average Performance`, `Needs Improvement`, `At Academic Risk`.

Use genuine, authorized, de-identified academic data. If you create synthetic records, label them synthetic and do not report their evaluation metrics as real-world model performance.
