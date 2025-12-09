#!/bin/bash
# Setup better automation

echo "=== Setting up Enhanced Automation ==="

# 1. Create systemd service for reliable automation
mkdir -p ~/.config/systemd/user

# Service to collect logs
cat > ~/.config/systemd/user/simple-logs.service << 'SERVICE'
[Unit]
Description=Simple Logs Collection
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/simple-logs/log-collector-enhanced.py
WorkingDirectory=%h/simple-logs
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
SERVICE

# Timer for hourly collection
cat > ~/.config/systemd/user/simple-logs.timer << 'TIMER'
[Unit]
Description=Collect logs hourly
Requires=simple-logs.service

[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
TIMER

# Service for Git upload
cat > ~/.config/systemd/user/simple-logs-git.service << 'GITSERVICE'
[Unit]
Description=Upload logs to GitHub
After=simple-logs.service

[Service]
Type=oneshot
ExecStart=%h/simple-logs/git-upload.sh
WorkingDirectory=%h/simple-logs

[Install]
WantedBy=multi-user.target
GITSERVICE

# Timer for Git upload (every 4 hours)
cat > ~/.config/systemd/user/simple-logs-git.timer << 'GITTIMER'
[Unit]
Description=Upload to GitHub every 4 hours
Requires=simple-logs-git.service

[Timer]
OnCalendar=*/4:00
Persistent=true

[Install]
WantedBy=timers.target
GITTIMER

# 2. Enable lingering for user services
echo "Enabling systemd user services..."
sudo loginctl enable-linger $(whoami)

# 3. Reload and start services
systemctl --user daemon-reload
systemctl --user enable simple-logs.timer simple-logs-git.timer
systemctl --user start simple-logs.timer simple-logs-git.timer

# 4. Create monitoring script
cat > ~/simple-logs/monitor-status.sh << 'MONITOR'
#!/bin/bash
echo "=== Simple Logs System Status ==="
echo "Time: $(date)"
echo ""

echo "📊 Systemd Timers:"
echo "-----------------"
systemctl --user list-timers --no-pager | grep -E "(simple-logs|NEXT|LEFT)"

echo ""
echo "📁 Recent Logs:"
echo "--------------"
find ~/simple-logs/daily -name "*.json" -type f -exec ls -lt {} + 2>/dev/null | head -5

echo ""
echo "🔗 Git Status:"
echo "-------------"
cd ~/simple-logs
git log --oneline -3 2>/dev/null || echo "Git not initialized"

echo ""
echo "💾 Disk Usage:"
echo "-------------"
du -sh ~/simple-logs
MONITOR

chmod +x ~/simple-logs/monitor-status.sh

echo ""
echo "✅ Automation setup complete!"
echo ""
echo "📋 To check status: ~/simple-logs/monitor-status.sh"
echo "⏰ Log collection: Hourly"
echo "📤 GitHub upload: Every 4 hours"
echo ""
echo "🛠️  Commands:"
echo "  systemctl --user status simple-logs.timer"
echo "  journalctl --user -u simple-logs.service -f"