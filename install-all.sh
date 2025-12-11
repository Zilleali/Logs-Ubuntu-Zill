#!/bin/bash
# Installation script for enhanced logging system

echo "🚀 Installing Enhanced Logging System..."
echo "=========================================="

# Check Python version
python3 --version || { echo "Python 3 is required"; exit 1; }

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install flask flask-cors flask-socketio cryptography pyjwt psutil requests || {
    echo "Failed to install dependencies"
    exit 1
}

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p ~/simple-logs/{daily,backups,alerts,reports,audit,templates/static}

# Make all scripts executable
echo "⚡ Setting executable permissions..."
chmod +x ~/simple-logs/*.py

# Create systemd services
echo "🎛️ Setting up systemd services..."

# Log collector service
cat > ~/.config/systemd/user/simple-logs-collect.service << SERVICE
[Unit]
Description=Simple Logs Collector
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/simple-logs/log-collector-optimized.py
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
SERVICE

# API server service
cat > ~/.config/systemd/user/simple-logs-api.service << SERVICE
[Unit]
Description=Simple Logs API Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/simple-logs/api-server.py
Restart=always
RestartSec=60
Environment="LOGS_API_KEY=$(openssl rand -hex 32)"

[Install]
WantedBy=default.target
SERVICE

# Dashboard service
cat > ~/.config/systemd/user/simple-logs-dashboard.service << SERVICE
[Unit]
Description=Simple Logs Dashboard
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/simple-logs/dashboard-enhanced.py
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
SERVICE

# Reload systemd
systemctl --user daemon-reload

# Enable services
echo "🔧 Enabling services..."
systemctl --user enable simple-logs-collect
systemctl --user enable simple-logs-api
systemctl --user enable simple-logs-dashboard

# Start services
echo "🚀 Starting services..."
systemctl --user start simple-logs-collect
systemctl --user start simple-logs-api
systemctl --user start simple-logs-dashboard

# Create configuration file
echo "⚙️ Creating default configuration..."
~/simple-logs/config-manager.py set system log_interval 300
~/simple-logs/config-manager.py set alerts cpu_threshold 80
~/simple-logs/config-manager.py set api enabled true

# Generate installation report
echo "📋 Generating installation report..."
cat > ~/simple-logs/installation-report.txt << REPORT
Enhanced Logging System Installation Report
==========================================
Date: $(date)
User: $(whoami)

Services Installed:
- simple-logs-collect: $(systemctl --user is-active simple-logs-collect)
- simple-logs-api: $(systemctl --user is-active simple-logs-api)
- simple-logs-dashboard: $(systemctl --user is-active simple-logs-dashboard)

Access Information:
🌐 Dashboard: http://localhost:5001
📡 API Server: http://localhost:8080
📱 Mobile API: http://localhost:8081

Default Credentials:
API Username: admin
API Password: admin

Directories:
Logs: ~/simple-logs/daily
Backups: ~/simple-logs/backups
Alerts: ~/simple-logs/alerts

To view logs:
systemctl --user status simple-logs-collect
journalctl --user -u simple-logs-collect -f

Next Steps:
1. Change default API credentials
2. Configure webhooks in ~/simple-logs/webhooks.json
3. Set up encryption keys if needed
REPORT

echo "✅ Installation complete!"
echo ""
echo "📋 See installation report: ~/simple-logs/installation-report.txt"
echo ""
echo "🎯 Quick Start:"
echo "   Open dashboard: http://localhost:5001"
echo "   API endpoint: http://localhost:8080/api/status"
echo ""
echo "🛠️  Management commands:"
echo "   Check status: systemctl --user status 'simple-logs-*'"
echo "   View logs: journalctl --user -u simple-logs-collect -f"
echo "   Configure: python3 ~/simple-logs/config-manager.py show"