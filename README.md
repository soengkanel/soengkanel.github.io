# NextHR - Multi-Tenant HR Management System

A comprehensive Django-based HR management system with multi-tenant support, featuring employee management, payroll, leave tracking, recruitment, training, and more.

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- **Python 3.10+**
- **PostgreSQL 12+**
- **Git**

### Step 1: Clone & Setup Environment
```bash
git clone <repository-url>
cd NextHR

# Create virtual environment
python -m venv venv

# Activate (choose your OS)
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Database
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
# Required settings:
#   DB_NAME=your_db_name
#   DB_USER=postgres
#   DB_PASSWORD=your_password
#   DB_HOST=localhost
#   DB_PORT=5432
```

**Generate Encryption Key (Required):**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output to ENCRYPTION_KEY in .env
```

### Step 4: Initialize Database & Tenants
```bash
# One command to setup everything!
python tenant_setup.py
```
This creates database, runs migrations, and sets up tenants (KK Company, OSM Company).

### Step 5: Setup Users & Sample Data
```bash
# Create users, roles, and permissions
python manage.py setup_initial_access_control --confirm

# Load master data (zones, buildings, floors, departments)
python master_data.py

# Populate nationalities for each tenant
python manage.py tenant_command populate_nationalities --schema=kk_company
python manage.py tenant_command populate_nationalities --schema=osm_company
```

### Step 6: Run the Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### Step 7: Access the Application
- **KK Company**: http://kk.localhost:8000
- **OSM Company**: http://osm.localhost:8000
- **Admin Panel**: http://localhost:8000/admin

**Default Login:**
- Username: `admin`
- Password: `admin123`

---

## 📝 Optional: Configure Hosts File

Add to your hosts file for custom domains:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac:** `/etc/hosts`

```
127.0.0.1 kk.localhost
127.0.0.1 osm.localhost
```

---

## 📚 Table of Contents

- [Quick Start](#-quick-start-5-minutes)
- [Multi-Tenant Architecture](#-multi-tenant-architecture)
- [Project Modules](#-project-modules)
- [Development Guidelines](#-development-guidelines)
- [Useful Commands](#-useful-commands)
- [Troubleshooting](#-troubleshooting)
- [Production Deployment](#-production-deployment)

---

## 🔐 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Managers | `m1`, `m2` | `manager123` |
| Users | `u1-u15` | `user123` |

⚠️ **Important:** Change these credentials in production!

---

## 🌐 Access URLs

### HTTP (Port 8000)
- **KK Company**: http://kk.localhost:8000
- **OSM Company**: http://osm.localhost:8000
- **Admin Panel**: http://localhost:8000/admin

### HTTPS (Port 8001) - Requires SSL Certificates
- **KK Company**: https://kk.lyp:8001
- **OSM Company**: https://osm.lyp:8001
- **Admin Panel**: https://kk.lyp:8001/admin

---

## 🏢 Multi-Tenant Architecture

This application uses **django-tenants** for multi-tenancy with PostgreSQL schema separation:

| Schema Type | Purpose | Data |
|------------|---------|------|
| **Public Schema** | Shared data | Company/tenant definitions, global users |
| **Tenant Schemas** | Isolated per company | Employees, workers, payroll, attendance, etc. |

Each tenant has its own database schema, ensuring **complete data isolation** between companies.

### Working with Tenants

```bash
# Run command for specific tenant
python manage.py tenant_command <command> --schema=<schema_name>

# Example: Populate nationalities for KK Company
python manage.py tenant_command populate_nationalities --schema=kk_company

# List all tenants
python manage.py list_tenants
```

---

## 📦 Project Modules

### Core HR Modules
| Module | Description |
|--------|-------------|
| **HR** | Employee management, departments, positions, onboarding |
| **Payroll** | Salary processing, components, pay slips, payroll runs |
| **Attendance** | Time tracking, check-in/out, overtime requests |
| **Leave** | Leave types, requests, approvals, balance tracking |
| **Recruitment** | Job postings, applications, candidate pipeline |
| **Performance** | Performance reviews, goals, KPIs, evaluations |
| **Training** | Training programs, courses, enrollments, certifications |

### Operational Modules
| Module | Description |
|--------|-------------|
| **Zone Management** | Worker assignments, zones, buildings, floors |
| **Cards** | ID card printing, batch printing, card history |
| **Document Tracking** | Visa, passport, work permit document tracking |
| **E-Forms** | Digital form builder and submissions |
| **Billing** | Invoicing, payment vouchers, service charges |

### Supporting Modules
| Module | Description |
|--------|-------------|
| **Project** | Project management, tasks, time tracking |
| **Expenses** | Expense claims, approvals, reimbursements |
| **Policies** | Company policies and document management |
| **Audit Management** | Comprehensive audit logging and activity tracking |

---

## 💻 Development Guidelines

### Code Style
- Follow **PEP 8** for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

### Reusable Components
```django
{% include 'components/employee_autocomplete.html' %}
{% include 'components/confirm_modal.html' %}
{% include 'components/delete_modal.html' %}
```

### Database Migrations Workflow
```bash
# 1. After model changes
python manage.py makemigrations

# 2. Apply to public schema
python manage.py migrate

# 3. Apply to all tenants
python manage.py migrate --tenant
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test hr

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🛠️ Useful Commands

### Database & Migrations
```bash
python manage.py makemigrations              # Create migrations
python manage.py migrate                     # Apply to public schema
python manage.py migrate --tenant            # Apply to all tenants
python manage.py showmigrations              # Show migration status
```

### Tenant Management
```bash
python manage.py tenant_command <command> --schema=<schema_name>
python manage.py list_tenants                # List all tenants
python manage.py populate_nationalities      # Populate public schema
```

### User & Access Control
```bash
python manage.py createsuperuser                              # Create superuser
python manage.py setup_initial_access_control --confirm       # Setup roles/permissions
```

### Development
```bash
python manage.py runserver 0.0.0.0:8000      # Start dev server
python manage.py shell                       # Open Django shell
python manage.py check                       # Check for issues
python manage.py collectstatic               # Collect static files
```

---

## 🔍 Troubleshooting

### ❌ Database Connection Errors

**Check PostgreSQL is running:**
```bash
# Linux/Mac
sudo systemctl status postgresql

# Windows - Check Services for PostgreSQL
```

**Test connection:**
```bash
psql -U postgres -h localhost
```

**Fix:** Verify credentials in `.env` file.

---

### ❌ Migration Issues

**Unmade migrations detected:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --tenant
```

**Reset database (⚠️ CAUTION - Deletes ALL data):**
```bash
python tenant_setup.py
```

---

### ❌ Tenant Not Found

**Symptoms:** 404 or tenant not found errors

**Solutions:**
- Verify domain mapping exists in database
- Check hosts file has correct entries
- Ensure `tenant_setup.py` was run successfully

---

### ❌ Missing Nationalities

**Symptoms:** Empty nationality dropdown

**Fix:**
```bash
python manage.py tenant_command populate_nationalities --schema=kk_company
python manage.py tenant_command populate_nationalities --schema=osm_company
```

---

### ❌ Static Files Not Loading

**Fix:**
```bash
python manage.py collectstatic --noinput
```

---

### ❌ Port Already in Use

**Fix:**
```bash
python manage.py runserver 0.0.0.0:8001  # Use different port
```

---

### ❌ UUID to BigInt Migration Error

**Symptoms:** Error: `cannot cast type uuid to bigint`

**This issue has been fixed!** If you encounter it:

```bash
# 1. Fake the problematic migration
python manage.py migrate project 0011 --fake

# 2. Fake additional migrations that may have the same issue
python manage.py migrate project 0012 --fake
python manage.py migrate project 0013 --fake
python manage.py migrate project 0014 --fake

# 3. Run migrations again
python manage.py migrate
```

The fix migration (0015) will handle the UUID to BigInt conversion properly.

---

## 🚀 Production Deployment

### Security Checklist ✅

#### 1. Update `.env` Settings
```env
DEBUG=False
SECRET_KEY=<generate-new-strong-secret-key>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

#### 2. Enable HTTPS
```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### 3. Change Default Passwords
- [ ] Change admin password
- [ ] Change database password
- [ ] Remove or disable default test users

#### 4. Database & Backups
- [ ] Configure PostgreSQL connection pooling
- [ ] Setup automated database backups
- [ ] Test restore procedures

#### 5. Monitoring & Logging
- [ ] Configure logging to files
- [ ] Setup error monitoring (Sentry recommended)
- [ ] Enable performance monitoring

#### 6. Static & Media Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Consider using AWS S3 or CDN for media files
```

### Deploy with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

### Deploy with Docker (Recommended)

```bash
# Build image
docker build -t nexthr:latest .

# Run container
docker run -d -p 8000:8000 --env-file .env nexthr:latest
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 5.2.1 |
| **Database** | PostgreSQL 12+ with django-tenants |
| **Frontend** | Bootstrap 5, HTMX |
| **API** | Django REST Framework |
| **Authentication** | Django Auth + Custom RBAC |
| **Task Queue** | Celery + Redis (optional) |
| **File Storage** | Local / AWS S3 |
| **Server** | Gunicorn + Nginx (production) |

---

## 📞 Support

For issues, bugs, or feature requests:
- Create an issue in the repository
- Contact the development team

---

## 📄 License

[Add your license information here]

---

## 🎉 Quick Reference Card

```bash
# Setup
python tenant_setup.py
python manage.py setup_initial_access_control --confirm
python master_data.py

# Run
python manage.py runserver 0.0.0.0:8000

# Access
http://kk.localhost:8000     # KK Company
http://osm.localhost:8000    # OSM Company
http://localhost:8000/admin  # Admin Panel

# Login
admin / admin123
```

---

**Made with ❤️ for NextHR**