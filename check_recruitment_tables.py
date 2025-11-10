#!/usr/bin/env python
"""
Check recruitment table structure
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def check_tables():
    """Check if recruitment tables exist and their structure"""

    # Check kk_company schema (tenant)
    schemas_to_check = ['public', 'kk_company']

    for schema in schemas_to_check:
        print(f"\n=== Checking schema: {schema} ===")

        with connection.cursor() as cursor:
            # Check if recruitment_candidate table exists
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'recruitment_candidate'
                AND table_schema = %s
                ORDER BY ordinal_position
            """, [schema])

            columns = cursor.fetchall()

            if columns:
                print(f"recruitment_candidate table columns ({len(columns)} total):")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")

                # Check if job_posting_id exists
                has_job_posting = any('job_posting' in col[0] for col in columns)
                if has_job_posting:
                    print("\n[OK] job_posting_id column exists")
                else:
                    print("\n[ERROR] job_posting_id column is MISSING!")

            else:
                print("[ERROR] recruitment_candidate table does not exist!")

            # Check if recruitment_jobposting table exists
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'recruitment_jobposting'
                AND table_schema = %s
            """, [schema])

            job_columns = cursor.fetchall()
            if job_columns:
                print(f"\n[OK] recruitment_jobposting table exists with {len(job_columns)} columns")
            else:
                print("\n[ERROR] recruitment_jobposting table does not exist!")

if __name__ == '__main__':
    check_tables()
