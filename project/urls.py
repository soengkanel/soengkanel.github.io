from django.urls import path
from . import views

app_name = 'project'

urlpatterns = [
    # Main views
    path('', views.project_list, name='project_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.project_create, name='project_create'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('<int:project_id>/settings/save/', views.project_settings_save, name='project_settings_save'),

    # Task management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/my/', views.my_tasks, name='my_tasks'),
    path('tasks/create/', views.task_create_full, name='task_create_full'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/assign/', views.task_assign, name='task_assign'),
    path('tasks/bulk-assign/', views.task_bulk_assign, name='task_bulk_assign'),
    path('tasks/<int:task_id>/progress/', views.task_update_progress, name='task_update_progress'),
    path('<int:project_id>/tasks/create/', views.task_create, name='task_create'),
    path('<int:project_id>/tasks/create-full/', views.task_create_full, name='task_create_full_with_project'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/status/', views.task_update_status, name='task_update_status'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('<int:project_id>/tasks/create-inline/', views.task_create_inline, name='task_create_inline'),
    path('tasks/<int:task_id>/update-inline/', views.task_update_inline, name='task_update_inline'),

    # Project team management (existing)
    path('<int:project_id>/team/add/', views.project_team_member_add, name='project_team_member_add'),
    path('team/<int:member_id>/edit/', views.project_team_member_edit, name='project_team_member_edit'),
    path('team/<int:member_id>/remove/', views.project_team_member_remove, name='project_team_member_remove'),

    # Project team inline editing
    path('<int:project_id>/team/add-inline/', views.team_member_add_inline, name='team_member_add_inline'),
    path('team-members/<int:member_id>/update-inline/', views.team_member_update_inline, name='team_member_update_inline'),

    # Team management (new)
    path('teams/', views.team_list, name='team_list'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/<int:team_id>/edit/', views.team_edit, name='team_edit'),
    path('teams/<int:team_id>/delete/', views.team_delete, name='team_delete'),
    path('teams/<int:team_id>/projects/', views.team_projects, name='team_projects'),
    path('teams/<int:team_id>/members/add/', views.team_member_add, name='team_member_add'),
    path('team-members/<int:member_id>/edit/', views.team_member_edit, name='team_member_edit'),
    path('team-members/<int:member_id>/remove/', views.team_member_remove, name='team_member_remove'),

    # Timesheet management
    path('timesheets/', views.timesheet_list, name='timesheet_list'),
    path('timesheets/quick-entry/', views.my_timesheet, name='timesheet_quick_entry'),
    path('timesheets/create/', views.timesheet_create, name='timesheet_create'),
    path('timesheets/<int:timesheet_id>/', views.timesheet_detail, name='timesheet_detail'),
    path('timesheets/<int:timesheet_id>/edit/', views.timesheet_edit, name='timesheet_edit'),
    path('timesheets/<int:timesheet_id>/submit/', views.timesheet_submit, name='timesheet_submit'),
    path('timesheets/<int:timesheet_id>/approve/', views.timesheet_approve, name='timesheet_approve'),
    path('timesheets/<int:timesheet_id>/entries/create/', views.timesheet_entry_create, name='timesheet_entry_create'),
    path('timesheet-entries/<int:entry_id>/edit/', views.timesheet_entry_edit, name='timesheet_entry_edit'),
    path('timesheet-entries/<int:entry_id>/delete/', views.timesheet_entry_delete, name='timesheet_entry_delete'),

    # Milestone management
    path('milestones/', views.milestone_list, name='milestone_list'),
    path('milestones/create/', views.milestone_create, name='milestone_create'),
    path('milestones/<int:milestone_id>/', views.milestone_detail, name='milestone_detail'),
    path('milestones/<int:milestone_id>/edit/', views.milestone_edit, name='milestone_edit'),
    path('milestones/<int:milestone_id>/status/', views.milestone_update_status, name='milestone_update_status'),
    path('milestones/<int:milestone_id>/approve/', views.milestone_approve, name='milestone_approve'),
    path('milestones/<int:milestone_id>/delete/', views.milestone_delete, name='milestone_delete'),
    path('<int:project_id>/milestones/create/', views.milestone_create, name='milestone_create_for_project'),
    path('<int:project_id>/milestones/create-inline/', views.milestone_create_inline, name='milestone_create_inline'),
    path('milestones/<int:milestone_id>/update-inline/', views.milestone_update_inline, name='milestone_update_inline'),

    # Document management
    path('<int:project_id>/documents/create/', views.document_create, name='document_create'),

    # Expense management
    path('<int:project_id>/expenses/create/', views.expense_create, name='expense_create'),
]