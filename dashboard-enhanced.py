#!/usr/bin/env python3
"""
Enhanced dashboard with real-time WebSocket updates
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import psutil
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store connected clients
connected_clients = 0

@app.route('/')
def index():
    return render_template('dashboard-enhanced.html')

@app.route('/api/real-time-data')
def real_time_data():
    """Get real-time system data"""
    return jsonify({
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'network': {
            'sent': psutil.net_io_counters().bytes_sent,
            'recv': psutil.net_io_counters().bytes_recv
        },
        'processes': len(psutil.pids()),
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    global connected_clients
    connected_clients += 1
    print(f"Client connected. Total: {connected_clients}")
    emit('connection_response', {'data': 'Connected to real-time feed'})

@socketio.on('disconnect')
def handle_disconnect():
    global connected_clients
    connected_clients -= 1
    print(f"Client disconnected. Total: {connected_clients}")

@socketio.on('request_update')
def handle_update_request(data):
    """Handle manual update request"""
    emit('system_update', get_system_data())

def background_thread():
    """Background thread for real-time updates"""
    while True:
        if connected_clients > 0:
            data = get_system_data()
            socketio.emit('real_time_update', data)
        time.sleep(5)  # Update every 5 seconds

def get_system_data():
    """Get comprehensive system data"""
    return {
        'cpu': {
            'percent': psutil.cpu_percent(interval=1),
            'cores': psutil.cpu_count(logical=False),
            'load': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        },
        'memory': {
            'percent': psutil.virtual_memory().percent,
            'used_gb': psutil.virtual_memory().used / (1024**3),
            'total_gb': psutil.virtual_memory().total / (1024**3)
        },
        'disk': {
            'percent': psutil.disk_usage('/').percent,
            'used_gb': psutil.disk_usage('/').used / (1024**3),
            'free_gb': psutil.disk_usage('/').free / (1024**3)
        },
        'network': {
            'sent_mb': psutil.net_io_counters().bytes_sent / (1024**2),
            'recv_mb': psutil.net_io_counters().bytes_recv / (1024**2),
            'connections': len(psutil.net_connections())
        },
        'users': len(psutil.users()),
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    print("🚀 Enhanced Dashboard with WebSocket")
    print("🌐 Open your browser to: http://localhost:5001")
    print("📡 WebSocket enabled for real-time updates")
    
    # Start background thread
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    
    socketio.run(app, host='127.0.0.1', port=5001, debug=False)