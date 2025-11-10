"""
Remove all migration files except __init__.py

WARNING: This will delete all migration files!
Make sure you have backed up your database first!
"""
import os
import sys

def find_migration_files():
    """Find all migration files in the project"""

    migration_files = []
    apps_to_process = []

    # Walk through the project directory
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and hidden directories
        if 'venv' in root or 'env' in root or '\\.git' in root or '__pycache__' in root:
            continue

        # Check if this is a migrations directory
        if root.endswith('migrations'):
            app_name = os.path.basename(os.path.dirname(root))
            apps_to_process.append(app_name)

            print(f"\nFound migrations in app: {app_name}")
            print(f"  Directory: {root}")

            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(root, file)
                    migration_files.append(file_path)
                    print(f"    - {file}")

    return migration_files, apps_to_process

def remove_migration_files(migration_files):
    """Remove migration files"""

    print("\n" + "=" * 60)
    print("REMOVING MIGRATION FILES")
    print("=" * 60)

    removed_count = 0
    failed_count = 0

    for file_path in migration_files:
        try:
            os.remove(file_path)
            print(f"[OK] Removed: {file_path}")
            removed_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to remove {file_path}: {e}")
            failed_count += 1

    print("\n" + "=" * 60)
    print(f"Summary: {removed_count} files removed, {failed_count} files failed")
    print("=" * 60)

    return removed_count, failed_count

def main():
    print("=" * 60)
    print("MIGRATION FILES REMOVAL SCRIPT")
    print("=" * 60)
    print("\nWARNING: This script will delete ALL migration files!")
    print("         (except __init__.py files)")
    print("\nBefore proceeding, make sure you have:")
    print("  1. Backed up your database (run backup_database.py)")
    print("  2. Committed your current code to git")
    print("  3. Understand that this cannot be easily undone")

    print("\n" + "=" * 60)

    # Find all migration files
    migration_files, apps = find_migration_files()

    if not migration_files:
        print("\n[INFO] No migration files found!")
        return

    print("\n" + "=" * 60)
    print(f"Found {len(migration_files)} migration files across {len(apps)} apps")
    print("=" * 60)

    # Ask for confirmation
    print("\nType 'DELETE ALL MIGRATIONS' to proceed (case-sensitive):")
    confirmation = input("> ")

    if confirmation != "DELETE ALL MIGRATIONS":
        print("\n[CANCELLED] Migration removal cancelled.")
        return

    # Remove files
    removed, failed = remove_migration_files(migration_files)

    if failed == 0:
        print("\n[SUCCESS] All migration files removed successfully!")
        print("\nNext steps:")
        print("  1. Run: python clean_migration_history.py")
        print("  2. Run: python regenerate_migrations.py")
    else:
        print(f"\n[WARNING] {failed} files failed to remove. Please check the errors above.")

if __name__ == '__main__':
    main()
