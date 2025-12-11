#!/usr/bin/env python3
"""
REST API server for remote monitoring
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import jwt
import hashlib

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Simple authentication
SECRET_KEY = os.getenv('LOGS_API_KEY', 'your-secret-key-here')
API_TOKENS = {}

def generate_token(username):
    """Generate JWT token"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except:
        return None

# Authentication middleware
@app.before_request
def require_auth():
    # Public endpoints
    public_endpoints = ['/api/status', '/api/login', '/api/register']
    if request.path in public_endpoints:
        return None
    
    # Check for token
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token or not verify_token(token):
        return jsonify({'error': 'Authentication required'}), 401

# Public endpoints
@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Simple authentication (in production, use proper auth)
    if username == 'admin' and password == 'admin':
        token = generate_token(username)
        return jsonify({'token': token, 'user': username})
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Protected endpoints
@app.route('/api/logs')
def api_logs():
    """Get recent logs"""
    days = request.args.get('days', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    logs = []
    base_dir = os.path.expanduser("~/simple-logs/daily")
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        date_dir = os.path.join(base_dir, date_str)
        
        if os.path.exists(date_dir):
            for file in sorted(os.listdir(date_dir)):
                if file.endswith('.json'):
                    file_path = os.path.join(date_dir, file)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            logs.append({
                                'file': file,
                                'date': date_str,
                                'data': data
                            })
                    except:
                        continue
        
        if len(logs) >= limit:
            break
    
    return jsonify({'logs': logs[:limit], 'count': len(logs)})

@app.route('/api/stats')
def api_stats():
    """Get system statistics"""
    import psutil
    
    return jsonify({
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'users': len(psutil.users()),
        'processes': len(psutil.pids()),
        'uptime': datetime.now().timestamp() - psutil.boot_time(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts')
def api_alerts():
    """Get recent alerts"""
    alert_dir = os.path.expanduser("~/simple-logs/alerts")
    alerts = []
    
    if os.path.exists(alert_dir):
        alert_files = sorted(
            [f for f in os.listdir(alert_dir) if f.endswith('.json')],
            reverse=True
        )[:10]
        
        for file in alert_files:
            file_path = os.path.join(alert_dir, file)
            try:
                with open(file_path, 'r') as f:
                    alerts.append(json.load(f))
            except:
                continue
    
    return jsonify({'alerts': alerts, 'count': len(alerts)})

@app.route('/api/collect', methods=['POST'])
def api_collect():
    """Trigger manual log collection"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['python3', os.path.expanduser('~/simple-logs/log-collector-enhanced.py')],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export')
def api_export():
    """Export logs as JSON file"""
    import tempfile
    import zipfile
    
    # Create temporary zip file
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, 'logs_export.zip')
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Add recent logs
        logs_dir = os.path.expanduser("~/simple-logs/daily")
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(logs_dir))
                    zipf.write(file_path, arcname)
    
    return send_file(zip_path, as_attachment=True, download_name='logs_export.zip')

if __name__ == '__main__':
    print("🚀 Starting API Server...")
    print("📡 Endpoints:")
    print("  GET  /api/status   - Check server status")
    print("  POST /api/login    - Get authentication token")
    print("  GET  /api/logs     - Get log data (requires auth)")
    print("  GET  /api/stats    - Get system stats (requires auth)")
    print("  GET  /api/alerts   - Get alerts (requires auth)")
    print("  POST /api/collect  - Trigger log collection (requires auth)")
    print("  GET  /api/export   - Export logs (requires auth)")
    print()
    print("🔐 Default credentials: admin/admin")
    print("🌐 Server running at: http://0.0.0.0:8080")
    
    app.run(host='0.0.0.0', port=8080, debug=False)