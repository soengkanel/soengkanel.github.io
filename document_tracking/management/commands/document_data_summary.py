from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from document_tracking.models import DocumentSubmission, DocumentUpdate


class Command(BaseCommand):
    help = 'Display a summary of document tracking data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DOCUMENT TRACKING SYSTEM SUMMARY ===\n'))
        
        # Total submissions
        total_submissions = DocumentSubmission.objects.count()
        self.stdout.write(f'📋 Total Document Submissions: {total_submissions}\n')
        
        # Status breakdown
        self.stdout.write(self.style.HTTP_INFO('📊 STATUS BREAKDOWN:'))
        status_counts = DocumentSubmission.objects.values('status').annotate(count=Count('status')).order_by('-count')
        for item in status_counts:
            status_display = dict(DocumentSubmission.STATUS_CHOICES).get(item['status'], item['status'])
            self.stdout.write(f'   • {status_display}: {item["count"]}')
        
        self.stdout.write('')
        
        # Document type breakdown
        self.stdout.write(self.style.HTTP_INFO('📄 DOCUMENT TYPE BREAKDOWN:'))
        type_counts = DocumentSubmission.objects.values('document_type').annotate(count=Count('document_type')).order_by('-count')
        for item in type_counts:
            type_display = dict(DocumentSubmission.DOCUMENT_TYPE_CHOICES).get(item['document_type'], item['document_type'])
            self.stdout.write(f'   • {type_display}: {item["count"]}')
        
        self.stdout.write('')
        
        # Processing entity breakdown
        self.stdout.write(self.style.HTTP_INFO('🏢 PROCESSING ENTITY BREAKDOWN:'))
        entity_counts = DocumentSubmission.objects.values('processing_entity').annotate(count=Count('processing_entity')).order_by('-count')
        for item in entity_counts:
            entity_display = dict(DocumentSubmission.PROCESSING_ENTITY_CHOICES).get(item['processing_entity'], item['processing_entity'])
            self.stdout.write(f'   • {entity_display}: {item["count"]}')
        
        self.stdout.write('')
        
        # Overdue submissions
        overdue_count = DocumentSubmission.objects.filter(
            expected_completion_date__lt=timezone.now().date(),
            status__in=['pending', 'submitted', 'under_review']
        ).count()
        self.stdout.write(self.style.WARNING(f'⚠️  OVERDUE SUBMISSIONS: {overdue_count}'))
        
        if overdue_count > 0:
            overdue_submissions = DocumentSubmission.objects.filter(
                expected_completion_date__lt=timezone.now().date(),
                status__in=['pending', 'submitted', 'under_review']
            )[:5]  # Show first 5
            
            for submission in overdue_submissions:
                days_overdue = submission.days_overdue
                self.stdout.write(f'   • {submission} ({days_overdue} days overdue)')
        
        self.stdout.write('')
        
        # Completed submissions
        completed_count = DocumentSubmission.objects.filter(status='completed').count()
        self.stdout.write(self.style.SUCCESS(f'✅ COMPLETED SUBMISSIONS: {completed_count}'))
        
        # Recent activity (last 7 days)
        recent_date = timezone.now().date() - timedelta(days=7)
        recent_count = DocumentSubmission.objects.filter(submission_date__gte=recent_date).count()
        self.stdout.write(f'📅 RECENT SUBMISSIONS (Last 7 days): {recent_count}')
        
        # Applicant statistics
        total_workers = DocumentSubmission.objects.filter(workers__isnull=False).distinct().count()
        total_vips = DocumentSubmission.objects.filter(vips__isnull=False).distinct().count()
        self.stdout.write(f'👥 SUBMISSIONS WITH WORKERS: {total_workers}')
        self.stdout.write(f'⭐ SUBMISSIONS WITH VIPs: {total_vips}')
        
        self.stdout.write('')
        
        # Document updates
        total_updates = DocumentUpdate.objects.count()
        self.stdout.write(f'📝 Total Document Updates: {total_updates}')
        
        # Most active submissions (most updates)
        if total_updates > 0:
            self.stdout.write(self.style.HTTP_INFO('📈 MOST ACTIVE SUBMISSIONS:'))
            active_submissions = DocumentSubmission.objects.annotate(
                update_count=Count('updates')
            ).filter(update_count__gt=0).order_by('-update_count')[:5]
            
            for submission in active_submissions:
                self.stdout.write(f'   • {submission} ({submission.update_count} updates)')
        
        self.stdout.write('')
        
        # Expiring documents (within 30 days)
        expiring_soon = DocumentSubmission.objects.filter(
            expiry_date__lte=timezone.now().date() + timedelta(days=30),
            expiry_date__gte=timezone.now().date(),
            status='completed'
        ).count()
        
        if expiring_soon > 0:
            self.stdout.write(self.style.WARNING(f'⏰ DOCUMENTS EXPIRING SOON (30 days): {expiring_soon}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== END OF SUMMARY ===')) 