from django import forms
from django.contrib.auth.models import User
from .models import Student

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    role = forms.ChoiceField(choices=[("STUDENT", "Student")])
    student_id = forms.CharField(max_length=30, required=False, help_text="Required for students. Enter the ID already in the student records.")

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ["user", "predicted_category", "success_probability", "risk_level", "prediction_reason", "created_at", "updated_at"]
        widgets = {
            "student_id": forms.TextInput(attrs={"placeholder": "e.g. STU001"}),
            "name": forms.TextInput(attrs={"placeholder": "Student full name"}),
        }
    def clean(self):
        data = super().clean()
        for field in ["previous_marks", "internal_marks", "assignment_score", "attendance", "practical_marks", "project_score", "assignment_completion"]:
            value = data.get(field)
            if value is not None and not 0 <= value <= 100:
                self.add_error(field, "Enter a value between 0 and 100.")
        if data.get("study_hours") is not None and data["study_hours"] > 24:
            self.add_error("study_hours", "Study hours cannot exceed 24.")
        return data
