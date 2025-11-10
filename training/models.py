from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from hr.models import Employee
import os


class Instructor(models.Model):
    """Instructor/Trainer model for managing course instructors"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile', verbose_name=_('User'))
    bio = models.TextField(_('Biography'), blank=True)
    expertise = models.CharField(_('Area of Expertise'), max_length=200, blank=True)
    certifications = models.TextField(_('Certifications'), blank=True)
    photo = models.ImageField(_('Photo'), upload_to='instructors/', blank=True, null=True)
    is_active = models.BooleanField(_('Active'), default=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = _('Instructor')
        verbose_name_plural = _('Instructors')
        ordering = ['user__first_name', 'user__last_name']


class Course(models.Model):
    """Enhanced course model with comprehensive LMS features"""
    CATEGORY_CHOICES = [
        ('technical', _('Technical Skills')),
        ('soft_skills', _('Soft Skills')),
        ('leadership', _('Leadership & Management')),
        ('compliance', _('Compliance & Regulations')),
        ('safety', _('Health & Safety')),
        ('onboarding', _('Onboarding & Orientation')),
        ('professional', _('Professional Development')),
        ('other', _('Other')),
    ]

    LEVEL_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]

    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]

    # Basic Information
    title = models.CharField(_('Course Title'), max_length=200)
    code = models.CharField(_('Course Code'), max_length=50, unique=True, help_text=_('Unique course identifier'))
    description = models.TextField(_('Description'))
    category = models.CharField(_('Category'), max_length=20, choices=CATEGORY_CHOICES, default='technical')
    level = models.CharField(_('Level'), max_length=20, choices=LEVEL_CHOICES, default='beginner')

    # Instructor & Media
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name='courses', verbose_name=_('Instructor'))
    thumbnail = models.ImageField(_('Thumbnail'), upload_to='courses/thumbnails/', blank=True, null=True)

    # Course Settings
    duration_hours = models.DecimalField(_('Duration (Hours)'), max_digits=5, decimal_places=1, validators=[MinValueValidator(0.1)])
    max_students = models.IntegerField(_('Maximum Students'), null=True, blank=True, validators=[MinValueValidator(1)])
    passing_score = models.IntegerField(_('Passing Score (%)'), default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Prerequisites
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_for', verbose_name=_('Prerequisites'))

    # Publishing
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_mandatory = models.BooleanField(_('Mandatory'), default=False, help_text=_('Required for all employees'))

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_courses', verbose_name=_('Created By'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def enrolled_count(self):
        """Count of enrolled students"""
        return self.enrollments.filter(status__in=['enrolled', 'in_progress', 'completed']).count()

    @property
    def completion_rate(self):
        """Percentage of students who completed the course"""
        total = self.enrollments.filter(status__in=['in_progress', 'completed']).count()
        if total == 0:
            return 0
        completed = self.enrollments.filter(status='completed').count()
        return round((completed / total) * 100, 1)

    @property
    def is_full(self):
        """Check if course is at capacity"""
        if self.max_students:
            return self.enrolled_count >= self.max_students
        return False

    @property
    def total_lessons(self):
        """Total number of lessons across all modules"""
        return Lesson.objects.filter(module__course=self).count()

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['-created_at']


class CourseModule(models.Model):
    """Module/Section within a course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name=_('Course'))
    title = models.CharField(_('Module Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    order = models.IntegerField(_('Order'), default=0)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    @property
    def lesson_count(self):
        return self.lessons.count()

    class Meta:
        verbose_name = _('Course Module')
        verbose_name_plural = _('Course Modules')
        ordering = ['course', 'order', 'id']
        unique_together = [['course', 'order']]


class Lesson(models.Model):
    """Individual lesson within a module"""
    CONTENT_TYPE_CHOICES = [
        ('video', _('Video')),
        ('document', _('Document/Reading')),
        ('presentation', _('Presentation')),
        ('interactive', _('Interactive Content')),
        ('quiz', _('Quiz/Assessment')),
    ]

    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons', verbose_name=_('Module'))
    title = models.CharField(_('Lesson Title'), max_length=200)
    content_type = models.CharField(_('Content Type'), max_length=20, choices=CONTENT_TYPE_CHOICES, default='document')
    description = models.TextField(_('Description'), blank=True)
    content = models.TextField(_('Content'), blank=True, help_text=_('Main lesson content (text/HTML)'))
    video_url = models.URLField(_('Video URL'), blank=True, help_text=_('YouTube, Vimeo, or direct video URL'))
    duration_minutes = models.IntegerField(_('Duration (Minutes)'), default=0, validators=[MinValueValidator(0)])
    order = models.IntegerField(_('Order'), default=0)
    is_mandatory = models.BooleanField(_('Mandatory'), default=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.module.course.code} - {self.module.title} - {self.title}"

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['module', 'order', 'id']
        unique_together = [['module', 'order']]


class CourseMaterial(models.Model):
    """Downloadable materials for lessons"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials', verbose_name=_('Lesson'))
    title = models.CharField(_('Title'), max_length=200)
    file = models.FileField(
        _('File'),
        upload_to='course_materials/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'zip', 'mp4', 'avi', 'mov'])]
    )
    file_type = models.CharField(_('File Type'), max_length=50, blank=True)
    file_size = models.IntegerField(_('File Size (bytes)'), blank=True, null=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.file_type = os.path.splitext(self.file.name)[1].lower()
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    class Meta:
        verbose_name = _('Course Material')
        verbose_name_plural = _('Course Materials')
        ordering = ['-created_at']


class CourseEnrollment(models.Model):
    """Enhanced enrollment with progress tracking"""
    STATUS_CHOICES = [
        ('enrolled', _('Enrolled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name=_('Course'))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='course_enrollments', verbose_name=_('Employee'))

    # Enrollment Details
    enrollment_date = models.DateField(_('Enrollment Date'), default=timezone.now)
    start_date = models.DateField(_('Start Date'), null=True, blank=True)
    completion_date = models.DateField(_('Completion Date'), null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='enrolled')

    # Progress
    progress_percentage = models.IntegerField(_('Progress (%)'), default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_accessed = models.DateTimeField(_('Last Accessed'), null=True, blank=True)

    # Assessment
    final_score = models.DecimalField(_('Final Score (%)'), max_digits=5, decimal_places=2, null=True, blank=True)
    certificate_issued = models.BooleanField(_('Certificate Issued'), default=False)
    certificate_date = models.DateField(_('Certificate Date'), null=True, blank=True)

    # Feedback
    feedback = models.TextField(_('Instructor Feedback'), blank=True)
    rating = models.IntegerField(_('Course Rating'), null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(_('Employee Review'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.course.title}"

    def update_progress(self):
        """Calculate and update progress percentage"""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = LessonProgress.objects.filter(
                enrollment=self,
                completed=True
            ).count()
            self.progress_percentage = round((completed_lessons / total_lessons) * 100)
        self.save()

    class Meta:
        verbose_name = _('Course Enrollment')
        verbose_name_plural = _('Course Enrollments')
        ordering = ['-enrollment_date']
        unique_together = [['course', 'employee']]


class LessonProgress(models.Model):
    """Track individual lesson completion"""
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='lesson_progress', verbose_name=_('Enrollment'))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records', verbose_name=_('Lesson'))

    started_at = models.DateTimeField(_('Started At'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)
    completed = models.BooleanField(_('Completed'), default=False)
    time_spent_minutes = models.IntegerField(_('Time Spent (Minutes)'), default=0)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.enrollment.employee.get_full_name()} - {self.lesson.title}"

    def mark_complete(self):
        """Mark lesson as completed"""
        self.completed = True
        self.completed_at = timezone.now()
        self.save()
        # Update enrollment progress
        self.enrollment.update_progress()

    class Meta:
        verbose_name = _('Lesson Progress')
        verbose_name_plural = _('Lesson Progress Records')
        ordering = ['-created_at']
        unique_together = [['enrollment', 'lesson']]


class Quiz(models.Model):
    """Quiz/Assessment for courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes', verbose_name=_('Course'))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='quizzes', verbose_name=_('Lesson'))

    title = models.CharField(_('Quiz Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    passing_score = models.IntegerField(_('Passing Score (%)'), default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    time_limit_minutes = models.IntegerField(_('Time Limit (Minutes)'), null=True, blank=True, validators=[MinValueValidator(1)])
    max_attempts = models.IntegerField(_('Maximum Attempts'), default=3, validators=[MinValueValidator(1)])
    is_final_exam = models.BooleanField(_('Final Exam'), default=False)
    randomize_questions = models.BooleanField(_('Randomize Questions'), default=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def question_count(self):
        return self.questions.count()

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ['course', '-created_at']


class QuizQuestion(models.Model):
    """Questions for quizzes"""
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', _('Multiple Choice')),
        ('true_false', _('True/False')),
        ('short_answer', _('Short Answer')),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name=_('Quiz'))
    question_text = models.TextField(_('Question'))
    question_type = models.CharField(_('Question Type'), max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    order = models.IntegerField(_('Order'), default=0)
    points = models.IntegerField(_('Points'), default=1, validators=[MinValueValidator(1)])

    # Multiple Choice Options
    option_a = models.CharField(_('Option A'), max_length=500, blank=True)
    option_b = models.CharField(_('Option B'), max_length=500, blank=True)
    option_c = models.CharField(_('Option C'), max_length=500, blank=True)
    option_d = models.CharField(_('Option D'), max_length=500, blank=True)

    correct_answer = models.CharField(_('Correct Answer'), max_length=500, help_text=_('For MC: A, B, C, or D. For T/F: True or False'))
    explanation = models.TextField(_('Explanation'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"

    class Meta:
        verbose_name = _('Quiz Question')
        verbose_name_plural = _('Quiz Questions')
        ordering = ['quiz', 'order']


class QuizAttempt(models.Model):
    """Track quiz attempts and scores"""
    STATUS_CHOICES = [
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('abandoned', _('Abandoned')),
    ]

    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='quiz_attempts', verbose_name=_('Enrollment'))
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts', verbose_name=_('Quiz'))

    attempt_number = models.IntegerField(_('Attempt Number'), default=1)
    started_at = models.DateTimeField(_('Started At'), auto_now_add=True)
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='in_progress')

    score = models.DecimalField(_('Score (%)'), max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(_('Passed'), default=False)
    answers = models.JSONField(_('Answers'), default=dict, blank=True)  # Store question_id: answer pairs

    time_spent_minutes = models.IntegerField(_('Time Spent (Minutes)'), default=0)

    def __str__(self):
        return f"{self.enrollment.employee.get_full_name()} - {self.quiz.title} - Attempt {self.attempt_number}"

    def calculate_score(self):
        """Calculate score based on answers"""
        if not self.answers:
            self.score = 0
            self.passed = False
            return

        total_points = 0
        earned_points = 0

        for question in self.quiz.questions.all():
            total_points += question.points
            user_answer = self.answers.get(str(question.id), '')
            if user_answer.strip().lower() == question.correct_answer.strip().lower():
                earned_points += question.points

        if total_points > 0:
            self.score = round((earned_points / total_points) * 100, 2)
            self.passed = self.score >= self.quiz.passing_score
        else:
            self.score = 0
            self.passed = False

        self.save()

    class Meta:
        verbose_name = _('Quiz Attempt')
        verbose_name_plural = _('Quiz Attempts')
        ordering = ['-started_at']


class Certificate(models.Model):
    """Generated certificates for course completion"""
    enrollment = models.OneToOneField(CourseEnrollment, on_delete=models.CASCADE, related_name='certificate', verbose_name=_('Enrollment'))
    certificate_number = models.CharField(_('Certificate Number'), max_length=100, unique=True)
    issued_date = models.DateField(_('Issue Date'), auto_now_add=True)
    expiry_date = models.DateField(_('Expiry Date'), null=True, blank=True)
    file = models.FileField(_('Certificate File'), upload_to='certificates/%Y/%m/', blank=True, null=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    def __str__(self):
        return f"{self.certificate_number} - {self.enrollment.employee.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate unique certificate number
            import uuid
            self.certificate_number = f"CERT-{timezone.now().year}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')
        ordering = ['-issued_date']


class LearningPath(models.Model):
    """Learning path with sequential courses"""
    title = models.CharField(_('Path Title'), max_length=200)
    description = models.TextField(_('Description'))
    courses = models.ManyToManyField(Course, through='LearningPathCourse', related_name='learning_paths', verbose_name=_('Courses'))
    is_active = models.BooleanField(_('Active'), default=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Learning Path')
        verbose_name_plural = _('Learning Paths')
        ordering = ['title']


class LearningPathCourse(models.Model):
    """Through model for LearningPath courses with order"""
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField(_('Order'), default=0)
    is_required = models.BooleanField(_('Required'), default=True)

    class Meta:
        ordering = ['learning_path', 'order']
        unique_together = [['learning_path', 'course'], ['learning_path', 'order']]
