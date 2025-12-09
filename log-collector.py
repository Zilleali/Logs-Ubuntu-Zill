#!/usr/bin/env python3
"""
Simple log collector - saves basic system info to a JSON file
This runs every time you want to collect logs
"""

import json
import os
import psutil
from datetime import datetime

# Create today's directory if it doesn't exist
today = datetime.now()
log_dir = os.path.expanduser(f"~/simple-logs/daily/{today.strftime('%Y-%m-%d')}")
os.makedirs(log_dir, exist_ok=True)

# Collect basic system information
data = {
    "timestamp": datetime.now().isoformat(),  # Current date and time
    "hostname": os.uname().nodename,         # Your computer's name
    "cpu_percent": psutil.cpu_percent(),      # CPU usage percentage
    "memory_percent": psutil.virtual_memory().percent,  # RAM usage percentage
    "disk_percent": psutil.disk_usage('/').percent,     # Disk usage percentage
    "users": [u.name for u in psutil.users()],  # List of logged-in users
    "boot_time": psutil.boot_time(),          # When system started
    "uptime": datetime.now().timestamp() - psutil.boot_time()  # How long running
}

# Save to a JSON file with current time as filename
filename = os.path.join(log_dir, f"log_{today.strftime('%H-%M')}.json")
with open(filename, 'w') as f:
    json.dump(data, f, indent=2)  # Save with nice formatting

print(f"✅ Log saved: {filename}")
print(f"   CPU: {data['cpu_percent']}% | Memory: {data['memory_percent']}% | Disk: {data['disk_percent']}%")
