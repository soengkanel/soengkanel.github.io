from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date, timedelta
import random
import uuid

from document_tracking.models import DocumentSubmission, DocumentUpdate
from zone.models import Worker


class Command(BaseCommand):
    help = 'Generate 30 mock document submissions with different scenarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing document submissions before generating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing document submissions...')
            DocumentSubmission.objects.all().delete()
            DocumentUpdate.objects.all().delete()

        # Get available workers and VIPs
        workers = list(Worker.objects.filter(status='active'))
        vips = list(VIP.objects.all())

        if not workers and not vips:
            self.stdout.write(
                self.style.ERROR('No workers or VIPs found. Please create some workers and VIPs first.')
            )
            return

        self.stdout.write(f'Found {len(workers)} workers and {len(vips)} VIPs')
        self.stdout.write('Generating 30 mock document submissions...')

        # Mock data definitions
        mock_scenarios = self.get_mock_scenarios()
        
        submissions_created = 0
        for i, scenario in enumerate(mock_scenarios):
            try:
                submission = self.create_submission(scenario, workers, vips)
                self.create_updates_for_submission(submission, scenario)
                submissions_created += 1
                
                self.stdout.write(f'Created: {submission}')
                
            except Exception as e:

                
                pass
                self.stdout.write(
                    self.style.ERROR(f'Error creating submission {i+1}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {submissions_created} document submissions!')
        )

    def get_mock_scenarios(self):
        """Define 30 different mock scenarios with various combinations"""
        scenarios = [
            # Scenario 1-5: Recent Visa Applications (Different statuses)
            {
                'document_type': 'visa_regular',
                'status': 'submitted',
                'processing_entity': 'building',
                'government_office': 'Immigration Department - Main Office',
                'days_ago': 5,
                'reference_number': 'VIS2024001234',
                'purpose': 'Tourist visa application for family vacation',
                'applicant_type': 'workers',
                'applicant_count': 2,
                'notes': 'All required documents submitted. Waiting for approval.'
            },
            {
                'document_type': 'visa_express',
                'status': 'completed',
                'processing_entity': 'people',
                'government_office': "People's Visa Service Center",
                'days_ago': 8,
                'reference_number': 'EXPRESS-VIS-2024-567',
                'purpose': 'Urgent business visa for conference attendance',
                'applicant_type': 'vips',
                'applicant_count': 1,
                'notes': 'Express processing completed successfully. Documents received.',
                'completed': True
            },
            {
                'document_type': 'visa_regular',
                'status': 'under_review',
                'processing_entity': 'embassy',
                'government_office': 'Embassy of Germany',
                'days_ago': 12,
                'reference_number': 'EMB-DE-2024-789',
                'purpose': 'Study visa application for university enrollment',
                'applicant_type': 'workers',
                'applicant_count': 1,
                'notes': 'Additional documentation requested by embassy.'
            },
            {
                'document_type': 'visa_regular',
                'status': 'approved',
                'processing_entity': 'consulate',
                'government_office': 'Consulate General of France',
                'days_ago': 15,
                'reference_number': 'CON-FR-2024-456',
                'purpose': 'Work visa application for temporary assignment',
                'applicant_type': 'mixed',
                'applicant_count': 3,
                'notes': 'Approved. Ready for document pickup.'
            },
            {
                'document_type': 'visa_express',
                'status': 'rejected',
                'processing_entity': 'building',
                'government_office': 'Immigration Appeals Office',
                'days_ago': 20,
                'reference_number': 'REJECT-2024-123',
                'purpose': 'Transit visa application',
                'applicant_type': 'workers',
                'applicant_count': 1,
                'notes': 'Rejected due to incomplete financial documentation. Can reapply with proper documents.'
            },

            # Scenario 6-10: Work Permit Applications
            {
                'document_type': 'work_permit_regular',
                'status': 'pending',
                'processing_entity': 'ministry',
                'government_office': 'Ministry of Labor and Employment',
                'days_ago': 2,
                'purpose': 'Work permit for construction workers',
                'applicant_type': 'workers',
                'applicant_count': 5,
                'notes': 'Initial application submitted. Awaiting document verification.'
            },
            {
                'document_type': 'work_permit_express',
                'status': 'submitted',
                'processing_entity': 'building',
                'government_office': 'Labor Department - Express Service',
                'days_ago': 7,
                'reference_number': 'WP-EXP-2024-890',
                'purpose': 'Express work permit for skilled technicians',
                'applicant_type': 'workers',
                'applicant_count': 3,
                'notes': 'Express processing requested due to urgent project deadline.'
            },
            {
                'document_type': 'work_permit_regular',
                'status': 'under_review',
                'processing_entity': 'ministry',
                'government_office': 'Ministry of Industry and Trade',
                'days_ago': 18,
                'reference_number': 'WP-REG-2024-345',
                'purpose': 'Work permits for manufacturing facility staff',
                'applicant_type': 'workers',
                'applicant_count': 8,
                'notes': 'Background checks in progress for all applicants.'
            },
            {
                'document_type': 'work_permit_express',
                'status': 'completed',
                'processing_entity': 'people',
                'government_office': "People's Employment Service",
                'days_ago': 25,
                'reference_number': 'WP-COMP-2024-678',
                'purpose': 'Work permits for hotel management team',
                'applicant_type': 'mixed',
                'applicant_count': 4,
                'notes': 'All permits issued successfully. Valid for 2 years.',
                'completed': True
            },
            {
                'document_type': 'work_permit_regular',
                'status': 'overdue',
                'processing_entity': 'building',
                'government_office': 'Regional Labor Office',
                'days_ago': 35,
                'reference_number': 'WP-OVER-2024-111',
                'purpose': 'Work permits for agricultural workers',
                'applicant_type': 'workers',
                'applicant_count': 12,
                'notes': 'Processing delayed due to seasonal application volume. Follow-up required.',
                'overdue': True
            },

            # Scenario 11-15: Passport Renewals
            {
                'document_type': 'passport_renewal',
                'status': 'submitted',
                'processing_entity': 'embassy',
                'government_office': 'Embassy Passport Services',
                'days_ago': 6,
                'reference_number': 'PASS-REN-2024-555',
                'purpose': 'Passport renewal for expired documents',
                'applicant_type': 'vips',
                'applicant_count': 2,
                'notes': 'Renewal applications submitted with expired passports.'
            },
            {
                'document_type': 'passport_renewal',
                'status': 'under_review',
                'processing_entity': 'consulate',
                'government_office': 'Consular Passport Division',
                'days_ago': 14,
                'reference_number': 'PASS-REV-2024-777',
                'purpose': 'Emergency passport renewal for travel',
                'applicant_type': 'workers',
                'applicant_count': 1,
                'notes': 'Emergency renewal requested for urgent medical travel.'
            },
            {
                'document_type': 'passport_renewal',
                'status': 'approved',
                'processing_entity': 'building',
                'government_office': 'National Passport Office',
                'days_ago': 19,
                'reference_number': 'PASS-APP-2024-999',
                'purpose': 'Regular passport renewal process',
                'applicant_type': 'mixed',
                'applicant_count': 6,
                'notes': 'New passports ready for collection.'
            },
            {
                'document_type': 'passport_renewal',
                'status': 'completed',
                'processing_entity': 'embassy',
                'government_office': 'Embassy Document Services',
                'days_ago': 28,
                'reference_number': 'PASS-DONE-2024-333',
                'purpose': 'Passport renewal for business travelers',
                'applicant_type': 'vips',
                'applicant_count': 3,
                'notes': 'All new passports issued and delivered.',
                'completed': True
            },
            {
                'document_type': 'passport_renewal',
                'status': 'pending',
                'processing_entity': 'other',
                'government_office': 'Third-Party Processing Center',
                'days_ago': 1,
                'purpose': 'Batch passport renewal for company employees',
                'applicant_type': 'workers',
                'applicant_count': 15,
                'notes': 'Large batch submission for annual passport renewals.'
            },

            # Scenario 16-20: Residence Permits
            {
                'document_type': 'residence_permit',
                'status': 'submitted',
                'processing_entity': 'ministry',
                'government_office': 'Ministry of Interior - Immigration Division',
                'days_ago': 10,
                'reference_number': 'RES-2024-1001',
                'purpose': 'Long-term residence permit application',
                'applicant_type': 'workers',
                'applicant_count': 2,
                'notes': 'Application for permanent residence status.'
            },
            {
                'document_type': 'residence_permit',
                'status': 'under_review',
                'processing_entity': 'building',
                'government_office': 'Immigration Services Center',
                'days_ago': 22,
                'reference_number': 'RES-REV-2024-2002',
                'purpose': 'Family reunification residence permits',
                'applicant_type': 'mixed',
                'applicant_count': 4,
                'notes': 'Family background verification in progress.'
            },
            {
                'document_type': 'residence_permit',
                'status': 'approved',
                'processing_entity': 'ministry',
                'government_office': 'Ministry of Justice - Legal Affairs',
                'days_ago': 27,
                'reference_number': 'RES-APP-2024-3003',
                'purpose': 'Student residence permits',
                'applicant_type': 'workers',
                'applicant_count': 7,
                'notes': 'Approved for university students. Valid for study duration.'
            },
            {
                'document_type': 'residence_permit',
                'status': 'overdue',
                'processing_entity': 'building',
                'government_office': 'Regional Immigration Office',
                'days_ago': 45,
                'reference_number': 'RES-OVER-2024-4004',
                'purpose': 'Investor residence permits',
                'applicant_type': 'vips',
                'applicant_count': 2,
                'notes': 'Processing delayed due to investment verification requirements.',
                'overdue': True
            },
            {
                'document_type': 'residence_permit',
                'status': 'completed',
                'processing_entity': 'ministry',
                'government_office': 'Central Immigration Authority',
                'days_ago': 33,
                'reference_number': 'RES-COMP-2024-5005',
                'purpose': 'Renewal of existing residence permits',
                'applicant_type': 'mixed',
                'applicant_count': 9,
                'notes': 'All residence permit renewals processed successfully.',
                'completed': True
            },

            # Scenario 21-25: Business Licenses
            {
                'document_type': 'business_license',
                'status': 'pending',
                'processing_entity': 'ministry',
                'government_office': 'Ministry of Commerce and Industry',
                'days_ago': 3,
                'purpose': 'Trading company business license',
                'applicant_type': 'vips',
                'applicant_count': 1,
                'notes': 'New business license application for import/export company.'
            },
            {
                'document_type': 'business_license',
                'status': 'submitted',
                'processing_entity': 'building',
                'government_office': 'Business Registration Office',
                'days_ago': 8,
                'reference_number': 'BL-2024-A100',
                'purpose': 'Restaurant business license',
                'applicant_type': 'workers',
                'applicant_count': 2,
                'notes': 'Food service license application with health department approval.'
            },
            {
                'document_type': 'business_license',
                'status': 'under_review',
                'processing_entity': 'ministry',
                'government_office': 'Ministry of Small Business Development',
                'days_ago': 11,
                'reference_number': 'BL-REV-2024-B200',
                'purpose': 'Technology startup business license',
                'applicant_type': 'mixed',
                'applicant_count': 3,
                'notes': 'Technology compliance review in progress.'
            },
            {
                'document_type': 'business_license',
                'status': 'approved',
                'processing_entity': 'building',
                'government_office': 'Municipal Business Office',
                'days_ago': 16,
                'reference_number': 'BL-APP-2024-C300',
                'purpose': 'Retail store business license',
                'applicant_type': 'vips',
                'applicant_count': 1,
                'notes': 'License approved for retail operations. Ready for collection.'
            },
            {
                'document_type': 'business_license',
                'status': 'completed',
                'processing_entity': 'ministry',
                'government_office': 'Department of Business Affairs',
                'days_ago': 21,
                'reference_number': 'BL-COMP-2024-D400',
                'purpose': 'Manufacturing facility license',
                'applicant_type': 'mixed',
                'applicant_count': 5,
                'notes': 'Manufacturing license issued with environmental compliance.',
                'completed': True
            },

            # Scenario 26-30: Mixed and Edge Cases
            {
                'document_type': 'other',
                'status': 'submitted',
                'processing_entity': 'other',
                'government_office': 'Special Documentation Office',
                'days_ago': 4,
                'reference_number': 'SPEC-2024-X001',
                'purpose': 'Special diplomatic documentation',
                'applicant_type': 'vips',
                'applicant_count': 1,
                'notes': 'Special case requiring diplomatic clearance.',
                'document_title': 'Diplomatic Travel Document'
            },
            {
                'document_type': 'visa_regular',
                'status': 'pending',
                'processing_entity': 'embassy',
                'government_office': 'Embassy of Canada',
                'days_ago': 0,
                'purpose': 'Multiple entry visa application',
                'applicant_type': 'workers',
                'applicant_count': 1,
                'notes': 'Same-day application for multiple entry visa.',
                'document_title': 'Multiple Entry Visa'
            },
            {
                'document_type': 'work_permit_regular',
                'status': 'expired',
                'processing_entity': 'building',
                'government_office': 'Expired Documents Office',
                'days_ago': 60,
                'reference_number': 'EXP-2024-OLD001',
                'purpose': 'Expired work permit replacement',
                'applicant_type': 'workers',
                'applicant_count': 3,
                'notes': 'Original permits expired. Replacement process initiated.',
                'overdue': True
            },
            {
                'document_type': 'passport_renewal',
                'status': 'rejected',
                'processing_entity': 'consulate',
                'government_office': 'Consulate Document Review',
                'days_ago': 30,
                'reference_number': 'REJ-PASS-2024-999',
                'purpose': 'Passport renewal with issues',
                'applicant_type': 'mixed',
                'applicant_count': 2,
                'notes': 'Rejected due to damaged original passport. Requires additional documentation.'
            },
            {
                'document_type': 'business_license',
                'status': 'overdue',
                'processing_entity': 'ministry',
                'government_office': 'Delayed Processing Department',
                'days_ago': 50,
                'reference_number': 'DELAY-BL-2024-LAST',
                'purpose': 'Complex multi-location business license',
                'applicant_type': 'vips',
                'applicant_count': 4,
                'notes': 'Complex application requiring multiple department approvals. Significant delays.',
                'overdue': True
            }
        ]
        
        return scenarios

    def create_submission(self, scenario, workers, vips):
        """Create a document submission based on scenario"""
        
        # Calculate dates
        submission_date = timezone.now().date() - timedelta(days=scenario.get('days_ago', 0))
        
        # Create the submission
        submission = DocumentSubmission(
            document_type=scenario['document_type'],
            status=scenario['status'],
            processing_entity=scenario['processing_entity'],
            government_office=scenario['government_office'],
            reference_number=scenario.get('reference_number', ''),
            document_title=scenario.get('document_title', ''),
            purpose=scenario['purpose'],
            submission_date=submission_date,
            notes=scenario['notes']
        )
        
        # Calculate expected completion date
        processing_days = submission.get_processing_days()
        if processing_days and submission_date:
            expected_date = submission_date + timedelta(days=processing_days)
            submission.expected_completion_date = expected_date
            
            # Handle overdue scenarios
            if scenario.get('overdue'):
                submission.expected_completion_date = submission_date + timedelta(days=processing_days)
                
            # Handle completed scenarios
            if scenario.get('completed'):
                completion_days = random.randint(processing_days - 3, processing_days + 2)
                submission.actual_completion_date = submission_date + timedelta(days=completion_days)
                
                # Set expiry date for completed documents
                if scenario['document_type'] in ['visa_regular', 'visa_express']:
                    submission.expiry_date = submission.actual_completion_date + timedelta(days=180)  # 6 months
                elif scenario['document_type'] in ['work_permit_regular', 'work_permit_express']:
                    submission.expiry_date = submission.actual_completion_date + timedelta(days=730)  # 2 years
                elif scenario['document_type'] == 'passport_renewal':
                    submission.expiry_date = submission.actual_completion_date + timedelta(days=3650)  # 10 years
                elif scenario['document_type'] == 'residence_permit':
                    submission.expiry_date = submission.actual_completion_date + timedelta(days=1095)  # 3 years
                elif scenario['document_type'] == 'business_license':
                    submission.expiry_date = submission.actual_completion_date + timedelta(days=365)  # 1 year

        submission.save()
        
        # Add applicants
        applicant_type = scenario.get('applicant_type', 'workers')
        applicant_count = scenario.get('applicant_count', 1)
        
        if applicant_type == 'workers' and workers:
            selected_workers = random.sample(workers, min(applicant_count, len(workers)))
            submission.workers.set(selected_workers)
        elif applicant_type == 'vips' and vips:
            selected_vips = random.sample(vips, min(applicant_count, len(vips)))
            submission.vips.set(selected_vips)
        elif applicant_type == 'mixed':
            # Mix of workers and VIPs
            worker_count = applicant_count // 2
            vip_count = applicant_count - worker_count
            
            if workers and worker_count > 0:
                selected_workers = random.sample(workers, min(worker_count, len(workers)))
                submission.workers.set(selected_workers)
            
            if vips and vip_count > 0:
                selected_vips = random.sample(vips, min(vip_count, len(vips)))
                submission.vips.set(selected_vips)
        
        return submission

    def create_updates_for_submission(self, submission, scenario):
        """Create realistic document updates for the submission"""
        
        # Create initial submission update
        if submission.submission_date:
            DocumentUpdate.objects.create(
                submission=submission,
                update_type='status_change',
                old_value='pending',
                new_value='submitted',
                notes=f'Document submission created and submitted to {submission.government_office}',
                created_at=timezone.make_aware(
                    datetime.combine(submission.submission_date, datetime.min.time())
                )
            )
        
        # Create additional updates based on status
        if submission.status in ['under_review', 'approved', 'completed', 'rejected']:
            review_date = submission.submission_date + timedelta(days=random.randint(3, 7))
            DocumentUpdate.objects.create(
                submission=submission,
                update_type='status_change',
                old_value='submitted',
                new_value='under_review',
                notes='Document received and under review by processing office',
                created_at=timezone.make_aware(
                    datetime.combine(review_date, datetime.min.time())
                )
            )
        
        if submission.status in ['approved', 'completed', 'rejected']:
            decision_date = submission.submission_date + timedelta(days=random.randint(7, 15))
            DocumentUpdate.objects.create(
                submission=submission,
                update_type='status_change',
                old_value='under_review',
                new_value=submission.status,
                notes=f'Document processing {submission.status}',
                created_at=timezone.make_aware(
                    datetime.combine(decision_date, datetime.min.time())
                )
            )
        
        # Add reference number update if it exists
        if submission.reference_number:
            ref_date = submission.submission_date + timedelta(days=random.randint(1, 3))
            DocumentUpdate.objects.create(
                submission=submission,
                update_type='reference_added',
                new_value=submission.reference_number,
                notes=f'Government reference number assigned: {submission.reference_number}',
                created_at=timezone.make_aware(
                    datetime.combine(ref_date, datetime.min.time())
                )
            )

        # Add document received update for completed submissions
        if submission.status == 'completed' and submission.actual_completion_date:
            DocumentUpdate.objects.create(
                submission=submission,
                update_type='document_received',
                new_value='Documents received and delivered',
                notes='Final documents received and delivered to applicants',
                created_at=timezone.make_aware(
                    datetime.combine(submission.actual_completion_date, datetime.min.time())
                )
            ) 