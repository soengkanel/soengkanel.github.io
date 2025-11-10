from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from hr.models import Employee
from decimal import Decimal
from datetime import timedelta
import uuid


class ExpenseCategory(models.Model):
    """Expense categories for classification"""
    name = models.CharField(_('Category Name'), max_length=100)
    code = models.CharField(_('Category Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)

    # Policy settings
    requires_receipt = models.BooleanField(_('Requires Receipt'), default=True)
    max_amount_per_claim = models.DecimalField(_('Max Amount Per Claim'), max_digits=12, decimal_places=2, null=True, blank=True)
    requires_approval = models.BooleanField(_('Requires Approval'), default=True)

    # GL Account integration
    gl_account = models.CharField(_('GL Account'), max_length=50, blank=True,
                                help_text=_('General Ledger account for ERPNext integration'))

    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Expense Category')
        verbose_name_plural = _('Expense Categories')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class ExpensePolicy(models.Model):
    """Expense policy configuration"""
    name = models.CharField(_('Policy Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)

    # Eligibility
    applies_to_all_employees = models.BooleanField(_('Applies to All Employees'), default=True)
    applicable_positions = models.ManyToManyField('hr.Position', blank=True, verbose_name=_('Applicable Positions'))
    applicable_departments = models.ManyToManyField('hr.Department', blank=True, verbose_name=_('Applicable Departments'))

    # Limits
    max_amount_per_claim = models.DecimalField(_('Max Amount Per Claim'), max_digits=12, decimal_places=2, default=0)
    max_amount_per_month = models.DecimalField(_('Max Amount Per Month'), max_digits=12, decimal_places=2, default=0)
    max_amount_per_year = models.DecimalField(_('Max Amount Per Year'), max_digits=12, decimal_places=2, default=0)

    # Approval workflow
    auto_approve_limit = models.DecimalField(_('Auto Approve Limit'), max_digits=12, decimal_places=2, default=0)
    requires_manager_approval = models.BooleanField(_('Requires Manager Approval'), default=True)
    requires_finance_approval = models.BooleanField(_('Requires Finance Approval'), default=False)
    finance_approval_limit = models.DecimalField(_('Finance Approval Limit'), max_digits=12, decimal_places=2, default=1000)

    # Document requirements
    receipt_required = models.BooleanField(_('Receipt Required'), default=True)
    receipt_required_above = models.DecimalField(_('Receipt Required Above'), max_digits=12, decimal_places=2, default=0)

    # Timing
    claim_deadline_days = models.PositiveIntegerField(_('Claim Deadline (Days)'), default=30,
                                                    help_text=_('Days after expense date to submit claim'))

    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Expense Policy')
        verbose_name_plural = _('Expense Policies')
        ordering = ['name']

    def __str__(self):
        return self.name


class ExpenseClaim(models.Model):
    """Employee expense claims"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('manager_approved', _('Manager Approved')),
        ('finance_approved', _('Finance Approved')),
        ('approved', _('Approved')),
        ('paid', _('Paid')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
    ]

    # Basic information
    claim_id = models.CharField(_('Claim ID'), max_length=20, unique=True, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='expense_claims')
    policy = models.ForeignKey(ExpensePolicy, on_delete=models.CASCADE, related_name='expense_claims')

    # Claim details
    title = models.CharField(_('Claim Title'), max_length=200)
    purpose = models.TextField(_('Purpose'), blank=True)
    expense_date = models.DateField(_('Expense Date'))
    total_amount = models.DecimalField(_('Total Amount'), max_digits=12, decimal_places=2, default=0)

    # Status and workflow
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_status = models.CharField(_('Payment Status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Approval workflow
    submitted_at = models.DateTimeField(_('Submitted At'), null=True, blank=True)
    manager_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='manager_approved_expenses')
    manager_approved_at = models.DateTimeField(_('Manager Approved At'), null=True, blank=True)
    finance_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='finance_approved_expenses')
    finance_approved_at = models.DateTimeField(_('Finance Approved At'), null=True, blank=True)

    # Rejection
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='rejected_expenses')
    rejected_at = models.DateTimeField(_('Rejected At'), null=True, blank=True)
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)

    # Payment details
    payment_method = models.CharField(_('Payment Method'), max_length=50, blank=True,
                                    choices=[('bank_transfer', _('Bank Transfer')), ('cash', _('Cash')), ('cheque', _('Cheque'))])
    payment_reference = models.CharField(_('Payment Reference'), max_length=100, blank=True)
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='processed_expense_payments')

    # ERPNext integration
    erp_expense_claim_id = models.CharField(_('ERP Expense Claim ID'), max_length=50, blank=True)
    erp_journal_entry_id = models.CharField(_('ERP Journal Entry ID'), max_length=50, blank=True)

    # System fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_expense_claims')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Expense Claim')
        verbose_name_plural = _('Expense Claims')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.claim_id} - {self.employee.full_name} - KHR {self.total_amount:,.2f}"

    def save(self, *args, **kwargs):
        # Generate claim ID
        if not self.claim_id:
            self.claim_id = self.generate_claim_id()

        # Calculate total amount from line items
        if self.pk:
            self.total_amount = sum(item.amount for item in self.line_items.all())

        # Update status timestamps
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        elif self.status == 'manager_approved' and not self.manager_approved_at:
            self.manager_approved_at = timezone.now()
        elif self.status == 'finance_approved' and not self.finance_approved_at:
            self.finance_approved_at = timezone.now()
        elif self.status == 'rejected' and not self.rejected_at:
            self.rejected_at = timezone.now()
        elif self.payment_status == 'paid' and not self.paid_at:
            self.paid_at = timezone.now()
            if self.status != 'paid':
                self.status = 'paid'

        super().save(*args, **kwargs)

    def generate_claim_id(self):
        """Generate unique claim ID"""
        year = timezone.now().year
        month = timezone.now().month
        count = ExpenseClaim.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count() + 1
        return f"EXP{year:04d}{month:02d}{count:04d}"

    @property
    def is_overdue(self):
        """Check if claim is overdue for submission"""
        if self.status != 'draft':
            return False
        deadline = self.expense_date + timedelta(days=self.policy.claim_deadline_days)
        return timezone.now().date() > deadline

    def can_edit(self, user):
        """Check if user can edit this claim"""
        if self.status not in ['draft', 'rejected']:
            return False
        return user == self.created_by or user.is_superuser

    def can_approve_manager(self, user):
        """Check if user can approve as manager"""
        if self.status != 'submitted':
            return False
        # Check if user is manager of employee
        return user == self.employee.user or user.is_superuser  # Simplified check

    def can_approve_finance(self, user):
        """Check if user can approve as finance"""
        if self.status != 'manager_approved':
            return False
        if not self.policy.requires_finance_approval:
            return False
        if self.total_amount < self.policy.finance_approval_limit:
            return False
        # Check if user has finance permission (simplified)
        return user.groups.filter(name__icontains='finance').exists() or user.is_superuser


class ExpenseClaimLineItem(models.Model):
    """Individual line items in expense claims"""
    claim = models.ForeignKey(ExpenseClaim, on_delete=models.CASCADE, related_name='line_items')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)

    # Item details
    description = models.CharField(_('Description'), max_length=200)
    expense_date = models.DateField(_('Expense Date'))
    amount = models.DecimalField(_('Amount'), max_digits=12, decimal_places=2)
    quantity = models.DecimalField(_('Quantity'), max_digits=10, decimal_places=2, default=1)
    unit_cost = models.DecimalField(_('Unit Cost'), max_digits=12, decimal_places=2, default=0)

    # Supporting documents
    receipt = models.FileField(_('Receipt'), upload_to='expense_receipts/', null=True, blank=True)
    additional_document = models.FileField(_('Additional Document'), upload_to='expense_documents/', null=True, blank=True)

    # ERPNext fields
    erp_expense_type = models.CharField(_('ERP Expense Type'), max_length=100, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Expense Claim Line Item')
        verbose_name_plural = _('Expense Claim Line Items')
        ordering = ['expense_date']

    def __str__(self):
        return f"{self.claim.claim_id} - {self.description} - KHR {self.amount:,.2f}"

    def save(self, *args, **kwargs):
        # Calculate amount from quantity and unit cost if not provided
        if self.quantity and self.unit_cost and not self.amount:
            self.amount = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def clean(self):
        # Validate receipt requirement
        if self.category.requires_receipt and not self.receipt:
            if self.amount > self.claim.policy.receipt_required_above:
                raise ValidationError(_('Receipt is required for this category and amount.'))


class EmployeeAdvance(models.Model):
    """Employee salary advances"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('paid', _('Paid')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
        ('fully_recovered', _('Fully Recovered')),
    ]

    RECOVERY_METHOD_CHOICES = [
        ('salary_deduction', _('Salary Deduction')),
        ('lump_sum', _('Lump Sum')),
        ('installments', _('Installments')),
    ]

    # Basic information
    advance_id = models.CharField(_('Advance ID'), max_length=20, unique=True, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_advances')

    # Advance details
    purpose = models.TextField(_('Purpose'))
    requested_amount = models.DecimalField(_('Requested Amount'), max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(_('Approved Amount'), max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(_('Paid Amount'), max_digits=12, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(_('Outstanding Amount'), max_digits=12, decimal_places=2, default=0)
    recovered_amount = models.DecimalField(_('Recovered Amount'), max_digits=12, decimal_places=2, default=0)

    # Recovery settings
    recovery_method = models.CharField(_('Recovery Method'), max_length=20, choices=RECOVERY_METHOD_CHOICES, default='salary_deduction')
    recovery_start_date = models.DateField(_('Recovery Start Date'), null=True, blank=True)
    number_of_installments = models.PositiveIntegerField(_('Number of Installments'), default=1)
    installment_amount = models.DecimalField(_('Installment Amount'), max_digits=12, decimal_places=2, default=0)

    # Status and workflow
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Approval
    submitted_at = models.DateTimeField(_('Submitted At'), null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='approved_employee_advances')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)

    # Rejection
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='rejected_advances')
    rejected_at = models.DateTimeField(_('Rejected At'), null=True, blank=True)
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)

    # Payment
    payment_date = models.DateField(_('Payment Date'), null=True, blank=True)
    payment_method = models.CharField(_('Payment Method'), max_length=50, blank=True)
    payment_reference = models.CharField(_('Payment Reference'), max_length=100, blank=True)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='processed_advance_payments')

    # ERPNext integration
    erp_employee_advance_id = models.CharField(_('ERP Employee Advance ID'), max_length=50, blank=True)

    # System fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_advances')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Employee Advance')
        verbose_name_plural = _('Employee Advances')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.advance_id} - {self.employee.full_name} - KHR {self.requested_amount:,.2f}"

    def save(self, *args, **kwargs):
        # Generate advance ID
        if not self.advance_id:
            self.advance_id = self.generate_advance_id()

        # Calculate outstanding amount
        self.outstanding_amount = self.paid_amount - self.recovered_amount

        # Calculate installment amount
        if self.approved_amount and self.number_of_installments:
            self.installment_amount = self.approved_amount / self.number_of_installments

        # Update status based on recovery
        if self.recovered_amount >= self.paid_amount and self.status == 'paid':
            self.status = 'fully_recovered'

        # Update timestamps
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        elif self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        elif self.status == 'rejected' and not self.rejected_at:
            self.rejected_at = timezone.now()

        super().save(*args, **kwargs)

    def generate_advance_id(self):
        """Generate unique advance ID"""
        year = timezone.now().year
        month = timezone.now().month
        count = EmployeeAdvance.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count() + 1
        return f"ADV{year:04d}{month:02d}{count:04d}"

    @property
    def recovery_percentage(self):
        """Calculate recovery percentage"""
        if self.paid_amount > 0:
            return (self.recovered_amount / self.paid_amount) * 100
        return 0


class AdvanceRecovery(models.Model):
    """Track advance recovery installments"""
    advance = models.ForeignKey(EmployeeAdvance, on_delete=models.CASCADE, related_name='recoveries')
    recovery_date = models.DateField(_('Recovery Date'))
    amount = models.DecimalField(_('Amount'), max_digits=12, decimal_places=2)
    recovery_method = models.CharField(_('Recovery Method'), max_length=50,
                                     choices=[('salary_deduction', _('Salary Deduction')),
                                            ('cash_payment', _('Cash Payment'))])

    # Payroll integration
    salary_slip_reference = models.CharField(_('Salary Slip Reference'), max_length=50, blank=True)

    notes = models.TextField(_('Notes'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Advance Recovery')
        verbose_name_plural = _('Advance Recoveries')
        ordering = ['-recovery_date']

    def __str__(self):
        return f"{self.advance.advance_id} - Recovery KHR {self.amount:,.2f} on {self.recovery_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update advance recovered amount
        self.advance.recovered_amount = sum(recovery.amount for recovery in self.advance.recoveries.all())
        self.advance.save()


class ExpenseApprovalWorkflow(models.Model):
    """Multi-level approval workflow for expenses"""
    APPROVAL_TYPE_CHOICES = [
        ('manager', _('Manager Approval')),
        ('finance', _('Finance Approval')),
        ('ceo', _('CEO Approval')),
        ('custom', _('Custom Approval')),
    ]

    name = models.CharField(_('Workflow Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)

    # Conditions
    min_amount = models.DecimalField(_('Minimum Amount'), max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(_('Maximum Amount'), max_digits=12, decimal_places=2, null=True, blank=True)
    categories = models.ManyToManyField(ExpenseCategory, blank=True, verbose_name=_('Applicable Categories'))

    # Approval levels
    level_1_type = models.CharField(_('Level 1 Type'), max_length=20, choices=APPROVAL_TYPE_CHOICES)
    level_1_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='level1_workflows', verbose_name=_('Level 1 Approver'))

    level_2_type = models.CharField(_('Level 2 Type'), max_length=20, choices=APPROVAL_TYPE_CHOICES, blank=True)
    level_2_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='level2_workflows', verbose_name=_('Level 2 Approver'))

    level_3_type = models.CharField(_('Level 3 Type'), max_length=20, choices=APPROVAL_TYPE_CHOICES, blank=True)
    level_3_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='level3_workflows', verbose_name=_('Level 3 Approver'))

    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Expense Approval Workflow')
        verbose_name_plural = _('Expense Approval Workflows')
        ordering = ['min_amount']

    def __str__(self):
        return f"{self.name} (KHR {self.min_amount:,.0f}+)"

    def applies_to_claim(self, claim):
        """Check if workflow applies to given claim"""
        if not self.is_active:
            return False

        # Check amount range
        if claim.total_amount < self.min_amount:
            return False
        if self.max_amount and claim.total_amount > self.max_amount:
            return False

        # Check categories
        if self.categories.exists():
            claim_categories = set(item.category for item in claim.line_items.all())
            if not claim_categories.intersection(set(self.categories.all())):
                return False

        return True
