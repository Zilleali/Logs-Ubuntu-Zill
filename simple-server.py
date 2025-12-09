#!/home/zille/simple-logs/venv/bin/python3
"""
Simple HTTP server for the dashboard
"""

import http.server
import socketserver
import json
import os
from datetime import datetime

PORT = 8080
LOG_DIR = os.path.expanduser("~/simple-logs")

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve dashboard HTML
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(os.path.join(LOG_DIR, 'dashboard.html'), 'rb') as f:
                self.wfile.write(f.read())
        
        # API endpoints
        elif self.path == '/api/stats':
            self.send_json_response(self.get_stats())
        
        elif self.path == '/api/collect':
            # Trigger log collection
            import subprocess
            result = subprocess.run(['python3', os.path.join(LOG_DIR, 'log-collector-enhanced.py')], 
                                  capture_output=True, text=True)
            self.send_json_response({
                "success": result.returncode == 0,
                "message": result.stdout if result.returncode == 0 else result.stderr
            })
        
        else:
            # Serve static files
            super().do_GET()
    
    def get_stats(self):
        """Get dashboard statistics"""
        # Count total log files
        total_logs = 0
        today_logs = 0
        recent_files = []
        
        daily_dir = os.path.join(LOG_DIR, 'daily')
        if os.path.exists(daily_dir):
            for root, dirs, files in os.walk(daily_dir):
                for file in files:
                    if file.endswith('.json'):
                        total_logs += 1
                        filepath = os.path.join(root, file)
                        # Check if from today
                        if datetime.fromtimestamp(os.path.getmtime(filepath)).date() == datetime.today().date():
                            today_logs += 1
                        # Add to recent files
                        recent_files.append(os.path.relpath(filepath, LOG_DIR))
        
        # Get 5 most recent files
        recent_files = sorted(recent_files, reverse=True)[:5]
        
        # Get disk usage
        import psutil
        disk_usage = psutil.disk_usage('/').percent
        
        return {
            "total_logs": total_logs,
            "today_logs": today_logs,
            "last_update": "Just now",  # Simplified
            "git_status": "Connected",
            "recent_files": recent_files,
            "disk_usage": round(disk_usage, 1)
        }
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def main():
    # Change to logs directory to serve files from there
    os.chdir(LOG_DIR)
    
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🌐 Dashboard running at: http://localhost:{PORT}")
        print(f"📁 Serving from: {LOG_DIR}")
        print("🛑 Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped")

if __name__ == "__main__":
    main()