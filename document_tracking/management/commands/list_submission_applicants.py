from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

from document_tracking.models import DocumentSubmission
from zone.models import Worker


class Command(BaseCommand):
    help = 'Display detailed list of workers and VIPs in document submissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--submission-id',
            type=int,
            help='Show applicants for a specific submission ID',
        )
        parser.add_argument(
            '--workers-only',
            action='store_true',
            help='Show only workers',
        )
        parser.add_argument(
            '--vips-only',
            action='store_true',
            help='Show only VIPs',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show summary statistics only',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DOCUMENT SUBMISSION APPLICANTS REPORT ===\n'))
        
        # Filter submissions based on options
        submissions = DocumentSubmission.objects.all().order_by('-submission_date', '-created_at')
        
        if options['submission_id']:
            submissions = submissions.filter(id=options['submission_id'])
            if not submissions.exists():
                self.stdout.write(self.style.ERROR(f'No submission found with ID: {options["submission_id"]}'))
                return

        if options['summary']:
            self.show_summary()
            return

        # Show detailed applicant information
        for submission in submissions:
            self.show_submission_applicants(submission, options)

        if not options['submission_id']:
            self.stdout.write('\n' + '='*80)
            self.show_overall_statistics()

    def show_submission_applicants(self, submission, options):
        """Display detailed applicant information for a submission"""
        
        self.stdout.write(f'\n📋 SUBMISSION: {submission.submission_id or "Pending ID"}')
        self.stdout.write(f'   Document Type: {submission.get_document_type_display()}')
        self.stdout.write(f'   Status: {submission.get_status_display()}')
        self.stdout.write(f'   Government Office: {submission.government_office}')
        if submission.submission_date:
            self.stdout.write(f'   Submission Date: {submission.submission_date.strftime("%B %d, %Y")}')
        self.stdout.write(f'   Total Applicants: {submission.total_applicants}')
        
        # Show workers
        if not options['vips_only']:
            workers = submission.workers.all()
            if workers:
                self.stdout.write(self.style.HTTP_INFO(f'\n   👥 WORKERS ({workers.count()}):'))
                for i, worker in enumerate(workers, 1):
                    self.stdout.write(f'      {i}. {self.format_worker_info(worker)}')
            elif not options['workers_only']:
                self.stdout.write('   👥 WORKERS: None')

        # Show VIPs
        if not options['workers_only']:
            vips = submission.vips.all()
            if vips:
                self.stdout.write(self.style.HTTP_INFO(f'\n   ⭐ VIPs ({vips.count()}):'))
                for i, vip in enumerate(vips, 1):
                    self.stdout.write(f'      {i}. {self.format_vip_info(vip)}')
            elif not options['vips_only']:
                self.stdout.write('   ⭐ VIPs: None')

        # Show purpose if available
        if submission.purpose:
            self.stdout.write(f'\n   📝 Purpose: {submission.purpose[:100]}{"..." if len(submission.purpose) > 100 else ""}')

        self.stdout.write('-' * 80)

    def format_worker_info(self, worker):
        """Format worker information for display"""
        info = f'{worker.get_full_name()}'
        details = []
        
        if worker.worker_id:
            details.append(f'ID: {worker.worker_id}')
        if worker.nationality:
            details.append(f'Nationality: {worker.nationality}')
        if worker.position:
            details.append(f'Position: {worker.position}')
        if worker.phone_number:
            details.append(f'Phone: {worker.phone_number}')
        if worker.email:
            details.append(f'Email: {worker.email}')
        
        if details:
            info += f' ({", ".join(details)})'
            
        return info

    def format_vip_info(self, vip):
        """Format VIP information for display"""
        info = f'{vip.first_name} {vip.last_name}'
        details = []
        
        if vip.nickname:
            details.append(f'Nickname: {vip.nickname}')
        if vip.vip_type:
            details.append(f'Type: {vip.get_vip_type_display()}')
        if vip.nationality:
            details.append(f'Nationality: {vip.nationality}')
        if vip.phone_number:
            details.append(f'Phone: {vip.phone_number}')
        if vip.email:
            details.append(f'Email: {vip.email}')
        
        if details:
            info += f' ({", ".join(details)})'
            
        return info

    def show_summary(self):
        """Show summary statistics only"""
        total_submissions = DocumentSubmission.objects.count()
        
        # Submissions with workers/VIPs
        submissions_with_workers = DocumentSubmission.objects.filter(workers__isnull=False).distinct().count()
        submissions_with_vips = DocumentSubmission.objects.filter(vips__isnull=False).distinct().count()
        submissions_with_both = DocumentSubmission.objects.filter(
            workers__isnull=False, vips__isnull=False
        ).distinct().count()
        submissions_with_none = DocumentSubmission.objects.filter(
            workers__isnull=True, vips__isnull=True
        ).count()

        self.stdout.write(f'📊 APPLICANT SUMMARY:')
        self.stdout.write(f'   Total Submissions: {total_submissions}')
        self.stdout.write(f'   Submissions with Workers: {submissions_with_workers}')
        self.stdout.write(f'   Submissions with VIPs: {submissions_with_vips}')
        self.stdout.write(f'   Submissions with Both: {submissions_with_both}')
        self.stdout.write(f'   Submissions with No Applicants: {submissions_with_none}')

        # Most frequently used workers
        self.stdout.write(f'\n👥 TOP WORKERS IN SUBMISSIONS:')
        top_workers = Worker.objects.annotate(
            submission_count=Count('document_submissions')
        ).filter(submission_count__gt=0).order_by('-submission_count')[:5]

        for i, worker in enumerate(top_workers, 1):
            self.stdout.write(f'   {i}. {worker.get_full_name()} - {worker.submission_count} submissions')

        # Most frequently used VIPs
        self.stdout.write(f'\n⭐ TOP VIPs IN SUBMISSIONS:')
        top_vips = VIP.objects.annotate(
            submission_count=Count('document_submissions')
        ).filter(submission_count__gt=0).order_by('-submission_count')[:5]

        for i, vip in enumerate(top_vips, 1):
            self.stdout.write(f'   {i}. {vip.first_name} {vip.last_name} - {vip.submission_count} submissions')

    def show_overall_statistics(self):
        """Show overall applicant statistics"""
        
        # Total unique applicants across all submissions
        unique_workers = Worker.objects.filter(document_submissions__isnull=False).distinct().count()
        unique_vips = VIP.objects.filter(document_submissions__isnull=False).distinct().count()
        
        # Average applicants per submission
        submissions_with_applicants = DocumentSubmission.objects.annotate(
            applicant_count=Count('workers') + Count('vips')
        ).filter(applicant_count__gt=0)
        
        avg_applicants = 0
        if submissions_with_applicants.exists():
            total_applicants = sum([s.total_applicants for s in submissions_with_applicants])
            avg_applicants = total_applicants / submissions_with_applicants.count()

        self.stdout.write(self.style.SUCCESS('\n📈 OVERALL STATISTICS:'))
        self.stdout.write(f'   Unique Workers in System: {unique_workers}')
        self.stdout.write(f'   Unique VIPs in System: {unique_vips}')
        self.stdout.write(f'   Average Applicants per Submission: {avg_applicants:.1f}')

        # Submissions by applicant count
        self.stdout.write(f'\n📊 SUBMISSIONS BY APPLICANT COUNT:')
        for i in range(1, 16):  # 1 to 15+ applicants
            if i == 15:
                count = DocumentSubmission.objects.annotate(
                    applicant_count=Count('workers') + Count('vips')
                ).filter(applicant_count__gte=i).count()
                if count > 0:
                    self.stdout.write(f'   15+ applicants: {count} submissions')
            else:
                count = DocumentSubmission.objects.annotate(
                    applicant_count=Count('workers') + Count('vips')
                ).filter(applicant_count=i).count()
                if count > 0:
                    self.stdout.write(f'   {i} applicant{"s" if i > 1 else ""}: {count} submission{"s" if count > 1 else ""}')

        self.stdout.write(self.style.SUCCESS('\n=== END OF REPORT ===')) 