from django.urls import path
from . import views

urlpatterns = [

    # Student
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/result/', views.exam_result, name='exam_result'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/exams/', views.available_exams, name='available_exams'),
    path('student/results/', views.my_results, name='my_results'),

    # Teacher
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/exams/', views.teacher_exams, name='teacher_exams'),
    path('teacher/exams/create/', views.create_exam, name='create_exam'),
    path('teacher/exams/<int:exam_id>/questions/', views.manage_questions, name='manage_questions'),
    path('teacher/exams/<int:exam_id>/publish/', views.publish_exam, name='publish_exam'),

    # Common
    path('redirect/', views.role_redirect, name='role_redirect'),
    path(
    'teacher/exam/<int:exam_id>/attempts/',
    views.teacher_exam_attempts,
    name='teacher_exam_attempts'
),

    path(
    'teacher/attempt/<int:attempt_id>/detail/',
    views.teacher_attempt_detail,
    name='teacher_attempt_detail'
),
    path(
    'teacher/exam/<int:exam_id>/edit/',
    views.edit_exam,
    name='edit_exam'
),

    path(
    'teacher/exam/<int:exam_id>/delete/',
    views.delete_exam,
    name='delete_exam'
),

    path(
    'teacher/exam/<int:exam_id>/duplicate/',
    views.duplicate_exam,
    name='duplicate_exam'
),
]