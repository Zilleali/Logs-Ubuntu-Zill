#!/usr/bin/env python3
"""
Mobile-optimized API endpoints
"""

from flask import Flask, jsonify, Response
import json
import os
from datetime import datetime
import psutil

app = Flask(__name__)

@app.route('/mobile/status')
def mobile_status():
    """Lightweight status for mobile"""
    return jsonify({
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'alerts': count_recent_alerts(),
        'last_update': datetime.now().isoformat(),
        'status': 'healthy' if psutil.cpu_percent() < 80 else 'warning'
    })

@app.route('/mobile/alerts')
def mobile_alerts():
    """Get alerts for mobile"""
    alerts = get_recent_alerts(10)
    return jsonify({
        'alerts': [{
            'title': a.get('type', 'Alert'),
            'message': a.get('message', ''),
            'severity': a.get('severity', 'INFO'),
            'time': a.get('timestamp', ''),
            'icon': get_icon_for_severity(a.get('severity'))
        } for a in alerts],
        'count': len(alerts)
    })

@app.route('/mobile/quick_stats')
def quick_stats():
    """Quick stats for mobile widget"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.expanduser(f"~/simple-logs/daily/{today}")
    
    log_count = 0
    if os.path.exists(log_dir):
        log_count = len([f for f in os.listdir(log_dir) if f.endswith('.json')])
    
    return jsonify({
        'logs_today': log_count,
        'uptime': int(datetime.now().timestamp() - psutil.boot_time()),
        'users': len(psutil.users()),
        'processes': len(psutil.pids())
    })

@app.route('/mobile/push_token', methods=['POST'])
def register_push_token():
    """Register mobile push token"""
    # In production, save to database
    return jsonify({'success': True})

def count_recent_alerts():
    """Count recent alerts"""
    alert_dir = os.path.expanduser("~/simple-logs/alerts")
    if os.path.exists(alert_dir):
        return len([f for f in os.listdir(alert_dir) if f.endswith('.json')])
    return 0

def get_recent_alerts(limit=10):
    """Get recent alerts"""
    alerts = []
    alert_dir = os.path.expanduser("~/simple-logs/alerts")
    
    if os.path.exists(alert_dir):
        files = sorted(
            [f for f in os.listdir(alert_dir) if f.endswith('.json')],
            reverse=True
        )[:limit]
        
        for file in files:
            try:
                with open(os.path.join(alert_dir, file), 'r') as f:
                    alerts.append(json.load(f))
            except:
                continue
    
    return alerts

def get_icon_for_severity(severity):
    """Get icon name for severity"""
    icons = {
        'CRITICAL': '🚨',
        'HIGH': '⚠️',
        'MEDIUM': '🔶',
        'LOW': '🔷',
        'INFO': 'ℹ️'
    }
    return icons.get(severity, '📌')

if __name__ == '__main__':
    print("📱 Mobile API Server")
    print("Endpoints:")
    print("  GET /mobile/status      - System status")
    print("  GET /mobile/alerts      - Recent alerts")
    print("  GET /mobile/quick_stats - Quick stats")
    print("  POST /mobile/push_token - Register push token")
    print()
    print("Running on: http://0.0.0.0:8081")
    
    app.run(host='0.0.0.0', port=8081, debug=False)