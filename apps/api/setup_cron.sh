#!/bin/bash
# WRHITW Cron Job Setup Script
# =============================
# This script installs the cron job for automated news fetching.
#
# Usage:
#   ./setup_cron.sh
#
# To verify installation:
#   crontab -l
#
# To view logs:
#   tail -f /tmp/wrhitw_fetcher.log

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CRON_FILE="$SCRIPT_DIR/wrhitw_cron.txt"

echo "WRHITW Cron Job Setup"
echo "====================="
echo ""

# Check if cron file exists
if [ ! -f "$CRON_FILE" ]; then
    echo "❌ Error: wrhitw_cron.txt not found in $SCRIPT_DIR"
    exit 1
fi

# Get current user's home directory
HOME_DIR=$(eval echo ~$USER)

# Update path in cron file
echo "📝 Updating cron configuration..."
TEMP_CRON=$(mktemp)
sed "s|/Users/bwan/.openclaw/workspace|$HOME_DIR/.openclaw/workspace|g" "$CRON_FILE" > "$TEMP_CRON"

# Install cron job
echo "⏰ Installing cron job..."
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

echo ""
echo "✅ Cron job installed successfully!"
echo ""
echo "📋 Installed cron jobs:"
crontab -l | grep wrhitw || echo "No wrhitw cron jobs found"
echo ""
echo "📝 To view logs:"
echo "   tail -f /tmp/wrhitw_fetcher.log"
echo ""
echo "🔧 To remove cron job:"
echo "   crontab -r"
echo ""
echo "⏱️  Next scheduled run:"
echo "   Check with: crontab -l"
echo ""
