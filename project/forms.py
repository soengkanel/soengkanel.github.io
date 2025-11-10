from django import forms
from django.forms import inlineformset_factory
from django.forms.widgets import DateInput, Select, TextInput, Textarea
from .models import (
    Project, ProjectTask, ProjectTeamMember, ProjectType,
    ProjectTemplate, Timesheet, TimesheetDetail, ProjectMilestone,
    ProjectExpense, ProjectUpdate, Team, TeamMember, ProjectSettings
)


class BaseModelForm(forms.ModelForm):
    """Base form with consistent compact styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.URLInput)):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'style': 'font-size: 12px; min-height: 28px;'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 3,
                    'style': 'font-size: 12px; min-height: 60px;'
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'form-select',
                    'style': 'font-size: 12px; min-height: 28px;'
                })
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'type': 'date',
                    'style': 'font-size: 12px; min-height: 28px;'
                })
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'style': 'font-size: 12px; min-height: 28px;'
                })
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'form-check-input',
                    'style': 'margin-top: 0.25rem;'
                })


class ProjectFilterForm(forms.Form):
    """Form for filtering projects"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search projects...',
            'class': 'form-input',
            'hx-get': '',
            'hx-target': '#project-cards',
            'hx-trigger': 'input changed delay:300ms, search'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Project.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '',
            'hx-target': '#project-cards',
            'hx-trigger': 'change'
        })
    )

    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + Project.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '',
            'hx-target': '#project-cards',
            'hx-trigger': 'change'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
            'hx-get': '',
            'hx-target': '#project-cards',
            'hx-trigger': 'change'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
            'hx-get': '',
            'hx-target': '#project-cards',
            'hx-trigger': 'change'
        })
    )


class ProjectForm(BaseModelForm):
    """Form for creating/editing projects with compact styling"""

    class Meta:
        model = Project
        fields = [
            'project_name', 'description', 'location', 'site_address',
            'client_name', 'client_contact', 'client_phone',
            'project_manager', 'expected_start_date', 'expected_end_date',
            'priority', 'status', 'estimated_cost', 'estimated_duration_days', 'notes'
        ]

        widgets = {
            'project_name': TextInput(attrs={
                'placeholder': 'Enter project name',
                'maxlength': '200',
                'data-validate': 'required'
            }),
            'description': Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe the project objectives and scope'
            }),
            'location': TextInput(attrs={
                'placeholder': 'Project location',
                'maxlength': '300'
            }),
            'site_address': Textarea(attrs={
                'rows': 2,
                'placeholder': 'Full site address'
            }),
            'client_name': TextInput(attrs={
                'placeholder': 'Client name',
                'maxlength': '200'
            }),
            'client_contact': TextInput(attrs={
                'placeholder': 'Contact person name',
                'maxlength': '100'
            }),
            'client_phone': TextInput(attrs={
                'placeholder': 'Phone number',
                'maxlength': '20'
            }),
            'expected_start_date': DateInput(attrs={
                'type': 'date',
                'title': 'Expected start date for the project',
                'data-validate': 'required'
            }),
            'expected_end_date': DateInput(attrs={
                'type': 'date',
                'title': 'Expected completion date'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'title': 'Total estimated cost'
            }),
            'estimated_duration_days': forms.NumberInput(attrs={
                'min': '0',
                'placeholder': '0',
                'title': 'Estimated duration in days'
            }),
            'notes': Textarea(attrs={
                'rows': 3,
                'placeholder': 'Additional notes, requirements, or comments'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default start date to today for new projects
        if not self.instance.pk and 'expected_start_date' in self.fields:
            from datetime import date
            if not self.initial.get('expected_start_date'):
                self.fields['expected_start_date'].initial = date.today()

        # Remove HTML5 required attribute from all fields to avoid issues with hidden tabs
        # We'll handle validation with JavaScript instead
        for field_name, field in self.fields.items():
            # Disable HTML5 required attribute rendering
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.pop('required', None)
                # Also ensure required is not set as an empty string
                if 'required' in field.widget.attrs:
                    del field.widget.attrs['required']

            # Override the widget's use_required_attribute method to prevent Django from adding it
            field.widget.use_required_attribute = lambda initial: False

            # Keep Django's validation but remove HTML required attribute
            if field_name in ['project_name', 'expected_start_date']:
                field.required = True
            else:
                field.required = False

        # Make status optional (will use default 'open' from model)
        if 'status' in self.fields:
            self.fields['status'].required = False

        # Add empty choice for optional select fields
        if 'project_manager' in self.fields:
            self.fields['project_manager'].empty_label = "Select Project Manager (Optional)"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('expected_start_date')
        end_date = cleaned_data.get('expected_end_date')

        # Set default status if not provided
        if not cleaned_data.get('status'):
            cleaned_data['status'] = 'open'

        # Validate date range
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                "Expected end date cannot be earlier than the start date."
            )

        return cleaned_data


class QuickTaskForm(BaseModelForm):
    """Quick form for adding tasks"""

    class Meta:
        model = ProjectTask
        fields = ['task_name', 'assigned_to', 'expected_end_date', 'priority']

        widgets = {
            'task_name': TextInput(attrs={
                'placeholder': 'Enter task name...',
                'class': 'form-input'
            }),
            'expected_end_date': DateInput(attrs={'type': 'date'}),
        }


class ProjectTaskForm(BaseModelForm):
    """Full form for creating/editing tasks"""

    # Override assigned_to to show employee names properly
    assigned_to = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Assigned To"
    )

    class Meta:
        model = ProjectTask
        fields = [
            'task_name', 'description', 'assigned_to',
            'expected_start_date', 'expected_end_date', 'priority',
            'estimated_hours', 'progress'
        ]

        widgets = {
            'expected_start_date': DateInput(attrs={'type': 'date'}),
            'expected_end_date': DateInput(attrs={'type': 'date'}),
            'estimated_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0'}),
            'progress': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
            'description': Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if project:
            # Limit assigned_to to project team members (Employee objects)
            from hr.models import Employee
            team_member_employee_ids = project.team_members.values_list('employee_id', flat=True)
            employees = Employee.objects.filter(
                id__in=team_member_employee_ids
            ).select_related('user')

            self.fields['assigned_to'].queryset = employees

            # Set choice labels to show full names
            self.fields['assigned_to'].choices = [('', '---------')] + [
                (emp.id, emp.user.get_full_name() if emp.user else emp.full_name) for emp in employees
            ]
        else:
            from hr.models import Employee
            self.fields['assigned_to'].queryset = Employee.objects.none()


class TeamMemberForm(BaseModelForm):
    """Form for adding team members to projects"""

    class Meta:
        model = ProjectTeamMember
        fields = ['employee', 'role', 'hourly_rate', 'start_date', 'end_date']

        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'hourly_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }


class TimesheetForm(BaseModelForm):
    """Form for creating/editing timesheets"""

    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'font-size: 12px; min-height: 28px;'
        }),
        help_text='Optional: Primary project for this timesheet'
    )

    class Meta:
        model = Timesheet
        fields = ['employee', 'start_date', 'end_date', 'notes']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'notes': Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set up employee queryset - filter by active status
        from hr.models import Employee
        self.fields['employee'].queryset = Employee.objects.filter(employment_status='active')

        # Set up project queryset - show all active projects
        self.fields['project'].queryset = Project.objects.filter(
            status__in=['open', 'in_progress']
        ).order_by('project_name')

        # Pre-select current user's employee if available
        if user and not self.instance.pk:
            try:
                employee = Employee.objects.get(user=user)
                self.fields['employee'].initial = employee
            except Employee.DoesNotExist:
                pass


class TimesheetEntryForm(BaseModelForm):
    """Form for timesheet entries"""

    class Meta:
        model = TimesheetDetail
        fields = [
            'activity_date', 'project', 'task', 'activity_type',
            'from_time', 'to_time', 'hours', 'description', 'is_billable'
        ]

        widgets = {
            'activity_date': DateInput(attrs={'type': 'date'}),
            'from_time': forms.TimeInput(attrs={'type': 'time'}),
            'to_time': forms.TimeInput(attrs={'type': 'time'}),
            'hours': forms.NumberInput(attrs={'step': '0.25', 'min': '0', 'max': '24'}),
            'description': Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)

        if employee:
            # Limit projects to those where the employee is a member
            self.fields['project'].queryset = Project.objects.filter(
                team_members__employee=employee
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        from_time = cleaned_data.get('from_time')
        to_time = cleaned_data.get('to_time')
        hours = cleaned_data.get('hours')

        # Auto-calculate hours if times are provided
        if from_time and to_time and not hours:
            from datetime import datetime, timedelta
            start = datetime.combine(datetime.today(), from_time)
            end = datetime.combine(datetime.today(), to_time)

            # Handle overnight work
            if end < start:
                end += timedelta(days=1)

            duration = end - start
            cleaned_data['hours'] = duration.total_seconds() / 3600

        return cleaned_data


class ProjectMilestoneForm(BaseModelForm):
    """Comprehensive form for creating and editing project milestones"""

    class Meta:
        model = ProjectMilestone
        fields = [
            'milestone_name', 'description', 'milestone_date', 'milestone_type',
            'status', 'completion_percentage', 'amount', 'is_billable',
            'requires_approval', 'task', 'deliverables', 'acceptance_criteria',
            'depends_on_milestones'
        ]

        widgets = {
            'milestone_name': TextInput(attrs={
                'placeholder': 'Enter milestone name...',
                'maxlength': '200'
            }),
            'description': Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe the milestone objectives and scope...'
            }),
            'milestone_date': DateInput(attrs={
                'type': 'date',
                'title': 'Target completion date for this milestone'
            }),
            'completion_percentage': forms.NumberInput(attrs={
                'min': '0',
                'max': '100',
                'step': '5',
                'placeholder': '0',
                'title': 'Current completion percentage'
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'title': 'Payment amount or budget allocation'
            }),
            'deliverables': Textarea(attrs={
                'rows': 3,
                'placeholder': 'List the specific deliverables for this milestone...'
            }),
            'acceptance_criteria': Textarea(attrs={
                'rows': 3,
                'placeholder': 'Define the criteria for milestone completion...'
            }),
            'depends_on_milestones': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        # Set field requirements
        self.fields['milestone_name'].required = True
        self.fields['milestone_date'].required = True

        if project:
            # Limit task choices to tasks in the same project
            self.fields['task'].queryset = ProjectTask.objects.filter(project=project)
            self.fields['task'].empty_label = "Select related task (optional)"

            # Limit dependency choices to other milestones in the same project
            existing_milestone = self.instance.pk if self.instance else None
            milestone_qs = ProjectMilestone.objects.filter(project=project)
            if existing_milestone:
                milestone_qs = milestone_qs.exclude(pk=existing_milestone)
            self.fields['depends_on_milestones'].queryset = milestone_qs
        else:
            self.fields['task'].queryset = ProjectTask.objects.none()
            self.fields['depends_on_milestones'].queryset = ProjectMilestone.objects.none()

        # Set help texts
        self.fields['milestone_type'].help_text = "Select the type of milestone"
        self.fields['is_billable'].help_text = "Check if this milestone is billable to the client"
        self.fields['requires_approval'].help_text = "Check if this milestone requires approval before completion"
        self.fields['amount'].help_text = "Payment amount for this milestone (if applicable)"

    def clean(self):
        cleaned_data = super().clean()
        milestone_type = cleaned_data.get('milestone_type')
        amount = cleaned_data.get('amount')
        is_billable = cleaned_data.get('is_billable')

        # Validate amount for payment milestones
        if milestone_type == 'payment' and not amount:
            raise forms.ValidationError("Payment milestones must have an amount specified.")

        # Validate billable amount
        if is_billable and not amount:
            raise forms.ValidationError("Billable milestones must have an amount specified.")

        return cleaned_data


class MilestoneFilterForm(forms.Form):
    """Form for filtering milestones with HTMX support"""

    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search milestones...',
            'class': 'form-control',
            'hx-get': '',
            'hx-target': '#milestone-list',
            'hx-trigger': 'input changed delay:300ms, search'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'All Status')] + ProjectMilestone.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '',
            'hx-target': '#milestone-list',
            'hx-trigger': 'change'
        })
    )

    milestone_type = forms.ChoiceField(
        choices=[('', 'All Types')] + ProjectMilestone.MILESTONE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '',
            'hx-target': '#milestone-list',
            'hx-trigger': 'change'
        })
    )

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="All Projects",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '',
            'hx-target': '#milestone-list',
            'hx-trigger': 'change'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'hx-get': '',
            'hx-target': '#milestone-list',
            'hx-trigger': 'change'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'hx-get': '',
            'hx-target': '#milestone-list',
            'hx-trigger': 'change'
        })
    )

    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'hx-get': '',
            'hx-target': '#milestone-list',
            'hx-trigger': 'change'
        })
    )

    requires_approval = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'hx-get': '',
            'hx-target': '#milestone-list',
            'hx-trigger': 'change'
        })
    )


class MilestoneStatusUpdateForm(forms.Form):
    """Quick form for updating milestone status and completion"""

    status = forms.ChoiceField(
        choices=ProjectMilestone.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'title': 'Select milestone status'
        })
    )

    completion_percentage = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '100',
            'step': '5',
            'title': 'Completion percentage'
        })
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Optional notes about the status update...'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        completion_percentage = cleaned_data.get('completion_percentage')

        # Auto-set completion percentage based on status
        if status == 'completed' and completion_percentage != 100:
            cleaned_data['completion_percentage'] = 100
        elif status == 'pending' and completion_percentage > 0:
            cleaned_data['completion_percentage'] = 0

        return cleaned_data


class MilestoneApprovalForm(forms.Form):
    """Form for milestone approval workflow"""

    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('request_changes', 'Request Changes')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

    comments = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Add comments about your approval decision...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comments'].required = True


class QuickMilestoneForm(BaseModelForm):
    """Quick form for adding milestones with minimal fields"""

    class Meta:
        model = ProjectMilestone
        fields = ['milestone_name', 'milestone_date', 'milestone_type', 'amount']

        widgets = {
            'milestone_name': TextInput(attrs={
                'placeholder': 'Milestone name...',
                'class': 'form-control',
                'maxlength': '200'
            }),
            'milestone_date': DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['milestone_name'].required = True
        self.fields['milestone_date'].required = True


class BulkMilestoneUpdateForm(forms.Form):
    """Form for bulk updating multiple milestones"""

    milestone_ids = forms.CharField(widget=forms.HiddenInput())

    action = forms.ChoiceField(
        choices=[
            ('', 'Select Action'),
            ('update_status', 'Update Status'),
            ('update_type', 'Update Type'),
            ('mark_billable', 'Mark as Billable'),
            ('mark_non_billable', 'Mark as Non-Billable'),
            ('delete', 'Delete Selected')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    new_status = forms.ChoiceField(
        choices=[('', 'Select Status')] + ProjectMilestone.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    new_type = forms.ChoiceField(
        choices=[('', 'Select Type')] + ProjectMilestone.MILESTONE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        new_status = cleaned_data.get('new_status')
        new_type = cleaned_data.get('new_type')

        if action == 'update_status' and not new_status:
            raise forms.ValidationError("Please select a new status.")

        if action == 'update_type' and not new_type:
            raise forms.ValidationError("Please select a new milestone type.")

        return cleaned_data


class ProjectExpenseForm(BaseModelForm):
    """Form for project expenses"""

    class Meta:
        model = ProjectExpense
        fields = [
            'expense_date', 'expense_type', 'description', 'amount',
            'task', 'is_billable', 'is_reimbursable', 'attachment_url'
        ]

        widgets = {
            'expense_date': DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'description': Textarea(attrs={'rows': 2}),
            'attachment_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }


class ProjectUpdateForm(BaseModelForm):
    """Form for project updates/comments"""

    class Meta:
        model = ProjectUpdate
        fields = ['comment', 'is_internal']

        widgets = {
            'comment': Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add your comment or update...'
            }),
        }


class TaskStatusForm(forms.Form):
    """Quick form for updating task status"""
    status = forms.ChoiceField(
        choices=ProjectTask.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select-sm',
            'hx-post': '',
            'hx-target': 'closest tr',
            'hx-trigger': 'change'
        })
    )


class ProjectStatusForm(forms.Form):
    """Quick form for updating project status"""
    status = forms.ChoiceField(
        choices=Project.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select-sm',
            'hx-post': '',
            'hx-trigger': 'change'
        })
    )


class BulkTaskAssignForm(forms.Form):
    """Form for bulk assigning tasks"""
    task_ids = forms.CharField(widget=forms.HiddenInput())
    assigned_to = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if project:
            # Get Employee objects from project team members
            from hr.models import Employee
            team_member_employee_ids = project.team_members.values_list('employee_id', flat=True)
            self.fields['assigned_to'].queryset = Employee.objects.filter(
                id__in=team_member_employee_ids
            ).select_related('user')


# Custom widgets for better UX
class DateRangeWidget(forms.MultiWidget):
    """Custom widget for date ranges"""

    def __init__(self, attrs=None):
        widgets = [
            DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            DateInput(attrs={'type': 'date', 'class': 'form-input'})
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.end]
        return [None, None]


class StatusBadgeWidget(forms.Select):
    """Custom widget that displays status as badges"""

    def __init__(self, attrs=None, choices=()):
        default_attrs = {'class': 'status-select'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, choices)


# Team Management Forms

class TeamForm(BaseModelForm):
    """Form for creating and editing teams"""

    class Meta:
        model = Team
        fields = [
            'team_name', 'description', 'team_type', 'max_members',
            'department', 'team_lead', 'status'
        ]

        widgets = {
            'description': Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the team\'s purpose and responsibilities...'
            }),
            'max_members': forms.NumberInput(attrs={'min': '1', 'max': '100'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get available employees and departments
        try:
            from hr.models import Employee, Department
            self.fields['team_lead'].queryset = Employee.objects.filter(employment_status='active')
            self.fields['department'].queryset = Department.objects.all()
        except:
            # Handle case where HR models don't exist
            self.fields['team_lead'].queryset = self.fields['team_lead'].queryset.none()
            self.fields['department'].queryset = self.fields['department'].queryset.none()


class TeamMemberFormNew(BaseModelForm):
    """Form for adding members to teams"""

    class Meta:
        model = TeamMember
        fields = [
            'employee', 'role', 'availability', 'allocation_percentage',
            'hourly_rate', 'responsibilities', 'start_date', 'end_date',
            'can_manage_team', 'can_assign_tasks', 'can_view_reports'
        ]

        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'allocation_percentage': forms.NumberInput(attrs={'min': '1', 'max': '100', 'step': '5'}),
            'hourly_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'responsibilities': Textarea(attrs={
                'rows': 3,
                'placeholder': 'Specific responsibilities in this team...'
            }),
        }

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)

        # Limit employee choices to those not already in the team
        if team:
            try:
                from hr.models import Employee
                existing_members = team.team_members.filter(is_active=True).values_list('employee_id', flat=True)
                self.fields['employee'].queryset = Employee.objects.filter(
                    employment_status='active'
                ).exclude(id__in=existing_members)
            except:
                self.fields['employee'].queryset = self.fields['employee'].queryset.none()

    def clean_allocation_percentage(self):
        allocation = self.cleaned_data.get('allocation_percentage')
        if allocation and (allocation < 1 or allocation > 100):
            raise forms.ValidationError("Allocation must be between 1% and 100%")
        return allocation

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be earlier than start date")

        return cleaned_data


class TeamFilterForm(forms.Form):
    """Filter form for team list"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search teams...'
        })
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + Team.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    team_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Team.TEAM_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    department = forms.ModelChoiceField(
        required=False,
        queryset=None,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set department queryset
        try:
            from hr.models import Department
            self.fields['department'].queryset = Department.objects.all()
        except:
            self.fields['department'].queryset = self.fields['department'].queryset.none()


class QuickTeamMemberForm(forms.Form):
    """Quick form for adding team members via HTMX"""

    employee_id = forms.CharField(widget=forms.HiddenInput())
    role = forms.ChoiceField(
        choices=TeamMember.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    availability = forms.ChoiceField(
        choices=TeamMember.AVAILABILITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    allocation_percentage = forms.IntegerField(
        initial=100,
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '100'
        })
    )
    hourly_rate = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Optional'
        })
    )


# Team Member Inline Formset for Team Creation
TeamMemberInlineFormSet = inlineformset_factory(
    Team,
    TeamMember,
    form=TeamMemberFormNew,
    extra=1,
    can_delete=True,
    fields=['employee', 'role', 'allocation_percentage', 'hourly_rate', 'availability']
)


# Project Settings Forms

class ProjectSettingsForm(BaseModelForm):
    """Comprehensive form for project-specific settings"""

    class Meta:
        model = ProjectSettings
        exclude = ['project', 'created_by', 'created_at', 'updated_at']

        widgets = {
            # Working time widgets
            'monday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'monday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'tuesday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'tuesday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'wednesday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'wednesday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'thursday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'thursday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'friday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'friday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'saturday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'saturday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'sunday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'sunday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'break_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'core_hours_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'core_hours_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),

            # Numeric fields
            'break_duration': forms.NumberInput(attrs={'min': '0', 'max': '240', 'class': 'form-control'}),
            'required_hours_per_day': forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'max': '24', 'class': 'form-control'}),
            'working_days_per_week': forms.NumberInput(attrs={'min': '1', 'max': '7', 'class': 'form-control'}),
            'overtime_rate_regular': forms.NumberInput(attrs={'step': '0.1', 'min': '1.0', 'max': '5.0', 'class': 'form-control'}),
            'overtime_rate_weekend': forms.NumberInput(attrs={'step': '0.1', 'min': '1.0', 'max': '5.0', 'class': 'form-control'}),
            'overtime_rate_holiday': forms.NumberInput(attrs={'step': '0.1', 'min': '1.0', 'max': '5.0', 'class': 'form-control'}),
            'min_overtime_minutes': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'max_overtime_hours_per_day': forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'class': 'form-control'}),
            'max_overtime_hours_per_week': forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'class': 'form-control'}),
            'overtime_auto_approve_threshold': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'late_grace_period': forms.NumberInput(attrs={'min': '0', 'max': '60', 'class': 'form-control'}),
            'early_leave_grace_period': forms.NumberInput(attrs={'min': '0', 'max': '60', 'class': 'form-control'}),
            'late_deduction_per_minute': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'absence_deduction_per_day': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'max_late_minutes_per_month': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'max_absences_per_month': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Organize fields into logical sections for template rendering
        self.field_sections = {
            'working_time': {
                'title': 'Working Time Settings',
                'description': 'Configure project-specific working hours and schedules',
                'toggle_field': 'use_custom_working_time',
                'fields': [
                    'monday_start', 'monday_end', 'tuesday_start', 'tuesday_end',
                    'wednesday_start', 'wednesday_end', 'thursday_start', 'thursday_end',
                    'friday_start', 'friday_end', 'saturday_start', 'saturday_end',
                    'sunday_start', 'sunday_end', 'break_duration', 'break_start',
                    'flexible_hours', 'core_hours_start', 'core_hours_end',
                    'required_hours_per_day'
                ]
            },
            'overtime': {
                'title': 'Overtime Rules',
                'description': 'Define overtime rates and approval requirements',
                'toggle_field': 'use_custom_overtime_rules',
                'fields': [
                    'overtime_rate_regular', 'overtime_rate_weekend', 'overtime_rate_holiday',
                    'min_overtime_minutes', 'max_overtime_hours_per_day',
                    'max_overtime_hours_per_week', 'overtime_requires_approval',
                    'overtime_auto_approve_threshold'
                ]
            },
            'attendance': {
                'title': 'Attendance Setup',
                'description': 'Configure attendance policies and requirements',
                'toggle_field': 'use_custom_attendance_rules',
                'fields': [
                    'late_grace_period', 'early_leave_grace_period',
                    'require_biometric_checkin', 'allow_remote_attendance',
                    'require_location_tracking', 'late_deduction_per_minute',
                    'absence_deduction_per_day', 'max_late_minutes_per_month',
                    'max_absences_per_month'
                ]
            }
        }

    def clean(self):
        cleaned_data = super().clean()

        # Validate working time consistency
        if cleaned_data.get('use_custom_working_time'):
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days:
                start = cleaned_data.get(f'{day}_start')
                end = cleaned_data.get(f'{day}_end')

                # If one is set, both should be set
                if (start and not end) or (end and not start):
                    raise forms.ValidationError(
                        f"Both start and end time must be set for {day.capitalize()} (or leave both empty)"
                    )

        # Validate flexible hours
        if cleaned_data.get('flexible_hours'):
            if not cleaned_data.get('core_hours_start') or not cleaned_data.get('core_hours_end'):
                raise forms.ValidationError(
                    "Core hours start and end times are required when flexible hours is enabled"
                )

        return cleaned_data