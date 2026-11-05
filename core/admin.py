from django.contrib import admin
from .models import Student, PredictionLog, AuditLog
admin.site.register(Student)
admin.site.register(PredictionLog)
admin.site.register(AuditLog)
