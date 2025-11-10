from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Create ProbationExtensionRequest table manually'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS zone_probationextensionrequest (
                    id BIGSERIAL PRIMARY KEY,
                    extension_duration_days INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    reviewed_at TIMESTAMPTZ NULL,
                    review_comments TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    probation_period_id BIGINT NOT NULL REFERENCES zone_workerprobationperiod(id) ON DELETE CASCADE,
                    requested_by_id INTEGER NULL REFERENCES auth_user(id) ON DELETE SET NULL,
                    reviewed_by_id INTEGER NULL REFERENCES auth_user(id) ON DELETE SET NULL
                );
                
                CREATE INDEX IF NOT EXISTS zone_probationextensionrequest_probation_period_id 
                ON zone_probationextensionrequest(probation_period_id);
                
                CREATE INDEX IF NOT EXISTS zone_probationextensionrequest_requested_by_id 
                ON zone_probationextensionrequest(requested_by_id);
                
                CREATE INDEX IF NOT EXISTS zone_probationextensionrequest_reviewed_by_id 
                ON zone_probationextensionrequest(reviewed_by_id);
            """)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created zone_probationextensionrequest table')
        )