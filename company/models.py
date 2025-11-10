from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse
from django_tenants.models import DomainMixin, TenantMixin


class Group(models.Model):
    """
    Model representing a group that can contain multiple companies

    When a Group is deleted, all related Companies will be cascade deleted
    due to the ForeignKey relationship with on_delete=models.CASCADE.
    This will also trigger tenant schema drops for each company due to
    auto_drop_schema=True setting in the Company model.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the group"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the group"
    )
    established_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when the group was established"
    )
    headquarters = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text="Headquarters location"
    )
    website = models.URLField(
        blank=True,
        null=True,
        help_text="Group website URL"
    )
    phone_regex = RegexValidator(
        regex=r'^(\+?855|0)\d{8,10}$',
        message="Phone number must be in Cambodia format: +855xxxxxxxx or 0xxxxxxxx (8-10 digits after prefix)"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Contact email address"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this group is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_group'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('company:group_detail', kwargs={'pk': self.pk})

    @property
    def total_companies(self):
        """Return the total number of companies in this group"""
        from django_tenants.utils import get_public_schema_name, schema_context

        with schema_context(get_public_schema_name()):
            return self.companies.count()

    @property
    def active_companies(self):
        """Return the number of active companies in this group"""
        from django_tenants.utils import get_public_schema_name, schema_context

        with schema_context(get_public_schema_name()):
            return self.companies.filter(is_active=True).count()

    def delete(self, *args, **kwargs):
        """
        Custom delete method to handle cascade deletion safely in multi-tenant environment

        This method:
            pass
        1. Logs the deletion for audit purposes
        2. Lists all companies that will be deleted
        3. Ensures proper cleanup of tenant schemas
        4. Handles any cleanup operations before deletion
        """
        from django.db import transaction

        # Get companies that will be deleted before deletion
        companies_to_delete = list(self.companies.all().values_list('name', 'schema_name'))
        company_count = len(companies_to_delete)

        try:
            with transaction.atomic():
                # Perform the deletion - Django will handle the CASCADE automatically
                # The Company model's auto_drop_schema=True will handle tenant schema cleanup
                super().delete(*args, **kwargs)

        except Exception as e:
            raise

    def get_cascade_deletion_info(self):
        """
        Get information about what will be deleted when this group is deleted

        Returns:
            dict: Information about cascade deletion impact
        """
        companies = self.companies.all()

        cascade_info = {
            'group_name': self.name,
            'companies_count': companies.count(),
            'companies': []
        }

        for company in companies:
            company_info = {
                'name': company.name,
                'schema_name': company.schema_name,
                'is_active': company.is_active,
                'domains': list(company.domains.all().values_list('domain', flat=True))
            }
            cascade_info['companies'].append(company_info)

        return cascade_info


class Company(TenantMixin):
    """
    Model representing a company with multi-tenant functionality enabled
    Each company gets its own database schema
    Uses django-tenant-users for global user authentication with tenant-specific permissions
    """
    COMPANY_TYPES = [
        ('corporation', 'Corporation'),
        ('llc', 'Limited Liability Company'),
        ('partnership', 'Partnership'),
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('nonprofit', 'Non-Profit Organization'),
        ('government', 'Government Entity'),
        ('other', 'Other'),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Name of the company"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='companies',
        help_text="The group this company belongs to"
    )
    company_type = models.CharField(
        max_length=50,
        choices=COMPANY_TYPES,
        default='corporation',
        help_text="Type of company"
    )
    registration_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Company registration number"
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Tax identification number"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the company"
    )
    company_address = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed company address information"
    )
    established_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when the company was established"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Company address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City where the company is located"
    )
    state_province = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="State or province"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Postal or ZIP code"
    )
    country = models.CharField(
        max_length=100,
        default='Cambodia',
        help_text="Country where the company is located"
    )
    website = models.URLField(
        blank=True,
        null=True,
        help_text="Company website URL"
    )
    phone_regex = RegexValidator(
        regex=r'^(\+?855|0)\d{8,10}$',
        message="Phone number must be in Cambodia format: +855xxxxxxxx or 0xxxxxxxx (8-10 digits after prefix)"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Contact email address"
    )
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        help_text="Company logo image"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this company is currently active"
    )

    # Tenant-specific fields
    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['group__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.group.name})"

    def get_absolute_url(self):
        return reverse('company:company_detail', kwargs={'pk': self.pk})

    @property
    def full_address(self):
        """Return the full formatted address"""
        address_parts = [
            self.address,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in address_parts if part])

    def save(self, *args, **kwargs):
        """Override save to auto-generate schema_name from company name"""
        if not self.schema_name:
            # Generate schema name from company name (lowercase, replace spaces/special chars with underscore)
            import re
            self.schema_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        super().save(*args, **kwargs)

    # Users are now tenant-specific, so no need for company-based user filtering


class Domain(DomainMixin):
    """
    Domain model for tenant routing
    Each company can have multiple domains pointing to their tenant schema
    """
    pass

    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'

    def __str__(self):
        return f"{self.domain} -> {self.tenant.name}"


class Branch(models.Model):
    """
    Model representing a branch/sub-company location
    Each company can have multiple branches
    """
    name = models.CharField(
        max_length=200,
        help_text="Name of the branch"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique branch code"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the branch"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Branch address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City where the branch is located"
    )
    state_province = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="State or province"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Postal or ZIP code"
    )
    country = models.CharField(
        max_length=100,
        default='Cambodia',
        help_text="Country where the branch is located"
    )
    phone_regex = RegexValidator(
        regex=r'^(\+?855|0)\d{8,10}$',
        message="Phone number must be in Cambodia format: +855xxxxxxxx or 0xxxxxxxx (8-10 digits after prefix)"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Branch contact email"
    )
    manager_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Branch manager name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this branch is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def full_address(self):
        """Return the full formatted address"""
        address_parts = [
            self.address,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in address_parts if part])


# UserCompanyAccess model removed - users are now tenant-specific
# Each company has its own isolated set of users
# No need for cross-company access control
