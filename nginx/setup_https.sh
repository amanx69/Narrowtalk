#!/usr/bin/env bash
set -e

DOMAIN="${1}"
EMAIL="${2}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Usage: sudo ./backend/nginx/setup_https.sh <domain> <email>"
    exit 1
fi

apt-get update -y
apt-get install -y nginx certbot python3-certbot-nginx

cp "$SCRIPT_DIR/narrow.conf" /etc/nginx/sites-available/narrow
sed -i "s/server_name _;/server_name $DOMAIN localhost;/" /etc/nginx/sites-available/narrow

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/narrow /etc/nginx/sites-enabled/narrow

nginx -t
systemctl enable nginx
systemctl restart nginx

certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect
