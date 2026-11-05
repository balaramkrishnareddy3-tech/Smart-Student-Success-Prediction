# Initial schema for Smart Student Success.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("student_id", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("age", models.PositiveSmallIntegerField(default=18)),
                ("department", models.CharField(default="Computer Science", max_length=100)),
                ("academic_year", models.CharField(default="2026-27", max_length=20)),
                ("semester", models.PositiveSmallIntegerField(default=1)),
                ("course", models.CharField(default="B.Tech", max_length=100)),
                ("previous_marks", models.FloatField(default=60)),
                ("internal_marks", models.FloatField(default=60)),
                ("assignment_score", models.FloatField(default=60)),
                ("attendance", models.FloatField(default=75)),
                ("practical_marks", models.FloatField(default=60)),
                ("project_score", models.FloatField(default=60)),
                ("study_hours", models.FloatField(default=2)),
                ("participation", models.FloatField(default=3)),
                ("backlogs", models.PositiveSmallIntegerField(default=0)),
                ("assignment_completion", models.FloatField(default=75)),
                ("predicted_category", models.CharField(blank=True, max_length=40)),
                ("success_probability", models.FloatField(blank=True, null=True)),
                ("risk_level", models.CharField(blank=True, choices=[("LOW", "Low Risk"), ("MEDIUM", "Medium Risk"), ("HIGH", "High Risk")], max_length=10)),
                ("prediction_reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PredictionLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(max_length=40)),
                ("probability", models.FloatField()),
                ("risk_level", models.CharField(max_length=10)),
                ("model_name", models.CharField(default="Rule-based baseline", max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="predictions", to="core.student")),
            ],
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
