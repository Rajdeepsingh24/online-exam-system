from urllib import request

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from .models import Exam, Question, Attempt, StudentAnswer
import json
from datetime import timedelta
from .models import Subject
from django.db.models import Avg, Count, Max
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum



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

    attempts = Attempt.objects.filter(
        student=request.user,
        completed=True
    ).select_related('exam')

    # Basic counts
    total_exams = exams.count()
    completed = attempts.count()
    pending = total_exams - completed

    # ------------------------
    # REAL PERFORMANCE LOGIC
    # ------------------------
    total_possible = 0
    total_obtained = 0

    for attempt in attempts:
        total_possible += attempt.exam.total_marks
        total_obtained += attempt.score

    if total_possible > 0:
        performance = int((total_obtained / total_possible) * 100)
    else:
        performance = 0

    # ------------------------
    # Recent attempts for chart
    # ------------------------
    recent_attempts = attempts.order_by('-id')[:5]

    chart_labels = json.dumps(
        [a.exam.title for a in recent_attempts][::-1]
    )

    chart_scores = json.dumps(
        [a.score for a in recent_attempts][::-1]
    )

    # ------------------------
    # Leaderboard (latest exam)
    # ------------------------
    latest_exam = Exam.objects.order_by('-id').first()

    leaderboard = []
    user_rank = None

    if latest_exam:
        exam_attempts = Attempt.objects.filter(
            exam=latest_exam,
            completed=True
        ).select_related('student').order_by('-score')

        leaderboard = list(exam_attempts)

        for index, attempt in enumerate(leaderboard):
            if attempt.student == request.user:
                user_rank = index + 1
                break

        leaderboard = leaderboard[:5]

    # ------------------------
    # Final Render
    # ------------------------
    return render(request, 'dashboard/student_dashboard.html', {
        'exams': exams,
        'total_exams': total_exams,
        'completed': completed,
        'pending': pending,
        'performance': performance,
        'recent_attempts': recent_attempts,
        'chart_labels': chart_labels,
        'chart_scores': chart_scores,
        'leaderboard': leaderboard,
        'latest_exam': latest_exam,
        'user_rank': user_rank
    })

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

    all_attempts = Attempt.objects.filter(
        exam__created_by=request.user,
        completed=True
    )

    attempts_count = all_attempts.count()
    avg_score = all_attempts.aggregate(avg=Avg('score'))['avg'] or 0

    # ======================
    # Exam Analytics Table
    # ======================
    exam_data = []

    for exam in exams:
        total_questions = Question.objects.filter(exam=exam).count()

        exam_attempts = Attempt.objects.filter(
            exam=exam,
            completed=True
        )

        total_attempts = exam_attempts.count()
        exam_avg_score = exam_attempts.aggregate(avg=Avg('score'))['avg'] or 0
        highest_score = exam_attempts.aggregate(max=Max('score'))['max'] or 0

        exam_data.append({
            'title': exam.title,
            'questions': total_questions,
            'attempts': total_attempts,
            'avg_score': round(exam_avg_score, 2),
            'highest_score': highest_score
        })

    # ======================
    # Chart Data
    # ======================
    exam_titles = []
    attempt_counts = []

    for exam in exams:
        exam_titles.append(exam.title)
        count = Attempt.objects.filter(
            exam=exam,
            completed=True
        ).count()
        attempt_counts.append(count)

    context = {
        'exams': exams,
        'exams_count': exams_count,
        'questions_count': questions_count,
        'attempts_count': attempts_count,
        'avg_score': round(avg_score, 2),
        'recent_attempts': all_attempts.order_by('-submitted_at')[:5],
        'chart_labels': json.dumps(exam_titles),
        'chart_data': json.dumps(attempt_counts),
        'exam_data': exam_data
    }

    return render(request, 'dashboard/teacher_dashboard.html', context)

# ==========================================
# STUDENT EXAM VIEW
# ==========================================
@login_required
def exam_detail(request, exam_id):

    if request.user.role != 'student':
        return HttpResponse("Access Denied")

    exam = get_object_or_404(Exam, id=exam_id)
    current_time = timezone.now()

    # Exam window check
    if current_time < exam.start_time:
        return render(request, 'exams/exam_not_started.html', {
    'exam': exam
})

    if current_time > exam.end_time:
        return render(request, 'exams/exam_closed.html', {
    'exam': exam
})

    # Get or create attempt
    attempt, created = Attempt.objects.get_or_create(
        student=request.user,
        exam=exam
    )

    # If already completed
    if attempt.completed:
        return redirect('exam_result', exam_id=exam.id)

    # Calculate allowed end time based on duration
    allowed_end_time = attempt.started_at + timedelta(
        minutes=exam.duration_minutes
    )

    # If duration exceeded
    if current_time > allowed_end_time:
        attempt.completed = True
        attempt.submitted_at = allowed_end_time
        attempt.save()
        return redirect('exam_result', exam_id=exam.id)

    # Remaining time for frontend
    remaining_seconds = int(
        (allowed_end_time - current_time).total_seconds()
    )

    questions = Question.objects.filter(exam=exam)

    # ==========================
    # POST (Submit Exam)
    # ==========================
    if request.method == "POST":

        # Backend time validation again (anti-hack)
        if timezone.now() > allowed_end_time:
            attempt.completed = True
            attempt.submitted_at = allowed_end_time
            attempt.save()
            return redirect('exam_result', exam_id=exam.id)

        score = 0

        for question in questions:
            selected_answer = request.POST.get(f"question_{question.id}")

            if selected_answer:
                StudentAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'selected_option': selected_answer}
                )

                if selected_answer == question.correct_answer:
                    score += question.marks

        attempt.score = score
        attempt.completed = True
        attempt.submitted_at = timezone.now()
        attempt.save()

        return redirect('exam_result', exam_id=exam.id)

    # ==========================
    # GET (Load Exam Page)
    # ==========================
    return render(request, 'exams/exam_detail.html', {
        'exam': exam,
        'questions': questions,
        'remaining_seconds': remaining_seconds
    })

# ==========================================
# RESULT VIEW
# ==========================================
@login_required
def exam_result(request, exam_id):

    if request.user.role != 'student':
        return HttpResponse("Access Denied")

    attempt = get_object_or_404(
        Attempt,
        student=request.user,
        exam_id=exam_id,
        completed=True
    )

    total_marks = Question.objects.filter(
        exam=attempt.exam
    ).aggregate(total=Sum('marks'))['total'] or 0

    answers = StudentAnswer.objects.filter(
        attempt=attempt
    ).select_related('question')

    correct_count = 0

    for ans in answers:
        if ans.selected_option == ans.question.correct_answer:
            correct_count += 1

    context = {
        'attempt': attempt,
        'total_marks': total_marks,
        'answers': answers,
        'correct_count': correct_count,
    }

    return render(request, 'exams/result.html', context)
@login_required
def teacher_exams(request):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exams = Exam.objects.filter(created_by=request.user)

    exam_data = []

    for exam in exams:
        question_count = exam.question_set.count()

        attempt_count = Attempt.objects.filter(
            exam=exam,
            completed=True
        ).count()

        exam_data.append({
            "id": exam.id,
            "title": exam.title,
            "duration": exam.duration_minutes,
            "is_active": exam.is_active,
            "questions": question_count,
            "attempts": attempt_count,
        })

    return render(request, "dashboard/teacher_exams.html", {
        "exam_data": exam_data
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
def teacher_exam_attempts(request, exam_id):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    attempts = Attempt.objects.filter(
        exam=exam,
        completed=True
    ).select_related('student').order_by('-submitted_at')

    return render(request, 'dashboard/teacher_exam_attempts.html', {
        'exam': exam,
        'attempts': attempts
    })


@login_required
def teacher_attempt_detail(request, attempt_id):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    attempt = get_object_or_404(
        Attempt,
        id=attempt_id,
        exam__created_by=request.user
    )

    answers = StudentAnswer.objects.filter(
        attempt=attempt
    ).select_related('question')

    return render(request, 'dashboard/teacher_attempt_detail.html', {
        'attempt': attempt,
        'answers': answers
    })
@login_required
def edit_exam(request, exam_id):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        created_by=request.user
    )

    subjects = Subject.objects.filter(created_by=request.user)

    if request.method == "POST":
        exam.title = request.POST.get('title')
        exam.duration_minutes = request.POST.get('duration')
        exam.total_marks = request.POST.get('total_marks')
        exam.start_time = request.POST.get('start_time')
        exam.end_time = request.POST.get('end_time')
        exam.subject_id = request.POST.get('subject')
        exam.save()

        return redirect('teacher_exams')

    return render(request, 'dashboard/edit_exam.html', {
        'exam': exam,
        'subjects': subjects
    })
@login_required
def delete_exam(request, exam_id):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        created_by=request.user
    )

    exam.delete()

    return redirect('teacher_exams')
@login_required
def duplicate_exam(request, exam_id):

    if request.user.role != 'teacher':
        return HttpResponse("Access Denied")

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        created_by=request.user
    )

    new_exam = Exam.objects.create(
        title=exam.title + " (Copy)",
        subject=exam.subject,
        duration_minutes=exam.duration_minutes,
        total_marks=exam.total_marks,
        start_time=exam.start_time,
        end_time=exam.end_time,
        created_by=request.user,
        is_active=False
    )

    # Copy questions
    for question in exam.question_set.all():
        question.pk = None
        question.exam = new_exam
        question.save()

    return redirect('teacher_exams')