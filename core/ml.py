"""
Transparent no-paid-API baseline prediction.
This is a deterministic heuristic, NOT a trained ML model. Train and evaluate a real
model with: python ml_engine/train_model.py (requires a real/synthetic labeled CSV).
"""
def predict_student(s):
    score = (
        0.22 * s.previous_marks + 0.22 * s.internal_marks +
        0.15 * s.assignment_score + 0.15 * s.attendance +
        0.10 * s.practical_marks + 0.08 * s.project_score +
        0.08 * min(s.study_hours * 10, 100)
    )
    penalty = min(s.backlogs * 3, 18)
    score = max(0, min(100, score - penalty))
    probability = round(score / 100, 4)
    if score >= 75 and s.attendance >= 75:
        category, risk = "High Performance", "LOW"
    elif score >= 55:
        category, risk = "Average Performance", "MEDIUM"
    elif score >= 40:
        category, risk = "Needs Improvement", "HIGH"
    else:
        category, risk = "At Academic Risk", "HIGH"
    reasons = []
    if s.attendance < 75: reasons.append(f"Attendance is {s.attendance:.1f}%, below the 75% target.")
    if s.internal_marks < 50: reasons.append("Internal examination marks need improvement.")
    if s.assignment_completion < 70: reasons.append("Assignment completion is below 70%.")
    if s.backlogs: reasons.append(f"{s.backlogs} previous backlog(s) recorded.")
    if s.study_hours < 2: reasons.append("Daily study time is below 2 hours.")
    if not reasons: reasons.append("Current indicators are within the configured baseline thresholds.")
    tips = []
    if s.attendance < 75: tips.append("Create an attendance recovery plan and attend every upcoming class.")
    if s.internal_marks < 60: tips.append("Revise weak topics for 30–45 minutes daily and attempt weekly practice tests.")
    if s.assignment_completion < 80: tips.append("Break pending assignments into small tasks with clear due dates.")
    if s.study_hours < 2: tips.append("Start with two focused study blocks each day and review progress weekly.")
    if s.backlogs: tips.append("Meet the subject teacher and create a backlog-clearing schedule.")
    if not tips: tips.append("Maintain the current routine and use weekly mock tests to sustain progress.")
    return category, probability, risk, " ".join(reasons), tips
