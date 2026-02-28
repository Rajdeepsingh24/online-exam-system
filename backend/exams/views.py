from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from .models import Exam, Question, Attempt, StudentAnswer
import json
from datetime import datetime
from .models import Subject
from django.db.models import Avg
from django.db.models import Max
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required



# ==========================================
# ROLE BASED REDIRECT AFTER LOGIN
# ==========================================
@login_required
def role_redirect(request):

    # Django Superuser = Admin
    if request.user.is_superuser:
        return redirect('/admin/')

    if request.user.role == 'teacher':
        return redirect('/teacher-dashboard/')

    if request.user.role == 'student':
        return redirect('/student-dashboard/')

    return redirect('/login/')


# ==========================================
# STUDENT DASHBOARD
# ==========================================
@login_required
def student_dashboard(request):

    if request.user.role != 'student':
        return redirect('login')

    exams = Exam.objects.filter(is_active=True)
    attempts = Attempt.objects.filter(student=request.user, completed=True)

    total_exams = exams.count()
    completed = attempts.count()
    pending = total_exams - completed

    performance = 0
    if total_exams > 0:
        performance = int((completed / total_exams) * 100)

    recent_attempts = attempts.order_by('-id')[:5]

    # Chart Data
    chart_labels = json.dumps([a.exam.title for a in recent_attempts][::-1])
    chart_scores = json.dumps([a.score for a in recent_attempts][::-1])

    return render(request, 'dashboard/student_dashboard.html', {
        'exams': exams,
        'total_exams': total_exams,
        'completed': completed,
        'pending': pending,
        'performance': performance,
        'recent_attempts': recent_attempts,
        'chart_labels': chart_labels,
        'chart_scores': chart_scores,
    })
# Latest Exam
    latest_exam = Exam.objects.order_by('-id').first()

    leaderboard = []
    user_rank = None

    if latest_exam:
        attempts = Attempt.objects.filter(
            exam=latest_exam,
            completed=True
        ).select_related('student').order_by('-score')

        leaderboard = list(attempts)

        for index, attempt in enumerate(leaderboard):
            if attempt.student == request.user:
                user_rank = index + 1
                break

        leaderboard = leaderboard[:5]  # Top 5 only

    context = {
        # existing context...
        'leaderboard': leaderboard,
        'latest_exam': latest_exam,
        'user_rank': user_rank
    }

    return render(request, 'dashboard/student_dashboard.html', context)

# ==========================================
# TEACHER DASHBOARD
# ==========================================
@login_required
def teacher_dashboard(request):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exams = Exam.objects.filter(created_by=request.user)
    exams_count = exams.count()

    questions_count = Question.objects.filter(
        exam__created_by=request.user
    ).count()

    attempts = Attempt.objects.filter(
        exam__created_by=request.user,
        completed=True
    ).order_by('-submitted_at')[:5]

    attempts_count = attempts.count()

    return render(request, 'dashboard/teacher_dashboard.html', {
        'exams_count': exams_count,
        'questions_count': questions_count,
        'attempts_count': attempts_count,
        'recent_attempts': attempts,
    })


# ==========================================
# STUDENT EXAM VIEW
# ==========================================
@login_required
def exam_detail(request, exam_id):

    if request.user.role != 'student':
        return HttpResponse("Access Denied")

    exam = get_object_or_404(Exam, id=exam_id)

    current_time = timezone.now()

    # Time validation
    if current_time < exam.start_time:
        return HttpResponse("Exam has not started yet.")

    if current_time > exam.end_time:
        return HttpResponse("Exam time is over.")

    # Get or create attempt
    attempt, created = Attempt.objects.get_or_create(
        student=request.user,
        exam=exam
    )

    if attempt.completed:
        return render(request, 'exams/already_completed.html', {
            'exam': exam
        })

    questions = Question.objects.filter(exam=exam)

    if request.method == "POST":

        score = 0

        for question in questions:
            selected_answer = request.POST.get(f"question_{question.id}")

            if selected_answer:

                # Save or update answer safely
                StudentAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'selected_option': selected_answer}
                )

                if selected_answer == question.correct_answer:
                    score += question.marks

        # Finalize attempt
        attempt.score = score
        attempt.completed = True
        attempt.submitted_at = timezone.now()
        attempt.save()

        return render(request, 'exams/submission_success.html', {
            'exam': exam
        })

    return render(request, 'exams/exam_detail.html', {
        'exam': exam,
        'questions': questions
    })


# ==========================================
# RESULT VIEW
# ==========================================
@login_required
def exam_result(request, exam_id):

    if request.user.role != 'student':
        return HttpResponse("Access Denied")

    try:
        attempt = Attempt.objects.get(
            student=request.user,
            exam_id=exam_id
        )
    except Attempt.DoesNotExist:
        return HttpResponse("Result not available.")

    if not attempt.completed:
        return HttpResponse("You have not completed this exam.")

    return render(request, 'exams/result.html', {
        'attempt': attempt
    })
@login_required
def teacher_exams(request):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exams = Exam.objects.filter(created_by=request.user)

    return render(request, 'dashboard/teacher_exams.html', {
        'exams': exams
    })
@login_required
def create_exam(request):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    subjects = Subject.objects.filter(created_by=request.user)

    if request.method == "POST":
        title = request.POST.get('title')
        duration = request.POST.get('duration')
        total_marks = request.POST.get('total_marks')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        subject_id = request.POST.get('subject')

        subject = Subject.objects.get(id=subject_id)

        exam = Exam.objects.create(
            title=title,
            subject=subject,
            duration_minutes=duration,
            total_marks=total_marks,
            start_time=start_time,
            end_time=end_time,
            created_by=request.user,
            is_active=True
        )

        return redirect('manage_questions', exam_id=exam.id)

    return render(request, 'dashboard/create_exam.html', {
        'subjects': subjects
    })
@login_required
def manage_questions(request, exam_id):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = Question.objects.filter(exam=exam)

    if request.method == "POST":
        question_text = request.POST.get('question_text')
        option_a = request.POST.get('option_a')
        option_b = request.POST.get('option_b')
        option_c = request.POST.get('option_c')
        option_d = request.POST.get('option_d')
        correct_answer = request.POST.get('correct_answer')
        marks = request.POST.get('marks')

        Question.objects.create(
            exam=exam,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            marks=marks
        )

        # auto update total marks
        exam.total_marks = sum(q.marks for q in questions) + int(marks)
        exam.save()

        return redirect('manage_questions', exam_id=exam.id)

    return render(request, 'dashboard/manage_questions.html', {
        'exam': exam,
        'questions': questions
    })
@login_required
def publish_exam(request, exam_id):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        created_by=request.user
    )

    exam.is_active = True
    exam.save()

    return redirect('teacher_exams')

@login_required
def available_exams(request):
    exams = Exam.objects.filter(is_active=True)

    return render(request, 'dashboard/available_exams.html', {
        'exams': exams
    })

@login_required
def my_results(request):
    attempts = Attempt.objects.filter(
        student=request.user,
        completed=True
    ).select_related('exam')

    return render(request, 'dashboard/my_results.html', {
        'attempts': attempts
    })

@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    return HttpResponse(f"You are starting exam: {exam.title}")