from django.contrib import admin
from django.urls import path
from core import views
urlpatterns = [
 path("admin/", admin.site.urls), path("", views.home, name="home"),
 path("register/", views.register_view, name="register"), path("login/", views.login_view, name="login"),
 path("logout/", views.logout_view, name="logout"), path("dashboard/", views.dashboard, name="dashboard"),
 path("risk-analysis/", views.risk_analysis, name="risk_analysis"),
 path("students/", views.student_list, name="student_list"), path("students/add/", views.student_create, name="student_create"),
 path("students/import/", views.import_students_csv, name="import_students_csv"),
 path("students/<int:pk>/", views.student_detail, name="student_detail"),
 path("students/<int:pk>/edit/", views.student_update, name="student_update"),
 path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
 path("students/<int:pk>/report.pdf", views.student_pdf_report, name="student_pdf_report"),
 path("reports/dashboard.pdf", views.dashboard_pdf_report, name="dashboard_pdf_report"),
 path("predict/<int:pk>/", views.predict_student, name="predict_student"),
 path("reports/students.csv", views.export_students_csv, name="export_students_csv"),
]
