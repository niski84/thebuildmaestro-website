#!/bin/bash
# Reload web server script - reloads nginx after deployment
set -e

# Configuration - can be overridden by environment variables
VPS_HOST="${VPS_HOST:-user@your-vps.com}"

echo "Reloading nginx on $VPS_HOST..."
ssh "$VPS_HOST" "sudo systemctl reload nginx"

echo "Web server reloaded successfully!"

