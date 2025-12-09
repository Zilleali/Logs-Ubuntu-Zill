#!/bin/bash
# Master control for logging system

case "$1" in
    "start")
        echo "Starting logging system..."
        systemctl --user start simple-logs-collect.timer
        systemctl --user start simple-logs-alerts.timer
        systemctl --user start simple-logs-git.timer
        echo "✅ Timers started"
        ;;
    "stop")
        echo "Stopping logging system..."
        systemctl --user stop simple-logs-collect.timer
        systemctl --user stop simple-logs-alerts.timer
        systemctl --user stop simple-logs-git.timer
        echo "✅ Timers stopped"
        ;;
    "status")
        systemctl --user list-timers --no-pager | grep simple-logs
        ;;
    "collect")
        echo "Collecting logs..."
        python3 ~/simple-logs/log-collector-enhanced.py
        ;;
    "alerts")
        echo "Checking alerts..."
        python3 ~/simple-logs/alert-system.py
        ;;
    "report")
        echo "Generating report..."
        python3 ~/simple-logs/daily-report.py
        ;;
    "dashboard")
        echo "Starting dashboard..."
        cd ~/simple-logs && python3 dashboard.py
        ;;
    "git")
        echo "Uploading to Git..."
        ~/simple-logs/git-upload.sh
        ;;
    "help"|"")
        echo "Usage: $0 {start|stop|status|collect|alerts|report|dashboard|git}"
        echo ""
        echo "  start     - Start all automation timers"
        echo "  stop      - Stop all automation timers"
        echo "  status    - Show timer status"
        echo "  collect   - Manually collect logs"
        echo "  alerts    - Manually check alerts"
        echo "  report    - Generate daily report"
        echo "  dashboard - Start web dashboard"
        echo "  git       - Upload to GitHub"
        ;;
    *)
        echo "Invalid command: $1"
        echo "Use '$0 help' for usage"
        ;;
esac