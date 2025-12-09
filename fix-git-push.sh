#!/bin/bash
echo "=== Fixing Git Push Issue ==="
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " github_user

# Go to logs directory
cd ~/simple-logs

# Remove existing remote if any
git remote remove origin 2>/dev/null || true

# Add SSH remote
git remote add origin git@github.com:${github_user}/Logs-Ubuntu-Zill.git

# Get GitHub private email
echo ""
echo "1. Go to: https://github.com/settings/emails"
echo "2. Find your 'private email' (looks like 12345678+username@users.noreply.github.com)"
echo "3. Copy it"
echo ""
read -p "Paste your GitHub private email: " github_email

# Set Git configuration
git config user.name "Simple Logger"
git config user.email "$github_email"

echo ""
echo "✅ Configuration updated!"
echo "Git email: $github_email"
echo "Git remote: git@github.com:${github_user}/Logs-Ubuntu-Zill.git"
echo ""
echo "Now try pushing:"
echo "  cd ~/simple-logs"
echo "  git add ."
echo "  git commit -m 'Fixed email configuration'"
echo "  git push -u origin main"
FIX
