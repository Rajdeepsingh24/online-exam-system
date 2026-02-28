from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from exams import views


urlpatterns = [

    # =========================
    # Public Pages
    # =========================
    path('', TemplateView.as_view(template_name="home.html"), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),


    # =========================
    # Authentication
    # =========================
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html'
        ),
        name='password_reset'
    ),

    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),


    # =========================
    # Role Redirect & Dashboards
    # =========================
    path('redirect/', views.role_redirect, name='redirect'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),


    # =========================
    # Admin Panel
    # =========================
    path('admin/', admin.site.urls),


    # =========================
    # Exams App Routes
    # =========================
    path('exams/', include('exams.urls')),
]