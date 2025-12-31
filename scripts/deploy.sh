#!/bin/bash
# Deployment script - deploys built site to VPS via rsync
set -e

# Configuration - can be overridden by environment variables
VPS_HOST="${VPS_HOST:-user@your-vps.com}"
VPS_PATH="${VPS_PATH:-/var/www/thebuildmaestro}"
BUILD_DIR="${BUILD_DIR:-build}"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if build directory exists
if [ ! -d "$BUILD_DIR" ]; then
    echo "Error: Build directory '$BUILD_DIR' not found."
    echo "Please run './scripts/build.sh' first."
    exit 1
fi

# Check if build directory has content
if [ ! -f "$BUILD_DIR/index.html" ]; then
    echo "Error: Build directory appears empty (no index.html found)."
    echo "Please run './scripts/build.sh' first."
    exit 1
fi

echo "Deploying to $VPS_HOST:$VPS_PATH..."
rsync -avz --delete "$BUILD_DIR/" "$VPS_HOST:$VPS_PATH/"

echo "Deployment complete!"
echo "Run './scripts/reload.sh' to reload the web server."

