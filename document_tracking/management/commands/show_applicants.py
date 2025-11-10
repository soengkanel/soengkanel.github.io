from django.core.management.base import BaseCommand
from document_tracking.models import DocumentSubmission


class Command(BaseCommand):
    help = 'Display detailed list of applicants in document submissions'

    def handle(self, *args, **options):
        self.stdout.write('=== DOCUMENT TRACKING - APPLICANTS DETAILED LIST ===\n')
        
        submissions = DocumentSubmission.objects.all().order_by('-submission_date', '-created_at')
        
        for i, submission in enumerate(submissions, 1):
            # Submission header
            self.stdout.write(f'{i}. SUBMISSION: {submission.submission_id or "Pending ID"}')
            self.stdout.write(f'   Document: {submission.get_document_type_display()}')
            self.stdout.write(f'   Status: {submission.get_status_display()}')
            self.stdout.write(f'   Office: {submission.government_office}')
            if submission.submission_date:
                self.stdout.write(f'   Date: {submission.submission_date.strftime("%B %d, %Y")}')
            
            # Workers
            workers = submission.workers.all()
            if workers:
                self.stdout.write(f'   WORKERS ({workers.count()}):')
                for j, worker in enumerate(workers, 1):
                    worker_info = f'      {j}. {worker.get_full_name()}'
                    if worker.worker_id:
                        worker_info += f' (ID: {worker.worker_id})'
                    if worker.nationality:
                        worker_info += f' - {worker.nationality}'
                    if worker.position:
                        worker_info += f' - {worker.position}'
                    self.stdout.write(worker_info)
            else:
                self.stdout.write('   WORKERS: None')
            
            vips = submission.vips.all()
            if vips:
                self.stdout.write(f'   VIPs ({vips.count()}):')
                for j, vip in enumerate(vips, 1):
                    vip_info = f'      {j}. {vip.first_name} {vip.last_name}'
                    if vip.nickname:
                        vip_info += f' ({vip.nickname})'
                    if vip.vip_type:
                        vip_info += f' - {vip.get_vip_type_display()}'
                    if vip.nationality:
                        vip_info += f' - {vip.nationality}'
                    self.stdout.write(vip_info)
            else:
                self.stdout.write('   VIPs: None')
            
            # Purpose
            if submission.purpose:
                purpose = submission.purpose[:80] + '...' if len(submission.purpose) > 80 else submission.purpose
                self.stdout.write(f'   Purpose: {purpose}')
            
            self.stdout.write('')  # Empty line between submissions
        
        # Summary
        total_submissions = submissions.count()
        total_workers_involved = sum([s.workers.count() for s in submissions])
        total_vips_involved = sum([s.vips.count() for s in submissions])
        
        self.stdout.write('=' * 60)
        self.stdout.write(f'SUMMARY:')
        self.stdout.write(f'Total Submissions: {total_submissions}')
        self.stdout.write(f'Total Worker Involvements: {total_workers_involved}')
        self.stdout.write(f'Total VIP Involvements: {total_vips_involved}')
        self.stdout.write(f'Total Applicant Involvements: {total_workers_involved + total_vips_involved}')
        self.stdout.write('=' * 60) 