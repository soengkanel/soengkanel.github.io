from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import connection
from .models import Company, Group
from .serializers import CompanySerializer, CompanyUpdateSerializer, GroupSerializer
from .permissions import CanUpdateOwnCompany, CanManageGroups


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update_current', 'upload_logo', 'delete_logo']:
            permission_classes = [CanUpdateOwnCompany]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer(self, *args, **kwargs):
        """Helper method to get the serializer like ModelViewSet"""
        return CompanySerializer(*args, **kwargs)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the current tenant's company information
        """
        try:
            # Get the current tenant schema name
            current_schema = connection.schema_name

            # Get the actual Company instance based on the schema name
            current_company = Company.objects.get(schema_name=current_schema)

            serializer = self.get_serializer(current_company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found for current tenant"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Could not retrieve company information: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['put', 'patch'])
    def update_current(self, request):
        """
        Update the current tenant's company information
        """
        try:
            # Get the current tenant schema name
            current_schema = connection.schema_name

            # Get the actual Company instance based on the schema name
            current_company = Company.objects.get(schema_name=current_schema)

            serializer = CompanyUpdateSerializer(
                current_company,
                data=request.data,
                partial=request.method == 'PATCH'
            )

            if serializer.is_valid():
                serializer.save()
                # Return full company data after update
                full_serializer = CompanySerializer(current_company)
                return Response(full_serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found for current tenant"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Could not update company information: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def upload_logo(self, request):
        """
        Upload a logo for the current tenant's company
        """
        try:
            # Get the current tenant schema name
            current_schema = connection.schema_name

            # Get the actual Company instance based on the schema name
            current_company = Company.objects.get(schema_name=current_schema)

            if 'logo' not in request.FILES:
                return Response(
                    {"error": "No logo file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            current_company.logo = request.FILES['logo']
            current_company.save()

            serializer = CompanySerializer(current_company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found for current tenant"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Could not upload logo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['delete'])
    def delete_logo(self, request):
        """
        Delete the logo for the current tenant's company
        """
        try:
            # Get the current tenant schema name
            current_schema = connection.schema_name

            # Get the actual Company instance based on the schema name
            current_company = Company.objects.get(schema_name=current_schema)

            if current_company.logo:
                current_company.logo.delete()
                current_company.logo = None
                current_company.save()

            serializer = CompanySerializer(current_company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found for current tenant"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Could not delete logo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GroupViewSet(viewsets.ModelViewSet):
    """
    Full CRUD ViewSet for Groups with cascade delete support

    Supports:
        pass
    - List all active groups
    - Retrieve group details
    - Create new groups
    - Update existing groups
    - Delete groups (with cascade deletion of companies)
    """
    queryset = Group.objects.filter(is_active=True)
    serializer_class = GroupSerializer
    permission_classes = [CanManageGroups]

    def get_queryset(self):
        """Override to allow access to inactive groups for superusers"""
        if self.request.user.is_superuser:
            return Group.objects.all()
        return Group.objects.filter(is_active=True)

    @action(detail=True, methods=['get'])
    def cascade_info(self, request, pk=None):
        """
        Get information about what will be deleted if this group is deleted
        """
        try:
            group = self.get_object()
            cascade_info = group.get_cascade_deletion_info()

            return Response({
                'cascade_deletion_info': cascade_info,
                'warning': f"Deleting this group will permanently delete {cascade_info['companies_count']} companies and all their data including tenant schemas."
            })
        except Group.DoesNotExist:
            return Response(
                {"error": "Group not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Could not retrieve cascade information: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a group with cascade deletion of all related companies

        This is a destructive operation that will:
            pass
        1. Delete all companies in the group
        2. Drop all tenant schemas for those companies
        3. Delete all tenant-specific data

        Requires superuser permissions for safety.
        """
        try:
            # Only allow superusers to delete groups due to destructive nature
            if not request.user.is_superuser:
                return Response(
                    {"error": "Only superusers can delete groups due to the destructive nature of cascade deletion"},
                    status=status.HTTP_403_FORBIDDEN
                )

            group = self.get_object()

            # Get cascade info before deletion
            cascade_info = group.get_cascade_deletion_info()

            # Confirm deletion intent with query parameter
            confirm_deletion = request.query_params.get('confirm_deletion', '').lower() == 'true'
            if not confirm_deletion:
                return Response({
                    'error': 'Deletion not confirmed',
                    'cascade_deletion_info': cascade_info,
                    'confirmation_required': True,
                    'message': 'To confirm deletion, add ?confirm_deletion=true to the request URL',
                    'warning': f"This will permanently delete {cascade_info['companies_count']} companies and all their data."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Perform the deletion
            group_name = group.name
            group.delete()

            return Response({
                'success': True,
                'message': f"Group '{group_name}' and all related companies have been successfully deleted",
                'deleted_info': cascade_info
            }, status=status.HTTP_204_NO_CONTENT)

        except Group.DoesNotExist:
            return Response(
                {"error": "Group not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to delete group: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )