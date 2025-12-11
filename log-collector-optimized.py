#!/usr/bin/env python3
"""
Optimized log collector with compression
"""

import json
import gzip
import base64
from datetime import datetime
import os

# Import from existing collector
import sys
sys.path.append(os.path.dirname(__file__))
from log-collector-enhanced import *

def save_compressed(data, filename):
    """Save data in compressed format"""
    json_str = json.dumps(data, separators=(',', ':'))  # Minify JSON
    compressed = gzip.compress(json_str.encode('utf-8'))
    
    # Save compressed
    with open(filename + '.gz', 'wb') as f:
        f.write(compressed)
    
    # Also save small summary
    summary = {
        'timestamp': data.get('metadata', {}).get('collection_time', ''),
        'cpu': data.get('resources', {}).get('cpu', {}).get('percent', 0),
        'memory': data.get('resources', {}).get('memory', {}).get('percent', 0),
        'disk': data.get('resources', {}).get('disk', {}).get('percent', 0)
    }
    
    with open(filename + '.summary', 'w') as f:
        json.dump(summary, f)
    
    return filename + '.gz'

def main():
    """Optimized main function"""
    print(f"🔍 Collecting optimized logs - {datetime.now().strftime('%H:%M:%S')}")
    
    # Create directory
    today = datetime.now()
    log_dir = os.path.expanduser(f"~/simple-logs/daily/{today.strftime('%Y-%m-%d')}")
    os.makedirs(log_dir, exist_ok=True)
    
    # Collect data (reuse existing functions)
    all_data = {
        "metadata": {
            "collection_id": str(uuid.uuid4())[:8],
            "collection_time": today.isoformat(),
            "version": "3.0",
            "compressed": True
        },
        "system": get_system_info(),
        "resources": get_resource_usage(),
        "users": get_users_and_processes(),
        "network": get_network_info(),
        "events": get_system_events()
    }
    
    # Save compressed
    filename = os.path.join(log_dir, f"log_{today.strftime('%H-%M-%S')}")
    compressed_file = save_compressed(all_data, filename)
    
    print(f"✅ Compressed log saved: {compressed_file}")
    print(f"📦 Size: {os.path.getsize(compressed_file) / 1024:.1f} KB")
    
    return compressed_file

if __name__ == "__main__":
    main()