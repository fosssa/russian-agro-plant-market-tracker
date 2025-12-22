#!/bin/sh

# ============================================
# Entrypoint Script for Frontend Container
# ============================================
# This script:
# 1. Generates htpasswd file from environment variables
# 2. Validates nginx configuration
# 3. Starts nginx in foreground mode
# ============================================

set -e

echo "Starting frontend container entrypoint..."

# ============================================
# Generate htpasswd file for Basic Authentication
# ============================================

if [ -z "$BASIC_AUTH_USER" ] || [ -z "$BASIC_AUTH_PASSWORD" ]; then
    echo "WARNING: BASIC_AUTH_USER or BASIC_AUTH_PASSWORD not set!"
    echo "Creating default credentials: admin / changeme"
    BASIC_AUTH_USER="${BASIC_AUTH_USER:-admin}"
    BASIC_AUTH_PASSWORD="${BASIC_AUTH_PASSWORD:-changeme}"
fi

echo "Generating htpasswd file for user: $BASIC_AUTH_USER"

# Create htpasswd file with credentials
htpasswd -bc /etc/nginx/auth/.htpasswd "$BASIC_AUTH_USER" "$BASIC_AUTH_PASSWORD"

# Secure the htpasswd file
chmod 644 /etc/nginx/auth/.htpasswd

echo "htpasswd file generated successfully"

# ============================================
# Validate nginx configuration
# ============================================

echo "Validating nginx configuration..."
nginx -t

echo "Nginx configuration is valid"

# ============================================
# Start nginx
# ============================================

echo "Starting nginx..."

# Execute the command passed to the script (from docker-compose.yml)
# If no command is provided, start nginx in foreground mode
if [ $# -eq 0 ]; then
    exec nginx -g 'daemon off;'
else
    exec "$@"
fi
