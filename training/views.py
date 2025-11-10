from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponseForbidden, FileResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
import os
import mimetypes

# Helper decorator for staff-only views
def staff_required(function=None, redirect_url='/employee/'):
    """
    Decorator to restrict access to staff and superuser only
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_staff or u.is_superuser,
        login_url=redirect_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
from .models import (
    Course, CourseModule, Lesson, CourseMaterial, CourseEnrollment,
    LessonProgress, Quiz, QuizQuestion, QuizAttempt, Certificate,
    Instructor, LearningPath
)
from .forms import (
    CourseForm, CourseEnrollmentForm, InstructorForm,
    BulkEnrollmentForm
)
from hr.models import Employee


# ==================== Dashboard Views ====================

@login_required
def dashboard(request):
    """Main LMS dashboard"""
    # Get employee
    try:
        employee = request.user.employee
    except:
        return redirect('training:course_list')

    # Get employee enrollments
    my_enrollments = CourseEnrollment.objects.filter(employee=employee).select_related('course', 'course__instructor')

    # Statistics
    total_enrolled = my_enrollments.count()
    in_progress = my_enrollments.filter(status='in_progress').count()
    completed = my_enrollments.filter(status='completed').count()
    avg_progress = my_enrollments.aggregate(Avg('progress_percentage'))['progress_percentage__avg'] or 0

    # Recent enrollments
    recent_enrollments = my_enrollments.order_by('-last_accessed', '-enrollment_date')[:5]

    # Available courses
    enrolled_course_ids = my_enrollments.values_list('course_id', flat=True)
    available_courses = Course.objects.filter(status='published').exclude(id__in=enrolled_course_ids)[:6]

    context = {
        'total_enrolled': total_enrolled,
        'in_progress': in_progress,
        'completed': completed,
        'avg_progress': round(avg_progress, 1),
        'recent_enrollments': recent_enrollments,
        'available_courses': available_courses,
        'employee': employee,
    }
    return render(request, 'training/dashboard.html', context)


# ==================== Course Views ====================

@login_required
def course_list(request):
    """List all published courses with filters"""
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    level_filter = request.GET.get('level', '')
    search_query = request.GET.get('search', '')

    # Base queryset - published courses only
    courses = Course.objects.filter(status='published').select_related('instructor', 'instructor__user')

    # Apply filters
    if category_filter:
        courses = courses.filter(category=category_filter)

    if level_filter:
        courses = courses.filter(level=level_filter)

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(instructor__user__first_name__icontains=search_query) |
            Q(instructor__user__last_name__icontains=search_query)
        )

    # Get category counts
    all_courses = Course.objects.filter(status='published')
    category_counts = {
        'all': all_courses.count(),
        'technical': all_courses.filter(category='technical').count(),
        'soft_skills': all_courses.filter(category='soft_skills').count(),
        'leadership': all_courses.filter(category='leadership').count(),
        'compliance': all_courses.filter(category='compliance').count(),
    }

    # Order by created date
    courses = courses.order_by('-created_at')

    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'category_filter': category_filter,
        'level_filter': level_filter,
        'search_query': search_query,
        'category_counts': category_counts,
        'category_choices': Course.CATEGORY_CHOICES,
        'level_choices': Course.LEVEL_CHOICES,
    }
    return render(request, 'training/course_list.html', context)


@login_required
def course_detail(request, pk):
    """View course details"""
    course = get_object_or_404(Course, pk=pk)

    # Get course modules and lessons
    modules = course.modules.prefetch_related('lessons').order_by('order')

    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    try:
        employee = request.user.employee
        enrollment = CourseEnrollment.objects.filter(course=course, employee=employee).first()
        is_enrolled = enrollment is not None
    except:
        pass

    # Get course statistics
    enrollments = course.enrollments.all()
    total_enrolled = enrollments.count()
    completed_count = enrollments.filter(status='completed').count()

    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'total_enrolled': total_enrolled,
        'completed_count': completed_count,
    }
    return render(request, 'training/course_detail.html', context)


@login_required
@require_POST
def course_enroll(request, pk):
    """Enroll current user in a course"""
    course = get_object_or_404(Course, pk=pk, status='published')

    try:
        employee = request.user.employee
    except:
        messages.error(request, _('You must be registered as an employee to enroll in courses.'))
        return redirect('training:course_detail', pk=pk)

    # Check if already enrolled
    if CourseEnrollment.objects.filter(course=course, employee=employee).exists():
        messages.warning(request, _('You are already enrolled in this course.'))
        return redirect('training:course_detail', pk=pk)

    # Check if course is full
    if course.is_full:
        messages.error(request, _('This course is full.'))
        return redirect('training:course_detail', pk=pk)

    # Create enrollment
    enrollment = CourseEnrollment.objects.create(
        course=course,
        employee=employee,
        enrollment_date=timezone.now().date(),
        status='enrolled'
    )

    messages.success(request, _('Successfully enrolled in the course!'))
    return redirect('training:learn_course', pk=course.pk)


@login_required
def learn_course(request, pk):
    """Course learning interface for enrolled students"""
    course = get_object_or_404(Course, pk=pk)

    try:
        employee = request.user.employee
        enrollment = get_object_or_404(CourseEnrollment, course=course, employee=employee)
    except:
        messages.error(request, _('You are not enrolled in this course.'))
        return redirect('training:course_detail', pk=pk)

    # Update last accessed
    enrollment.last_accessed = timezone.now()
    enrollment.save()

    # Get course modules and lessons with progress
    modules = course.modules.prefetch_related('lessons').order_by('order')

    # Get lesson progress
    lesson_progress = {
        lp.lesson_id: lp
        for lp in LessonProgress.objects.filter(enrollment=enrollment)
    }

    # Attach progress to lessons
    for module in modules:
        for lesson in module.lessons.all():
            lesson.progress = lesson_progress.get(lesson.id)

    # Get first incomplete lesson
    first_incomplete = None
    for module in modules:
        for lesson in module.lessons.all():
            if not lesson.progress or not lesson.progress.completed:
                first_incomplete = lesson
                break
        if first_incomplete:
            break

    context = {
        'course': course,
        'enrollment': enrollment,
        'modules': modules,
        'first_incomplete': first_incomplete,
    }
    return render(request, 'training/learn_course.html', context)


@login_required
def lesson_view(request, course_pk, lesson_pk):
    """View a specific lesson"""
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, module__course=course)

    try:
        employee = request.user.employee
        enrollment = get_object_or_404(CourseEnrollment, course=course, employee=employee)
    except:
        messages.error(request, _('You are not enrolled in this course.'))
        return redirect('training:course_detail', pk=course_pk)

    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    if created or not lesson_progress.started_at:
        lesson_progress.started_at = timezone.now()
        lesson_progress.save()

    # Update enrollment status
    if enrollment.status == 'enrolled':
        enrollment.status = 'in_progress'
        enrollment.start_date = timezone.now().date()
        enrollment.save()

    # Get lesson materials
    materials = lesson.materials.all()

    # Process video URL to get embed URL
    video_embed_url = None
    if lesson.video_url:
        video_url = lesson.video_url
        if 'youtube.com/watch?v=' in video_url:
            video_id = video_url.split('watch?v=')[-1].split('&')[0]
            video_embed_url = f'https://www.youtube.com/embed/{video_id}'
        elif 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[-1].split('?')[0]
            video_embed_url = f'https://www.youtube.com/embed/{video_id}'
        elif 'youtube.com/embed/' in video_url:
            video_embed_url = video_url
        elif 'vimeo.com/' in video_url:
            video_id = video_url.split('vimeo.com/')[-1].split('?')[0]
            video_embed_url = f'https://player.vimeo.com/video/{video_id}'
        else:
            # Direct video URL
            video_embed_url = video_url

    # Get next and previous lessons
    all_lessons = Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
    lesson_list = list(all_lessons)
    try:
        current_index = lesson_list.index(lesson)
        next_lesson = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None
        prev_lesson = lesson_list[current_index - 1] if current_index > 0 else None
    except ValueError:
        next_lesson = None
        prev_lesson = None

    context = {
        'course': course,
        'lesson': lesson,
        'lesson_progress': lesson_progress,
        'materials': materials,
        'enrollment': enrollment,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
        'video_embed_url': video_embed_url,
    }
    return render(request, 'training/lesson_view.html', context)


@login_required
@require_POST
def lesson_complete(request, course_pk, lesson_pk):
    """Mark a lesson as complete"""
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, module__course=course)

    try:
        employee = request.user.employee
        enrollment = get_object_or_404(CourseEnrollment, course=course, employee=employee)
    except:
        return JsonResponse({'success': False, 'error': 'Not enrolled'}, status=403)

    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    # Mark as complete
    lesson_progress.mark_complete()

    # Check if all lessons are complete
    total_lessons = course.total_lessons
    completed_lessons = LessonProgress.objects.filter(enrollment=enrollment, completed=True).count()

    if total_lessons > 0 and completed_lessons >= total_lessons:
        # Check if there's a final quiz
        final_quiz = Quiz.objects.filter(course=course, is_final_exam=True).first()
        if final_quiz:
            # Check if passed final quiz
            passed_attempt = QuizAttempt.objects.filter(
                enrollment=enrollment,
                quiz=final_quiz,
                passed=True
            ).exists()
            if passed_attempt:
                enrollment.status = 'completed'
                enrollment.completion_date = timezone.now().date()
                enrollment.save()
        else:
            # No final quiz, mark as completed
            enrollment.status = 'completed'
            enrollment.completion_date = timezone.now().date()
            enrollment.save()

    return JsonResponse({
        'success': True,
        'progress': enrollment.progress_percentage,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
    })


# ==================== Enrollment Management Views ====================

@login_required
def enrollment_list(request):
    """List all enrollments with filters (admin view)"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    course_filter = request.GET.get('course', '')
    search_query = request.GET.get('search', '')

    # Base queryset
    enrollments = CourseEnrollment.objects.select_related('employee', 'course', 'course__instructor')

    # Apply filters
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)

    if course_filter:
        enrollments = enrollments.filter(course_id=course_filter)

    if search_query:
        enrollments = enrollments.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(course__title__icontains=search_query) |
            Q(course__code__icontains=search_query)
        )

    # Get status counts
    all_enrollments = CourseEnrollment.objects.all()
    status_counts = {
        'all': all_enrollments.count(),
        'enrolled': all_enrollments.filter(status='enrolled').count(),
        'in_progress': all_enrollments.filter(status='in_progress').count(),
        'completed': all_enrollments.filter(status='completed').count(),
    }

    # Order by enrollment date
    enrollments = enrollments.order_by('-enrollment_date')

    # Pagination
    paginator = Paginator(enrollments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get courses for filter
    courses = Course.objects.all().order_by('title')

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'course_filter': course_filter,
        'search_query': search_query,
        'status_counts': status_counts,
        'courses': courses,
        'status_choices': CourseEnrollment.STATUS_CHOICES,
    }
    return render(request, 'training/enrollment_list.html', context)


@login_required
def enrollment_detail(request, pk):
    """View enrollment details"""
    enrollment = get_object_or_404(
        CourseEnrollment.objects.select_related('employee', 'course', 'course__instructor'),
        pk=pk
    )

    # Get lesson progress
    lesson_progress = enrollment.lesson_progress.select_related('lesson', 'lesson__module').order_by('lesson__module__order', 'lesson__order')

    # Get quiz attempts
    quiz_attempts = enrollment.quiz_attempts.select_related('quiz').order_by('-started_at')

    context = {
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'quiz_attempts': quiz_attempts,
    }
    return render(request, 'training/enrollment_detail.html', context)


@login_required
def enrollment_create(request):
    """Create a new enrollment"""
    if request.method == 'POST':
        form = CourseEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, _('Enrollment created successfully!'))
            return redirect('training:enrollment_list')
    else:
        form = CourseEnrollmentForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'training/enrollment_form.html', context)


@login_required
def enrollment_delete(request, pk):
    """Delete an enrollment"""
    enrollment = get_object_or_404(CourseEnrollment, pk=pk)

    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, _('Enrollment deleted successfully!'))
        return redirect('training:enrollment_list')

    context = {
        'enrollment': enrollment,
    }
    return render(request, 'training/enrollment_confirm_delete.html', context)


# ==================== Quiz Views ====================

@login_required
def quiz_take(request, course_pk, quiz_pk):
    """Take a quiz"""
    course = get_object_or_404(Course, pk=course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk, course=course)

    try:
        employee = request.user.employee
        enrollment = get_object_or_404(CourseEnrollment, course=course, employee=employee)
    except:
        messages.error(request, _('You are not enrolled in this course.'))
        return redirect('training:course_detail', pk=course_pk)

    # Check attempts
    attempt_count = QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz).count()
    if attempt_count >= quiz.max_attempts:
        messages.error(request, _('You have reached the maximum number of attempts for this quiz.'))
        return redirect('training:learn_course', pk=course_pk)

    # Get or create quiz attempt
    quiz_attempt = QuizAttempt.objects.filter(
        enrollment=enrollment,
        quiz=quiz,
        status='in_progress'
    ).first()

    if not quiz_attempt:
        quiz_attempt = QuizAttempt.objects.create(
            enrollment=enrollment,
            quiz=quiz,
            attempt_number=attempt_count + 1
        )

    # Get questions
    questions = quiz.questions.all().order_by('order')
    if quiz.randomize_questions:
        questions = questions.order_by('?')

    context = {
        'course': course,
        'quiz': quiz,
        'quiz_attempt': quiz_attempt,
        'questions': questions,
        'attempt_count': attempt_count,
    }
    return render(request, 'training/quiz_take.html', context)


@login_required
@require_POST
def quiz_submit(request, course_pk, quiz_pk, attempt_pk):
    """Submit quiz answers"""
    course = get_object_or_404(Course, pk=course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk, course=course)
    quiz_attempt = get_object_or_404(QuizAttempt, pk=attempt_pk, quiz=quiz)

    try:
        employee = request.user.employee
        enrollment = get_object_or_404(CourseEnrollment, course=course, employee=employee)
    except:
        return JsonResponse({'success': False, 'error': 'Not enrolled'}, status=403)

    # Check ownership
    if quiz_attempt.enrollment != enrollment:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    # Get answers from POST data
    answers = {}
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = key.split('_')[1]
            answers[question_id] = value

    # Save answers and calculate score
    quiz_attempt.answers = answers
    quiz_attempt.status = 'completed'
    quiz_attempt.completed_at = timezone.now()
    quiz_attempt.calculate_score()

    # Update enrollment final score if this is the final exam
    if quiz.is_final_exam:
        enrollment.final_score = quiz_attempt.score
        if quiz_attempt.passed:
            enrollment.status = 'completed'
            enrollment.completion_date = timezone.now().date()
            # Generate certificate
            if not hasattr(enrollment, 'certificate'):
                Certificate.objects.create(enrollment=enrollment)
                enrollment.certificate_issued = True
                enrollment.certificate_date = timezone.now().date()
        enrollment.save()

    return JsonResponse({
        'success': True,
        'score': float(quiz_attempt.score),
        'passed': quiz_attempt.passed,
        'redirect_url': f'/training/courses/{course_pk}/quiz/{quiz_pk}/result/{quiz_attempt.pk}/'
    })


@login_required
def quiz_result(request, course_pk, quiz_pk, attempt_pk):
    """View quiz results"""
    course = get_object_or_404(Course, pk=course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk, course=course)
    quiz_attempt = get_object_or_404(QuizAttempt, pk=attempt_pk, quiz=quiz)

    try:
        employee = request.user.employee
        enrollment = get_object_or_404(CourseEnrollment, course=course, employee=employee)
    except:
        messages.error(request, _('You are not enrolled in this course.'))
        return redirect('training:course_detail', pk=course_pk)

    # Check ownership
    if quiz_attempt.enrollment != enrollment:
        return HttpResponseForbidden()

    # Get questions with answers
    questions = quiz.questions.all().order_by('order')

    # Add user answers to questions
    for question in questions:
        question.user_answer = quiz_attempt.answers.get(str(question.id), '')
        question.is_correct = question.user_answer.strip().lower() == question.correct_answer.strip().lower()

    context = {
        'course': course,
        'quiz': quiz,
        'quiz_attempt': quiz_attempt,
        'questions': questions,
        'enrollment': enrollment,
    }
    return render(request, 'training/quiz_result.html', context)


# ==================== Reports Views ====================

@login_required
def reports_overview(request):
    """LMS reports and analytics overview"""
    # Overall statistics
    total_courses = Course.objects.filter(status='published').count()
    total_enrollments = CourseEnrollment.objects.count()
    total_completed = CourseEnrollment.objects.filter(status='completed').count()
    avg_completion_rate = (total_completed / total_enrollments * 100) if total_enrollments > 0 else 0

    # Top courses by enrollment
    top_courses = Course.objects.filter(status='published').annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]

    # Recent completions
    recent_completions = CourseEnrollment.objects.filter(
        status='completed'
    ).select_related('employee', 'course').order_by('-completion_date')[:10]

    context = {
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_completed': total_completed,
        'avg_completion_rate': round(avg_completion_rate, 1),
        'top_courses': top_courses,
        'recent_completions': recent_completions,
    }
    return render(request, 'training/reports_overview.html', context)


# ==================== Course Management Views ====================

@login_required
@staff_required
def course_create(request):
    """Create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, _('Course created successfully!'))
            return redirect('training:course_edit', pk=course.pk)
    else:
        form = CourseForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'training/course_form.html', context)


@login_required
@staff_required
def course_edit(request, pk):
    """Edit an existing course"""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, _('Course updated successfully!'))
            return redirect('training:course_edit', pk=course.pk)
    else:
        form = CourseForm(instance=course)

    # Get modules for this course
    modules = course.modules.prefetch_related('lessons').order_by('order')

    context = {
        'form': form,
        'course': course,
        'modules': modules,
        'action': 'Edit',
    }
    return render(request, 'training/course_form.html', context)


@login_required
@staff_required
def course_delete(request, pk):
    """Delete a course"""
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        course.delete()
        messages.success(request, _('Course deleted successfully!'))
        return redirect('training:course_list')

    context = {
        'course': course,
    }
    return render(request, 'training/course_confirm_delete.html', context)


# ==================== Module Management Views ====================

@login_required
@staff_required
def module_create(request, course_pk):
    """Create a new module for a course"""
    course = get_object_or_404(Course, pk=course_pk)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        order = request.POST.get('order', 0)

        module = CourseModule.objects.create(
            course=course,
            title=title,
            description=description,
            order=order
        )
        messages.success(request, _('Module created successfully!'))
        return redirect('training:course_edit', pk=course_pk)

    context = {
        'course': course,
    }
    return render(request, 'training/module_form.html', context)


@login_required
@staff_required
def module_edit(request, pk):
    """Edit a module"""
    module = get_object_or_404(CourseModule, pk=pk)

    if request.method == 'POST':
        module.title = request.POST.get('title')
        module.description = request.POST.get('description', '')
        module.order = request.POST.get('order', module.order)
        module.save()
        messages.success(request, _('Module updated successfully!'))
        return redirect('training:course_edit', pk=module.course.pk)

    # Get lessons for this module
    lessons = module.lessons.order_by('order')

    context = {
        'module': module,
        'lessons': lessons,
    }
    return render(request, 'training/module_form.html', context)


@login_required
@staff_required
@require_POST
def module_delete(request, pk):
    """Delete a module"""
    module = get_object_or_404(CourseModule, pk=pk)
    course_pk = module.course.pk

    module.delete()
    messages.success(request, _('Module deleted successfully!'))
    return redirect('training:course_edit', pk=course_pk)


# ==================== Lesson Management Views ====================

@login_required
@staff_required
def lesson_create(request, module_pk):
    """Create a new lesson for a module"""
    module = get_object_or_404(CourseModule, pk=module_pk)

    if request.method == 'POST':
        title = request.POST.get('title')
        content_type = request.POST.get('content_type', 'document')
        description = request.POST.get('description', '')
        content = request.POST.get('content', '')
        video_url = request.POST.get('video_url', '')
        duration_minutes = request.POST.get('duration_minutes', 0)
        order = request.POST.get('order', 0)
        is_mandatory = request.POST.get('is_mandatory') == 'on'

        lesson = Lesson.objects.create(
            module=module,
            title=title,
            content_type=content_type,
            description=description,
            content=content,
            video_url=video_url,
            duration_minutes=duration_minutes,
            order=order,
            is_mandatory=is_mandatory
        )
        messages.success(request, _('Lesson created successfully!'))
        return redirect('training:module_edit', pk=module_pk)

    context = {
        'module': module,
        'content_type_choices': Lesson.CONTENT_TYPE_CHOICES,
    }
    return render(request, 'training/lesson_form.html', context)


@login_required
@staff_required
def lesson_edit(request, pk):
    """Edit a lesson"""
    lesson = get_object_or_404(Lesson, pk=pk)

    if request.method == 'POST':
        lesson.title = request.POST.get('title')
        lesson.content_type = request.POST.get('content_type', 'document')
        lesson.description = request.POST.get('description', '')
        lesson.content = request.POST.get('content', '')
        lesson.video_url = request.POST.get('video_url', '')
        lesson.duration_minutes = request.POST.get('duration_minutes', 0)
        lesson.order = request.POST.get('order', lesson.order)
        lesson.is_mandatory = request.POST.get('is_mandatory') == 'on'
        lesson.save()
        messages.success(request, _('Lesson updated successfully!'))
        return redirect('training:module_edit', pk=lesson.module.pk)

    # Get materials for this lesson
    materials = lesson.materials.all()

    context = {
        'lesson': lesson,
        'materials': materials,
        'content_type_choices': Lesson.CONTENT_TYPE_CHOICES,
    }
    return render(request, 'training/lesson_form.html', context)


@login_required
@staff_required
@require_POST
def lesson_delete(request, pk):
    """Delete a lesson"""
    lesson = get_object_or_404(Lesson, pk=pk)
    module_pk = lesson.module.pk

    lesson.delete()
    messages.success(request, _('Lesson deleted successfully!'))
    return redirect('training:module_edit', pk=module_pk)


# ==================== Material Management Views ====================

@login_required
@staff_required
def material_upload(request, lesson_pk):
    """Upload material for a lesson"""
    lesson = get_object_or_404(Lesson, pk=lesson_pk)

    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')

        if file:
            material = CourseMaterial.objects.create(
                lesson=lesson,
                title=title,
                file=file
            )
            messages.success(request, _('Material uploaded successfully!'))
        else:
            messages.error(request, _('Please select a file to upload.'))

        return redirect('training:lesson_edit', pk=lesson_pk)

    context = {
        'lesson': lesson,
    }
    return render(request, 'training/material_upload.html', context)


@login_required
@staff_required
@require_POST
def material_delete(request, pk):
    """Delete a material"""
    material = get_object_or_404(CourseMaterial, pk=pk)
    lesson_pk = material.lesson.pk

    material.delete()
    messages.success(request, _('Material deleted successfully!'))
    return redirect('training:lesson_edit', pk=lesson_pk)


@login_required
@xframe_options_exempt
def serve_course_material(request, material_id):
    """
    Serve course material files without X-Frame-Options restriction
    This allows PDFs and other documents to be embedded in iframes
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"serve_course_material called for material_id={material_id}, user={request.user}")

    material = get_object_or_404(CourseMaterial, pk=material_id)
    logger.info(f"Material found: {material.title}, file: {material.file.name}")

    # Check if user has access to this material
    # User must be enrolled in the course or be staff
    course = material.lesson.module.course

    try:
        employee = request.user.employee
        is_enrolled = CourseEnrollment.objects.filter(
            course=course,
            employee=employee
        ).exists()

        logger.info(f"Enrollment check: is_enrolled={is_enrolled}, is_staff={request.user.is_staff}")

        if not (is_enrolled or request.user.is_staff or request.user.is_superuser):
            logger.warning(f"Access denied for user {request.user}")
            return HttpResponseForbidden("You don't have access to this material")
    except Exception as e:
        logger.error(f"Error checking enrollment: {e}")
        if not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden("You don't have access to this material")

    # Get the file path
    file_path = material.file.path

    if not os.path.exists(file_path):
        return HttpResponse("File not found", status=404)

    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'

    # Open and serve the file
    try:
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)

        # Set content disposition based on file type
        # For PDFs, display inline; for others, suggest download
        if content_type == 'application/pdf':
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        else:
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'

        # CRITICAL: Allow iframe embedding by removing X-Frame-Options
        # The @xframe_options_exempt decorator should handle this, but let's be explicit

        # Don't set X-Frame-Options at all for same-origin iframes
        # This allows the PDF to be displayed in an iframe on the same domain

        return response
    except Exception as e:
        return HttpResponse(f"Error serving file: {str(e)}", status=500)


# ==================== Mock Data Generation ====================

@login_required
def generate_mock_data(request):
    """Generate mock LMS data for testing (staff only)"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to generate mock data.'))
        return redirect('training:dashboard')

    try:
        # Get or create instructor
        try:
            employee = request.user.employee
            instructor, created = Instructor.objects.get_or_create(
                user=request.user,
                defaults={
                    'bio': 'Experienced instructor with expertise in multiple domains.',
                    'expertise': 'Leadership, Communication, Technical Training',
                    'is_active': True
                }
            )
        except:
            messages.error(request, _('Could not find employee profile. Please ensure you have an employee record.'))
            return redirect('training:dashboard')

        courses_created = []

        # Course 1: Leadership and Communication
        course1, created = Course.objects.update_or_create(
            code='LEAD-101',
            defaults={
                'title': 'Leadership and Communication Essentials',
                'description': '''Master the fundamental skills of effective leadership and communication.

This comprehensive course covers everything from self-awareness and emotional intelligence to team management and strategic communication. Learn practical techniques that you can apply immediately in your workplace.

Throughout this course, you'll develop:
• Core leadership competencies and styles
• Effective communication strategies for different audiences
• Conflict resolution and negotiation skills
• Team building and motivation techniques
• Decision-making and problem-solving frameworks

Perfect for aspiring leaders, new managers, and anyone looking to enhance their leadership capabilities.''',
                'category': 'leadership',
                'level': 'intermediate',
                'instructor': instructor,
                'duration_hours': 24,
                'max_students': 30,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False
            }
        )
        if created:
            courses_created.append('Leadership and Communication Essentials')

        # Clear existing modules for this course
        course1.modules.all().delete()

        # Module 1
        module1 = CourseModule.objects.create(
            course=course1,
            title='Introduction to Leadership',
            description='Understand the fundamentals of leadership and discover your leadership style.',
            order=1
        )

        Lesson.objects.create(
            module=module1,
            title='What is Leadership?',
            content_type='text',
            duration_minutes=30,
            description='Explore the definition and core concepts of leadership',
            content='''<h2>Understanding Leadership</h2>
<p>Leadership is the art of motivating a group of people to act toward achieving a common goal. In a business setting, this can mean directing workers and colleagues with a strategy to meet the company's needs.</p>

<h3>Key Characteristics of Effective Leaders:</h3>
<ul>
<li><strong>Vision:</strong> The ability to see the big picture and set clear goals</li>
<li><strong>Communication:</strong> Articulating ideas clearly and listening actively</li>
<li><strong>Integrity:</strong> Being honest, ethical, and consistent</li>
<li><strong>Empathy:</strong> Understanding and relating to others' perspectives</li>
<li><strong>Decisiveness:</strong> Making timely and well-considered decisions</li>
</ul>''',
            order=1,
            is_mandatory=True
        )

        Lesson.objects.create(
            module=module1,
            title='Leadership Styles and Approaches',
            content_type='video',
            duration_minutes=45,
            description='Discover different leadership styles and when to use them',
            content='''<h2>Leadership Styles</h2>
<p>Different situations call for different leadership approaches.</p>

<h3>Common Leadership Styles:</h3>
<h4>1. Transformational Leadership</h4>
<p>Inspires and motivates followers to exceed expectations.</p>

<h4>2. Servant Leadership</h4>
<p>Focuses on serving others and prioritizing their needs.</p>

<h4>3. Democratic Leadership</h4>
<p>Involves team members in decision-making processes.</p>''',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            order=2,
            is_mandatory=True
        )

        # Module 2
        module2 = CourseModule.objects.create(
            course=course1,
            title='Communication Fundamentals',
            description='Master the essential skills of effective communication in professional settings.',
            order=2
        )

        Lesson.objects.create(
            module=module2,
            title='Principles of Effective Communication',
            content_type='text',
            duration_minutes=35,
            description='Learn the core principles that make communication effective',
            content='''<h2>The Foundation of Effective Communication</h2>
<p>Communication is the lifeblood of any organization. Effective communication ensures that information flows smoothly, relationships strengthen, and goals are achieved.</p>

<h3>Barriers to Effective Communication</h3>
<ul>
<li><strong>Physical barriers:</strong> Noise, distance, technical issues</li>
<li><strong>Psychological barriers:</strong> Stress, emotions, attitudes</li>
<li><strong>Language barriers:</strong> Jargon, technical terms</li>
<li><strong>Cultural barriers:</strong> Different norms and expectations</li>
</ul>''',
            order=1,
            is_mandatory=True
        )

        Lesson.objects.create(
            module=module2,
            title='Active Listening Skills',
            content_type='video',
            duration_minutes=40,
            description='Develop your ability to truly hear and understand others',
            content='''<h2>The Power of Active Listening</h2>
<p>Active listening is one of the most important skills a leader can develop.</p>

<h3>Components of Active Listening</h3>
<ul>
<li>Pay attention</li>
<li>Show you're listening</li>
<li>Provide feedback</li>
<li>Defer judgment</li>
<li>Respond appropriately</li>
</ul>''',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            order=2,
            is_mandatory=True
        )

        # Course 2: Technical Skills
        course2, created = Course.objects.update_or_create(
            code='TECH-101',
            defaults={
                'title': 'Introduction to Python Programming',
                'description': '''Learn Python programming from scratch. This beginner-friendly course covers all the fundamentals you need to start coding in Python.

What you'll learn:
• Python syntax and basic programming concepts
• Data types, variables, and operators
• Control flow and loops
• Functions and modules
• Object-oriented programming basics
• Working with files and data

No prior programming experience required!''',
                'category': 'technical',
                'level': 'beginner',
                'instructor': instructor,
                'duration_hours': 20,
                'max_students': 50,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False
            }
        )
        if created:
            courses_created.append('Introduction to Python Programming')

        course2.modules.all().delete()

        module3 = CourseModule.objects.create(
            course=course2,
            title='Getting Started with Python',
            description='Set up your development environment and write your first Python program.',
            order=1
        )

        Lesson.objects.create(
            module=module3,
            title='Installing Python',
            content_type='text',
            duration_minutes=20,
            description='Download and install Python on your computer',
            content='''<h2>Setting Up Python</h2>
<p>Before we start coding, we need to install Python.</p>

<h3>Installation Steps:</h3>
<ol>
<li>Visit python.org</li>
<li>Download the latest version</li>
<li>Run the installer</li>
<li>Verify installation</li>
</ol>''',
            order=1,
            is_mandatory=True
        )

        Lesson.objects.create(
            module=module3,
            title='Your First Python Program',
            content_type='text',
            duration_minutes=25,
            description='Write and run your first Python code',
            content='''<h2>Hello, World!</h2>
<p>Let's write your first Python program.</p>

<pre><code>print("Hello, World!")</code></pre>

<p>This simple program outputs text to the screen.</p>''',
            order=2,
            is_mandatory=True
        )

        # Course 3: Soft Skills
        course3, created = Course.objects.update_or_create(
            code='SOFT-101',
            defaults={
                'title': 'Time Management and Productivity',
                'description': '''Master time management techniques to boost your productivity and achieve better work-life balance.

Learn how to:
• Prioritize tasks effectively
• Overcome procrastination
• Use time management tools and techniques
• Manage interruptions and distractions
• Set and achieve goals
• Maintain work-life balance''',
                'category': 'soft_skills',
                'level': 'beginner',
                'instructor': instructor,
                'duration_hours': 8,
                'max_students': 40,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False
            }
        )
        if created:
            courses_created.append('Time Management and Productivity')

        course3.modules.all().delete()

        module4 = CourseModule.objects.create(
            course=course3,
            title='Fundamentals of Time Management',
            description='Learn the core principles of effective time management.',
            order=1
        )

        Lesson.objects.create(
            module=module4,
            title='Understanding Time Management',
            content_type='text',
            duration_minutes=30,
            description='What is time management and why it matters',
            content='''<h2>Time Management Basics</h2>
<p>Time management is the process of planning and controlling how you spend your time.</p>

<h3>Benefits:</h3>
<ul>
<li>Increased productivity</li>
<li>Reduced stress</li>
<li>Better work quality</li>
<li>Improved work-life balance</li>
</ul>''',
            order=1,
            is_mandatory=True
        )

        Lesson.objects.create(
            module=module4,
            title='Prioritization Techniques',
            content_type='text',
            duration_minutes=35,
            description='Learn how to prioritize your tasks',
            content='''<h2>Setting Priorities</h2>
<p>Not all tasks are equally important.</p>

<h3>The Eisenhower Matrix:</h3>
<ul>
<li><strong>Urgent & Important:</strong> Do first</li>
<li><strong>Important, Not Urgent:</strong> Schedule</li>
<li><strong>Urgent, Not Important:</strong> Delegate</li>
<li><strong>Neither:</strong> Eliminate</li>
</ul>''',
            order=2,
            is_mandatory=True
        )

        # Create some enrollments
        employees = Employee.objects.filter(employment_status='active')[:5]
        enrollments_created = 0

        for employee in employees:
            # Enroll in course 1
            enrollment, created = CourseEnrollment.objects.get_or_create(
                employee=employee,
                course=course1,
                defaults={
                    'enrollment_date': timezone.now().date(),
                    'status': 'enrolled'
                }
            )
            if created:
                enrollments_created += 1

            # Enroll some in course 2
            if enrollments_created % 2 == 0:
                enrollment2, created2 = CourseEnrollment.objects.get_or_create(
                    employee=employee,
                    course=course2,
                    defaults={
                        'enrollment_date': timezone.now().date(),
                        'status': 'in_progress',
                        'progress_percentage': 30
                    }
                )
                if created2:
                    enrollments_created += 1

        messages.success(request, _(
            f'✓ Mock data generated successfully!\n'
            f'• Courses created/updated: {len(courses_created) + 3}\n'
            f'• Total modules: {CourseModule.objects.filter(course__in=[course1, course2, course3]).count()}\n'
            f'• Total lessons: {Lesson.objects.filter(module__course__in=[course1, course2, course3]).count()}\n'
            f'• Enrollments created: {enrollments_created}'
        ))

        return redirect('training:course_list')

    except Exception as e:
        messages.error(request, _(f'Error generating mock data: {str(e)}'))
        return redirect('training:dashboard')
