#!/bin/bash
# VPS setup script - initial setup for the VPS server
# Run this script ON THE VPS (not locally)
set -e

echo "Setting up VPS for thebuildmaestro website..."

# Configuration
WEB_ROOT="/var/www/thebuildmaestro"
DOMAIN="thebuildmaestro.com"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Install nginx
if ! command -v nginx &> /dev/null; then
    echo "Installing nginx..."
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y nginx
    elif command -v yum &> /dev/null; then
        yum install -y nginx
    else
        echo "Package manager not found. Please install nginx manually."
        exit 1
    fi
else
    echo "Nginx already installed."
fi

# Create web root directory
echo "Creating web root directory: $WEB_ROOT"
mkdir -p "$WEB_ROOT"
chown -R www-data:www-data "$WEB_ROOT" 2>/dev/null || chown -R nginx:nginx "$WEB_ROOT" 2>/dev/null

# Create nginx configuration
NGINX_CONFIG="/etc/nginx/sites-available/$DOMAIN"
if [ ! -f "$NGINX_CONFIG" ]; then
    echo "Creating nginx configuration..."
    cat > "$NGINX_CONFIG" <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    root $WEB_ROOT;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
EOF

    # Enable the site (Debian/Ubuntu)
    if [ -d "/etc/nginx/sites-enabled" ]; then
        ln -sf "$NGINX_CONFIG" "/etc/nginx/sites-enabled/$DOMAIN"
    fi

    echo "Nginx configuration created at $NGINX_CONFIG"
    echo "Please review and customize it as needed."
else
    echo "Nginx configuration already exists at $NGINX_CONFIG"
fi

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and edit $NGINX_CONFIG if needed"
echo "2. Add SSL certificate (e.g., using certbot: certbot --nginx -d $DOMAIN -d www.$DOMAIN)"
echo "3. Deploy your site using: ./scripts/deploy.sh"
echo "4. Restart nginx: sudo systemctl restart nginx"

