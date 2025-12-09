#!/bin/bash
# Enhanced runner with alerts

echo "========================================"
echo "   Enhanced Logging System"
echo "========================================"
echo ""

echo "🔍 Step 1: Checking system alerts..."
python3 ~/simple-logs/alert-system.py

echo ""
echo "🔄 Step 2: Collecting system logs..."
python3 ~/simple-logs/log-collector-enhanced.py

echo ""
echo "📤 Step 3: Uploading to GitHub..."
~/simple-logs/git-upload.sh

echo ""
echo "📊 Step 4: Generating daily report..."
python3 ~/simple-logs/daily-report.py 2>/dev/null || echo "Report generation skipped"

echo ""
echo "✅ All tasks completed!"
echo "========================================"