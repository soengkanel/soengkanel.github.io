"""
Team-related API views for NextHR.

This module contains all ViewSets and views related to team management,
including teams and team members.
"""
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import connection

from project.models import Team, TeamMember
from ..serializers import TeamSerializer, TeamMemberSerializer
from ..mixins import TenantFilterMixin


class TeamViewSet(TenantFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing teams.

    Provides CRUD operations for teams with tenant filtering,
    search, ordering, and team member management.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team_type', 'status', 'department', 'is_project_based']
    search_fields = ['team_name', 'team_code', 'description']
    ordering_fields = ['team_name', 'created_at']
    ordering = ['team_name']

    def perform_create(self, serializer):
        super().perform_create(serializer)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get team members"""
        team = self.get_object()
        members = TeamMember.objects.filter(team=team, is_active=True)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to team"""
        team = self.get_object()

        if team.is_full:
            return Response({'error': f'Team is at maximum capacity ({team.max_members} members)'},
                          status=status.HTTP_400_BAD_REQUEST)

        serializer = TeamMemberSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(team=team, added_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamMemberViewSet(TenantFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing team members.

    Provides CRUD operations for team members with tenant filtering,
    search, and ordering capabilities.
    """
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team', 'employee', 'role', 'availability', 'is_active']
    search_fields = ['employee__full_name', 'role', 'custom_role']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        current_tenant = connection.tenant
        create_kwargs = {'added_by': self.request.user}

        if hasattr(serializer.Meta.model, 'company'):
            create_kwargs['company'] = current_tenant

        serializer.save(**create_kwargs)