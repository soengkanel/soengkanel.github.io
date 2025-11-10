#!/bin/bash
# ==============================
# GuanYu Deployment Script
# ==============================

APP_NAME="Guanyu"
DEPLOY_DIR="/var/www"
NEW_DIR="GuanYu-lyp"
BACKUP_NAME="${APP_NAME}_backup_$(date +%F_%H-%M)"

echo "🚀 Starting Deployment for $APP_NAME..."

cd $DEPLOY_DIR || { echo "❌ Failed to enter $DEPLOY_DIR"; exit 1; }

# 1. Backup current code
if [ -d "$APP_NAME" ]; then
    echo "📦 Backing up current $APP_NAME to $BACKUP_NAME"
    mv $APP_NAME $BACKUP_NAME
else
    echo "⚠️ No existing $APP_NAME found, skipping backup."
fi

# 2. Rename new code
if [ -d "$NEW_DIR" ]; then
    echo "📂 Renaming $NEW_DIR → $APP_NAME"
    mv $NEW_DIR $APP_NAME
else
    echo "❌ $NEW_DIR not found. Deployment aborted."
    exit 1
fi

# 3. Restore .env file from backup if exists
if [ -f "$BACKUP_NAME/.env" ]; then
    echo "🔑 Restoring .env file"
    cp $BACKUP_NAME/.env $APP_NAME/.env
else
    echo "⚠️ No .env found in backup. Skipping."
fi

# 4. Copy existing virtual environment (venv)
if [ -d "$BACKUP_NAME/venv" ]; then
    echo "🐍 Copying existing virtual environment"
    cp -r $BACKUP_NAME/venv $APP_NAME/venv
else
    echo "⚠️ No existing venv found. You may need to recreate it."
fi

# 5. Restart service
echo "🔄 Restarting service: $APP_NAME"
sudo systemctl restart guanyu

# 6. Check service status
sudo systemctl status guanyu --no-pager

# 7. Reload nginx
echo "🌐 Checking Nginx configuration..."
sudo nginx -t && sudo systemctl reload nginx

# 8. Tail logs
echo "📜 Tailing logs (Ctrl+C to exit)"
sudo tail -f /var/log/nginx/error.log
