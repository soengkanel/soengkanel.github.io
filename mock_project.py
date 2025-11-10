#!/usr/bin/env python
"""
Mock Project Data Generator for NextHR
Run this script with: python mock_project.py

This script creates 10 diverse mock projects for the NextHR Django application,
handling the multi-tenant architecture properly using schema_context for the kk_company tenant.
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction, connection
from django.utils import timezone

def create_mock_projects():
    """Create 10 mock projects with realistic data for kk_company tenant"""

    # Reset any bad database state
    try:
        connection.close()
    except:
        pass

    print("="*60)
    print(" NextHR - Mock Project Data Generator")
    print("="*60)
    print()
    print("Initializing project creation for KK Company tenant...")

    # Set schema to kk_company tenant (following NextHR multi-tenant architecture)
    try:
        from django_tenants.utils import schema_context
        from company.models import Company

        # Get the KK Company tenant
        kk_tenant = Company.objects.get(schema_name='kk_company')
        print(f"[INFO] Found KK Company tenant: {kk_tenant}")

        with schema_context(kk_tenant.schema_name):
            print(f"[INFO] Switched to tenant schema: {kk_tenant.schema_name}")
            _create_projects_data()

    except ImportError:
        print("[WARNING] django_tenants not available, trying direct schema connection...")
        # If django_tenants is not available, try direct creation
        try:
            connection.set_schema('kk_company')
            _create_projects_data()
        except:
            # Fall back to default schema
            print("[WARNING] Could not set tenant schema, using default schema")
            _create_projects_data()
    except Exception as e:
        print(f"[ERROR] Tenant setup failed: {e}")
        print("[WARNING] Falling back to default schema")
        _create_projects_data()

def _create_projects_data():
    """Internal function to create project data"""

    projects_data = [
        {
            'project_name': 'E-Commerce Platform Development',
            'description': 'Development of a comprehensive e-commerce platform with modern web technologies, payment integration, mobile responsiveness, inventory management, and advanced analytics. Features include multi-vendor support, real-time chat, and AI-powered recommendations.',
            'status': 'in_progress',
            'priority': 'high',
            'billing_method': 'time_and_material',
            'estimated_cost': 75000.00,
            'estimated_hours': 1200.00,
            'percent_complete': 65.00,
            'days_offset_start': -90,  # Started 90 days ago
            'days_duration': 180,      # 6 months project
            'project_type': 'Software Development',
        },
        {
            'project_name': 'Mobile Banking Application',
            'description': 'Secure mobile banking application with biometric authentication, real-time transactions, comprehensive financial management features, investment tracking, and budgeting tools. Includes fraud detection and regulatory compliance.',
            'status': 'in_progress',
            'priority': 'urgent',
            'billing_method': 'fixed_cost',
            'estimated_cost': 120000.00,
            'estimated_hours': 2000.00,
            'percent_complete': 45.00,
            'days_offset_start': -60,
            'days_duration': 240,
            'project_type': 'Software Development',
        },
        {
            'project_name': 'HR Management System Upgrade',
            'description': 'Complete overhaul of the existing HR management system with new features for payroll processing, attendance tracking, performance management, employee self-service portal, and advanced reporting capabilities.',
            'status': 'completed',
            'priority': 'medium',
            'billing_method': 'milestone_based',
            'estimated_cost': 45000.00,
            'estimated_hours': 800.00,
            'percent_complete': 100.00,
            'days_offset_start': -180,
            'days_duration': 120,
            'project_type': 'System Integration',
        },
        {
            'project_name': 'Cloud Infrastructure Migration',
            'description': 'Migration of legacy systems to cloud infrastructure with improved scalability, security, disaster recovery capabilities, automated deployment pipelines, and comprehensive monitoring solutions.',
            'status': 'in_progress',
            'priority': 'high',
            'billing_method': 'time_and_material',
            'estimated_cost': 95000.00,
            'estimated_hours': 1500.00,
            'percent_complete': 30.00,
            'days_offset_start': -30,
            'days_duration': 200,
            'project_type': 'Infrastructure',
        },
        {
            'project_name': 'Customer Portal Development',
            'description': 'Development of a customer-facing portal for account management, service requests, support ticket tracking, knowledge base access, and real-time communication with support staff.',
            'status': 'open',
            'priority': 'medium',
            'billing_method': 'fixed_cost',
            'estimated_cost': 35000.00,
            'estimated_hours': 600.00,
            'percent_complete': 0.00,
            'days_offset_start': 15,  # Starting in 15 days
            'days_duration': 90,
            'project_type': 'Software Development',
        },
        {
            'project_name': 'Data Analytics Dashboard',
            'description': 'Business intelligence dashboard with real-time data visualization, KPI tracking, automated reporting capabilities, predictive analytics, and interactive data exploration tools.',
            'status': 'in_progress',
            'priority': 'medium',
            'billing_method': 'time_and_material',
            'estimated_cost': 55000.00,
            'estimated_hours': 900.00,
            'percent_complete': 75.00,
            'days_offset_start': -120,
            'days_duration': 150,
            'project_type': 'Analytics',
        },
        {
            'project_name': 'Mobile App Security Audit',
            'description': 'Comprehensive security audit of mobile applications including vulnerability assessment, penetration testing, code review, compliance verification, and security recommendations.',
            'status': 'on_hold',
            'priority': 'high',
            'billing_method': 'fixed_cost',
            'estimated_cost': 25000.00,
            'estimated_hours': 400.00,
            'percent_complete': 20.00,
            'days_offset_start': -45,
            'days_duration': 60,
            'project_type': 'Security',
        },
        {
            'project_name': 'Inventory Management System',
            'description': 'Development of an automated inventory management system with barcode scanning, RFID tracking, real-time inventory monitoring, supplier integration, and demand forecasting capabilities.',
            'status': 'in_progress',
            'priority': 'medium',
            'billing_method': 'milestone_based',
            'estimated_cost': 68000.00,
            'estimated_hours': 1100.00,
            'percent_complete': 55.00,
            'days_offset_start': -75,
            'days_duration': 160,
            'project_type': 'System Integration',
        },
        {
            'project_name': 'Website Redesign Project',
            'description': 'Complete redesign of corporate website with modern UI/UX, improved performance, enhanced SEO optimization, mobile responsiveness, and accessibility compliance.',
            'status': 'completed',
            'priority': 'low',
            'billing_method': 'fixed_cost',
            'estimated_cost': 18000.00,
            'estimated_hours': 300.00,
            'percent_complete': 100.00,
            'days_offset_start': -200,
            'days_duration': 45,
            'project_type': 'Software Development',
        },
        {
            'project_name': 'API Integration Platform',
            'description': 'Development of a centralized API integration platform for connecting various third-party services and internal systems with rate limiting, authentication, monitoring, and documentation.',
            'status': 'open',
            'priority': 'high',
            'billing_method': 'time_and_material',
            'estimated_cost': 85000.00,
            'estimated_hours': 1400.00,
            'percent_complete': 0.00,
            'days_offset_start': 30,
            'days_duration': 180,
            'project_type': 'System Integration',
        }
    ]

    print()
    print("Creating mock projects...")
    print("-" * 40)

    created_count = 0
    updated_count = 0
    failed_count = 0

    # Process each project
    for proj_data in projects_data:
        try:
            # Try to create project if the model is available
            try:
                from project.models import Project, ProjectType
                from company.models import Company
                from hr.models import Employee, Department

                # Calculate dates
                today = timezone.now().date()
                start_date = today + timedelta(days=proj_data['days_offset_start'])
                end_date = start_date + timedelta(days=proj_data['days_duration'])

                # Set actual dates for completed projects
                actual_start_date = start_date if proj_data['status'] in ['in_progress', 'completed', 'on_hold'] else None
                actual_end_date = end_date if proj_data['status'] == 'completed' else None

                # Get or create company (kk_company tenant)
                company = None
                try:
                    company = Company.objects.filter(schema_name='kk_company').first()
                    if not company:
                        # Try to find any company in the current schema
                        company = Company.objects.first()
                except:
                    pass

                # Get a random department
                department = None
                try:
                    departments = Department.objects.all()
                    if departments.exists():
                        department = random.choice(departments)
                except:
                    pass

                # Get random employees for project manager and team lead
                project_manager = None
                team_lead = None
                try:
                    employees = Employee.objects.all()
                    if employees.exists():
                        project_manager = random.choice(employees)
                        team_lead = random.choice(employees)
                except:
                    pass

                # Get or create a project type based on project data
                project_type = None
                try:
                    type_name = proj_data.get('project_type', 'Software Development')
                    project_type, created = ProjectType.objects.get_or_create(
                        type_name=type_name,
                        defaults={
                            'description': f'{type_name} projects - automatically created for mock data',
                            'is_active': True
                        }
                    )
                    if created:
                        print(f"  |-- Created project type: {type_name}")
                except Exception as e:
                    print(f"  |-- Warning: Could not create project type: {e}")
                    pass

                # Generate some actual cost and hours for in-progress and completed projects
                actual_cost = None
                actual_hours = None
                if proj_data['status'] in ['in_progress', 'completed']:
                    cost_multiplier = proj_data['percent_complete'] / 100
                    actual_cost = Decimal(str(proj_data['estimated_cost'])) * Decimal(str(cost_multiplier))
                    actual_hours = Decimal(str(proj_data['estimated_hours'])) * Decimal(str(cost_multiplier))

                # Create project record
                project, project_created = Project.objects.update_or_create(
                    project_name=proj_data['project_name'],
                    defaults={
                        'description': proj_data['description'],
                        'project_type': project_type,
                        'company': company,
                        'department': department,
                        'project_manager': project_manager,
                        'team_lead': team_lead,
                        'expected_start_date': start_date,
                        'expected_end_date': end_date,
                        'actual_start_date': actual_start_date,
                        'actual_end_date': actual_end_date,
                        'status': proj_data['status'],
                        'priority': proj_data['priority'],
                        'percent_complete': Decimal(str(proj_data['percent_complete'])),
                        'estimated_cost': Decimal(str(proj_data['estimated_cost'])),
                        'actual_cost': actual_cost,
                        'total_sales_amount': Decimal(str(proj_data['estimated_cost'])) * Decimal('1.15'),  # 15% markup
                        'billing_method': proj_data['billing_method'],
                        'estimated_hours': Decimal(str(proj_data['estimated_hours'])),
                        'actual_hours': actual_hours,
                        'notes': f'Mock project data generated for {proj_data["project_name"]}',
                        'is_active': True,
                        'is_milestone_tracking': proj_data['billing_method'] == 'milestone_based',
                        'collect_progress': True,
                    }
                )

                if project_created:
                    created_count += 1
                    print(f"[+] Created project: {project.project_code:<15} - {proj_data['project_name']}")
                else:
                    updated_count += 1
                    print(f"[*] Updated project: {project.project_code:<15} - {proj_data['project_name']}")

                print(f"  |-- Status: {proj_data['status']:<12} Priority: {proj_data['priority']:<8} Progress: {proj_data['percent_complete']:.0f}%")

                # Create some project team members for new projects
                if project_created and employees.exists():
                    try:
                        from project.models import ProjectTeamMember

                        # Add 2-4 random team members to each project
                        team_size = random.randint(2, min(4, employees.count()))
                        selected_employees = random.sample(list(employees), team_size)

                        roles = ['Developer', 'QA Engineer', 'Business Analyst', 'Designer', 'DevOps Engineer']

                        for i, emp in enumerate(selected_employees):
                            if emp != project_manager and emp != team_lead:  # Don't duplicate PM and TL
                                role = random.choice(roles)
                                allocation = random.choice([75, 100, 50])  # Common allocation percentages

                                team_member, tm_created = ProjectTeamMember.objects.get_or_create(
                                    project=project,
                                    employee=emp,
                                    defaults={
                                        'role': role,
                                        'allocation_percentage': allocation,
                                        'hourly_rate': Decimal(str(random.randint(25, 85))),  # $25-85/hour
                                        'start_date': project.expected_start_date or timezone.now().date(),
                                        'is_active': True
                                    }
                                )

                                if tm_created:
                                    print(f"  |-- Added team member: {emp.full_name if hasattr(emp, 'full_name') else emp} ({role})")

                    except Exception as e:
                        print(f"  |-- Warning: Could not create team members: {e}")
                        pass

            except ImportError:
                # Project models not available, skip project creation
                failed_count += 1
                print(f"[-] Project models not available, skipping: {proj_data['project_name']}")
            except Exception as e:
                failed_count += 1
                print(f"[-] Failed to create project '{proj_data['project_name']}': {str(e)[:60]}...")

        except Exception as e:
            failed_count += 1
            print(f"[-] Failed to process project '{proj_data.get('project_name', 'unknown')}': {str(e)[:50]}")
            # Reset connection on error
            try:
                connection.close()
            except:
                pass

    print()
    print("="*60)
    print(f" Summary")
    print("="*60)
    print(f"  * Projects created: {created_count}")
    print(f"  * Projects updated: {updated_count}")
    print(f"  * Failed: {failed_count}")
    print(f"  * Total processed: {created_count + updated_count}")
    print()
    print(" Project Information:")
    print("-"*60)
    print("  * Project codes are auto-generated (PRJ-YYYY-NNNN)")
    print("  * Projects span various statuses: open, in_progress, completed, on_hold")
    print("  * Estimated costs range from $18K to $120K")
    print("  * Different billing methods: fixed_cost, time_and_material, milestone_based")
    print()
    print(" Project Status Distribution:")
    status_counts = {}
    for proj in projects_data:
        status = proj['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    for status, count in status_counts.items():
        print(f"  * {status.replace('_', ' ').title()}: {count} projects")
    print()
    print("="*60)
    print(" [SUCCESS] Mock project data generation completed successfully!")
    print("="*60)


if __name__ == '__main__':
    try:
        create_mock_projects()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}")
        print("Please make sure Django is properly configured and project models are available")
        import traceback
        print("\nFull error details:")
        traceback.print_exc()
        sys.exit(1)