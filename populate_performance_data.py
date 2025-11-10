"""
Populate performance reviews and goals for an employee
Multi-tenant aware script for NextHR system
"""

import os
import django
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from django.contrib.auth.models import User
from django.utils import timezone
from django_tenants.utils import schema_context, get_tenant_model
from hr.models import Employee
from performance.models import PerformanceReview, Goal

def populate_performance_data():
    """Populate performance reviews and goals for User Three"""

    TenantModel = get_tenant_model()

    # List available tenants
    tenants = TenantModel.objects.exclude(schema_name='public').all()

    print("\n" + "="*60)
    print("Available Tenants:")
    print("="*60)
    for idx, tenant in enumerate(tenants, 1):
        print(f"{idx}. {tenant.schema_name} - {tenant.name}")

    # Get tenant selection
    print("\n" + "="*60)
    tenant_choice = input("Select tenant number (or press Enter for 'kk_company'): ").strip()

    if tenant_choice:
        try:
            selected_tenant = list(tenants)[int(tenant_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Exiting.")
            return
    else:
        selected_tenant = TenantModel.objects.get(schema_name='kk_company')

    print(f"\n✓ Selected tenant: {selected_tenant.schema_name}")
    print("="*60)

    # Work within the tenant schema
    with schema_context(selected_tenant.schema_name):
        # Find User Three (u3@ngt.com.kh)
        try:
            user = User.objects.get(username='u3')
            print(f"✓ Found user: {user.username} - {user.get_full_name()} ({user.email})")
        except User.DoesNotExist:
            print("✗ User 'u3' not found. Available users:")
            users = User.objects.all()[:10]
            for u in users:
                print(f"  - {u.username} ({u.get_full_name()})")
            return

        # Get employee profile
        try:
            employee = user.employee
            print(f"✓ Found employee: {employee.employee_id} - {employee.full_name}")
        except Employee.DoesNotExist:
            print("✗ Employee profile not found for this user")
            return

        # Find a reviewer (use admin or first staff user)
        reviewer = User.objects.filter(is_staff=True).first()
        if not reviewer:
            reviewer = User.objects.first()
        print(f"✓ Reviewer: {reviewer.username}")

        print("\n" + "="*60)
        print("Creating Performance Reviews...")
        print("="*60)

        # Delete existing data
        PerformanceReview.objects.filter(employee=employee).delete()
        Goal.objects.filter(employee=employee).delete()
        print("✓ Cleared existing performance data")

        # Create Performance Reviews
        today = timezone.now().date()

        reviews_data = [
            {
                'review_period': 'annual',
                'review_date': today - timedelta(days=30),
                'period_start': today - timedelta(days=395),
                'period_end': today - timedelta(days=30),
                'overall_rating': 4,
                'strengths': 'Excellent communication skills, consistently meets deadlines, proactive problem solver, good team player.',
                'areas_for_improvement': 'Could improve technical documentation, needs to work on delegation skills.',
                'goals_achieved': 'Successfully completed all Q4 2024 objectives, delivered 3 major projects on time.',
                'comments': 'Strong performer with great potential for leadership roles.',
                'status': 'completed',
            },
            {
                'review_period': 'semi_annual',
                'review_date': today - timedelta(days=180),
                'period_start': today - timedelta(days=365),
                'period_end': today - timedelta(days=180),
                'overall_rating': 5,
                'strengths': 'Outstanding technical skills, mentored 2 junior developers, implemented efficiency improvements.',
                'areas_for_improvement': 'Continue developing leadership and public speaking skills.',
                'goals_achieved': 'Exceeded all H1 targets, reduced deployment time by 40%, improved code quality metrics.',
                'comments': 'Exceptional performance. Recommended for senior role.',
                'status': 'completed',
            },
            {
                'review_period': 'quarterly',
                'review_date': today - timedelta(days=90),
                'period_start': today - timedelta(days=180),
                'period_end': today - timedelta(days=90),
                'overall_rating': 4,
                'strengths': 'Adaptable to change, strong analytical thinking, collaborative approach.',
                'areas_for_improvement': 'Time management during peak periods, stakeholder communication.',
                'goals_achieved': 'Completed Q3 deliverables, participated in 2 cross-functional projects.',
                'comments': 'Solid quarter with consistent results.',
                'status': 'completed',
            },
            {
                'review_period': 'quarterly',
                'review_date': today - timedelta(days=15),
                'period_start': today - timedelta(days=90),
                'period_end': today,
                'overall_rating': None,
                'strengths': '',
                'areas_for_improvement': '',
                'goals_achieved': '',
                'comments': 'Review in progress.',
                'status': 'in_progress',
            },
        ]

        created_reviews = []
        for review_data in reviews_data:
            review = PerformanceReview.objects.create(
                employee=employee,
                reviewer=reviewer,
                **review_data
            )
            created_reviews.append(review)
            status_icon = "✓" if review.status == 'completed' else "⋯"
            rating_display = f"{review.overall_rating}/5" if review.overall_rating else "Not rated"
            print(f"{status_icon} {review.get_review_period_display()} - {review.review_date} - Rating: {rating_display}")

        print(f"\n✓ Created {len(created_reviews)} performance reviews")

        print("\n" + "="*60)
        print("Creating Goals...")
        print("="*60)

        goals_data = [
            {
                'title': 'Complete Advanced Technical Training',
                'description': 'Finish AWS Solutions Architect certification and complete 3 advanced Django courses.',
                'priority': 'high',
                'status': 'completed',
                'start_date': today - timedelta(days=120),
                'target_date': today - timedelta(days=30),
                'completion_date': today - timedelta(days=25),
                'progress': 100,
            },
            {
                'title': 'Improve Code Quality Metrics',
                'description': 'Reduce bug count by 30% and increase test coverage to 85% across all modules.',
                'priority': 'high',
                'status': 'in_progress',
                'start_date': today - timedelta(days=90),
                'target_date': today + timedelta(days=30),
                'completion_date': None,
                'progress': 75,
            },
            {
                'title': 'Mentor Junior Developers',
                'description': 'Provide weekly mentoring sessions to 2 junior developers, help them achieve their learning objectives.',
                'priority': 'medium',
                'status': 'in_progress',
                'start_date': today - timedelta(days=60),
                'target_date': today + timedelta(days=60),
                'completion_date': None,
                'progress': 60,
            },
            {
                'title': 'Lead Performance Optimization Project',
                'description': 'Lead initiative to improve system response time by 40% and reduce database query times.',
                'priority': 'high',
                'status': 'in_progress',
                'start_date': today - timedelta(days=45),
                'target_date': today + timedelta(days=45),
                'completion_date': None,
                'progress': 50,
            },
            {
                'title': 'Develop API Documentation',
                'description': 'Create comprehensive API documentation for all endpoints with examples and best practices.',
                'priority': 'medium',
                'status': 'in_progress',
                'start_date': today - timedelta(days=30),
                'target_date': today + timedelta(days=60),
                'completion_date': None,
                'progress': 40,
            },
            {
                'title': 'Implement Automated Testing Pipeline',
                'description': 'Set up CI/CD pipeline with automated testing, code quality checks, and deployment automation.',
                'priority': 'high',
                'status': 'not_started',
                'start_date': today,
                'target_date': today + timedelta(days=90),
                'completion_date': None,
                'progress': 0,
            },
            {
                'title': 'Attend Leadership Workshop',
                'description': 'Participate in leadership development program to prepare for senior role responsibilities.',
                'priority': 'medium',
                'status': 'not_started',
                'start_date': today + timedelta(days=15),
                'target_date': today + timedelta(days=75),
                'completion_date': None,
                'progress': 0,
            },
            {
                'title': 'Reduce Technical Debt',
                'description': 'Refactor legacy modules, update deprecated dependencies, improve code maintainability.',
                'priority': 'medium',
                'status': 'in_progress',
                'start_date': today - timedelta(days=20),
                'target_date': today + timedelta(days=70),
                'completion_date': None,
                'progress': 30,
            },
        ]

        created_goals = []
        for goal_data in goals_data:
            goal = Goal.objects.create(
                employee=employee,
                created_by=reviewer,
                **goal_data
            )
            created_goals.append(goal)
            status_icons = {
                'completed': '✓',
                'in_progress': '⋯',
                'not_started': '○',
            }
            icon = status_icons.get(goal.status, '?')
            print(f"{icon} {goal.title} - {goal.get_priority_display()} priority - {goal.progress}% complete")

        print(f"\n✓ Created {len(created_goals)} goals")

        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Employee: {employee.full_name} ({employee.employee_id})")
        print(f"Total Reviews: {len(created_reviews)}")
        print(f"  - Completed: {sum(1 for r in created_reviews if r.status == 'completed')}")
        print(f"  - In Progress: {sum(1 for r in created_reviews if r.status == 'in_progress')}")

        completed_ratings = [r.overall_rating for r in created_reviews if r.overall_rating]
        if completed_ratings:
            avg_rating = sum(completed_ratings) / len(completed_ratings)
            print(f"  - Average Rating: {avg_rating:.1f}/5")

        print(f"\nTotal Goals: {len(created_goals)}")
        print(f"  - Completed: {sum(1 for g in created_goals if g.status == 'completed')}")
        print(f"  - In Progress: {sum(1 for g in created_goals if g.status == 'in_progress')}")
        print(f"  - Not Started: {sum(1 for g in created_goals if g.status == 'not_started')}")

        print("\n" + "="*60)
        print("✓ Performance data population completed successfully!")
        print("="*60)
        print(f"\nView at: http://kk.lyp:8000/employee/performance/")
        print("="*60)

if __name__ == '__main__':
    try:
        populate_performance_data()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
