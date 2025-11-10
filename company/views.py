from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django_tenants.utils import get_tenant
from .models import Group, Company, Branch
from .forms import BranchForm


def company_dashboard(request):
    """
    Dashboard view showing overview of groups and companies
    """
    # Get statistics
    total_groups = Group.objects.count()
    active_groups = Group.objects.filter(is_active=True).count()
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(is_active=True).count()
    
    # Get recent groups and companies
    recent_groups = Group.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_companies = Company.objects.filter(is_active=True).select_related('group').order_by('-created_at')[:5]
    
    # Get groups with company counts
    groups_with_counts = Group.objects.annotate(
        company_count=Count('companies'),
        active_company_count=Count('companies', filter=Q(companies__is_active=True))
    ).filter(is_active=True).order_by('-company_count')[:10]
    
    context = {
        'total_groups': total_groups,
        'active_groups': active_groups,
        'total_companies': total_companies,
        'active_companies': active_companies,
        'recent_groups': recent_groups,
        'recent_companies': recent_companies,
        'groups_with_counts': groups_with_counts,
    }
    
    return render(request, 'company/dashboard.html', context)


# Group Views
class GroupListView(ListView):
    model = Group
    template_name = 'company/group_list.html'
    context_object_name = 'groups'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Group.objects.annotate(
            company_count=Count('companies'),
            active_company_count=Count('companies', filter=Q(companies__is_active=True))
        ).order_by('name')
        
        # Filter by search query
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(headquarters__icontains=search_query)
            )
        
        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class GroupDetailView(DetailView):
    model = Group
    template_name = 'company/group_detail.html'
    context_object_name = 'group'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get companies in this group with pagination
        companies_list = self.object.companies.select_related().order_by('name')
        paginator = Paginator(companies_list, 10)
        page = self.request.GET.get('page')
        companies = paginator.get_page(page)
        context['companies'] = companies
        return context


class GroupCreateView(CreateView):
    model = Group
    template_name = 'company/group_form.html'
    fields = [
        'name', 'description', 'established_date', 'headquarters',
        'website', 'phone_number', 'email', 'is_active'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, f'Group "{form.instance.name}" was created successfully.')
        return super().form_valid(form)


class GroupUpdateView(UpdateView):
    model = Group
    template_name = 'company/group_form.html'
    fields = [
        'name', 'description', 'established_date', 'headquarters',
        'website', 'phone_number', 'email', 'is_active'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, f'Group "{form.instance.name}" was updated successfully.')
        return super().form_valid(form)


class GroupDeleteView(DeleteView):
    model = Group
    template_name = 'company/group_confirm_delete.html'
    success_url = reverse_lazy('company:group_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'Group "{obj.name}" was deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Company Views
class CompanyListView(ListView):
    model = Company
    template_name = 'company/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Company.objects.select_related('group').order_by('group__name', 'name')
        
        # Filter by search query
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(group__name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(registration_number__icontains=search_query) |
                Q(city__icontains=search_query)
            )
        
        # Filter by group
        group_filter = self.request.GET.get('group')
        if group_filter:
            queryset = queryset.filter(group_id=group_filter)
        
        # Filter by company type
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(company_type=type_filter)
        
        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['group_filter'] = self.request.GET.get('group', '')
        context['type_filter'] = self.request.GET.get('type', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['groups'] = Group.objects.filter(is_active=True).order_by('name')
        context['company_types'] = Company.COMPANY_TYPES
        return context


class CompanyDetailView(DetailView):
    model = Company
    template_name = 'company/company_detail.html'
    context_object_name = 'company'
    
    def get_queryset(self):
        return Company.objects.select_related('group')


class CompanyCreateView(CreateView):
    model = Company
    template_name = 'company/company_form.html'
    fields = [
        'name', 'group', 'company_type', 'registration_number', 'tax_id',
        'description', 'company_address', 'established_date', 'address', 'city', 'state_province',
        'postal_code', 'country', 'website', 'phone_number', 'email', 'logo', 'is_active'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, f'Company "{form.instance.name}" was created successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.filter(is_active=True).order_by('name')
        return context


class CompanyUpdateView(UpdateView):
    model = Company
    template_name = 'company/company_form.html'
    fields = [
        'name', 'group', 'company_type', 'registration_number', 'tax_id',
        'description', 'company_address', 'established_date', 'address', 'city', 'state_province',
        'postal_code', 'country', 'website', 'phone_number', 'email', 'logo', 'is_active'
    ]
    
    def form_valid(self, form):
        messages.success(self.request, f'Company "{form.instance.name}" was updated successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.filter(is_active=True).order_by('name')
        return context


class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'company/company_confirm_delete.html'
    success_url = reverse_lazy('company:company_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'Company "{obj.name}" was deleted successfully.')
        return super().delete(request, *args, **kwargs)


# API Views for AJAX calls
class GroupAPIView(View):
    def get(self, request):
        """Return groups as JSON for AJAX calls"""
        search = request.GET.get('search', '')
        groups = Group.objects.filter(is_active=True)
        
        if search:
            groups = groups.filter(name__icontains=search)
        
        groups_data = [
            {
                'id': group.id,
                'name': group.name,
                'headquarters': group.headquarters,
                'company_count': group.total_companies
            }
            for group in groups.order_by('name')[:20]
        ]
        
        return JsonResponse({'groups': groups_data})


class CompanyAPIView(View):
    def get(self, request):
        """Return companies as JSON for AJAX calls"""
        search = request.GET.get('search', '')
        group_id = request.GET.get('group_id', '')
        
        companies = Company.objects.select_related('group').filter(is_active=True)
        
        if search:
            companies = companies.filter(
                Q(name__icontains=search) |
                Q(group__name__icontains=search)
            )
        
        if group_id:
            companies = companies.filter(group_id=group_id)
        
        companies_data = [
            {
                'id': company.id,
                'name': company.name,
                'group_name': company.group.name,
                'company_type': company.get_company_type_display(),
                'city': company.city,
                'country': company.country
            }
            for company in companies.order_by('name')[:20]
        ]
        
        return JsonResponse({'companies': companies_data})


@login_required
def current_company_view(request):
    """
    View to display and edit current tenant's company information
    """
    # Get the current tenant (company)
    current_company = get_tenant(request)

    # If the current tenant is not a Company instance, handle gracefully
    if not isinstance(current_company, Company):
        # Fallback for development or when not in tenant context
        current_company = Company.objects.first()

    if not current_company:
        messages.error(request, 'No company information found.')
        context = {
            'company': None,
            'page_title': 'Company Profile',
        }
        return render(request, 'company/current_company.html', context)

    if request.method == 'POST':
        # Handle form submission for editing
        try:
            # Update company fields
            current_company.name = request.POST.get('name', current_company.name)
            current_company.description = request.POST.get('description', current_company.description)
            current_company.company_address = request.POST.get('company_address', current_company.company_address)
            current_company.registration_number = request.POST.get('registration_number', current_company.registration_number)
            current_company.tax_id = request.POST.get('tax_id', current_company.tax_id)
            current_company.email = request.POST.get('email', current_company.email)
            current_company.phone_number = request.POST.get('phone_number', current_company.phone_number)
            current_company.website = request.POST.get('website', current_company.website)
            current_company.address = request.POST.get('address', current_company.address)
            current_company.city = request.POST.get('city', current_company.city)
            current_company.state_province = request.POST.get('state_province', current_company.state_province)
            current_company.postal_code = request.POST.get('postal_code', current_company.postal_code)
            current_company.country = request.POST.get('country', current_company.country)

            # Handle logo upload/removal
            if request.POST.get('remove_logo') == 'true':
                current_company.logo = None
            elif 'logo' in request.FILES:
                current_company.logo = request.FILES['logo']

            # Handle established_date
            established_date = request.POST.get('established_date')
            if established_date:
                from datetime import datetime
                try:
                    current_company.established_date = datetime.strptime(established_date, '%Y-%m-%d').date()
                except ValueError:
                    pass  # Keep existing date if invalid format

            current_company.save()
            messages.success(request, 'Company profile updated successfully.')

        except Exception as e:
            messages.error(request, f'Error updating company profile: {str(e)}')

    # Get branches for this company
    branches = Branch.objects.annotate(
        employee_count=Count('employees')
    ).order_by('name')

    context = {
        'company': current_company,
        'branches': branches,
        'page_title': f'{current_company.name} - Company Profile' if current_company else 'Company Profile',
    }

    return render(request, 'company/current_company.html', context)


# Branch Views
class BranchListView(ListView):
    model = Branch
    template_name = 'company/branch_list.html'
    context_object_name = 'branches'
    paginate_by = 20

    def get_queryset(self):
        queryset = Branch.objects.annotate(
            employee_count=Count('employees')
        ).order_by('name')

        # Filter by search query
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(manager_name__icontains=search_query)
            )

        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class BranchDetailView(DetailView):
    model = Branch
    template_name = 'company/branch_detail.html'
    context_object_name = 'branch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get employees in this branch with pagination
        employees_list = self.object.employees.select_related('department', 'position').order_by('employee_id')
        paginator = Paginator(employees_list, 20)
        page = self.request.GET.get('page')
        employees = paginator.get_page(page)
        context['employees'] = employees
        return context


class BranchCreateView(CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'company/branch_form.html'
    success_url = reverse_lazy('company:branch_list')

    def form_valid(self, form):
        messages.success(self.request, f'Branch "{form.instance.name}" was created successfully.')
        return super().form_valid(form)


class BranchUpdateView(UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'company/branch_form.html'
    success_url = reverse_lazy('company:branch_list')

    def form_valid(self, form):
        messages.success(self.request, f'Branch "{form.instance.name}" was updated successfully.')
        return super().form_valid(form)


class BranchDeleteView(DeleteView):
    model = Branch
    template_name = 'company/branch_confirm_delete.html'
    success_url = reverse_lazy('company:branch_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'Branch "{obj.name}" was deleted successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
def branch_create_inline(request):
    """Inline branch creation for AJAX requests"""
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save()
            return JsonResponse({
                'success': True,
                'branch': {
                    'id': branch.id,
                    'name': branch.name,
                    'code': branch.code,
                    'city': branch.city,
                    'manager_name': branch.manager_name,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
