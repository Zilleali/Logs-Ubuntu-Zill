#!/bin/bash
# Complete Logs System Manager

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}${BOLD}=== Simple Logs System Manager ===${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

case "$1" in
    "start")
        print_header
        echo "Starting all automation timers..."
        systemctl --user start simple-logs-collect.timer
        systemctl --user start simple-logs-alerts.timer
        systemctl --user start simple-logs-git.timer
        systemctl --user start simple-logs-report.timer
        print_success "All timers started"
        echo ""
        systemctl --user list-timers --no-pager | grep simple-logs
        ;;
        
    "stop")
        print_header
        echo "Stopping all automation timers..."
        systemctl --user stop simple-logs-collect.timer
        systemctl --user stop simple-logs-alerts.timer
        systemctl --user stop simple-logs-git.timer
        systemctl --user stop simple-logs-report.timer
        print_success "All timers stopped"
        ;;
        
    "restart")
        print_header
        echo "Restarting all services..."
        systemctl --user daemon-reload
        systemctl --user restart simple-logs-collect.timer
        systemctl --user restart simple-logs-alerts.timer
        systemctl --user restart simple-logs-git.timer
        systemctl --user restart simple-logs-report.timer
        print_success "All services restarted"
        ;;
        
    "collect"|"log")
        print_header
        echo "Collecting system logs..."
        systemctl --user start simple-logs-collect.service
        echo ""
        journalctl --user -u simple-logs-collect.service --no-pager | tail -20
        ;;
        
    "alerts"|"alert")
        print_header
        echo "Checking for system alerts..."
        systemctl --user start simple-logs-alerts.service
        echo ""
        journalctl --user -u simple-logs-alerts.service --no-pager | tail -20
        ;;
        
    "report")
        print_header
        echo "Generating daily report..."
        systemctl --user start simple-logs-report.service
        echo ""
        journalctl --user -u simple-logs-report.service --no-pager | tail -20
        ;;
        
    "git"|"push")
        print_header
        echo "Uploading logs to GitHub..."
        systemctl --user start simple-logs-git.service
        echo ""
        journalctl --user -u simple-logs-git.service --no-pager | tail -20
        ;;
        
    "dashboard"|"web")
        print_header
        echo "Starting web dashboard..."
        echo -e "${YELLOW}The dashboard will open in your browser at: http://localhost:5000${NC}"
        echo "Press Ctrl+C to stop the dashboard"
        echo ""
        cd ~/simple-logs && python3 dashboard.py
        ;;
        
    "status"|"info")
        print_header
        echo -e "${BOLD}System Status:${NC}"
        echo ""
        
        # Timer status
        echo -e "${BOLD}📅 Automation Timers:${NC}"
        systemctl --user list-timers --no-pager | grep -A2 -B2 "simple-logs"
        
        echo ""
        # Service status
        echo -e "${BOLD}⚙️  Service Status:${NC}"
        for service in collect alerts git report; do
            if systemctl --user is-active --quiet simple-logs-$service.service; then
                echo -e "  simple-logs-$service.service: ${GREEN}Active${NC}"
            else
                echo -e "  simple-logs-$service.service: ${YELLOW}Inactive${NC}"
            fi
        done
        
        echo ""
        # Log files
        echo -e "${BOLD}📁 Log Files:${NC}"
        TODAY=$(date +%Y-%m-%d)
        TODAY_DIR="$HOME/simple-logs/daily/$TODAY"
        if [ -d "$TODAY_DIR" ]; then
            COUNT=$(ls -1 "$TODAY_DIR"/*.json 2>/dev/null | wc -l)
            echo -e "  Today's logs ($TODAY): ${GREEN}$COUNT files${NC}"
            ls -lt "$TODAY_DIR"/*.json 2>/dev/null | head -3 | awk '{print "    " $6 " " $7 " " $8 " " $9}'
        else
            echo -e "  Today's logs: ${YELLOW}No logs yet${NC}"
        fi
        
        echo ""
        # Alerts
        echo -e "${BOLD}🚨 Recent Alerts:${NC}"
        ALERT_COUNT=$(find ~/simple-logs/alerts -name "*.json" -type f -mtime -1 2>/dev/null | wc -l)
        echo -e "  Last 24 hours: ${YELLOW}$ALERT_COUNT alerts${NC}"
        
        echo ""
        # System info
        echo -e "${BOLD}💻 System Info:${NC}"
        echo "  $(hostname) - $(uptime -p | sed 's/up //')"
        
        echo ""
        # Quick commands
        echo -e "${BOLD}🎛️  Quick Commands:${NC}"
        echo "  $0 start     - Start all automation"
        echo "  $0 dashboard - Open web dashboard"
        echo "  $0 collect   - Collect logs now"
        echo "  $0 status    - Show this status"
        ;;
        
    "logs"|"view")
        print_header
        echo "Recent log files:"
        echo ""
        find ~/simple-logs/daily -name "*.json" -type f -exec ls -lt {} + 2>/dev/null | head -10 | \
            awk '{printf "  %s %s %s\n", $6, $7, $8, $9}'
        ;;
        
    "test")
        print_header
        echo "🧪 Testing all components..."
        echo ""
        
        echo -e "${BOLD}1. Testing log collector...${NC}"
        systemctl --user start simple-logs-collect.service
        sleep 2
        journalctl --user -u simple-logs-collect.service --no-pager | grep -E "(✅|❌|Error|saved)" | tail -3
        
        echo ""
        echo -e "${BOLD}2. Testing alert system...${NC}"
        systemctl --user start simple-logs-alerts.service
        sleep 2
        journalctl --user -u simple-logs-alerts.service --no-pager | grep -E "(✅|🚨|⚠️|Alert)" | tail -3
        
        echo ""
        echo -e "${BOLD}3. Testing Git upload...${NC}"
        systemctl --user start simple-logs-git.service
        sleep 2
        journalctl --user -u simple-logs-git.service --no-pager | grep -E "(✅|📭|🚀|GitHub)" | tail -3
        
        echo ""
        echo -e "${BOLD}4. Testing report generation...${NC}"
        systemctl --user start simple-logs-report.service
        sleep 2
        journalctl --user -u simple-logs-report.service --no-pager | grep -E "(✅|📊|Report|generated)" | tail -3
        
        echo ""
        print_success "All tests completed!"
        ;;
        
    "setup"|"init")
        print_header
        echo "Initializing logging system..."
        echo ""
        
        # Enable lingering
        echo "1. Enabling user service lingering..."
        sudo loginctl enable-linger $(whoami)
        
        # Reload systemd
        echo "2. Reloading systemd..."
        systemctl --user daemon-reload
        
        # Enable services
        echo "3. Enabling services..."
        systemctl --user enable simple-logs-collect.service
        systemctl --user enable simple-logs-alerts.service
        systemctl --user enable simple-logs-git.service
        systemctl --user enable simple-logs-report.service
        
        # Enable timers
        echo "4. Enabling timers..."
        systemctl --user enable simple-logs-collect.timer
        systemctl --user enable simple-logs-alerts.timer
        systemctl --user enable simple-logs-git.timer
        systemctl --user enable simple-logs-report.timer
        
        # Start timers
        echo "5. Starting timers..."
        systemctl --user start simple-logs-collect.timer
        systemctl --user start simple-logs-alerts.timer
        systemctl --user start simple-logs-git.timer
        systemctl --user start simple-logs-report.timer
        
        print_success "Setup complete!"
        echo ""
        echo "📅 Automation schedule:"
        echo "  • Log collection: Every 30 minutes"
        echo "  • Alert checks: Every hour"
        echo "  • Git upload: Every 2 hours"
        echo "  • Daily report: 11:30 PM daily"
        ;;
        
    "help"|"--help"|"-h"|"")
        print_header
        echo -e "${BOLD}Usage:${NC} $0 {command}"
        echo ""
        echo -e "${BOLD}Main Commands:${NC}"
        echo "  start     - Start all automation timers"
        echo "  stop      - Stop all automation timers"
        echo "  restart   - Restart all services"
        echo "  status    - Show system status"
        echo "  setup     - Initial setup (run this first)"
        echo ""
        echo -e "${BOLD}Action Commands:${NC}"
        echo "  collect   - Collect logs now"
        echo "  alerts    - Check for alerts now"
        echo "  report    - Generate report now"
        echo "  git       - Upload to GitHub now"
        echo "  dashboard - Start web dashboard"
        echo "  logs      - View recent log files"
        echo ""
        echo -e "${BOLD}Utility Commands:${NC}"
        echo "  test      - Test all components"
        echo "  help      - Show this help"
        echo ""
        echo -e "${BOLD}Examples:${NC}"
        echo "  $0 setup     # First-time setup"
        echo "  $0 start     # Start automation"
        echo "  $0 dashboard # Open dashboard"
        echo "  $0 status    # Check status"
        ;;
        
    *)
        print_error "Unknown command: $1"
        echo ""
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac 
