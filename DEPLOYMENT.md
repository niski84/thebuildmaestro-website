# Deployment Guide for VPS

This guide explains how to deploy thebuildmaestro.com to a VPS (Virtual Private Server).

## Overview

The site is a static website generated from Flask templates. The deployment process:
1. Generates static HTML files using Frozen-Flask
2. Copies files to the VPS via rsync
3. Serves files using nginx

## Prerequisites

### Local Machine
- Python 3.7+
- pip
- Node.js and npm (for optional Grunt build)
- rsync
- SSH access to your VPS

### VPS Server
- Ubuntu/Debian or similar Linux distribution
- nginx installed
- SSH access configured
- Domain name pointing to your VPS IP

## Initial VPS Setup

1. **SSH into your VPS:**
   ```bash
   ssh user@your-vps.com
   ```

2. **Run the setup script on the VPS:**
   ```bash
   # Copy the setup script to your VPS first
   scp scripts/setup-vps.sh user@your-vps.com:/tmp/
   ssh user@your-vps.com
   sudo bash /tmp/setup-vps.sh
   ```

   Or manually:
   ```bash
   sudo apt-get update
   sudo apt-get install -y nginx
   sudo mkdir -p /var/www/thebuildmaestro
   sudo chown -R www-data:www-data /var/www/thebuildmaestro
   ```

3. **Configure nginx:**
   ```bash
   # Copy the example configuration
   sudo cp nginx.conf.example /etc/nginx/sites-available/thebuildmaestro.com
   sudo ln -s /etc/nginx/sites-available/thebuildmaestro.com /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **Set up SSL (recommended):**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d thebuildmaestro.com -d www.thebuildmaestro.com
   ```

## Deployment Process

### Quick Deployment

The easiest way to deploy:

```bash
make deploy-full
```

This builds the site and deploys it to your VPS.

### Step-by-Step Deployment

1. **Build the static site:**
   ```bash
   make build
   # or
   ./scripts/build.sh
   ```
   
   This generates static HTML files in the `build/` directory.

2. **Deploy to VPS:**
   ```bash
   make deploy
   # or
   ./scripts/deploy.sh
   ```
   
   Configure the VPS connection by setting environment variables:
   ```bash
   export VPS_HOST="user@your-vps.com"
   export VPS_PATH="/var/www/thebuildmaestro"
   make deploy
   ```

3. **Reload web server:**
   ```bash
   make reload
   # or
   ./scripts/reload.sh
   ```

## Configuration

### Environment Variables

You can configure deployment using environment variables:

```bash
# VPS connection details
export VPS_HOST="user@your-vps.com"
export VPS_PATH="/var/www/thebuildmaestro"
export BUILD_DIR="build"  # Build output directory

# Flask configuration (optional)
export CANONICAL_DOMAIN="https://thebuildmaestro.com"
export FLASK_DEBUG="False"
```

### Makefile Configuration

Edit the `Makefile` to set default values:

```makefile
VPS_HOST ?= user@your-vps.com
VPS_PATH ?= /var/www/thebuildmaestro
BUILD_DIR ?= build
```

## Troubleshooting

### Build fails
- Ensure Python 3.7+ is installed
- Activate virtualenv: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Deployment fails
- Check SSH access: `ssh user@your-vps.com`
- Verify rsync is installed: `which rsync`
- Check VPS_PATH exists and is writable
- Ensure SSH key authentication is set up

### nginx issues
- Test configuration: `sudo nginx -t`
- Check logs: `sudo tail -f /var/log/nginx/error.log`
- Verify permissions: `ls -la /var/www/thebuildmaestro`

### Site not updating
- Clear browser cache
- Check build directory has new files: `ls -la build/`
- Verify deployment completed: Check rsync output
- Reload nginx: `sudo systemctl reload nginx`

## Maintenance

### Updating Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Backup
```bash
# Backup current deployment
ssh user@your-vps.com "tar -czf /tmp/backup-$(date +%Y%m%d).tar.gz /var/www/thebuildmaestro"
scp user@your-vps.com:/tmp/backup-*.tar.gz ./backups/
```

### Monitoring
The site includes a health check endpoint (if running Flask directly):
- Health endpoint: `/health`

For static sites, monitor the nginx logs:
```bash
sudo tail -f /var/log/nginx/thebuildmaestro-access.log
```

## Alternative: Using Git Hooks

You can set up automated deployment using Git post-receive hooks on your VPS:

1. Create a bare repository on VPS:
   ```bash
   git init --bare /opt/thebuildmaestro.git
   ```

2. Create post-receive hook:
   ```bash
   cat > /opt/thebuildmaestro.git/hooks/post-receive << 'EOF'
   #!/bin/bash
   WORK_TREE=/var/www/thebuildmaestro
   git --git-dir=/opt/thebuildmaestro.git --work-tree=$WORK_TREE checkout -f
   cd $WORK_TREE
   source venv/bin/activate
   python freeze.py
   sudo systemctl reload nginx
   EOF
   chmod +x /opt/thebuildmaestro.git/hooks/post-receive
   ```

3. Add remote to local repository:
   ```bash
   git remote add vps user@your-vps.com:/opt/thebuildmaestro.git
   ```

4. Deploy:
   ```bash
   git push vps master
   ```

## Security Considerations

1. **Use SSH keys** instead of passwords
2. **Keep software updated**: `sudo apt-get update && sudo apt-get upgrade`
3. **Use SSL/HTTPS** (Let's Encrypt is free)
4. **Restrict SSH access**: Use firewall rules
5. **Regular backups**: Automate backup process
6. **Monitor logs**: Check for unusual activity

## Support

For issues or questions:
- Check nginx error logs
- Verify file permissions
- Test locally first: `python niski84.py`
- Review deployment script output

