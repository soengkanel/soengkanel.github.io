from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Instructor, Course, CourseModule, Lesson, CourseMaterial,
    CourseEnrollment, LessonProgress, Quiz, QuizQuestion,
    QuizAttempt, Certificate, LearningPath, LearningPathCourse
)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    """Admin interface for Instructors"""
    list_display = ['user', 'expertise', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'expertise']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'is_active')
        }),
        (_('Professional Details'), {
            'fields': ('expertise', 'bio', 'certifications', 'photo')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class CourseModuleInline(admin.TabularInline):
    """Inline for Course Modules"""
    model = CourseModule
    extra = 1
    fields = ['title', 'description', 'order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Courses"""
    list_display = [
        'code', 'title', 'category', 'level', 'instructor',
        'status', 'enrolled_count', 'duration_hours', 'created_at'
    ]
    list_filter = ['status', 'category', 'level', 'is_mandatory', 'created_at']
    search_fields = ['title', 'code', 'description', 'instructor__user__first_name', 'instructor__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'enrolled_count', 'completion_rate', 'total_lessons']
    filter_horizontal = ['prerequisites']
    inlines = [CourseModuleInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'code', 'description', 'category', 'level', 'thumbnail')
        }),
        (_('Instructor & Settings'), {
            'fields': ('instructor', 'duration_hours', 'max_students', 'passing_score')
        }),
        (_('Prerequisites'), {
            'fields': ('prerequisites',),
            'classes': ('collapse',)
        }),
        (_('Publishing'), {
            'fields': ('status', 'is_mandatory')
        }),
        (_('Statistics'), {
            'fields': ('enrolled_count', 'completion_rate', 'total_lessons'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class LessonInline(admin.TabularInline):
    """Inline for Lessons"""
    model = Lesson
    extra = 1
    fields = ['title', 'content_type', 'duration_minutes', 'order', 'is_mandatory']


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    """Admin interface for Course Modules"""
    list_display = ['course', 'title', 'order', 'lesson_count', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'description', 'course__title', 'course__code']
    readonly_fields = ['created_at', 'updated_at', 'lesson_count']
    inlines = [LessonInline]

    fieldsets = (
        (_('Module Information'), {
            'fields': ('course', 'title', 'description', 'order')
        }),
        (_('Metadata'), {
            'fields': ('lesson_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class CourseMaterialInline(admin.TabularInline):
    """Inline for Course Materials"""
    model = CourseMaterial
    extra = 1
    fields = ['title', 'file', 'file_type']
    readonly_fields = ['file_type']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for Lessons"""
    list_display = [
        'module', 'title', 'content_type', 'duration_minutes',
        'order', 'is_mandatory', 'created_at'
    ]
    list_filter = ['content_type', 'is_mandatory', 'module__course', 'created_at']
    search_fields = ['title', 'description', 'module__title', 'module__course__title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CourseMaterialInline]

    fieldsets = (
        (_('Lesson Information'), {
            'fields': ('module', 'title', 'content_type', 'description', 'order')
        }),
        (_('Content'), {
            'fields': ('content', 'video_url', 'duration_minutes', 'is_mandatory')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    """Admin interface for Course Materials"""
    list_display = ['lesson', 'title', 'file_type', 'file_size', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['title', 'lesson__title', 'lesson__module__course__title']
    readonly_fields = ['file_type', 'file_size', 'created_at']

    def file_size(self, obj):
        if obj.file_size:
            # Convert bytes to KB/MB
            if obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "N/A"
    file_size.short_description = _('File Size')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for Course Enrollments"""
    list_display = [
        'employee', 'course', 'enrollment_date', 'status',
        'progress_percentage', 'final_score', 'certificate_issued', 'created_at'
    ]
    list_filter = [
        'status', 'certificate_issued', 'enrollment_date',
        'completion_date', 'course', 'created_at'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'course__title', 'course__code'
    ]
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage']
    date_hierarchy = 'enrollment_date'

    fieldsets = (
        (_('Enrollment Information'), {
            'fields': ('course', 'employee', 'enrollment_date', 'start_date', 'status')
        }),
        (_('Progress'), {
            'fields': ('progress_percentage', 'last_accessed', 'completion_date')
        }),
        (_('Assessment'), {
            'fields': ('final_score', 'certificate_issued', 'certificate_date')
        }),
        (_('Feedback'), {
            'fields': ('feedback', 'rating', 'review')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['update_progress']

    def update_progress(self, request, queryset):
        """Update progress for selected enrollments"""
        for enrollment in queryset:
            enrollment.update_progress()
        self.message_user(request, _('Progress updated for selected enrollments.'))
    update_progress.short_description = _('Update progress percentage')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    """Admin interface for Lesson Progress"""
    list_display = [
        'enrollment', 'lesson', 'completed', 'started_at',
        'completed_at', 'time_spent_minutes', 'created_at'
    ]
    list_filter = ['completed', 'started_at', 'completed_at', 'created_at']
    search_fields = [
        'enrollment__employee__first_name', 'enrollment__employee__last_name',
        'lesson__title', 'enrollment__course__title'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


class QuizQuestionInline(admin.TabularInline):
    """Inline for Quiz Questions"""
    model = QuizQuestion
    extra = 1
    fields = ['question_text', 'question_type', 'order', 'points', 'correct_answer']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin interface for Quizzes"""
    list_display = [
        'course', 'title', 'passing_score', 'time_limit_minutes',
        'max_attempts', 'is_final_exam', 'question_count', 'created_at'
    ]
    list_filter = ['is_final_exam', 'course', 'created_at']
    search_fields = ['title', 'description', 'course__title', 'course__code']
    readonly_fields = ['created_at', 'updated_at', 'question_count']
    inlines = [QuizQuestionInline]

    fieldsets = (
        (_('Quiz Information'), {
            'fields': ('course', 'lesson', 'title', 'description')
        }),
        (_('Settings'), {
            'fields': (
                'passing_score', 'time_limit_minutes', 'max_attempts',
                'is_final_exam', 'randomize_questions'
            )
        }),
        (_('Metadata'), {
            'fields': ('question_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Admin interface for Quiz Questions"""
    list_display = [
        'quiz', 'question_text_short', 'question_type',
        'order', 'points', 'created_at'
    ]
    list_filter = ['question_type', 'quiz__course', 'created_at']
    search_fields = ['question_text', 'quiz__title', 'quiz__course__title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Question Information'), {
            'fields': ('quiz', 'question_text', 'question_type', 'order', 'points')
        }),
        (_('Answer Options'), {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
        (_('Explanation'), {
            'fields': ('explanation',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def question_text_short(self, obj):
        return obj.question_text[:100] + '...' if len(obj.question_text) > 100 else obj.question_text
    question_text_short.short_description = _('Question')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """Admin interface for Quiz Attempts"""
    list_display = [
        'enrollment', 'quiz', 'attempt_number', 'status',
        'score', 'passed', 'started_at', 'completed_at'
    ]
    list_filter = ['status', 'passed', 'quiz__course', 'started_at', 'completed_at']
    search_fields = [
        'enrollment__employee__first_name', 'enrollment__employee__last_name',
        'quiz__title', 'enrollment__course__title'
    ]
    readonly_fields = ['started_at']
    date_hierarchy = 'started_at'

    fieldsets = (
        (_('Attempt Information'), {
            'fields': ('enrollment', 'quiz', 'attempt_number', 'status')
        }),
        (_('Results'), {
            'fields': ('score', 'passed', 'answers', 'time_spent_minutes')
        }),
        (_('Timestamps'), {
            'fields': ('started_at', 'completed_at')
        }),
    )

    actions = ['recalculate_scores']

    def recalculate_scores(self, request, queryset):
        """Recalculate scores for selected attempts"""
        for attempt in queryset:
            attempt.calculate_score()
        self.message_user(request, _('Scores recalculated for selected attempts.'))
    recalculate_scores.short_description = _('Recalculate scores')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin interface for Certificates"""
    list_display = [
        'certificate_number', 'enrollment', 'issued_date',
        'expiry_date', 'created_at'
    ]
    list_filter = ['issued_date', 'expiry_date', 'created_at']
    search_fields = [
        'certificate_number', 'enrollment__employee__first_name',
        'enrollment__employee__last_name', 'enrollment__course__title'
    ]
    readonly_fields = ['certificate_number', 'issued_date', 'created_at']
    date_hierarchy = 'issued_date'

    fieldsets = (
        (_('Certificate Information'), {
            'fields': ('enrollment', 'certificate_number', 'file')
        }),
        (_('Validity'), {
            'fields': ('issued_date', 'expiry_date')
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class LearningPathCourseInline(admin.TabularInline):
    """Inline for Learning Path Courses"""
    model = LearningPathCourse
    extra = 1
    fields = ['course', 'order', 'is_required']


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    """Admin interface for Learning Paths"""
    list_display = ['title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [LearningPathCourseInline]

    fieldsets = (
        (_('Path Information'), {
            'fields': ('title', 'description', 'is_active')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
