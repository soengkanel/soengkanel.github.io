#!/usr/bin/env python3
"""
Script to compile Django application to .pyc files for source code protection.
This will create a dist/ directory with only compiled bytecode files.
"""

import os
import py_compile
import shutil
import sys
from pathlib import Path
import compileall

def should_exclude_file(file_path, exclude_dirs):
    """Check if file should be excluded from compilation."""
    # Special case: never exclude .env files
    if file_path.name == '.env':
        return False
    
    path_str = str(file_path).replace('\\', '/')
    
    # Skip files in excluded directories (check path components, not substring)
    path_parts = path_str.split('/')
    for exclude_dir in exclude_dirs:
        if exclude_dir in path_parts:
            return True
    
    # Skip files that shouldn't be compiled (but allow .env)
    if file_path.name.startswith('.') and file_path.name != '.env':
        return True
    
    if file_path.suffix in ['.pyc', '.pyo', '.pyd', '__pycache__']:
        return True
        
    return False

def should_copy_non_python(file_path, copy_extensions):
    """Check if non-Python file should be copied."""
    # Always copy .env file
    if file_path.name == '.env':
        return True
    
    # Skip documentation and guideline files
    file_name = file_path.name.lower()
    doc_keywords = [
        'readme', 'changelog', 'guideline', 'guide', 'setup', 
        'manual', 'reference', 'architecture', 'operations',
        'hsts_fix', 'browser_', 'deprecated'
    ]
    
    # Skip if filename contains documentation keywords
    if file_path.suffix.lower() == '.md':
        for keyword in doc_keywords:
            if keyword in file_name:
                return False
    
    # Skip specific documentation files
    skip_files = {
        'readme.md', 'changelog.md', 'deployment_readme.md',
        'https_setup_guideline.md', 'nginx_django_setup.md',
        'http_setup_guideline.md', 'browser_hsts_fix.md'
    }
    
    if file_name in skip_files:
        return False
    
    return file_path.suffix.lower() in copy_extensions

def compile_django_project():
    """Compile entire Django project to .pyc files."""
    
    # Configuration
    source_dir = Path('.')
    dist_dir = Path('dist')
    production_dist = Path('/var/www/GuanYu/dist')
    
    # Directories to exclude from compilation
    exclude_dirs = [
        '__pycache__',
        '.git',
        'venv',
        'env',
        '.venv',
        'node_modules',
        'staticfiles',
        'media',
        'logs',
        'dist',
        '.pytest_cache',
        '.coverage',
        'htmlcov'
    ]
    
    # File extensions to copy (non-Python files that are needed)
    copy_extensions = {
        '.html', '.css', '.js', '.json', '.txt', '.md', '.yml', '.yaml',
        '.xml', '.csv', '.sql', '.png', '.jpg', '.jpeg', '.gif', '.svg',
        '.ico', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.pdf',
        '.xlsx', '.xls', '.docx', '.doc', '.zip', '.tar', '.gz'
    }
    
    # Clean and create dist directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)
    
    print(f"Compiling Django project from {source_dir} to {dist_dir}")
    print("=" * 60)
    
    # Check for .env file in root
    env_file = source_dir / '.env'
    if env_file.exists():
        print(f"[INFO] Found .env file at: {env_file}")
    else:
        print(f"[WARNING] No .env file found at: {env_file}")
    
    compiled_count = 0
    copied_count = 0
    skipped_count = 0
    
    # Walk through all files in source directory
    for root, dirs, files in os.walk(source_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        root_path = Path(root)
        
        # Skip if current directory should be excluded
        if should_exclude_file(root_path, exclude_dirs):
            continue
            
        for file in files:
            source_file = root_path / file
            
            # Calculate relative path from source directory
            try:
                rel_path = source_file.relative_to(source_dir)
            except ValueError:
                continue
                
            # Skip excluded files
            if should_exclude_file(source_file, exclude_dirs):
                skipped_count += 1
                continue
            
            # Create target directory structure
            target_dir = dist_dir / rel_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            
            if source_file.suffix == '.py':
                # Compile Python files to .pyc
                try:
                    target_file = target_dir / (source_file.stem + '.pyc')
                    py_compile.compile(str(source_file), str(target_file), doraise=True)
                    print(f"[OK] Compiled: {rel_path} -> {rel_path.with_suffix('.pyc')}")
                    compiled_count += 1
                except Exception as e:
                    print(f"[FAIL] Failed to compile {rel_path}: {e}")
                    
            elif should_copy_non_python(source_file, copy_extensions):
                # Copy non-Python files that are needed
                target_file = target_dir / source_file.name
                try:
                    shutil.copy2(str(source_file), str(target_file))
                    if source_file.name == '.env':
                        print(f"[COPY] ✓ .env file copied: {rel_path}")
                    else:
                        print(f"[COPY] Copied: {rel_path}")
                    copied_count += 1
                except Exception as e:
                    print(f"[FAIL] Failed to copy {rel_path}: {e}")
            else:
                skipped_count += 1
    
    print("=" * 60)
    print(f"Compilation Summary:")
    print(f"  Python files compiled: {compiled_count}")
    print(f"  Non-Python files copied: {copied_count}")
    print(f"  Files skipped: {skipped_count}")
    
    # Create a startup script for the compiled version
    create_startup_script(dist_dir)
    
    # Copy essential configuration files
    copy_essential_files(source_dir, dist_dir)
    
    print(f"\n✓ Compilation complete! Compiled application available in: {dist_dir.absolute()}")
    
    # Modify .env for production (set DEV_ENV=False)
    modify_env_for_production(dist_dir)
    
    # Copy to production location
    copy_to_production(dist_dir, production_dist)
    
    print(f"\nTo deploy and run the compiled application:")
    print(f"  cd {production_dist}")
    print(f"\n📋 Initial Production Setup (Run ONLY ONCE):")
    print(f"  python run_compiled.py migrate")
    print(f"  python run_compiled.py setup_initial_access_control --confirm")
    print(f"  python run_compiled.py collectstatic --noinput")
    print(f"\n🚀 Start Production Server:")
    print(f"  python run_compiled.py runserver")
    print(f"\n⚠️  IMPORTANT: setup_initial_access_control should only be run ONCE during initial deployment!")

def create_startup_script(dist_dir):
    """Create a startup script for the compiled application."""
    
    startup_script = '''#!/usr/bin/env python3
"""
Startup script for compiled Django application.
This script runs the Django application using only .pyc files.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Run the compiled Django application."""
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "the virtual environment is activated?"
        ) from exc
    
    # Run Django management command
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''
    
    script_path = dist_dir / 'run_compiled.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    print(f"[OK] Created startup script: run_compiled.py")

def copy_essential_files(source_dir, dist_dir):
    """Copy essential configuration and data files."""
    
    essential_files = [
        'requirements.txt',
        'env.example'
    ]
    
    for file_name in essential_files:
        source_file = source_dir / file_name
        if source_file.exists():
            target_file = dist_dir / file_name
            try:
                shutil.copy2(str(source_file), str(target_file))
                print(f"[OK] Copied essential file: {file_name}")
            except Exception as e:
                print(f"[FAIL] Failed to copy {file_name}: {e}")

def modify_env_for_production(dist_dir):
    """Modify .env file for production deployment."""
    env_file = dist_dir / '.env'
    
    if not env_file.exists():
        print(f"[WARNING] No .env file found in dist directory")
        return
    
    print(f"[INFO] Modifying .env for production deployment...")
    
    try:
        # Read the current .env file
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Track if we found and modified settings
        dev_env_found = False
        debug_found = False
        db_name_found = False
        
        # Modify the lines
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Set DEV_ENV=False for production
            if stripped_line.startswith('DEV_ENV=') or stripped_line.startswith('#DEV_ENV='):
                lines[i] = 'DEV_ENV=False\n'
                dev_env_found = True
                print(f"[OK] Set DEV_ENV=False")
            
            # Keep SHOW_ENV_FOOTER=True for production (so footer shows with "Production Environment")
            elif stripped_line.startswith('SHOW_ENV_FOOTER=') or stripped_line.startswith('#SHOW_ENV_FOOTER='):
                lines[i] = 'SHOW_ENV_FOOTER=True\n'
                print(f"[OK] Set SHOW_ENV_FOOTER=True")
            
            # Change database name from UAT to production
            elif stripped_line.startswith('DB_NAME='):
                current_db = stripped_line.split('=', 1)[1]
                if 'uat' in current_db.lower():
                    # Remove _uat suffix for production
                    production_db = current_db.replace('_uat', '').replace('_UAT', '')
                    lines[i] = f'DB_NAME={production_db}\n'
                    db_name_found = True
                    print(f"[OK] Changed DB_NAME from {current_db} to {production_db}")
                else:
                    db_name_found = True
                    print(f"[INFO] DB_NAME already set to: {current_db}")
            
            # Set SETUP_INITIAL_DATA=False for production (prevent re-running initial setup)
            elif stripped_line.startswith('SETUP_INITIAL_DATA='):
                lines[i] = 'SETUP_INITIAL_DATA=False\n'
                print(f"[OK] Set SETUP_INITIAL_DATA=False (production safety)")
            
            # Set DEBUG=False for production
            elif stripped_line.startswith('DEBUG=') and not stripped_line.startswith('#'):
                lines[i] = 'DEBUG=False\n'
                debug_found = True
                print(f"[OK] Set DEBUG=False")
            
            # Set MEDIA_ROOT for production (shared location)
            elif stripped_line.startswith('MEDIA_ROOT='):
                current_media_root = stripped_line.split('=', 1)[1]
                production_media_root = '/var/www/GuanYu/media'
                lines[i] = f'MEDIA_ROOT={production_media_root}\n'
                print(f"[OK] Set shared MEDIA_ROOT to {production_media_root}")
        
        # Add missing settings if not found in file
        if not dev_env_found:
            lines.append('\n# Production Settings\n')
            lines.append('DEV_ENV=False\n')
            lines.append('SHOW_ENV_FOOTER=True\n')
            print(f"[OK] Added DEV_ENV=False and SHOW_ENV_FOOTER=True to .env")
        
        # Write back the modified .env file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"[SUCCESS] ✓ Production .env configured")
        print(f"[INFO] Environment footer will show 'Production Environment'")
        if db_name_found and 'uat' in str(lines).lower():
            print(f"[INFO] Database name changed from UAT to production")
        
    except Exception as e:

        
        pass
        print(f"[ERROR] Failed to modify .env file: {e}")
        print(f"[INFO] Please manually set DEV_ENV=False in the production .env file")

def backup_production_dist(production_dist):
    """Backup existing production dist with timestamp."""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_parent = production_dist.parent / "backup"
    backup_dir = backup_parent / f"dist_backup_{timestamp}"
    
    # Ensure backup directory exists
    backup_parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📂 Backing up existing production dist...")
    print(f"[INFO] Creating backup: {backup_dir}")
    
    try:
        shutil.copytree(str(production_dist), str(backup_dir))
        print(f"[SUCCESS] ✓ Backup created at: {backup_dir}")
        
        # Keep only the last 5 backups
        cleanup_old_backups(backup_parent)
        
    except Exception as e:

        
        pass
        print(f"[WARNING] Failed to create backup: {e}")
        response = input("[PROMPT] Continue without backup? (yes/no): ")
        if response.lower() != 'yes':
            print("[INFO] Deployment cancelled")
            raise KeyboardInterrupt("User cancelled deployment")
    
    return backup_dir

def cleanup_old_backups(backup_dir, keep_count=5):
    """Remove old backup directories, keeping only the most recent ones."""
    try:
        # Find all backup directories in the backup folder
        backup_dirs = sorted([
            d for d in backup_dir.glob("dist_backup_*")
            if d.is_dir()
        ], key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old backups if more than keep_count
        if len(backup_dirs) > keep_count:
            for old_backup in backup_dirs[keep_count:]:
                print(f"[INFO] Removing old backup: {old_backup.name}")
                shutil.rmtree(old_backup)
        
        print(f"[INFO] Keeping {min(len(backup_dirs), keep_count)} most recent backups")
        
    except Exception as e:

        
        pass
        print(f"[WARNING] Failed to cleanup old backups: {e}")

def copy_to_production(source_dist, production_dist):
    """Copy compiled dist to production location."""
    try:
        print(f"\n📦 Copying to production location...")
        print(f"From: {source_dist.absolute()}")
        print(f"To: {production_dist.absolute()}")
        
        # Backup existing production dist if it exists
        if production_dist.exists():
            backup_production_dist(production_dist)
            # Remove the old dist after successful backup
            print(f"[INFO] Removing old production dist...")
            shutil.rmtree(production_dist)
        
        # Create parent directory if it doesn't exist
        production_dist.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy entire dist directory to production location
        shutil.copytree(str(source_dist), str(production_dist))
        
        print(f"[SUCCESS] ✓ Production deployment ready at: {production_dist.absolute()}")
        
        # Restart production service
        restart_production_service()
        
    except PermissionError as e:

        
        pass
        print(f"[ERROR] Permission denied copying to production location: {e}")
        print(f"[INFO] You may need to run with sudo or check directory permissions")
        print(f"[INFO] Manual copy command: sudo cp -r {source_dist} {production_dist.parent}/")
    except Exception as e:
        print(f"[ERROR] Failed to copy to production location: {e}")
        print(f"[INFO] Manual copy command: cp -r {source_dist} {production_dist.parent}/")

def restart_production_service():
    """Restart production Django service."""
    import subprocess
    
    service_name = 'guanyu.service'
    sudo_password = 'admin@2020'
    
    print(f"\n🔄 Restarting production service...")
    
    try:
        # Restart the guanyu service with password
        print(f"[INFO] Running: sudo systemctl restart {service_name}")
        cmd = f'echo "{sudo_password}" | sudo -S systemctl restart {service_name}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"[SUCCESS] ✓ Service '{service_name}' restarted successfully")
            
            # Check service status
            status_cmd = f'echo "{sudo_password}" | sudo -S systemctl is-active {service_name}'
            status_result = subprocess.run(status_cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if status_result.returncode == 0 and status_result.stdout.strip() == 'active':
                print(f"[SUCCESS] ✓ Service '{service_name}' is running")
                return True
            else:
                print(f"[WARNING] Service '{service_name}' may not be running properly")
                print(f"[INFO] Check status manually: sudo systemctl status {service_name}")
                
        else:
            print(f"[ERROR] Failed to restart '{service_name}'")
            if result.stderr:
                print(f"[ERROR] {result.stderr}")
            print(f"[INFO] Try manually: sudo systemctl restart {service_name}")
            
    except subprocess.TimeoutExpired:

            
        pass
        print(f"[WARNING] Timeout restarting service '{service_name}'")
        print(f"[INFO] Service may still be restarting, check manually: sudo systemctl status {service_name}")
    except FileNotFoundError:
        print(f"[ERROR] systemctl not available")
        print(f"[INFO] Restart manually: sudo systemctl restart {service_name}")
    except Exception as e:
        print(f"[ERROR] Error restarting service: {e}")
        print(f"[INFO] Restart manually: sudo systemctl restart {service_name}")
    
    return False

def create_deployment_readme(dist_dir):
    """Create deployment instructions for the compiled application."""
    
    readme_content = '''# Compiled Django Application Deployment

This directory contains the compiled version of your Django application with source code protection.

## Directory Structure
- All Python files have been compiled to .pyc bytecode files
- Static files, templates, and configuration files are included
- Source .py files are NOT included for code protection

## Deployment Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
    pass
venv\\Scripts\\activate
# On Linux/Mac:
    pass
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
1. Copy `env.example` to `.env`
2. Configure your environment variables in `.env`
3. Set up your database connection
4. Configure static file serving if needed

### 3. Database Setup

#### First-Time Production Deployment:
    pass
```bash
# Run migrations
python run_compiled.py migrate

# Set up initial access control (ONLY RUN ONCE)
python run_compiled.py setup_initial_access_control --confirm

# Collect static files
python run_compiled.py collectstatic --noinput

# Create superuser (optional - only if needed)
python run_compiled.py createsuperuser
```

#### Subsequent Deployments:
    pass
```bash
# Only run migrations and collect static files
python run_compiled.py migrate
python run_compiled.py collectstatic --noinput
```

⚠️ **IMPORTANT**: The `setup_initial_access_control` command should ONLY be run during the very first production deployment. Running it again will reset your access control data!

### 4. Running the Application

#### Development Server
```bash
python run_compiled.py runserver
```

#### Production Server
```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 core.wsgi:application

# Or use the compiled manage.py equivalent
python run_compiled.py runserver 0.0.0.0:8000
```

## Important Notes

1. **Source Code Protection**: This compiled version contains only .pyc files, protecting your source code
2. **Python Version**: Ensure the target environment uses the same Python version used for compilation
3. **Dependencies**: All dependencies from requirements.txt must be installed
4. **Environment Variables**: Configure all necessary environment variables
5. **Database**: Set up and configure your database connection
6. **Static Files**: Run collectstatic for production deployment

## Troubleshooting

- If you get import errors, ensure all dependencies are installed
- Check that Python version matches the compilation environment
- Verify all environment variables are properly configured
- Ensure database is accessible and configured correctly

## Security Notes

- .pyc files provide basic source code obfuscation but are not encryption
- For maximum security, consider additional tools like PyArmor for advanced obfuscation
- Protect your deployment environment and access credentials
- Regular security updates for dependencies are still important
'''
    
    readme_path = dist_dir / 'DEPLOYMENT_README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"[OK] Created deployment guide: DEPLOYMENT_README.md")

if __name__ == '__main__':
    try:
        compile_django_project()
        print(f"\n[SUCCESS] Your Django application has been compiled to .pyc files.")
        print(f"[INFO] Check the 'dist' directory for the compiled application.")
        
    except KeyboardInterrupt:

        
        pass
        print(f"\n[WARN] Compilation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error during compilation: {e}")
        sys.exit(1)