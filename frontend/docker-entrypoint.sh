#!/bin/sh
set -eu

cat > /usr/share/nginx/html/config.js <<EOF
window.API_BASE_URL = "${API_BASE_URL:-http://localhost:8001}";
EOF
