from django.urls import path
from . import views

urlpatterns = [
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/result/', views.exam_result, name='exam_result'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/exams/', views.teacher_exams, name='teacher_exams'),
    path('teacher/exams/create/', views.create_exam, name='create_exam'),
    path('student/exams/', views.available_exams, name='available_exams'),
    path('student/results/', views.my_results, name='my_results'),
    path('start-exam/<int:exam_id>/', views.start_exam, name='start_exam'),
    path('teacher/exams/<int:exam_id>/questions/', 
     views.manage_questions, 
     name='manage_questions'),
     path(
    'teacher/exams/<int:exam_id>/publish/',
    views.publish_exam,
    name='publish_exam'
),
]