# Production + Nginx Setup Guide

Complete guide for hosting Django applications with Nginx reverse proxy.

## Quick Reference

### Check Current Mode
```bash
ps aux | grep -E "(runserver|gunicorn)" | grep -v grep
```
- See `runserver` = **Development Mode** 📘
- See `gunicorn` = **Production Mode** 📗

### Switch Modes
**To Production:**
```bash
sudo pkill -f runserver
sudo systemctl daemon-reload
sudo systemctl start guanyu
```

**To Development:**
```bash
sudo systemctl stop guanyu
screen -dmS django bash -c "cd /var/www/GuanYu && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"
```

---

## Architecture Overview

```
Browser → Nginx (port 80) → Django Server (port 8000)
```

- **Nginx**: Serves static/media files, handles HTTP requests
- **Django**: Handles application logic and dynamic content
- **External Storage**: 8.5TB drive for media files

---

## Prerequisites

- Ubuntu Server with sudo access
- Python 3.x installed
- Django project ready

---

## Development Setup

### 1. Install Required Packages

```bash
sudo apt update
sudo apt install -y nginx python3-venv python3-pip
```

### 2. Setup Django Environment

```bash
cd /var/www/GuanYu
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Django Settings

Update `core/settings.py`:
```python
# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = '/mnt/storage/guanyu-media'  # External storage

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### 4. Prepare Media Storage

```bash
# Create media directory on external storage
sudo mkdir -p /mnt/storage/guanyu-media/
sudo chown administrator:www-data /mnt/storage/guanyu-media
sudo chmod 755 /mnt/storage/guanyu-media

# Copy existing media files
cp -r media/* /mnt/storage/guanyu-media
```

### 5. Configure Nginx for Development (HTTP-Only)

Create `/etc/nginx/sites-available/guanyu`:
```nginx
# HTTP-only server (HTTPS removed as of 2025-08-28)
server {
    listen 80;
    server_name kk.lyp osm.lyp 192.168.10.22;
    
    client_max_body_size 100M;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Static files
    location /static/ {
        alias /var/www/GuanYu/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files (using shared directory)
    location /media/ {
        alias /var/www/GuanYu/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Proxy to Django development server
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Security headers (removed HSTS for HTTP-only setup)
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### 6. Enable Nginx Configuration

```bash
# Enable site
sudo ln -sf /etc/nginx/sites-available/guanyu /etc/nginx/sites-enabled/guanyu

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart services
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 7. Start Django Development Server

```bash
cd /var/www/GuanYu
source venv/bin/activate
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

**For background operation:**
```bash
screen -S django
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
# Press Ctrl+A, then D to detach
```

---

## Production Setup

### 1. Install Gunicorn

```bash
source venv/bin/activate
pip install gunicorn
```

### 2. Create Gunicorn Configuration

Create `/var/www/GuanYu/gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 60
keepalive = 5
preload_app = True
user = "administrator"
group = "administrator"
```

### 3. Create Systemd Service

Create `/etc/systemd/system/guanyu.service`:
```ini
[Unit]
Description=GuanYu Django Application
After=network.target
Wants=network.target

[Service]
Type=exec
User=administrator
Group=administrator
WorkingDirectory=/var/www/GuanYu
Environment="PATH=/var/www/GuanYu/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=core.settings"  # ⚠️ IMPORTANT: Must use core.settings, NOT simple_settings
ExecStart=/var/www/GuanYu/venv/bin/gunicorn core.wsgi:application --config /var/www/GuanYu/gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=append:/var/www/GuanYu/logs/gunicorn.log
StandardError=append:/var/www/GuanYu/logs/gunicorn-error.log

[Install]
WantedBy=multi-user.target
```

### 4. Update Nginx for Production (HTTP-Only)

Update `/etc/nginx/sites-available/guanyu`:
```nginx
# HTTP-only production server (HTTPS removed as of 2025-08-28)
server {
    listen 80;
    server_name kk.lyp osm.lyp 192.168.10.22;
    
    client_max_body_size 100M;
    
    # Security headers (removed HSTS for HTTP-only setup)
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
    
    # Static files
    location /static/ {
        alias /var/www/GuanYu/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files (using shared directory)
    location /media/ {
        alias /mnt/storage/guanyu-media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
}
```

### 5. Start Production Services

```bash
# Create logs directory
mkdir -p /var/www/GuanYu/logs

# Reload systemd
sudo systemctl daemon-reload

# Start and enable Gunicorn
sudo systemctl enable guanyu
sudo systemctl start guanyu

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status guanyu
sudo systemctl status nginx
```

---

## Network Configuration

### Hosts File Configuration

**Server (`/etc/hosts`):**
```
192.168.10.22 lyp
192.168.10.22 kk.lyp
192.168.10.22 osm.lyp
```

**Client machines:**
- **Windows:** `C:\Windows\System32\drivers\etc\hosts`
- **Linux/Mac:** `/etc/hosts`

Add:
```
192.168.10.22 kk.lyp
192.168.10.22 osm.lyp
```

---

## File Permissions for Media Storage

### Fix Permissions Script

```bash
#!/bin/bash
# Fix media permissions for nginx access
sudo chmod -R 755 /mnt/storage/guanyu-media
sudo chown -R administrator:www-data /mnt/storage/guanyu-media/
sudo chmod 755 /mnt/storage/guanyu-media/
sudo chmod 755 /mnt/storage/
```

### For Excel Import Issues

```bash
# Fix permissions after each import
sudo find /mnt/storage/guanyu-media/guanyu-media/worker_import_images/ -type d -exec chmod 755 {} \;
sudo find /mnt/storage/guanyu-media/guanyu-media/worker_import_images/ -type f -exec chmod 644 {} \;
sudo chown -R administrator:www-data /mnt/storage/guanyu-media/worker_import_images/
```

### Worker Import Permission Issues

**Problem:** Worker photos and documents fail to save during import with permission errors.

**Root Cause:** The `worker_photos/` and `worker_documents/` directories may be owned by `root` instead of the application user, causing Django's encrypted file saving to fail.

**Solution:**
```bash
# Check current permissions
ls -la /media/administrator/Storage/guanyu-media/

# Fix ownership and permissions for worker directories
sudo chown -R administrator:www-data /mnt/storage/guanyu-media/guanyu-media/worker_photos/
sudo chown -R administrator:www-data /mnt/storage/guanyu-media/guanyu-media/worker_documents/
sudo chmod -R 775 /mnt/storage/guanyu-media/guanyu-media/worker_photos/
sudo chmod -R 775 /mnt/storage/guanyu-media/guanyu-media/worker_documents/
```

**Technical Details:**
- Worker photos saved to: `worker_photos/photo_*.enc` (EncryptedImageField)
- Worker documents saved to: `worker_documents/passport_*.enc` (EncryptedFileField)
- Files are encrypted using FileEncryptionHandler before storage
- Django save process: `zone/views.py:6526` (photos), `zone/views.py:6447` (documents)

---

## Access URLs (HTTP-Only as of 2025-08-28)

### Development
- **Main:** http://192.168.10.22/ or http://kk.lyp:8000/
- **Subdomains:** http://kk.lyp:8000/, http://osm.lyp:8000/
- **Admin:** http://kk.lyp:8000/admin/

### Production
- **Main:** http://kk.lyp/ (port 80 via Nginx)
- **Subdomains:** http://osm.lyp/
- **Admin:** http://kk.lyp/admin/

**Note:** All HTTPS URLs have been deprecated. If you encounter HTTPS redirects, the Nginx configuration needs to be updated to remove SSL settings.

---

## Troubleshooting

### Common Issues

**1. Apache2 Conflicts:**
```bash
sudo systemctl stop apache2
sudo systemctl disable apache2
sudo systemctl restart nginx
```

**2. Permission Issues:**
```bash
# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Fix media permissions
sudo chmod -R 755 /mnt/storage/guanyu-media/guanyu-media/
sudo chown -R administrator:www-data /mnt/storage/guanyu-media/
```

**3. Django Server Issues:**
```bash
# Check if Django is running
curl http://localhost:8000

# Restart Django (development)
pkill -f runserver
python manage.py runserver 0.0.0.0:8000

# Restart Gunicorn (production)
sudo systemctl restart guanyu
```

**4. Static Files Not Loading:**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

**5. Worker Import Permission Errors:**
```bash
# Error: [Errno 13] Permission denied: '/media/.../worker_photos/photo_*.enc'
# Error: [Errno 13] Permission denied: '/media/.../worker_documents/passport_*.enc'

# Fix worker photo/document directory permissions:
sudo chown -R administrator:www-data /mnt/storage/guanyu-media//worker_photos/
sudo chown -R administrator:www-data /mnt/storage/guanyu-media/worker_documents/
sudo chmod -R 775 /mnt/storage/guanyu-media/worker_photos/
sudo chmod -R 775 /mnt/storage/guanyu-media/worker_documents/
```

### Service Status Commands

```bash
# Check services
sudo systemctl status nginx
sudo systemctl status guanyu  # Production only
ps aux | grep runserver       # Development only

# View logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u guanyu -f  # Production only
```

### Port Usage Check

```bash
sudo netstat -tlnp | grep -E ':80|:8000'
ss -tlnp | grep -E ':80|:8000'
```

---

## How to Check Current Mode

### Quick Check (One Command)

```bash
# See which mode is active
ps aux | grep -E "(runserver|gunicorn)" | grep -v grep
```

**What You'll See:**

| Mode | You'll See | Key Word |
|------|------------|----------|
| **Development** | `python manage.py runserver 0.0.0.0:8000` | `runserver` |
| **Production** | `gunicorn core.wsgi:application` | `gunicorn` |
| **Nothing Running** | (no output) | - |

### Detailed Status Check

```bash
# For Development Mode
ps aux | grep runserver

# For Production Mode  
sudo systemctl status guanyu
```

### Quick Status Script

```bash
# Create this helper script
cat > check_mode.sh << 'EOF'
#!/bin/bash
if ps aux | grep -q "[r]unserver"; then
    echo "✅ DEVELOPMENT MODE (runserver)"
elif ps aux | grep -q "[g]unicorn"; then
    echo "✅ PRODUCTION MODE (gunicorn)"
else
    echo "❌ NO SERVER RUNNING"
fi
EOF
chmod +x check_mode.sh
./check_mode.sh
```

---

## Switching Between Modes

### Switch to Production Mode

**Direct Commands (Run These):**
```bash
# 1. Stop development server
sudo pkill -f "python manage.py runserver"

# 2. Create logs directory
mkdir -p /var/www/GuanYu/logs

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Start Gunicorn
sudo systemctl start guanyu
sudo systemctl enable guanyu

# 5. Verify it's running
sudo systemctl status guanyu
```

### Switch to Development Mode

**Direct Commands (Run These):**
```bash
# 1. Stop Gunicorn
sudo systemctl stop guanyu
sudo systemctl disable guanyu

# 2. Start development server (choose one):

# Option A: In terminal (stays open)
cd /var/www/GuanYu
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Option B: In background (recommended)
screen -dmS django bash -c "cd /var/www/GuanYu && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"

# 3. Verify it's running
ps aux | grep runserver
```

### Common Issues When Switching

**Line Ending Error (Windows → Linux):**
```bash
# If you see: '\r': command not found
sed -i 's/\r$//' your_script.sh
```

**Permission Denied:**
```bash
# Always use sudo for systemctl
sudo systemctl start guanyu
```

**Service Not Found:**
```bash
# Reload systemd first
sudo systemctl daemon-reload
```

---

## Key Differences: Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| **Django Server** | `runserver 0.0.0.0:8000` | Gunicorn + systemd |
| **Process Management** | Manual/Screen | Systemd service |
| **Restart Method** | `Ctrl+C` + restart | `systemctl restart guanyu` |
| **Logs** | Terminal output | `/var/www/GuanYu/logs/` |
| **Performance** | Single-threaded | Multi-worker |
| **Security** | Basic | Enhanced headers |
| **Auto-start** | Manual | Systemd auto-start |
| **Monitoring** | Manual | Systemd + logs |
| **Code Changes** | Auto-reload | Requires restart |
| **Direct Access** | http://localhost:8000 | Only through Nginx |

---

## Storage Structure

```
/var/www/GuanYu/                    # Django project
├── core/                           # Django app
├── static/                         # Source static files
├── staticfiles/                    # Collected static files (Nginx serves)
├── venv/                          # Virtual environment
├── logs/                          # Application logs (production)
└── requirements.txt

/media/administrator/Storage/guanyu-media/  # External storage (8.5TB)
├── company_logos/                  # Company assets
├── worker_import_images/           # Excel import images
└── [other_media_files]/           # User uploads
```

---

## Security Notes

- Media files are served directly by Nginx (not Django)
- External storage mounted at `/mnt/storage/`
- Proper file permissions prevent unauthorized access
- Security headers protect against common attacks
- Production uses Gunicorn instead of Django dev server

---

This guide covers both development (Django runserver) and production (Gunicorn) setups with external storage for optimal performance and storage capacity.