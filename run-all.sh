#!/bin/bash
# Main runner - does both collection and upload
# Run this whenever you want to save and upload logs

echo "========================================"
echo "   Simple Logging System"
echo "========================================"
echo ""

echo "🔄 Step 1: Collecting system logs..."
python3 ~/simple-logs/log-collector.py

echo ""
echo "📤 Step 2: Uploading to GitHub..."
~/simple-logs/git-upload.sh

echo ""
echo "✅ All done!"
echo "Logs saved locally and uploaded to GitHub"
echo "========================================"
