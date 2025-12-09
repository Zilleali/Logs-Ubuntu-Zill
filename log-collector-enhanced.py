#!/home/zille/simple-logs/venv/bin/python3
import sys
import os

"""
Enhanced log collector with more system info
"""

import json
import os
# Add user site-packages to path
user_site = os.path.expanduser("~/.local/lib/python3.12/site-packages")
if os.path.exists(user_site):
    sys.path.append(user_site)

# Add venv site-packages
venv_site = os.path.join(os.path.dirname(__file__), "venv", "lib", "python3.12", "site-packages")
if os.path.exists(venv_site):
    sys.path.append(venv_site)

import psutil
import subprocess
from datetime import datetime
import socket
import platform

# Create today's directory
today = datetime.now()
log_dir = os.path.expanduser(f"~/simple-logs/daily/{today.strftime('%Y-%m-%d')}")
os.makedirs(log_dir, exist_ok=True)

def get_system_info():
    """Get comprehensive system information"""
    info = {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
    return info

def get_resource_usage():
    """Get system resource usage"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count": psutil.cpu_count(),
        "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
        "disk_used_gb": round(psutil.disk_usage('/').used / (1024**3), 2),
        "disk_percent": psutil.disk_usage('/').percent,
    }

def get_users_and_processes():
    """Get user and process information"""
    return {
        "logged_in_users": [u.name for u in psutil.users()],
        "total_processes": len(psutil.pids()),
        "top_processes": get_top_processes(5),
    }

def get_top_processes(n=5):
    """Get top n processes by CPU usage"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu": proc.info['cpu_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Sort by CPU usage and get top n
    processes.sort(key=lambda x: x['cpu'], reverse=True)
    return processes[:n]

def get_network_info():
    """Get network information"""
    return {
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "network_connections": len(psutil.net_connections()),
        "bytes_sent_mb": round(psutil.net_io_counters().bytes_sent / (1024**2), 2),
        "bytes_recv_mb": round(psutil.net_io_counters().bytes_recv / (1024**2), 2),
    }

def get_system_events():
    """Get recent system events"""
    try:
        # Get last 5 logins
        last_output = subprocess.run(['last', '-n', '5'], capture_output=True, text=True).stdout
        # Get uptime
        uptime_output = subprocess.run(['uptime', '-p'], capture_output=True, text=True).stdout
        # Get current date/time
        date_output = subprocess.run(['date'], capture_output=True, text=True).stdout
        
        return {
            "recent_logins": last_output.strip().split('\n'),
            "uptime": uptime_output.strip(),
            "current_datetime": date_output.strip(),
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    """Collect all data and save"""
    all_data = {
        "system": get_system_info(),
        "resources": get_resource_usage(),
        "users": get_users_and_processes(),
        "network": get_network_info(),
        "events": get_system_events(),
        "collection_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to JSON file
    filename = os.path.join(log_dir, f"system_log_{today.strftime('%H-%M-%S')}.json")
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    # Also create a readable summary
    summary_file = os.path.join(log_dir, f"summary_{today.strftime('%H-%M')}.txt")
    with open(summary_file, 'w') as f:
        f.write(f"=== System Summary ===\n")
        f.write(f"Time: {all_data['collection_time']}\n")
        f.write(f"Hostname: {all_data['system']['hostname']}\n")
        f.write(f"Uptime: {all_data['events'].get('uptime', 'N/A')}\n")
        f.write(f"CPU Usage: {all_data['resources']['cpu_percent']}%\n")
        f.write(f"Memory Usage: {all_data['resources']['memory_percent']}%\n")
        f.write(f"Disk Usage: {all_data['resources']['disk_percent']}%\n")
        f.write(f"Users: {', '.join(all_data['users']['logged_in_users'])}\n")
        f.write(f"Processes: {all_data['users']['total_processes']}\n")
    
    print(f"✅ Enhanced log saved: {filename}")
    print(f"📊 CPU: {all_data['resources']['cpu_percent']}% | "
          f"Memory: {all_data['resources']['memory_percent']}% | "
          f"Disk: {all_data['resources']['disk_percent']}%")

if __name__ == "__main__":
    main()
