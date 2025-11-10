from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal

from hr.models import Employee, EmployeeDocument, IDCard, IDCardRequest, ProbationPeriod, OvertimeClaim, OvertimePolicy, EmployeeOnboarding, OnboardingTaskInstance
from hr.forms import OvertimeClaimForm, EmployeeDocumentForm
from attendance.models import AttendanceRecord, BreakRecord, OvertimeRequest, AttendanceCorrection
from payroll.models import SalarySlip, SalaryAdvance, EmployeeLoan, EmployeeBenefit
from leave.models import LeaveApplication, LeaveAllocation, LeaveType, Holiday
from eform.models import Form, FormSubmission, CertificateRequest, ExtensionRequest
from project.models import Project
from training.models import Course, CourseEnrollment, LessonProgress
from suggestions.models import Suggestion
from announcements.models import Announcement, AnnouncementRead
from performance.models import PerformanceReview, Goal


# ============================================================================
# EMPLOYEE SELF-SERVICE DASHBOARD
# ============================================================================

@login_required
def employee_dashboard(request):
    """
    Employee self-service dashboard showing overview of all personal data
    """
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact HR to create your employee profile.')
        return redirect('dashboard:home')
    except AttributeError:
        messages.error(request, 'Employee profile not found. Please contact HR to link your account to an employee profile.')
        return redirect('dashboard:home')

    # Get current date info
    today = timezone.now().date()
    current_month = today.replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)

    # Leave balance
    current_year = today.year
    leave_allocations = LeaveAllocation.objects.filter(
        employee=employee,
        year=current_year
    ).select_related('leave_type')

    total_leave_days = sum(alloc.allocated_days for alloc in leave_allocations)
    used_leave_days = sum(alloc.used_days for alloc in leave_allocations)
    remaining_leave_days = total_leave_days - used_leave_days

    # Recent leave applications
    recent_leaves = LeaveApplication.objects.filter(
        employee=employee
    ).order_by('-created_at')[:5]

    # Pending leave applications
    pending_leaves = LeaveApplication.objects.filter(
        employee=employee,
        status='pending'
    ).count()

    # Attendance summary (current month)
    attendance_records = AttendanceRecord.objects.filter(
        employee=employee,
        date__gte=current_month,
        date__lt=next_month
    )

    total_days_worked = attendance_records.filter(status='present').count()
    total_late_days = attendance_records.filter(status='late').count()
    total_absences = attendance_records.filter(status='absent').count()
    total_hours = attendance_records.aggregate(Sum('total_hours'))['total_hours__sum'] or 0

    # Recent attendance (last 7 days)
    last_7_days = today - timedelta(days=7)
    recent_attendance = AttendanceRecord.objects.filter(
        employee=employee,
        date__gte=last_7_days,
        date__lte=today
    ).order_by('-date')[:7]

    # Payroll info
    latest_payslip = SalarySlip.objects.filter(
        employee=employee,
        status__in=['approved', 'paid']
    ).order_by('-payment_date').first()

    # Overtime claims
    pending_overtime = OvertimeClaim.objects.filter(
        employee=employee,
        status__in=['draft', 'submitted']
    ).count()

    approved_overtime_hours = OvertimeClaim.objects.filter(
        employee=employee,
        status='approved',
        work_date__gte=current_month,
        work_date__lt=next_month
    ).aggregate(Sum('total_hours'))['total_hours__sum'] or 0

    # Documents
    total_documents = EmployeeDocument.objects.filter(employee=employee).count()

    # ID Card
    active_id_card = IDCard.objects.filter(employee=employee, is_active=True).first()
    pending_id_requests = IDCardRequest.objects.filter(
        employee=employee,
        status__in=['pending', 'in_progress']
    ).count()

    # Probation status
    probation = ProbationPeriod.objects.filter(
        employee=employee,
        status='active'
    ).first()

    # Onboarding status (for new employees)
    onboarding = None
    try:
        onboarding = EmployeeOnboarding.objects.get(employee=employee)
        # Only show if onboarding is not completed or cancelled
        if onboarding.status not in ['completed', 'cancelled']:
            # Calculate if employee is in first 90 days
            days_since_joining = (today - employee.hire_date).days if employee.hire_date else 999
            if days_since_joining > 90:
                onboarding = None  # Hide onboarding info after 90 days
    except EmployeeOnboarding.DoesNotExist:
        pass

    # Upcoming holidays
    upcoming_holidays = Holiday.objects.filter(
        date__gte=today,
        date__lt=next_month
    ).order_by('date')[:5]

    # Suggestion Box statistics
    my_suggestions_count = Suggestion.objects.filter(employee=employee).count()
    pending_suggestions_count = Suggestion.objects.filter(
        employee=employee,
        status__in=['submitted', 'under_review']
    ).count()
    implemented_suggestions_count = Suggestion.objects.filter(
        employee=employee,
        status='implemented'
    ).count()
    total_suggestions_count = Suggestion.objects.count()

    # Announcements
    recent_announcements = Announcement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).filter(
        Q(expiry_date__isnull=True) | Q(expiry_date__gt=timezone.now())
    ).filter(
        Q(target_audience='all') |
        Q(target_audience='department', target_departments=employee.department)
    ).distinct().order_by('-is_pinned', '-publish_date')[:5]

    # Get unread announcement count
    read_announcement_ids = AnnouncementRead.objects.filter(
        employee=employee
    ).values_list('announcement_id', flat=True)

    unread_announcements_count = Announcement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).filter(
        Q(expiry_date__isnull=True) | Q(expiry_date__gt=timezone.now())
    ).filter(
        Q(target_audience='all') |
        Q(target_audience='department', target_departments=employee.department)
    ).exclude(id__in=read_announcement_ids).distinct().count()

    context = {
        'employee': employee,
        'today': today,

        # Leave summary
        'total_leave_days': total_leave_days,
        'used_leave_days': used_leave_days,
        'remaining_leave_days': remaining_leave_days,
        'leave_allocations': leave_allocations,
        'recent_leaves': recent_leaves,
        'pending_leaves': pending_leaves,

        # Attendance summary
        'total_days_worked': total_days_worked,
        'total_late_days': total_late_days,
        'total_absences': total_absences,
        'total_hours': round(total_hours, 2),
        'recent_attendance': recent_attendance,

        # Payroll
        'latest_payslip': latest_payslip,

        # Overtime
        'pending_overtime': pending_overtime,
        'approved_overtime_hours': round(approved_overtime_hours, 2),

        # Documents & ID
        'total_documents': total_documents,
        'active_id_card': active_id_card,
        'pending_id_requests': pending_id_requests,

        # Probation
        'probation': probation,

        # Onboarding (for new employees)
        'onboarding': onboarding,

        # Holidays
        'upcoming_holidays': upcoming_holidays,

        # Suggestions
        'my_suggestions_count': my_suggestions_count,
        'pending_suggestions_count': pending_suggestions_count,
        'implemented_suggestions_count': implemented_suggestions_count,
        'total_suggestions_count': total_suggestions_count,

        # Announcements
        'recent_announcements': recent_announcements,
        'unread_announcements_count': unread_announcements_count,
    }

    return render(request, 'employee_portal/dashboard.html', context)


# ============================================================================
# EMPLOYEE PROFILE
# ============================================================================

@login_required
def employee_profile(request):
    """
    View comprehensive employee and user profile
    """
    user = request.user

    try:
        employee = user.employee
    except:
        employee = None

    # Get user's active role assignment if it exists
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.get(user=user, is_active=True)
    except:
        role_assignment = None

    # Handle permissions based on user type
    permissions = []
    permission_source = "none"

    if user.is_superuser:
        # For superusers, show role permissions if they have a role
        if role_assignment and role_assignment.role:
            permissions = role_assignment.role.permissions.all()
            permission_source = "role_superuser"
        else:
            permission_source = "superuser"
    elif role_assignment and role_assignment.role:
        # Regular users get role permissions
        permissions = role_assignment.role.permissions.all()
        permission_source = "role"
    else:
        permissions = []
        permission_source = "none"

    # Get direct permissions count for info
    direct_permissions_count = user.user_permissions.count()

    context = {
        'employee': employee,
        'user': user,
        'role_assignment': role_assignment,
        'permissions': permissions,
        'permission_source': permission_source,
        'direct_permissions_count': direct_permissions_count,
        'total_system_permissions': 294 if user.is_superuser else 0,
    }

    return render(request, 'employee_portal/profile.html', context)


# ============================================================================
# ATTENDANCE VIEWS
# ============================================================================

@login_required
@permission_required('attendance.view_attendancerecord', raise_exception=True)
def attendance_list(request):
    """
    View own attendance records with check-in/check-out functionality
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Check today's attendance - allow multiple check-ins per day
    today = timezone.now().date()

    # Get the latest attendance record (most recent)
    latest_attendance = AttendanceRecord.objects.filter(
        employee=employee,
        date=today
    ).order_by('-clock_in').first()

    # Get all attendance records for today
    today_attendances = AttendanceRecord.objects.filter(
        employee=employee,
        date=today
    ).order_by('-clock_in')

    # Determine if currently checked in (latest record has no check-out)
    is_currently_checked_in = latest_attendance and not latest_attendance.clock_out if latest_attendance else False

    # Get active projects for selection
    active_projects = Project.objects.filter(status__in=['in_progress', 'planned']).order_by('project_name')

    # Handle check-in/check-out actions
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'check_in':
            # Get selected project
            project_id = request.POST.get('project')
            current_project = None
            if project_id:
                try:
                    current_project = Project.objects.get(id=project_id)
                except Project.DoesNotExist:
                    pass

            # Get location data
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            # Get reason
            reason = request.POST.get('reason', '').strip()

            # Create new attendance record (allows multiple check-ins per day)
            attendance = AttendanceRecord.objects.create(
                employee=employee,
                date=today,
                clock_in=timezone.now(),
                status='present',
                current_project=current_project,
                clock_in_latitude=latitude if latitude else None,
                clock_in_longitude=longitude if longitude else None,
                notes=reason if reason else ''
            )

            if reason:
                messages.success(request, f'Checked in at {attendance.clock_in.strftime("%H:%M")} - {reason}')
            else:
                messages.success(request, f'Checked in successfully at {attendance.clock_in.strftime("%H:%M")}')
            return redirect('employee_portal:attendance_list')

        elif action == 'check_out':
            if not is_currently_checked_in:
                messages.error(request, 'You need to check in first.')
            else:
                # Get location data
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')

                # Get reason
                reason = request.POST.get('reason', '').strip()

                # Update the latest attendance with check-out time
                latest_attendance.clock_out = timezone.now()
                latest_attendance.clock_out_latitude = latitude if latitude else None
                latest_attendance.clock_out_longitude = longitude if longitude else None

                # Append reason to notes if provided
                if reason:
                    if latest_attendance.notes:
                        latest_attendance.notes += f' | Check-out: {reason}'
                    else:
                        latest_attendance.notes = f'Check-out: {reason}'
                elif not latest_attendance.notes:
                    latest_attendance.notes = ''

                # Calculate total hours
                clock_in_dt = latest_attendance.clock_in
                clock_out_dt = latest_attendance.clock_out
                total_seconds = (clock_out_dt - clock_in_dt).total_seconds()
                latest_attendance.total_hours = round(total_seconds / 3600, 2)

                latest_attendance.save()

                if reason:
                    messages.success(request, f'Checked out at {latest_attendance.clock_out.strftime("%H:%M")} - {reason}')
                else:
                    messages.success(request, f'Checked out successfully at {latest_attendance.clock_out.strftime("%H:%M")}')
                return redirect('employee_portal:attendance_list')

    # Get filter parameters
    month = request.GET.get('month')
    year = request.GET.get('year')
    status = request.GET.get('status')

    # Base queryset
    attendance_records = AttendanceRecord.objects.filter(employee=employee)

    # Apply filters
    if month and year:
        try:
            filter_date = datetime(int(year), int(month), 1).date()
            next_month = (filter_date + timedelta(days=32)).replace(day=1)
            attendance_records = attendance_records.filter(
                date__gte=filter_date,
                date__lt=next_month
            )
        except:
            pass

    if status:
        attendance_records = attendance_records.filter(status=status)

    # Order by date descending
    attendance_records = attendance_records.order_by('-date')

    # Pagination
    paginator = Paginator(attendance_records, 31)  # One month
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Summary statistics
    total_hours = attendance_records.aggregate(Sum('total_hours'))['total_hours__sum'] or 0
    total_present = attendance_records.filter(status='present').count()
    total_late = attendance_records.filter(status='late').count()
    total_absent = attendance_records.filter(status='absent').count()

    context = {
        'employee': employee,
        'page_obj': page_obj,
        'total_hours': round(total_hours, 2),
        'total_present': total_present,
        'total_late': total_late,
        'total_absent': total_absent,
        'selected_month': month,
        'selected_year': year,
        'selected_status': status,
        'latest_attendance': latest_attendance,
        'today_attendances': today_attendances,
        'is_currently_checked_in': is_currently_checked_in,
        'today': today,
        'active_projects': active_projects,
    }

    return render(request, 'employee_portal/attendance_list.html', context)


@login_required
@permission_required('attendance.view_attendancerecord', raise_exception=True)
def attendance_detail(request, attendance_id):
    """
    View attendance record details
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    attendance = get_object_or_404(AttendanceRecord, id=attendance_id, employee=employee)

    # Get break records
    breaks = BreakRecord.objects.filter(attendance=attendance).order_by('start_time')

    context = {
        'employee': employee,
        'attendance': attendance,
        'breaks': breaks,
    }

    return render(request, 'employee_portal/attendance_detail.html', context)


# ============================================================================
# PAYSLIP VIEWS
# ============================================================================

@login_required
@permission_required('payroll.view_salaryslip', raise_exception=True)
def payslip_list(request):
    """
    View own payslips
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get payslips
    payslips = SalarySlip.objects.filter(
        employee=employee,
        status__in=['approved', 'paid']
    ).order_by('-payment_date')

    # Pagination
    paginator = Paginator(payslips, 12)  # 12 months
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'employee': employee,
        'page_obj': page_obj,
    }

    return render(request, 'employee_portal/payslip_list.html', context)


@login_required
@permission_required('payroll.view_salaryslip', raise_exception=True)
def payslip_detail(request, payslip_id):
    """
    View payslip details
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    payslip = get_object_or_404(SalarySlip, id=payslip_id, employee=employee)

    context = {
        'employee': employee,
        'payslip': payslip,
    }

    return render(request, 'employee_portal/payslip_detail.html', context)


# ============================================================================
# DOCUMENT VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_employeedocument', raise_exception=True)
def document_list(request):
    """
    View own documents
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    documents = EmployeeDocument.objects.filter(employee=employee).order_by('-created_at')

    context = {
        'employee': employee,
        'documents': documents,
    }

    return render(request, 'employee_portal/document_list.html', context)


@login_required
@permission_required('hr.add_employeedocument', raise_exception=True)
def document_upload(request):
    """
    Upload a new document
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    if request.method == 'POST':
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.employee = employee
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('employee_portal:document_list')
    else:
        form = EmployeeDocumentForm()

    context = {
        'employee': employee,
        'form': form,
    }

    return render(request, 'employee_portal/document_upload.html', context)


# ============================================================================
# OVERTIME CLAIM VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_overtimeclaim', raise_exception=True)
def overtime_claim_list(request):
    """
    View own overtime claims
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    claims = OvertimeClaim.objects.filter(employee=employee).order_by('-work_date')

    # Pagination
    paginator = Paginator(claims, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'employee': employee,
        'page_obj': page_obj,
    }

    return render(request, 'employee_portal/overtime_claim_list.html', context)


@login_required
@permission_required('hr.add_overtimeclaim', raise_exception=True)
def overtime_claim_create(request):
    """
    Create new overtime claim
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    if request.method == 'POST':
        form = OvertimeClaimForm(request.POST)
        if form.is_valid():
            # Check if overtime policy exists
            try:
                default_policy = OvertimePolicy.objects.first()
                if not default_policy:
                    messages.error(request, 'No overtime policy found. Please contact HR to set up overtime policies.')
                    return redirect('employee_portal:overtime_claim_list')
            except:
                messages.error(request, 'Unable to access overtime policies. Please contact HR.')
                return redirect('employee_portal:overtime_claim_list')

            claim = form.save(commit=False)
            claim.employee = employee
            claim.claim_date = timezone.now().date()
            claim.status = 'draft'
            claim.overtime_policy = default_policy

            # Calculate hours (basic calculation)
            from datetime import datetime, timedelta
            start_dt = datetime.combine(claim.work_date, claim.start_time)
            end_dt = datetime.combine(claim.work_date, claim.end_time)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)

            total_seconds = (end_dt - start_dt).total_seconds()
            total_hours = round(total_seconds / 3600, 2)
            claim.total_hours = total_hours
            claim.overtime_hours = total_hours

            claim.save()
            messages.success(request, 'Overtime claim submitted successfully.')
            return redirect('employee_portal:overtime_claim_list')
    else:
        form = OvertimeClaimForm(initial={'work_date': timezone.now().date()})

    context = {
        'employee': employee,
        'form': form,
    }

    return render(request, 'employee_portal/overtime_claim_form.html', context)


# ============================================================================
# TRAINING VIEWS
# ============================================================================

@login_required
def training_courses(request):
    """
    View available training courses and employee's enrollments
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get employee enrollments
    my_enrollments = CourseEnrollment.objects.filter(employee=employee).select_related('course', 'course__instructor')

    # Statistics
    total_enrolled = my_enrollments.count()
    in_progress = my_enrollments.filter(status='in_progress').count()
    completed = my_enrollments.filter(status='completed').count()

    # Get filter parameters
    category_filter = request.GET.get('category', '')
    level_filter = request.GET.get('level', '')
    search_query = request.GET.get('search', '')

    # Get available courses (published only)
    enrolled_course_ids = my_enrollments.values_list('course_id', flat=True)
    available_courses = Course.objects.filter(status='published').select_related('instructor', 'instructor__user')

    # Apply filters
    if category_filter:
        available_courses = available_courses.filter(category=category_filter)

    if level_filter:
        available_courses = available_courses.filter(level=level_filter)

    if search_query:
        available_courses = available_courses.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Order by created date
    available_courses = available_courses.order_by('-created_at')

    # Pagination for available courses
    paginator = Paginator(available_courses, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Annotate each course with enrollment status
    for course in page_obj:
        course.is_enrolled = course.id in enrolled_course_ids

    context = {
        'employee': employee,
        'my_enrollments': my_enrollments,
        'total_enrolled': total_enrolled,
        'in_progress': in_progress,
        'completed': completed,
        'page_obj': page_obj,
        'category_filter': category_filter,
        'level_filter': level_filter,
        'search_query': search_query,
        'category_choices': Course.CATEGORY_CHOICES,
        'level_choices': Course.LEVEL_CHOICES,
    }

    return render(request, 'employee_portal/training_courses.html', context)


@login_required
def training_course_detail(request, course_id):
    """
    View course details before enrolling
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    course = get_object_or_404(Course, pk=course_id, status='published')

    # Get course modules and lessons
    modules = course.modules.prefetch_related('lessons').order_by('order')

    # Check if user is enrolled
    enrollment = CourseEnrollment.objects.filter(course=course, employee=employee).first()
    is_enrolled = enrollment is not None

    # Get course statistics
    total_enrolled = course.enrollments.count()
    completed_count = course.enrollments.filter(status='completed').count()

    context = {
        'employee': employee,
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'total_enrolled': total_enrolled,
        'completed_count': completed_count,
    }

    return render(request, 'employee_portal/training_course_detail.html', context)


@login_required
def training_enroll(request, course_id):
    """
    Enroll in a course
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'You must be registered as an employee to enroll in courses.')
        return redirect('employee_portal:training_courses')

    course = get_object_or_404(Course, pk=course_id, status='published')

    # Check if already enrolled
    if CourseEnrollment.objects.filter(course=course, employee=employee).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('employee_portal:training_my_courses')

    # Check if course is full
    if course.is_full:
        messages.error(request, 'This course is full. Please contact HR for assistance.')
        return redirect('employee_portal:training_course_detail', course_id=course_id)

    # Create enrollment
    enrollment = CourseEnrollment.objects.create(
        course=course,
        employee=employee,
        enrollment_date=timezone.now().date(),
        status='enrolled'
    )

    messages.success(request, f'Successfully enrolled in "{course.title}"! You can now start learning.')
    return redirect('employee_portal:training_my_courses')


@login_required
def training_my_courses(request):
    """
    View employee's enrolled courses
    """
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get filter parameters
    status_filter = request.GET.get('status', '')

    # Get employee enrollments
    enrollments = CourseEnrollment.objects.filter(employee=employee).select_related('course', 'course__instructor')

    # Apply status filter
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)

    # Order by enrollment date
    enrollments = enrollments.order_by('-enrollment_date')

    # Pagination
    paginator = Paginator(enrollments, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_enrolled = CourseEnrollment.objects.filter(employee=employee).count()
    in_progress = CourseEnrollment.objects.filter(employee=employee, status='in_progress').count()
    completed = CourseEnrollment.objects.filter(employee=employee, status='completed').count()

    context = {
        'employee': employee,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_enrolled': total_enrolled,
        'in_progress': in_progress,
        'completed': completed,
        'status_choices': CourseEnrollment.STATUS_CHOICES,
    }

    return render(request, 'employee_portal/training_my_courses.html', context)


# ============================================================================
# EMPLOYEE PERFORMANCE & GOALS
# ============================================================================

@login_required
def employee_performance(request):
    """
    Employee view of their performance reviews and goals
    """
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get performance reviews
    reviews = PerformanceReview.objects.filter(employee=employee).order_by('-review_date')

    # Get goals
    goals = Goal.objects.filter(employee=employee).order_by('-created_at')

    # Calculate statistics
    total_reviews = reviews.count()
    completed_reviews = reviews.filter(status='completed').count()

    # Calculate average rating
    completed_reviews_with_rating = reviews.filter(status='completed', overall_rating__isnull=False)
    avg_rating = completed_reviews_with_rating.aggregate(avg=Sum('overall_rating'))['avg']
    if avg_rating and total_reviews > 0:
        avg_rating = round(avg_rating / completed_reviews_with_rating.count(), 1)

    # Goals statistics
    total_goals = goals.count()
    completed_goals = goals.filter(status='completed').count()
    in_progress_goals = goals.filter(status='in_progress').count()
    not_started_goals = goals.filter(status='not_started').count()

    # Recent reviews (last 5)
    recent_reviews = reviews[:5]

    # Active goals
    active_goals = goals.filter(status__in=['not_started', 'in_progress'])[:10]

    context = {
        'employee': employee,
        'total_reviews': total_reviews,
        'completed_reviews': completed_reviews,
        'avg_rating': avg_rating,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'in_progress_goals': in_progress_goals,
        'not_started_goals': not_started_goals,
        'recent_reviews': recent_reviews,
        'active_goals': active_goals,
    }

    return render(request, 'employee_portal/performance.html', context)


@login_required
def employee_performance_review_detail(request, pk):
    """
    Employee view of a specific performance review
    """
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Ensure employee can only see their own reviews
    review = get_object_or_404(PerformanceReview, pk=pk, employee=employee)

    context = {
        'employee': employee,
        'review': review,
    }

    return render(request, 'employee_portal/performance_review_detail.html', context)


@login_required
def employee_goal_detail(request, pk):
    """
    Employee view of a specific goal
    """
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Ensure employee can only see their own goals
    goal = get_object_or_404(Goal, pk=pk, employee=employee)

    context = {
        'employee': employee,
        'goal': goal,
    }

    return render(request, 'employee_portal/goal_detail.html', context)


@login_required
def request_forms(request):
    """
    Employee view to browse and access available request forms
    """
    from eform.models import Form, FormSubmission

    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get published forms that are available to employees
    available_forms = Form.objects.filter(
        status='published',
        is_public=True
    ).order_by('-created_at')

    # Get employee's recent submissions
    my_recent_submissions = FormSubmission.objects.filter(
        submitted_by=request.user
    ).select_related('form').order_by('-submitted_at')[:5]

    # Count total submissions by this employee
    total_submissions = FormSubmission.objects.filter(submitted_by=request.user).count()

    context = {
        'employee': employee,
        'available_forms': available_forms,
        'my_recent_submissions': my_recent_submissions,
        'total_submissions': total_submissions,
    }

    return render(request, 'employee_portal/request_forms.html', context)


@login_required
def fill_request_form(request, form_id):
    """
    Employee view to fill and submit a form
    """
    from eform.models import Form, FormField, FormSubmission
    import json

    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    form = get_object_or_404(Form, id=form_id, status='published', is_public=True)

    # Check if form allows multiple submissions
    if not form.allow_multiple_submissions:
        existing_submission = FormSubmission.objects.filter(
            form=form,
            submitted_by=request.user
        ).first()
        if existing_submission:
            messages.warning(request, 'You have already submitted this form.')
            return redirect('employee_portal:view_form_submission', submission_id=existing_submission.id)

    if request.method == 'POST':
        # Collect form data
        form_data = {}
        files_data = {}

        for field in form.fields.all():
            field_name = f'field_{field.id}'

            if field.field_type == 'file':
                if field_name in request.FILES:
                    # Handle file upload
                    uploaded_file = request.FILES[field_name]
                    # Save file and store path
                    files_data[field.label] = uploaded_file.name
            elif field.field_type == 'checkbox':
                # Handle checkbox - can have multiple values
                form_data[field.label] = request.POST.getlist(field_name)
            else:
                form_data[field.label] = request.POST.get(field_name, '')

        # Create submission
        submission = FormSubmission.objects.create(
            form=form,
            submitted_by=request.user,
            data=form_data,
            email=request.user.email,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        messages.success(request, f'Form "{form.title}" submitted successfully!')
        return redirect('employee_portal:view_form_submission', submission_id=submission.id)

    # Get form fields
    fields = form.fields.all().order_by('order')

    context = {
        'employee': employee,
        'form': form,
        'fields': fields,
    }

    return render(request, 'employee_portal/fill_request_form.html', context)


@login_required
def my_form_submissions(request):
    """
    Employee view to see their form submissions
    """
    from eform.models import FormSubmission

    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get all submissions by this employee
    submissions = FormSubmission.objects.filter(
        submitted_by=request.user
    ).select_related('form').order_by('-submitted_at')

    context = {
        'employee': employee,
        'submissions': submissions,
    }

    return render(request, 'employee_portal/my_form_submissions.html', context)


@login_required
def view_form_submission(request, submission_id):
    """
    Employee view to see a specific form submission
    """
    from eform.models import FormSubmission

    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Ensure employee can only see their own submissions
    submission = get_object_or_404(
        FormSubmission,
        id=submission_id,
        submitted_by=request.user
    )

    context = {
        'employee': employee,
        'submission': submission,
    }

    return render(request, 'employee_portal/view_form_submission.html', context)


@login_required
def holiday_calendar(request):
    """
    Employee view to see public holidays in calendar format
    """
    import calendar
    from collections import defaultdict

    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    today = timezone.now().date()

    # Get year from query param, default to current year
    selected_year = int(request.GET.get('year', today.year))

    # Get all holidays for the selected year
    holidays = Holiday.objects.filter(year=selected_year).order_by('date')

    # Group holidays by month
    holidays_by_month = defaultdict(list)
    for holiday in holidays:
        holidays_by_month[holiday.date.month].append(holiday)

    # Create calendar data for each month
    cal = calendar.Calendar(firstweekday=6)  # Start week on Sunday
    months_data = []

    # Determine starting month
    # If viewing current year, start from current month
    # Otherwise, show all months from January
    if selected_year == today.year:
        start_month = today.month
        end_month = 13
    else:
        start_month = 1
        end_month = 13

    for month in range(start_month, end_month):
        month_name = calendar.month_name[month]
        weeks = cal.monthdayscalendar(selected_year, month)

        # Get holidays for this month
        month_holidays = holidays_by_month.get(month, [])
        holiday_dates = {h.date.day: h for h in month_holidays}

        # Format weeks data
        formatted_weeks = []
        for week in weeks:
            formatted_week = []
            for day in week:
                if day == 0:
                    formatted_week.append(None)
                else:
                    day_date = datetime(selected_year, month, day).date()
                    is_today = day_date == today
                    holiday = holiday_dates.get(day)
                    formatted_week.append({
                        'day': day,
                        'is_today': is_today,
                        'holiday': holiday,
                        'date': day_date
                    })
            formatted_weeks.append(formatted_week)

        months_data.append({
            'name': month_name,
            'number': month,
            'weeks': formatted_weeks,
            'holidays': month_holidays
        })

    # Statistics - count holidays from current month onwards for current year
    if selected_year == today.year:
        upcoming_holidays = holidays.filter(date__gte=today.replace(day=1))
        total_holidays = upcoming_holidays.count()
        public_holidays = upcoming_holidays.filter(is_optional=False).count()
        optional_holidays = upcoming_holidays.filter(is_optional=True).count()
    else:
        total_holidays = holidays.count()
        public_holidays = holidays.filter(is_optional=False).count()
        optional_holidays = holidays.filter(is_optional=True).count()

    # Year options (current year +/- 2 years)
    year_options = list(range(today.year - 2, today.year + 3))

    context = {
        'employee': employee,
        'selected_year': selected_year,
        'months_data': months_data,
        'total_holidays': total_holidays,
        'public_holidays': public_holidays,
        'optional_holidays': optional_holidays,
        'year_options': year_options,
        'today': today,
    }

    return render(request, 'employee_portal/holiday_calendar.html', context)


# ============================================================================
# ONBOARDING VIEWS
# ============================================================================

@login_required
def onboarding_overview(request):
    """
    Employee view of their onboarding progress and information
    """
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get onboarding record
    onboarding = None
    try:
        onboarding = EmployeeOnboarding.objects.get(employee=employee)
    except EmployeeOnboarding.DoesNotExist:
        pass

    # If no onboarding record exists, show a message
    if not onboarding:
        context = {
            'employee': employee,
            'onboarding': None,
            'no_onboarding': True,
        }
        return render(request, 'employee_portal/onboarding_overview.html', context)

    # Get probation info
    probation = ProbationPeriod.objects.filter(employee=employee, status='active').first()

    # Get required documents
    required_documents = EmployeeDocument.objects.filter(employee=employee).order_by('-created_at')

    # Calculate days since joining
    days_since_joining = (timezone.now().date() - employee.hire_date).days if employee.hire_date else 0

    # Calculate remaining tasks
    remaining_tasks = onboarding.total_tasks - onboarding.completed_tasks

    # Get task instances
    task_instances = OnboardingTaskInstance.objects.filter(onboarding=onboarding).order_by('due_date', 'priority')
    completed_task_instances = task_instances.filter(status='completed')
    pending_task_instances = task_instances.exclude(status='completed')

    context = {
        'employee': employee,
        'onboarding': onboarding,
        'probation': probation,
        'required_documents': required_documents,
        'days_since_joining': days_since_joining,
        'remaining_tasks': remaining_tasks,
        'task_instances': task_instances,
        'completed_task_instances': completed_task_instances,
        'pending_task_instances': pending_task_instances,
        'no_onboarding': False,
    }

    return render(request, 'employee_portal/onboarding_overview.html', context)


@login_required
def complete_onboarding_task(request, task_id):
    """
    Mark an onboarding task as completed by the employee
    """
    if request.method != 'POST':
        return redirect('employee_portal:onboarding_overview')

    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get the task instance
    task = get_object_or_404(OnboardingTaskInstance, id=task_id)

    # Verify the task belongs to the logged-in employee
    if task.onboarding.employee != employee:
        messages.error(request, 'You do not have permission to complete this task.')
        return redirect('employee_portal:onboarding_overview')

    # Check if task requires approval
    if task.requires_approval:
        messages.warning(request, 'This task requires HR approval and cannot be self-completed.')
        return redirect('employee_portal:onboarding_overview')

    # Check if task is already completed
    if task.status == 'completed':
        messages.info(request, 'This task is already marked as completed.')
        return redirect('employee_portal:onboarding_overview')

    # Mark task as completed
    task.status = 'completed'
    task.completion_date = timezone.now().date()
    task.save()

    # Update parent onboarding progress
    onboarding = task.onboarding
    completed_count = OnboardingTaskInstance.objects.filter(
        onboarding=onboarding,
        status='completed'
    ).count()
    onboarding.completed_tasks = completed_count
    onboarding.save()

    messages.success(request, f'Task "{task.title}" marked as complete!')
    return redirect('employee_portal:onboarding_overview')
