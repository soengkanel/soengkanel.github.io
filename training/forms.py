from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    Course, CourseModule, Lesson, CourseMaterial,
    CourseEnrollment, Quiz, QuizQuestion, Instructor
)


class InstructorForm(forms.ModelForm):
    """Form for creating and editing instructors"""

    class Meta:
        model = Instructor
        fields = ['user', 'bio', 'expertise', 'certifications', 'photo', 'is_active']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'certifications': forms.Textarea(attrs={'rows': 3}),
        }


class CourseForm(forms.ModelForm):
    """Form for creating and editing courses"""

    class Meta:
        model = Course
        fields = [
            'title', 'code', 'description', 'category', 'level',
            'instructor', 'thumbnail', 'duration_hours', 'max_students',
            'passing_score', 'prerequisites', 'status', 'is_mandatory'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'prerequisites': forms.CheckboxSelectMultiple(),
        }


class CourseModuleForm(forms.ModelForm):
    """Form for creating and editing course modules"""

    class Meta:
        model = CourseModule
        fields = ['course', 'title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LessonForm(forms.ModelForm):
    """Form for creating and editing lessons"""

    class Meta:
        model = Lesson
        fields = [
            'module', 'title', 'content_type', 'description', 'content',
            'video_url', 'duration_minutes', 'order', 'is_mandatory'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'content': forms.Textarea(attrs={'rows': 6}),
        }


class CourseMaterialForm(forms.ModelForm):
    """Form for uploading course materials"""

    class Meta:
        model = CourseMaterial
        fields = ['lesson', 'title', 'file']


class CourseEnrollmentForm(forms.ModelForm):
    """Form for enrolling employees in courses"""

    class Meta:
        model = CourseEnrollment
        fields = [
            'course', 'employee', 'enrollment_date', 'start_date',
            'status', 'completion_date', 'final_score',
            'certificate_issued', 'certificate_date', 'feedback', 'rating', 'review'
        ]
        widgets = {
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
            'certificate_date': forms.DateInput(attrs={'type': 'date'}),
            'feedback': forms.Textarea(attrs={'rows': 3}),
            'review': forms.Textarea(attrs={'rows': 3}),
        }


class QuizForm(forms.ModelForm):
    """Form for creating and editing quizzes"""

    class Meta:
        model = Quiz
        fields = [
            'course', 'lesson', 'title', 'description', 'passing_score',
            'time_limit_minutes', 'max_attempts', 'is_final_exam', 'randomize_questions'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class QuizQuestionForm(forms.ModelForm):
    """Form for creating and editing quiz questions"""

    class Meta:
        model = QuizQuestion
        fields = [
            'quiz', 'question_text', 'question_type', 'order', 'points',
            'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'explanation'
        ]
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 2}),
        }


class BulkEnrollmentForm(forms.Form):
    """Form for bulk enrolling employees in a course"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(status='published'),
        label=_('Course'),
        help_text=_('Select the course for enrollment')
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label=_('Employees'),
        help_text=_('Select employees to enroll')
    )
    enrollment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Enrollment Date'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        from hr.models import Employee
        super().__init__(*args, **kwargs)
        self.fields['employees'].queryset = Employee.objects.filter(employment_status='active')
