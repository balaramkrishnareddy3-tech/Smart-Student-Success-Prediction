import csv
import json
import io
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Q
from django.db import transaction
from django.utils import timezone
from .forms import RegisterForm, StudentForm
from .models import Student, PredictionLog, AuditLog
from .ml import predict_student as run_prediction


def user_role(user):
    if not user.is_authenticated:
        return "GUEST"
    if user.is_superuser or user.is_staff or user.groups.filter(name="ADMIN").exists():
        return "ADMIN"
    if user.groups.filter(name="TEACHER").exists():
        return "TEACHER"
    if user.groups.filter(name="STUDENT").exists():
        return "STUDENT"
    return "UNASSIGNED"


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if user_role(request.user) not in allowed_roles:
                messages.error(request, "You do not have permission to access that page.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def student_record_for(user):
    return Student.objects.filter(user=user).first()


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/home.html")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(username=data["username"]).exists():
                form.add_error("username", "Username already exists.")
            elif data["role"] == "STUDENT" and not data.get("student_id"):
                form.add_error("student_id", "Student ID is required for student registration.")
            else:
                linked_student = None
                if data["role"] == "STUDENT":
                    linked_student = Student.objects.filter(student_id=data["student_id"]).first()
                    if not linked_student:
                        form.add_error("student_id", "No student record matches this ID. Ask your teacher to add your record first.")
                    elif linked_student.user_id:
                        form.add_error("student_id", "This student record is already linked to an account.")
                if not form.errors:
                    user = User.objects.create_user(data["username"], data["email"], data["password"])
                    group, _ = Group.objects.get_or_create(name=data["role"])
                    user.groups.add(group)
                    if linked_student:
                        linked_student.user = user
                        linked_student.save(update_fields=["user"])
                    login(request, user)
                    messages.success(request, "Account created successfully.")
                    return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "core/auth.html", {"form": form, "heading": "Create your account", "button": "Register"})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        selected_role = request.POST.get("role", "").upper()
        user = authenticate(request, username=request.POST.get("username", "").strip(), password=request.POST.get("password", ""))
        if user:
            actual_role = user_role(user)
            if selected_role in {"STUDENT", "TEACHER", "ADMIN"} and actual_role == selected_role:
                if selected_role != "STUDENT" or student_record_for(user):
                    login(request, user)
                    return redirect("dashboard")
                messages.error(request, "Your student account is not linked to a student record. Contact your teacher.")
            else:
                messages.error(request, "Selected login type does not match this account.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "core/login.html")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return render(request, "core/logout_confirm.html")


@login_required
def dashboard(request):
    role = user_role(request.user)
    if role == "STUDENT":
        student = student_record_for(request.user)
        if not student:
            messages.error(request, "Your account is not linked to a student record. Contact your teacher.")
            return redirect("login")
        return render(request, "core/student_portal.html", {"student": student, "tips": run_prediction(student)[4], "progress_items": [("Attendance", student.attendance), ("Internal marks", student.internal_marks), ("Assignments", student.assignment_score), ("Project score", student.project_score)]})
    if role not in {"ADMIN", "TEACHER"}:
        messages.error(request, "Your account has no assigned role. Contact the administrator.")
        return redirect("login")
    students = Student.objects.all()
    recent = students.order_by("-updated_at")[:7]
    predicted = students.exclude(risk_level="")
    chart_students = students.order_by("-updated_at")[:10]
    total = students.count()
    avg_marks = students.aggregate(v=Avg("internal_marks"))["v"] or 0
    avg_attendance = students.aggregate(v=Avg("attendance"))["v"] or 0
    risk_counts = [predicted.filter(risk_level=x).count() for x in ["LOW", "MEDIUM", "HIGH"]]
    warnings = students.filter(Q(attendance__lt=75) | Q(internal_marks__lt=50) | Q(backlogs__gt=0)).order_by("attendance", "internal_marks")[:8]
    context = {
        "total": total, "avg_marks": avg_marks, "avg_attendance": avg_attendance,
        "high_risk": students.filter(risk_level="HIGH").count(),
        "low_attendance": students.filter(attendance__lt=75).count(),
        "low_marks": students.filter(internal_marks__lt=50).count(),
        "backlog_count": students.filter(backlogs__gt=0).count(),
        "recent": recent, "risk_counts": risk_counts,
        "predicted_total": predicted.count(),
        "risk_percent": round((risk_counts[2] / predicted.count()) * 100, 1) if predicted.exists() else 0,
        "chart_labels": [s.student_id for s in chart_students],
        "chart_marks": [s.internal_marks for s in chart_students],
        "chart_attendance": [s.attendance for s in chart_students],
        "chart_study": [s.study_hours for s in chart_students],
        "chart_assignments": [s.assignment_score for s in chart_students],
        "warnings": warnings,
    }
    return render(request, "core/dashboard.html", context)


@role_required("ADMIN", "TEACHER")
def risk_analysis(request):
    """Risk analysis using the project's transparent baseline prediction rules."""
    students = list(Student.objects.all().order_by("department", "name"))
    analyzed = []
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    department_counts = {}

    for student in students:
        category, probability, risk, reason, tips = run_prediction(student)
        counts[risk] += 1
        department = student.department or "Unspecified"
        department_counts.setdefault(department, {"LOW": 0, "MEDIUM": 0, "HIGH": 0})
        department_counts[department][risk] += 1
        analyzed.append({
            "student": student,
            "risk": risk,
            "category": category,
            "probability": round(probability * 100, 1),
            "reason": reason,
            "tips": tips,
        })

    high_risk_students = [row for row in analyzed if row["risk"] == "HIGH"]
    high_risk_students.sort(key=lambda row: (
        row["student"].attendance,
        row["student"].internal_marks,
        -row["student"].backlogs,
    ))

    departments = sorted(department_counts)
    context = {
        "total": len(students),
        "low_count": counts["LOW"],
        "medium_count": counts["MEDIUM"],
        "high_count": counts["HIGH"],
        "risk_labels_json": json.dumps(["Low Risk", "Medium Risk", "High Risk"]),
        "risk_values_json": json.dumps([counts["LOW"], counts["MEDIUM"], counts["HIGH"]]),
        "department_labels_json": json.dumps(departments),
        "department_high_json": json.dumps([department_counts[d]["HIGH"] for d in departments]),
        "department_medium_json": json.dumps([department_counts[d]["MEDIUM"] for d in departments]),
        "department_low_json": json.dumps([department_counts[d]["LOW"] for d in departments]),
        "high_risk_students": high_risk_students[:25],
        "analyzed_count": len(analyzed),
    }
    return render(request, "core/risk_analysis.html", context)


@role_required("ADMIN", "TEACHER")
def student_list(request):
    q = request.GET.get("q", "").strip()
    risk = request.GET.get("risk", "").strip()
    students = Student.objects.all().order_by("name")
    if q:
        students = students.filter(Q(name__icontains=q) | Q(student_id__icontains=q) | Q(department__icontains=q))
    if risk in {"LOW", "MEDIUM", "HIGH"}:
        students = students.filter(risk_level=risk)
    return render(request, "core/students.html", {"students": students, "q": q, "risk": risk})


@role_required("ADMIN", "TEACHER")
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            AuditLog.objects.create(actor=request.user, action=f"Created student record {student.student_id}")
            messages.success(request, "Student record saved.")
            return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm()
    return render(request, "core/student_form.html", {"form": form, "heading": "Add student record", "button": "Save student"})


@role_required("ADMIN", "TEACHER")
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(actor=request.user, action=f"Updated student record {student.student_id}")
            messages.success(request, "Student record updated.")
            return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, "core/student_form.html", {"form": form, "heading": "Edit student record", "button": "Save changes", "student": student})


@role_required("ADMIN", "TEACHER")
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student_id = student.student_id
        student.delete()
        AuditLog.objects.create(actor=request.user, action=f"Deleted student record {student_id}")
        messages.success(request, f"Student {student_id} was deleted.")
        return redirect("student_list")
    return render(request, "core/student_confirm_delete.html", {"student": student})


@login_required
def student_detail(request, pk):
    if user_role(request.user) == "STUDENT":
        student = get_object_or_404(Student, pk=pk, user=request.user)
    elif user_role(request.user) in {"ADMIN", "TEACHER"}:
        student = get_object_or_404(Student, pk=pk)
    else:
        return redirect("login")
    tips = []
    if student.predicted_category:
        _, _, _, _, tips = run_prediction(student)
    history = student.predictions.order_by("-created_at")[:6]
    success_percent = round(student.success_probability * 100, 1) if student.success_probability is not None else None
    return render(request, "core/student_detail.html", {"student": student, "tips": tips, "history": history, "success_percent": success_percent})


@role_required("ADMIN", "TEACHER")
def predict_student(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden("Prediction requests must use POST.")
    student = get_object_or_404(Student, pk=pk)
    category, probability, risk, reason, tips = run_prediction(student)
    student.predicted_category, student.success_probability, student.risk_level, student.prediction_reason = category, probability, risk, reason
    student.save()
    PredictionLog.objects.create(student=student, category=category, probability=probability, risk_level=risk)
    AuditLog.objects.create(actor=request.user, action=f"Generated prediction for {student.student_id}")
    messages.success(request, "Baseline analysis refreshed. Treat this as decision support, not a definitive judgment.")
    return redirect("student_detail", pk=student.pk)


@role_required("ADMIN", "TEACHER")
def import_students_csv(request):
    if request.method == "POST":
        upload = request.FILES.get("csv_file")
        if not upload or not upload.name.lower().endswith(".csv"):
            messages.error(request, "Please choose a .csv file.")
            return redirect("student_list")
        try:
            decoded = upload.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(decoded))
            required = {"student_id", "name"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise ValueError("CSV must include at least student_id and name columns.")
            created, skipped = 0, 0
            allowed = {f.name for f in Student._meta.fields} - {
                "id", "user", "predicted_category", "success_probability", "risk_level",
                "prediction_reason", "created_at", "updated_at"
            }
            with transaction.atomic():
                for row in reader:
                    payload = {k: v for k, v in row.items() if k in allowed and v not in (None, "")}
                    if not payload.get("student_id") or not payload.get("name"):
                        skipped += 1
                        continue
                    if Student.objects.filter(student_id=payload["student_id"]).exists():
                        skipped += 1
                        continue
                    try:
                        student = Student(**payload)
                        student.full_clean()
                        student.save()
                        created += 1
                    except (ValueError, TypeError, Exception):
                        skipped += 1
            AuditLog.objects.create(actor=request.user, action=f"Imported {created} student records from CSV")
            messages.success(request, f"Import complete: {created} added, {skipped} skipped.")
        except (UnicodeDecodeError, csv.Error, ValueError) as exc:
            messages.error(request, f"Could not import CSV: {exc}")
        return redirect("student_list")
    return redirect("student_list")


@role_required("ADMIN", "TEACHER")
def export_students_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="student_analytics.csv"'
    writer = csv.writer(response)
    writer.writerow(["student_id", "name", "department", "semester", "previous_marks", "internal_marks", "assignment_score", "attendance", "practical_marks", "project_score", "study_hours", "backlogs", "predicted_category", "success_probability", "risk_level"])
    for s in Student.objects.all().order_by("name"):
        writer.writerow([s.student_id, s.name, s.department, s.semester, s.previous_marks, s.internal_marks, s.assignment_score, s.attendance, s.practical_marks, s.project_score, s.study_hours, s.backlogs, s.predicted_category, s.success_probability, s.risk_level])
    return response


@login_required
def student_pdf_report(request, pk):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    if user_role(request.user) == "STUDENT":
        student = get_object_or_404(Student, pk=pk, user=request.user)
    elif user_role(request.user) in {"ADMIN", "TEACHER"}:
        student = get_object_or_404(Student, pk=pk)
    else:
        return redirect("login")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("Student Academic Report", styles["Title"]), Paragraph("Smart Student Success Prediction & Analysis System", styles["Normal"]), Spacer(1, 12)]
    data = [
        ["Student ID", student.student_id], ["Name", student.name], ["Department", student.department],
        ["Semester", str(student.semester)], ["Attendance", f"{student.attendance:.1f}%"],
        ["Internal marks", f"{student.internal_marks:.1f}/100"], ["Assignment score", f"{student.assignment_score:.1f}/100"],
        ["Study hours/day", str(student.study_hours)], ["Backlogs", str(student.backlogs)],
        ["Prediction", student.predicted_category or "Not analyzed"],
        ["Success score (baseline)", f"{student.success_probability * 100:.1f}%" if student.success_probability is not None else "—"],
        ["Risk level", student.get_risk_level_display() or "Not analyzed"],
    ]
    table = Table(data, colWidths=[48*mm, 112*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EAF2F8")),("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#182536")),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#CBD5E1")),("PADDING",(0,0),(-1,-1),8),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold")]))
    story += [table, Spacer(1, 14), Paragraph("Prediction explanation", styles["Heading2"]), Paragraph(student.prediction_reason or "No prediction has been generated yet.", styles["BodyText"]), Spacer(1, 8), Paragraph("Recommendations", styles["Heading2"])]
    tips = run_prediction(student)[4]
    for tip in tips:
        story.append(Paragraph("• " + tip, styles["BodyText"]))
    story += [Spacer(1, 12), Paragraph("Important: this report contains a transparent heuristic baseline estimate. It is not a validated real-world prediction and must not be used as the sole basis for academic decisions.", styles["Italic"])]
    doc.build(story)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="student_{student.student_id}_report.pdf"'
    return response


@role_required("ADMIN", "TEACHER")
def dashboard_pdf_report(request):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    students = Student.objects.all().order_by("name")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm)
    styles = getSampleStyleSheet()
    total = students.count()
    avg = students.aggregate(v=Avg("internal_marks"))["v"] or 0
    att = students.aggregate(v=Avg("attendance"))["v"] or 0
    story = [Paragraph("Student Success — Dashboard Report", styles["Title"]), Paragraph(f"Generated {timezone.localtime():%d %b %Y, %I:%M %p}", styles["Normal"]), Spacer(1, 10)]
    story.append(Paragraph(f"Students: {total} &nbsp;&nbsp; Average marks: {avg:.1f}% &nbsp;&nbsp; Average attendance: {att:.1f}% &nbsp;&nbsp; High risk: {students.filter(risk_level='HIGH').count()}", styles["Heading2"]))
    data = [["ID", "Student", "Department", "Sem", "Attendance", "Marks", "Prediction", "Risk"]]
    for s in students:
        data.append([s.student_id, s.name, s.department, str(s.semester), f"{s.attendance:.0f}%", f"{s.internal_marks:.0f}", s.predicted_category or "Pending", s.risk_level or "—"])
    table = Table(data, repeatRows=1, colWidths=[25*mm, 38*mm, 35*mm, 12*mm, 23*mm, 18*mm, 43*mm, 20*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#12344A")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#CBD5E1")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F1F5F9")]),("PADDING",(0,0),(-1,-1),6),("FONTSIZE",(0,0),(-1,-1),8)]))
    story.append(table)
    doc.build(story)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="student_dashboard_report.pdf"'
    return response
