#!/bin/bash
# WRHITW News Fetcher - Automatic Cron Setup
# This script sets up the cron job for automatic news fetching

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_VENV="$SCRIPT_DIR/venv/bin/python"
FETCHER_SCRIPT="$SCRIPT_DIR/fetch_news_scheduled.py"
LOG_FILE="/tmp/wrhitw_fetcher.log"
CRON_SCHEDULE="0 */4 * * *"

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}WRHITW News Fetcher - Cron Setup${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""

# Check if running from correct directory
if [ ! -f "$FETCHER_SCRIPT" ]; then
    echo -e "${RED}Error: fetch_news_scheduled.py not found!${NC}"
    echo "Please run this script from the apps/api directory."
    exit 1
fi

# Check if Python venv exists
if [ ! -f "$PYTHON_VENV" ]; then
    echo -e "${RED}Error: Python virtual environment not found!${NC}"
    echo "Please create it with: python3 -m venv venv"
    exit 1
fi

# Check if required packages are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! $PYTHON_VENV -c "import requests, feedparser" 2>/dev/null; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    $PYTHON_VENV -m pip install requests feedparser --quiet
fi
echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Test run the script
echo -e "${YELLOW}Testing news fetcher...${NC}"
if $PYTHON_VENV "$FETCHER_SCRIPT" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ News fetcher test passed${NC}"
else
    echo -e "${RED}✗ News fetcher test failed!${NC}"
    echo "Please check the script for errors."
    exit 1
fi
echo ""

# Setup cron job
echo -e "${YELLOW}Setting up cron job...${NC}"
CRON_JOB="$CRON_SCHEDULE cd $SCRIPT_DIR && $PYTHON_VENV $FETCHER_SCRIPT >> $LOG_FILE 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "fetch_news_scheduled.py"; then
    echo -e "${YELLOW}Cron job already exists. Updating...${NC}"
    (crontab -l 2>/dev/null | grep -v "fetch_news_scheduled.py"; echo "$CRON_JOB") | crontab -
else
    echo -e "${YELLOW}Adding new cron job...${NC}"
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
fi

echo -e "${GREEN}✓ Cron job installed${NC}"
echo ""

# Verify cron job
echo -e "${YELLOW}Verifying cron setup...${NC}"
if crontab -l 2>/dev/null | grep -q "fetch_news_scheduled.py"; then
    echo -e "${GREEN}✓ Cron job verified${NC}"
    echo ""
    echo -e "${GREEN}Current crontab:${NC}"
    crontab -l | grep "fetch_news_scheduled.py"
else
    echo -e "${RED}✗ Cron job verification failed!${NC}"
    exit 1
fi
echo ""

# Summary
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "News fetcher will run:${GREEN} Every 4 hours${NC}"
echo -e "Log file: ${YELLOW}$LOG_FILE${NC}"
echo ""
echo -e "To view logs:${NC} tail -f $LOG_FILE"
echo -e "To test manually:${NC} cd $SCRIPT_DIR && ./venv/bin/python fetch_news_scheduled.py"
echo -e "To view cron:${NC} crontab -l"
echo ""
echo -e "${GREEN}Happy fetching! 🐶${NC}"
