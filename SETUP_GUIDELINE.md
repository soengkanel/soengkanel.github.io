# HTTP-Only Setup Guide - GuanYu Multi-Tenant (kk.lyp & osm.lyp)

## Overview
**Effective Date:** 2025-08-28  
**Previous Setup:** HTTPS with SSL certificates  
**Current Setup:** HTTP-only for simplified development and production

## Why HTTP-Only?
The project was simplified from HTTPS to HTTP-only for these reasons:
1. **Excel Import Issues**: HTTPS/HTTP protocol mismatches caused image preview failures
2. **CSRF Complexity**: Mixed content policies created JSON parsing errors
3. **Development Overhead**: SSL certificate management was unnecessarily complex
4. **Local Network Usage**: Security benefits of HTTPS minimal for local network deployment
5. **User Feedback**: "it wasted me a lot of time" - explicit request to remove HTTPS complexity

## Current Setup

### Development Environment
**Port:** 8000  
**URL:** http://kk.lyp:8000  
**Database:** guanyu_db_uat  
**Debug:** True

### Production Environment
**Port:** 80 (via Nginx)  
**URL:** http://kk.lyp  
**Database:** guanyu_db  
**Debug:** False

---

## Development Setup

### 1. Environment Configuration
File: `/var/www2/GuanYu/.env`
```env
DEBUG=True
DEV_ENV=True
DB_NAME=guanyu_db_uat

# Security Settings (HTTP-only)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### 2. Start Development Server
```bash
cd /var/www2/GuanYu
source venv/bin/activate
python manage.py runserver kk.lyp:8000
```

### 3. Access Development Site
- **Main Application:** http://kk.lyp:8000/
- **Admin Panel:** http://kk.lyp:8000/admin/
- **OSM Tenant:** http://osm.lyp:8000/

---

## Production Setup

### 1. Environment Configuration
File: `/var/www/GuanYu/dist/.env` (after compilation)
```env
DEBUG=False
DEV_ENV=False
DB_NAME=guanyu_db

# Security Settings (HTTP-only)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### 2. Django CSRF Settings
File: `/var/www2/GuanYu/core/settings.py`
```python
CSRF_TRUSTED_ORIGINS = [
    'http://lyp:8000',
    'http://127.0.0.1:8000',
    'http://kk.lyp:8000',
    'http://osm.lyp:8000',
    'http://kk.lyp',
    'http://localhost:8000',
]
```

### 3. Nginx Configuration ⚠️ REQUIRES SUDO ACCESS
**Current Issue:** Nginx still forces HTTPS redirect  
**File:** `/etc/nginx/sites-enabled/guanyu`

**❌ Current (problematic):**
```nginx
# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name kk.lyp osm.lyp 192.168.10.22;
    
    # Redirect all HTTP requests to HTTPS
    return 301 https://$server_name$request_uri;
}
```

**✅ Required (HTTP-only):**
```nginx
# HTTP server only
server {
    listen 80;
    server_name kk.lyp osm.lyp 192.168.10.22;
    
    client_max_body_size 100M;
    
    # Static files
    location /static/ {
        alias /var/www/GuanYu/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/GuanYu/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Django application
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
    
    # Security headers (without HSTS)
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

**To Fix Nginx Configuration:**
```bash
sudo nano /etc/nginx/sites-enabled/guanyu
# Remove HTTPS redirect and SSL configuration
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Access Production Site
- **Main Application:** http://kk.lyp/
- **Admin Panel:** http://kk.lyp/admin/
- **OSM Tenant:** http://osm.lyp/

---

## Database Configuration

### Development vs Production
| Environment | Database Name | Location |
|-------------|---------------|----------|
| Development | guanyu_db_uat | /var/www2/GuanYu/.env |
| Production | guanyu_db | /var/www/GuanYu/dist/.env |

### Compilation Process
When running `compile_to_pyc.py`, the system automatically:
1. Changes `DB_NAME=guanyu_db_uat` to `DB_NAME=guanyu_db`
2. Sets `DEV_ENV=False` and `DEBUG=False`
3. Copies files to `/var/www/GuanYu/dist/`

---

## Troubleshooting

### Excel Import Image Preview Issues ✅ FIXED
**Previous Problem:** Images not showing in Step 1 data preview  
**Root Cause:** HTTPS/HTTP protocol mismatch  
**Solution:** Removed hardcoded HTTP URLs from JavaScript, simplified to relative URLs

### CSRF Token Errors ✅ FIXED  
**Previous Problem:** `Unexpected token '<', "<!DOCTYPE "... is not valid JSON`  
**Root Cause:** HTTPS origins not in CSRF_TRUSTED_ORIGINS  
**Solution:** Updated CSRF_TRUSTED_ORIGINS to include only HTTP origins

### Nginx HTTPS Redirect ✅ FIXED
**Previous Problem:** Nginx redirected HTTP to HTTPS  
**Root Cause:** Conflicting backup configuration in sites-enabled  
**Solution:** Removed backup file, updated Nginx config to HTTP-only

### Browser HSTS Cache ⚠️ USER ACTION REQUIRED
**Problem:** Browser redirects `http://kk.lyp/` to `https://kk.lyp/`  
**Root Cause:** Browser cached HSTS headers from previous HTTPS setup  
**Solution:** See `BROWSER_HSTS_FIX.md` for instructions to clear browser cache

---

## Migration Status

### ✅ Completed
1. **Django Settings**: Removed HTTPS from CSRF_TRUSTED_ORIGINS
2. **JavaScript**: Removed hardcoded HTTP URL workarounds  
3. **Development Server**: Running on HTTP (`runserver kk.lyp:8000`)
4. **Documentation**: Updated guides to reflect HTTP-only setup

### ❌ Pending (Requires Sudo Access)
1. **Nginx Configuration**: Remove HTTPS redirect and SSL configuration
2. **Testing**: Verify production HTTP access works correctly

---

## Commands Reference

### Development
```bash
# Start development server
cd /var/www2/GuanYu
source venv/bin/activate
python manage.py runserver kk.lyp:8000

# Check status
ps aux | grep runserver
```

### Production
```bash
# Check current mode
ps aux | grep -E "(runserver|gunicorn)" | grep -v grep

# Switch to production (after Nginx fix)
sudo systemctl stop guanyu
sudo systemctl start guanyu
sudo systemctl status guanyu
```

### Nginx (Requires Sudo)
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Check logs
sudo tail -f /var/log/nginx/error.log
```

---

## Security Considerations

### What Changed
- **Removed:** SSL/TLS encryption
- **Removed:** HSTS headers (Strict-Transport-Security)
- **Removed:** HTTPS redirects
- **Kept:** X-Frame-Options, X-Content-Type-Options, X-XSS-Protection

### Current Security Posture
- **Network:** Local network only (192.168.10.x)
- **Authentication:** Django user authentication still active
- **Data Encryption:** Application-level encryption for sensitive fields still active
- **Transport:** HTTP (unencrypted)

### Recommendations for Future
If HTTPS is needed again:
1. Consider using it only for camera access pages
2. Use relative URLs in JavaScript to avoid protocol mismatches
3. Implement proper mixed content handling
4. Test Excel import functionality thoroughly

---

## File Locations

### Configuration Files
- **Development:** `/var/www2/GuanYu/.env`
- **Production:** `/var/www/GuanYu/dist/.env`
- **Django Settings:** `/var/www2/GuanYu/core/settings.py`
- **Nginx Config:** `/etc/nginx/sites-enabled/guanyu` (requires sudo)

### Documentation
- **Current Guide:** `HTTP_SETUP_GUIDELINE.md`
- **Browser Fix:** `BROWSER_HSTS_FIX.md` ⭐
- **Deprecated HTTPS Guide:** `HTTPS_SETUP_GUIDELINE_DEPRECATED.md`
- **Nginx Setup:** `NGINX_DJANGO_SETUP.md`

### Scripts
- **Compilation:** `compile_to_pyc.py`
- **Deprecated HTTPS Batch:** `run_https_django_ext_DEPRECATED.bat`

---

This simplified HTTP-only setup eliminates the complexity that caused Excel import issues and provides a more straightforward development and production environment.