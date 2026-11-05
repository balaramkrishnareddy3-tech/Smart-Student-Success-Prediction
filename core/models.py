from django.conf import settings
from django.db import models

class Student(models.Model):
    RISK_CHOICES = [("LOW", "Low Risk"), ("MEDIUM", "Medium Risk"), ("HIGH", "High Risk")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    student_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    age = models.PositiveSmallIntegerField(default=18)
    department = models.CharField(max_length=100, default="Computer Science")
    academic_year = models.CharField(max_length=20, default="2026-27")
    semester = models.PositiveSmallIntegerField(default=1)
    course = models.CharField(max_length=100, default="B.Tech")
    previous_marks = models.FloatField(default=60)
    internal_marks = models.FloatField(default=60)
    assignment_score = models.FloatField(default=60)
    attendance = models.FloatField(default=75)
    practical_marks = models.FloatField(default=60)
    project_score = models.FloatField(default=60)
    study_hours = models.FloatField(default=2)
    participation = models.FloatField(default=3)
    backlogs = models.PositiveSmallIntegerField(default=0)
    assignment_completion = models.FloatField(default=75)
    predicted_category = models.CharField(max_length=40, blank=True)
    success_probability = models.FloatField(null=True, blank=True)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, blank=True)
    prediction_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class PredictionLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="predictions")
    category = models.CharField(max_length=40)
    probability = models.FloatField()
    risk_level = models.CharField(max_length=10)
    model_name = models.CharField(max_length=100, default="Rule-based baseline")
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
