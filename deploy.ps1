# ==============================
# Windows One-Click Deployment for GuanYu
# ==============================

# Local and remote paths
$localPath = "C:\Deployment\GuanYu-lyp"
$remoteUser = "administrator"
$remoteHost = "10.10.4.11"
$remotePath = "/var/www/GuanYu"

Write-Output "🔄 Step 1: Git Pull (Local)"
cd $localPath
git pull

Write-Output "📦 Step 2: Uploading to Server..."
scp -r $localPath ${remoteUser}@${remoteHost}:${remotePath}

Write-Output "🚀 Step 3: Running deploy.sh on Server..."
ssh ${remoteUser}@${remoteHost} "cd /var/www/GuanYu && ./deploy.sh"

Write-Output "✅ Deployment completed!"
