#!/bin/bash
# Simple Git uploader
# This script uploads your logs to GitHub

cd ~/simple-logs

# Initialize Git repository if it doesn't exist
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git config user.name "Simple Logger"
    # Use GitHub's private email
    git config user.email "12345678+Zilleali@users.noreply.github.com"
    # Ignore the daily folder in Git (we'll add it manually)
    echo "daily/" > .gitignore
fi

# Add all files to Git staging area
git add .

# Create a commit with current timestamp
commit_message="Auto-update: $(date '+%Y-%m-%d %H:%M')"
git commit -m "$commit_message" 2>/dev/null || echo "No changes to commit"

# Check if GitHub remote is configured
if ! git remote | grep -q origin; then
    echo ""
    echo "⚠️ GitHub connection not set up yet."
    echo "To connect to GitHub, run these commands:"
    echo "  cd ~/simple-logs"
    echo "  git remote add origin git@github.com:zilleali/Logs-Ubuntu-Zill.git"
    echo "  git push -u origin main"
else
    # Try to push to GitHub
    echo "Pushing to GitHub..."
    git push origin main 2>/dev/null || git push origin master 2>/dev/null || echo "Push failed - check internet connection"
fi

