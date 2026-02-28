from django.contrib import admin
from .models import Subject, Exam, Question, Attempt, StudentAnswer

admin.site.register(Subject)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Attempt)
admin.site.register(StudentAnswer)

# Register your models here.
