# API ViewSets for HR module
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Employee, Department, Position, EmployeeDocument, EmployeeHistory


class EmployeePagination(PageNumberPagination):
    """Custom pagination class for Employee API"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


from .serializers import (
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateUpdateSerializer,
    EmployeeDocumentSerializer,
    EmployeeHistorySerializer,
    EmployeeMinimalSerializer,
    DepartmentSerializer,
    PositionSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List all employees",
        description="Get a list of all employees with filtering and search capabilities",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search employees by name, email, or employee ID',
                required=False
            ),
            OpenApiParameter(
                name='department',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by department ID',
                required=False
            ),
            OpenApiParameter(
                name='position',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by position ID',
                required=False
            ),
            OpenApiParameter(
                name='employment_status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by employment status (active, on_leave, suspended, terminated)',
                required=False
            ),
            OpenApiParameter(
                name='manager',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by manager ID',
                required=False
            ),
        ],
        tags=['Employees']
    ),
    create=extend_schema(
        summary="Create a new employee",
        description="Create a new employee record",
        tags=['Employees']
    ),
    retrieve=extend_schema(
        summary="Get employee details",
        description="Get detailed information about a specific employee",
        tags=['Employees']
    ),
    update=extend_schema(
        summary="Update an employee",
        description="Update all fields of an employee record",
        tags=['Employees']
    ),
    partial_update=extend_schema(
        summary="Partially update an employee",
        description="Update specific fields of an employee record",
        tags=['Employees']
    ),
    destroy=extend_schema(
        summary="Delete an employee",
        description="Soft delete an employee by setting their status to terminated",
        tags=['Employees']
    ),
)
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee CRUD operations
    """
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = EmployeePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'employment_status', 'manager', 'nationality', 'gender']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id', 'phone_number']
    ordering_fields = ['employee_id', 'first_name', 'last_name', 'hire_date', 'created_at']
    ordering = ['employee_id']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        elif self.action == 'minimal':
            return EmployeeMinimalSerializer
        return EmployeeDetailSerializer

    def get_queryset(self):
        """Apply additional filters based on query parameters"""
        queryset = super().get_queryset()

        # Add custom search logic
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )

        # Filter by multiple departments
        departments = self.request.query_params.getlist('departments[]')
        if departments:
            queryset = queryset.filter(department__in=departments)

        # Filter by work location
        work_location = self.request.query_params.get('work_location', None)
        if work_location:
            queryset = queryset.filter(work_location__icontains=work_location)

        return queryset

    def destroy(self, request, *args, **kwargs):
        """Soft delete - change status to terminated instead of deleting"""
        instance = self.get_object()
        instance.employment_status = 'terminated'
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Get minimal employee data",
        description="Get minimal employee data for dropdowns and references",
        tags=['Employees']
    )
    @action(detail=False, methods=['get'])
    def minimal(self, request):
        """Get minimal employee data for dropdowns"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = EmployeeMinimalSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get active employees",
        description="Get all active employees",
        tags=['Employees']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active employees"""
        queryset = self.get_queryset().filter(employment_status='active')
        serializer = EmployeeListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get employee documents",
        description="Get all documents for a specific employee",
        tags=['Employees']
    )
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for an employee"""
        employee = self.get_object()
        documents = employee.documents.all()
        serializer = EmployeeDocumentSerializer(documents, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get employee history",
        description="Get history events for a specific employee",
        tags=['Employees']
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get history for an employee"""
        employee = self.get_object()
        history = employee.history.all()
        serializer = EmployeeHistorySerializer(history, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get employee subordinates",
        description="Get all employees managed by this employee",
        tags=['Employees']
    )
    @action(detail=True, methods=['get'])
    def subordinates(self, request, pk=None):
        """Get all subordinates of an employee"""
        employee = self.get_object()
        subordinates = employee.subordinates.filter(employment_status='active')
        serializer = EmployeeListSerializer(subordinates, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Search employees",
        description="Search employees with advanced filters",
        tags=['Employees']
    )
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search for employees"""
        data = request.data
        queryset = self.get_queryset()

        # Apply filters from request body
        if 'first_name' in data:
            queryset = queryset.filter(first_name__icontains=data['first_name'])
        if 'last_name' in data:
            queryset = queryset.filter(last_name__icontains=data['last_name'])
        if 'department' in data:
            queryset = queryset.filter(department=data['department'])
        if 'position' in data:
            queryset = queryset.filter(position=data['position'])
        if 'employment_status' in data:
            queryset = queryset.filter(employment_status=data['employment_status'])
        if 'hire_date_from' in data:
            queryset = queryset.filter(hire_date__gte=data['hire_date_from'])
        if 'hire_date_to' in data:
            queryset = queryset.filter(hire_date__lte=data['hire_date_to'])
        if 'manager' in data:
            queryset = queryset.filter(manager=data['manager'])

        serializer = EmployeeListSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List all departments",
        description="Get a list of all departments",
        tags=['Departments']
    ),
    create=extend_schema(
        summary="Create a new department",
        description="Create a new department",
        tags=['Departments']
    ),
    retrieve=extend_schema(
        summary="Get department details",
        description="Get details of a specific department",
        tags=['Departments']
    ),
    update=extend_schema(
        summary="Update a department",
        description="Update all fields of a department",
        tags=['Departments']
    ),
    partial_update=extend_schema(
        summary="Partially update a department",
        description="Update specific fields of a department",
        tags=['Departments']
    ),
    destroy=extend_schema(
        summary="Delete a department",
        description="Delete a department",
        tags=['Departments']
    ),
)
class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department CRUD operations
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(
        summary="List all positions",
        description="Get a list of all positions",
        tags=['Positions']
    ),
    create=extend_schema(
        summary="Create a new position",
        description="Create a new position",
        tags=['Positions']
    ),
    retrieve=extend_schema(
        summary="Get position details",
        description="Get details of a specific position",
        tags=['Positions']
    ),
    update=extend_schema(
        summary="Update a position",
        description="Update all fields of a position",
        tags=['Positions']
    ),
    partial_update=extend_schema(
        summary="Partially update a position",
        description="Update specific fields of a position",
        tags=['Positions']
    ),
    destroy=extend_schema(
        summary="Delete a position",
        description="Delete a position",
        tags=['Positions']
    ),
)
class PositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Position CRUD operations
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'level']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'level', 'created_at']
    ordering = ['department', 'level']

    def get_queryset(self):
        """Apply additional filters"""
        queryset = super().get_queryset()

        # Filter by department if provided
        department_id = self.request.query_params.get('department', None)
        if department_id:
            queryset = queryset.filter(department=department_id)

        return queryset


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee Document CRUD operations
    """
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'document_type']
    ordering_fields = ['issue_date', 'expiry_date', 'created_at']
    ordering = ['-issue_date']

    def get_queryset(self):
        """Filter documents by employee if employee_id is provided"""
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee_id', None)
        if employee_id:
            queryset = queryset.filter(employee=employee_id)
        return queryset