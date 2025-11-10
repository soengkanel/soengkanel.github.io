from django.core.management.base import BaseCommand
from training.models import Course


class Command(BaseCommand):
    help = 'Populate business training courses (Sales, Analytics, Marketing)'

    def handle(self, *args, **kwargs):
        courses_data = [
            # ==================== SALES TOOLS ====================
            {
                'title': 'CRM Fundamentals: Salesforce for Beginners',
                'code': 'SALES-CRM-101',
                'description': '''Master the basics of Customer Relationship Management using Salesforce.
Learn how to manage leads, contacts, accounts, and opportunities. Track customer interactions,
create reports, and use dashboards to monitor sales performance. Perfect for sales representatives
and account managers looking to leverage CRM tools effectively.''',
                'category': 'professional',
                'level': 'beginner',
                'duration_hours': 8.0,
                'max_students': 30,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Advanced Sales Techniques and Negotiation',
                'code': 'SALES-ADV-201',
                'description': '''Elevate your sales skills with advanced techniques in consultative selling,
objection handling, and negotiation strategies. Learn the psychology of selling, closing techniques,
and how to build long-term customer relationships. Includes role-playing exercises and real-world scenarios.''',
                'category': 'professional',
                'level': 'advanced',
                'duration_hours': 12.0,
                'max_students': 25,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Sales Pipeline Management',
                'code': 'SALES-PIPE-102',
                'description': '''Learn to effectively manage your sales pipeline from prospecting to closing.
Understand stages of the sales cycle, qualify leads using BANT methodology, forecast revenue accurately,
and optimize conversion rates. Includes hands-on exercises with CRM tools.''',
                'category': 'professional',
                'level': 'intermediate',
                'duration_hours': 6.0,
                'max_students': 30,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'B2B Sales Strategies',
                'code': 'SALES-B2B-201',
                'description': '''Comprehensive guide to business-to-business sales. Learn account-based selling,
stakeholder mapping, value proposition development, and complex deal management. Master the art of
selling to multiple decision-makers and navigating long sales cycles.''',
                'category': 'professional',
                'level': 'intermediate',
                'duration_hours': 10.0,
                'max_students': 25,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Sales Communication and Presentation Skills',
                'code': 'SALES-COMM-101',
                'description': '''Develop powerful communication skills for sales success. Learn to create
compelling presentations, deliver persuasive pitches, handle Q&A sessions, and use storytelling
to engage prospects. Includes practical exercises and video feedback.''',
                'category': 'soft_skills',
                'level': 'beginner',
                'duration_hours': 6.0,
                'max_students': 30,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },

            # ==================== DATA ANALYTICS ====================
            {
                'title': 'Excel for Data Analysis: From Basics to Advanced',
                'code': 'DATA-EXCEL-101',
                'description': '''Master Microsoft Excel for data analysis. Learn advanced formulas,
pivot tables, data visualization, conditional formatting, and data validation. Includes VLOOKUP,
INDEX-MATCH, array formulas, and Power Query basics. Perfect for analysts and business professionals.''',
                'category': 'technical',
                'level': 'beginner',
                'duration_hours': 15.0,
                'max_students': 40,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Power BI: Business Intelligence and Reporting',
                'code': 'DATA-POWERBI-201',
                'description': '''Learn to create powerful interactive dashboards and reports using Microsoft Power BI.
Master DAX formulas, data modeling, relationships, and advanced visualizations. Transform raw data
into actionable insights and share interactive reports across your organization.''',
                'category': 'technical',
                'level': 'intermediate',
                'duration_hours': 12.0,
                'max_students': 30,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'SQL for Data Analytics',
                'code': 'DATA-SQL-201',
                'description': '''Master SQL for data analysis and reporting. Learn to write efficient queries,
join tables, aggregate data, use subqueries, and optimize query performance. Work with real databases
and solve practical business problems using SQL.''',
                'category': 'technical',
                'level': 'intermediate',
                'duration_hours': 16.0,
                'max_students': 30,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Data Visualization Best Practices',
                'code': 'DATA-VIZ-102',
                'description': '''Learn principles of effective data visualization. Understand when to use different
chart types, design principles for dashboards, color theory, and storytelling with data.
Includes hands-on practice with Tableau, Power BI, and Excel.''',
                'category': 'technical',
                'level': 'beginner',
                'duration_hours': 8.0,
                'max_students': 35,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Python for Data Analysis',
                'code': 'DATA-PYTHON-301',
                'description': '''Advanced data analysis using Python. Master pandas, NumPy, and matplotlib libraries.
Learn data cleaning, transformation, statistical analysis, and creating visualizations.
Includes real-world datasets and projects.''',
                'category': 'technical',
                'level': 'advanced',
                'duration_hours': 20.0,
                'max_students': 25,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Business Analytics Fundamentals',
                'code': 'DATA-BIZ-101',
                'description': '''Introduction to business analytics concepts. Learn descriptive, predictive,
and prescriptive analytics. Understand KPIs, metrics, and how to measure business performance.
Apply statistical thinking to solve business problems.''',
                'category': 'professional',
                'level': 'beginner',
                'duration_hours': 10.0,
                'max_students': 40,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Google Analytics for Business',
                'code': 'DATA-GA-201',
                'description': '''Master Google Analytics 4 to track and analyze website performance.
Learn to set up tracking, create custom reports, analyze user behavior, measure conversions,
and make data-driven decisions to improve online presence.''',
                'category': 'technical',
                'level': 'intermediate',
                'duration_hours': 8.0,
                'max_students': 30,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },

            # ==================== MARKETING ====================
            {
                'title': 'Digital Marketing Fundamentals',
                'code': 'MKT-DIG-101',
                'description': '''Comprehensive introduction to digital marketing. Learn SEO, SEM, social media marketing,
email marketing, content marketing, and analytics. Understand customer journey mapping and
creating integrated digital marketing strategies.''',
                'category': 'professional',
                'level': 'beginner',
                'duration_hours': 14.0,
                'max_students': 40,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Social Media Marketing Strategy',
                'code': 'MKT-SOCIAL-201',
                'description': '''Master social media marketing across platforms including Facebook, Instagram,
LinkedIn, and Twitter. Learn content strategy, community management, paid advertising,
influencer marketing, and measuring ROI from social media campaigns.''',
                'category': 'professional',
                'level': 'intermediate',
                'duration_hours': 10.0,
                'max_students': 35,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Content Marketing and Storytelling',
                'code': 'MKT-CONTENT-102',
                'description': '''Learn to create compelling content that engages audiences and drives conversions.
Master blog writing, video content, infographics, and storytelling techniques.
Develop content strategies aligned with business goals.''',
                'category': 'professional',
                'level': 'beginner',
                'duration_hours': 8.0,
                'max_students': 30,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'SEO and SEM Mastery',
                'code': 'MKT-SEO-201',
                'description': '''Advanced search engine optimization and marketing. Learn keyword research,
on-page and off-page SEO, technical SEO, link building, and Google Ads campaigns.
Includes hands-on projects and Google Analytics integration.''',
                'category': 'technical',
                'level': 'intermediate',
                'duration_hours': 12.0,
                'max_students': 30,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Email Marketing Campaigns',
                'code': 'MKT-EMAIL-101',
                'description': '''Master email marketing from strategy to execution. Learn list building,
segmentation, A/B testing, email design, automation workflows, and measuring campaign performance.
Use tools like Mailchimp and HubSpot.''',
                'category': 'professional',
                'level': 'beginner',
                'duration_hours': 6.0,
                'max_students': 35,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Marketing Analytics and ROI Measurement',
                'code': 'MKT-ANALYTICS-201',
                'description': '''Learn to measure and optimize marketing performance. Understand attribution models,
calculate ROI, create marketing dashboards, and use data to optimize campaigns.
Master Google Analytics, Facebook Pixel, and marketing automation tools.''',
                'category': 'technical',
                'level': 'intermediate',
                'duration_hours': 10.0,
                'max_students': 30,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Brand Strategy and Positioning',
                'code': 'MKT-BRAND-201',
                'description': '''Develop strong brand strategies. Learn brand positioning, identity development,
brand messaging, competitive analysis, and brand equity measurement.
Create comprehensive brand guidelines and positioning statements.''',
                'category': 'professional',
                'level': 'intermediate',
                'duration_hours': 8.0,
                'max_students': 25,
                'passing_score': 70,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Marketing Automation with HubSpot',
                'code': 'MKT-AUTO-202',
                'description': '''Master marketing automation using HubSpot. Learn to create workflows,
lead scoring, automated email sequences, landing pages, and track customer lifecycle.
Integrate with CRM and measure automation effectiveness.''',
                'category': 'technical',
                'level': 'intermediate',
                'duration_hours': 10.0,
                'max_students': 25,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
            {
                'title': 'Conversion Rate Optimization (CRO)',
                'code': 'MKT-CRO-301',
                'description': '''Advanced course on optimizing conversion rates. Learn A/B testing methodologies,
user experience optimization, landing page design, psychological triggers, and analytics.
Use tools like Google Optimize and Hotjar.''',
                'category': 'professional',
                'level': 'advanced',
                'duration_hours': 12.0,
                'max_students': 20,
                'passing_score': 75,
                'status': 'published',
                'is_mandatory': False,
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for course_data in courses_data:
            try:
                course, created = Course.objects.update_or_create(
                    code=course_data['code'],
                    defaults={
                        'title': course_data['title'],
                        'description': course_data['description'],
                        'category': course_data['category'],
                        'level': course_data['level'],
                        'duration_hours': course_data['duration_hours'],
                        'max_students': course_data['max_students'],
                        'passing_score': course_data['passing_score'],
                        'status': course_data['status'],
                        'is_mandatory': course_data['is_mandatory'],
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[+] Created: {course.code} - {course.title}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'[*] Updated: {course.code} - {course.title}')
                    )
            except Exception as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.ERROR(f'[!] Error with {course_data["code"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Summary ==='
                f'\nCreated: {created_count}'
                f'\nUpdated: {updated_count}'
                f'\nSkipped: {skipped_count}'
                f'\nTotal: {len(courses_data)}'
            )
        )
