#!/usr/bin/env python3
"""
Alert system for high resource usage
"""

import json
import os
import psutil
from datetime import datetime

def check_alerts():
    """Check system resources and create alerts if needed"""
    alerts = []
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 80:
        alerts.append(f"⚠️ HIGH CPU USAGE: {cpu_percent}%")
    
    # Check memory usage
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > 85:
        alerts.append(f"⚠️ HIGH MEMORY USAGE: {memory_percent}%")
    
    # Check disk usage
    disk_percent = psutil.disk_usage('/').percent
    if disk_percent > 90:
        alerts.append(f"⚠️ HIGH DISK USAGE: {disk_percent}%")
    
    # Check temperature (if available)
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current > 80:  # 80°C threshold
                        alerts.append(f"🌡️ HIGH TEMP {name}: {entry.current}°C")
    except:
        pass
    
    return alerts

def save_alerts(alerts):
    """Save alerts to file"""
    if alerts:
        alert_dir = os.path.expanduser("~/simple-logs/alerts")
        os.makedirs(alert_dir, exist_ok=True)
        
        alert_file = os.path.join(alert_dir, f"alerts_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json")
        
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "system": {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent
            }
        }
        
        with open(alert_file, 'w') as f:
            json.dump(alert_data, f, indent=2)
        
        # Also print to terminal
        print("🚨 ALERTS FOUND:")
        for alert in alerts:
            print(f"  • {alert}")
        
        return True
    else:
        print("✅ No alerts - system normal")
        return False

def main():
    """Main alert check"""
    print(f"🔍 Checking system alerts - {datetime.now().strftime('%H:%M:%S')}")
    alerts = check_alerts()
    
    if save_alerts(alerts):
        # Could add notification here (email, desktop notification, etc.)
        pass

if __name__ == "__main__":
    main()