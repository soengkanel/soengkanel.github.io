#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tenant Setup Script for GuanYu Multi-Tenant Django Application

This script handles:
    pass
1. Database reset
2. Django migrations
3. KK and OSM tenant setup
4. Django superuser creation

Usage:
    python tenant_setup.py [--skip-db-reset] [--skip-confirm]
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import argparse

# Set console encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')


class TenantSetupManager:
    def __init__(self):
        self.load_env_config()
        
    def load_env_config(self):
        """Load database configuration from .env file"""
        if not os.path.exists('.env'):
            self.error("ERROR: .env file not found!")
            sys.exit(1)
            
        load_dotenv()
        
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'guanyu')
        }
        
        self.info("Database Configuration:")
        self.info(f"   Host: {self.db_config['host']}:{self.db_config['port']}")
        self.info(f"   Database: {self.db_config['database']}")
        self.info(f"   User: {self.db_config['user']}")
        print()

    def info(self, message):
        """Print info message"""
        print(f"[INFO] {message}")
        
    def warning(self, message):
        """Print warning message"""
        print(f"[WARNING] {message}")
        
    def error(self, message):
        """Print error message"""
        print(f"[ERROR] {message}")
        
    def success(self, message):
        """Print success message"""
        print(f"[SUCCESS] {message}")

    def run_command(self, command, description, check=True):
        """Run a shell command with error handling"""
        self.info(f"{description}...")
        try:
            if isinstance(command, str):
                result = subprocess.run(command, shell=True, check=check, 
                                      capture_output=True, text=True, encoding='utf-8')
            else:
                result = subprocess.run(command, check=check, 
                                      capture_output=True, text=True, encoding='utf-8')
            
            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(result.stderr)
                
            return result
        except subprocess.CalledProcessError as e:
            self.error(f"Failed to {description.lower()}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return None
        except Exception as e:
            self.error(f"Command execution error: {str(e)}")
            return None

    def check_required_files(self):
        """Check if all required files exist"""
        self.info("Checking required files...")
        
        required_files = [
            'manage.py',
            'requirements.txt',
            '.env'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            self.error(f"Missing required files: {', '.join(missing_files)}")
            self.info("Make sure you're running this script from the Django project root directory")
            return False
        
        self.success("All required files found")
        return True

    def check_django_installation(self):
        """Check if Django is properly installed"""
        self.info("Checking Django installation...")
        try:
            result = subprocess.run([sys.executable, '-c', 'import django; print(django.get_version())'], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                self.success(f"Django {result.stdout.strip()} is installed")
                return True
            else:
                self.error("Django is not installed or not accessible")
                self.info("Please run: python setup_requirements.py first")
                return False
        except Exception as e:
            self.error(f"Error checking Django installation: {e}")
            return False



    def test_database_connection(self):
        """Test database connection before proceeding"""
        self.info("Testing database connection...")
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database='postgres',
                connect_timeout=5
            )
            conn.close()
            self.success("Database connection successful")
            return True
        except psycopg2.Error as e:
            self.error(f"Database connection failed: {e}")
            self.info("Please check:")
            self.info("  1. PostgreSQL is running")
            self.info("  2. Database credentials in .env file are correct")
            self.info("  3. Database server is accessible")
            return False

    def reset_database(self, skip_confirm=False):
        """Drop and recreate the database"""
        self.info("Step 1: Database Reset...")
        
        # Test database connection
        if not self.test_database_connection():
            return False
        
        if not skip_confirm:
            self.warning("WARNING: This will delete all existing data!")
            confirm = input("Are you sure you want to continue? (y/N): ").strip().lower()
            if confirm != 'y':
                self.info("Setup cancelled by user")
                return False

        try:
            # Connect to PostgreSQL server (not to the specific database)
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database='postgres'  # Connect to default postgres database
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Terminate all connections to the target database
            self.info(f"Terminating active connections to '{self.db_config['database']}'...")
            cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{self.db_config['database']}'
                  AND pid <> pg_backend_pid()
            """)
            
            # Drop database if it exists
            self.info(f"Dropping database '{self.db_config['database']}'...")
            cursor.execute(f"DROP DATABASE IF EXISTS {self.db_config['database']}")
            
            # Create new database
            self.info(f"Creating database '{self.db_config['database']}'...")
            cursor.execute(f"CREATE DATABASE {self.db_config['database']}")
            
            cursor.close()
            conn.close()
            
            self.success("Database reset completed successfully!")
            return True
            
        except psycopg2.Error as e:

            
            pass
            self.error(f"Database reset failed: {e}")
            if "does not exist" in str(e):
                self.info("Database doesn't exist, will be created during migrations")
                return True
            return False

    def run_migrations(self):
        """Run Django migrations"""
        self.info("Step 2: Running migrations...")
        
        # Check if manage.py exists
        if not os.path.exists('manage.py'):
            self.error("manage.py file not found! Make sure you're in the Django project root.")
            return False
        
        # Run initial migrations
        result = self.run_command([sys.executable, 'manage.py', 'migrate'], "Run initial migrations")
        if result is None or result.returncode != 0:
            return False
            
        # Run tenant migrations
        result = self.run_command([sys.executable, 'manage.py', 'migrate', '--tenant'], "Run tenant migrations")
        if result is None or result.returncode != 0:
            return False
            
        self.success("Migrations completed successfully!")
        return True

    def create_superuser(self):
        """Create Django superuser"""
        self.info("Step 3: Creating Django superuser...")
        
        # Create superuser with predefined credentials
        result = self.run_command([
            sys.executable, 'manage.py', 'shell', '-c',
            """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@ngt.com.kh', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
"""
        ], "Create Django superuser")
        
        if result is None or result.returncode != 0:
            self.warning("Superuser creation failed, but continuing...")
            return True  # Don't fail the entire setup for this
            
        self.success("Django superuser created successfully!")
        return True

    def setup_tenants(self):
        """Setup KK and OSM tenant companies"""
        self.info("Step 4: Setting up tenants...")
        
        # Setup KK Company
        self.info("Setting up KK Company...")
        result = self.run_command([
            sys.executable, 'manage.py', 'tenant_setup',
            '--company-name', 'KK Company',
            '--company-domain', 'kk.lyp'
        ], "Setup KK Company tenant")
        
        if result is None or result.returncode != 0:
            return False
        
        # Setup OSM Company
        self.info("Setting up OSM Company...")
        result = self.run_command([
            sys.executable, 'manage.py', 'tenant_setup',
            '--company-name', 'OSM Company', 
            '--company-domain', 'osm.lyp',
            '--skip-admin'
        ], "Setup OSM Company tenant")
        
        if result is None or result.returncode != 0:
            return False
            
        self.success("Tenants setup completed successfully!")
        return True



    def show_final_status(self):
        """Show final setup status and access information"""
        print("\n" + "="*60)
        self.success("TENANT SETUP COMPLETE!")
        print("="*60)
        
        self.info("\nAccess URLs:")
        self.info("  - Main Admin: http://localhost:8000/admin")
        self.info("  - KK Company: http://kk.lyp:8000")
        self.info("  - OSM Company: http://osm.lyp:8000")
        
        self.info("\nDefault Login Credentials:")
        self.info("  - Username: admin")
        self.info("  - Password: admin123")
        
        self.info("\nNext Steps:")
        self.info("  1. Run: python generate_access_control.py (create users)")
        self.info("  2. Run: python quick_demo.py (generate demo data)")
        self.info("  3. Start your development server: python manage.py runserver")
        self.info("  4. Add domain entries to your hosts file if needed:")
        self.info("     127.0.0.1 localhost")
        self.info("     127.0.0.1 kk.lyp") 
        self.info("     127.0.0.1 osm.lyp")
        self.info("  5. Access the admin interfaces using the URLs above")
        
        print("\n" + "="*60)
        self.success("Your multi-tenant app is ready to use!")
        print()

    def run_setup(self, skip_db_reset=False, skip_confirm=False):
        """Run the tenant setup process"""
        self.success("Starting Tenant Setup")
        print("="*60)
        print()
        
        try:
            # Pre-flight checks
            if not self.check_required_files():
                return False
            print()
            
            # Check Django installation
            if not self.check_django_installation():
                return False
            print()
            
            # Step 1: Reset database
            if not skip_db_reset:
                if not self.reset_database(skip_confirm):
                    return False
                print()
            else:
                self.info("Step 1: Skipping database reset")
                print()
            
            # Step 2: Run migrations
            if not self.run_migrations():
                return False
            print()
            
            # Step 3: Create superuser
            if not self.create_superuser():
                return False
            print()
            
            # Step 4: Setup tenants
            if not self.setup_tenants():
                return False
            print()
            

            
            # Show final status
            self.show_final_status()
            return True
            
        except KeyboardInterrupt:

            
            pass
            self.warning("\n\nSetup interrupted by user")
            return False
        except Exception as e:
            self.error(f"\n\nSetup failed with error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Tenant setup for GuanYu')
    parser.add_argument('--skip-db-reset', action='store_true',
                       help='Skip database reset (drop/create)')
    parser.add_argument('--skip-confirm', action='store_true',
                       help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    setup_manager = TenantSetupManager()
    success = setup_manager.run_setup(
        skip_db_reset=args.skip_db_reset, 
        skip_confirm=args.skip_confirm
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()