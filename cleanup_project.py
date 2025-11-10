"""
Cleanup script to remove temporary test files, debug scripts, and unused documentation

This script will identify and remove:
    pass
1. Test scripts (test_*.py)
2. Debug scripts (debug_*.py, check_*.py, trace_*.py, verify_*.py)
3. Fake migration scripts (fake_*.py)
4. Temporary documentation files
5. Empty/nul files
"""
import os
import sys
from datetime import datetime

# Files to remove (organized by category)
FILES_TO_REMOVE = {
    'Test Scripts': [
        'test_timesheet_operations.py',
        'test_tenant_setup_safe.py',
        'test_import_api_views.py',
        'test_migration_scenario.py',
        'test_fk_add_minimal.py',
        'test_final_fix.py',
        'test_router_registration.py',
        'test_actual_migration_scenario.py',
        'test_migrate_command.py',
        'test_admin_registration.py',
        'test_addfield_foreignkey.py',
        'test_tenant_schema_query.py',
        'test_verbose_tenant_migrate.py',
        'test_django_field_validation.py',
        'test_postgres_fk_creation.py',
        'test_tenant_migration.py',
    ],
    'Debug Scripts': [
        'debug_migration_direct.py',
    ],
    'Check Scripts': [
        'check_employees.py',
        'check_tenants.py',
        'check_project_tables.py',
        'check_mock_projects.py',
        'check_timesheet_table.py',
        'check_schemas.py',
        'check_migration_order.py',
    ],
    'Trace Scripts': [
        'trace_timesheet_query.py',
        'trace_full_dependency_chain.py',
    ],
    'Verify Scripts': [
        'verify_system_health.py',
        'verify_dependency_fix.py',
    ],
    'Fake Migration Scripts': [
        'fake_migration_0008.py',
        'fake_hr_0064.py',
        'fake_0007b.py',
    ],
    'Temporary Documentation': [
        'HOW_TO_VIEW_SCHEMAS.md',
        'MIGRATION_FIX_SUMMARY.md',
        'ROOT_CAUSE_AND_FIX.md',
        'POST_FIX_VERIFICATION.md',
    ],
    'Empty/Null Files': [
        'nul',
    ],
}

# Files to KEEP (important documentation and utilities)
FILES_TO_KEEP = [
    'README.md',
    'CHANGELOG.md',
    'SETUP_GUIDELINE.md',
    'NGINX_DJANGO_SETUP.md',
    'COMPILED_APP_GUIDE.md',
    'TENANT_ROUTING_GUIDE.md',
    'TENANT_PARAMETER_GUIDE.md',
    'ProjectTimeline.md',
    'PAYSLIP_SETUP.md',
    'project_status.md',
    'DEVELOPER_CHECKLIST.md',
    'MIGRATION_RESET_GUIDE.md',  # Keep the migration reset guide
    'backup_database.py',  # Keep migration reset utilities
    'remove_migrations.py',
    'clean_migration_history.py',
    'regenerate_migrations.py',
    'manage.py',
    'tenant_setup.py',
]

def create_backup_list():
    """Create a list of files to be removed for backup purposes"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'cleanup_backup_list_{timestamp}.txt'

    with open(backup_file, 'w') as f:
        f.write("Files to be removed by cleanup_project.py\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 60 + "\n\n")

        for category, files in FILES_TO_REMOVE.items():
            f.write(f"\n{category}:\n")
            f.write("-" * 40 + "\n")
            for file in files:
                file_path = os.path.join('.', file)
                exists = "EXISTS" if os.path.exists(file_path) else "NOT FOUND"
                f.write(f"  [{exists}] {file}\n")

    return backup_file

def preview_cleanup():
    """Preview what will be removed"""

    print("=" * 60)
    print("CLEANUP PREVIEW")
    print("=" * 60)

    total_files = 0
    total_size = 0
    existing_files = []

    for category, files in FILES_TO_REMOVE.items():
        print(f"\n{category}:")
        print("-" * 40)

        category_count = 0
        for file in files:
            file_path = os.path.join('.', file)
            if os.path.exists(file_path):
                try:
                    size = os.path.getsize(file_path)
                    size_kb = size / 1024
                    print(f"  [EXISTS] {file} ({size_kb:.2f} KB)")
                    total_files += 1
                    total_size += size
                    category_count += 1
                    existing_files.append((category, file, file_path, size))
                except Exception as e:
                    print(f"  [ERROR] {file} - Cannot access: {e}")
            else:
                print(f"  [NOT FOUND] {file}")

    print("\n" + "=" * 60)
    print(f"Total files to remove: {total_files}")
    print(f"Total size: {total_size / 1024:.2f} KB ({total_size / (1024*1024):.2f} MB)")
    print("=" * 60)

    return existing_files, total_files, total_size

def remove_files(files_to_remove):
    """Remove the files"""

    print("\n" + "=" * 60)
    print("REMOVING FILES")
    print("=" * 60)

    removed_count = 0
    failed_count = 0
    total_size_removed = 0

    for category, filename, file_path, size in files_to_remove:
        try:
            os.remove(file_path)
            print(f"[OK] Removed: {filename}")
            removed_count += 1
            total_size_removed += size
        except Exception as e:
            print(f"[ERROR] Failed to remove {filename}: {e}")
            failed_count += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files removed: {removed_count}")
    print(f"Files failed: {failed_count}")
    print(f"Space freed: {total_size_removed / 1024:.2f} KB ({total_size_removed / (1024*1024):.2f} MB)")
    print("=" * 60)

    return removed_count, failed_count

def main():
    print("=" * 60)
    print("PROJECT CLEANUP SCRIPT")
    print("=" * 60)
    print("\nThis script will remove temporary and debug files from your project.")
    print("\nCategories to clean:")
    print("  - Test scripts (test_*.py)")
    print("  - Debug scripts (debug_*.py)")
    print("  - Check scripts (check_*.py)")
    print("  - Trace scripts (trace_*.py)")
    print("  - Verify scripts (verify_*.py)")
    print("  - Fake migration scripts (fake_*.py)")
    print("  - Temporary documentation files")
    print("  - Empty/null files")
    print("\nIMPORTANT FILES WILL BE KEPT:")
    print("  - Main documentation (README.md, setup guides, etc.)")
    print("  - Migration reset utilities (backup_database.py, etc.)")
    print("  - Core project files (manage.py, tenant_setup.py, etc.)")

    print("\n" + "=" * 60)

    # Create backup list
    print("\nCreating backup list...")
    backup_file = create_backup_list()
    print(f"[OK] Backup list created: {backup_file}")

    # Preview cleanup
    files_to_remove, total_files, total_size = preview_cleanup()

    if total_files == 0:
        print("\n[INFO] No files to remove. Project is already clean!")
        return

    # Ask for confirmation
    print("\n" + "=" * 60)
    print("Type 'CLEAN PROJECT' to proceed (case-sensitive):")
    print("Or press Ctrl+C to cancel")
    confirmation = input("> ")

    if confirmation != "CLEAN PROJECT":
        print("\n[CANCELLED] Cleanup cancelled.")
        return

    # Remove files
    removed, failed = remove_files(files_to_remove)

    if failed == 0:
        print("\n[SUCCESS] Project cleanup completed successfully!")
        print(f"\nBackup list saved to: {backup_file}")
        print("\nYour project is now cleaner and more organized!")
    else:
        print(f"\n[WARNING] {failed} files failed to remove.")
        print("Please check the errors above.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Cleanup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
