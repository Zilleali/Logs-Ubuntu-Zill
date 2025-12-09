#!/usr/bin/env python3
"""
Complete web dashboard for system logs
"""

from flask import Flask, render_template, jsonify, send_file
import json
import os
import glob
import psutil
from datetime import datetime, timedelta
import threading
import webbrowser

app = Flask(__name__)
LOG_DIR = os.path.expanduser("~/simple-logs")

# Create templates directory
os.makedirs(os.path.join(LOG_DIR, "templates"), exist_ok=True)

# Create main template
with open(os.path.join(LOG_DIR, "templates", "index.html"), "w") as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Logs Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <style>
        body {
    font-family: 'Inter', Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background: #eef1f5;
    color: #333;
}

/* Main Container */
.container {
    max-width: 1250px;
    margin: 0 auto;
    background: #ffffff;
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}

/* Header */
.header {
    text-align: center;
    margin-bottom: 40px;
}
.header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0d6efd;
}
.header p {
    color: #6c757d;
    margin-top: 8px;
}

/* Buttons */
.controls {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 25px;
}
.controls button {
    flex: 1;
    min-width: 180px;
    padding: 12px 18px;
    background: #0d6efd;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: 0.3s ease;
    box-shadow: 0 3px 6px rgba(13,110,253,0.25);
}
.controls button:hover {
    background: #0a58ca;
    transform: translateY(-2px);
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: linear-gradient(to bottom right, #ffffff, #f7f9fc);
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border-left: 6px solid #0d6efd;
    transition: 0.3s;
}
.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.stat-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0d6efd;
}

/* Section blocks */
.recent-logs {
    background: #f5f7fb;
    padding: 24px;
    border-radius: 16px;
    margin-top: 30px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}
.recent-logs h2 {
    margin-top: 0;
    color: #0d6efd;
}

/* Log entries */
.log-entry {
    background: #ffffff;
    padding: 14px;
    margin: 6px 0;
    border-radius: 10px;
    border-left: 5px solid #198754;
    box-shadow: 0 3px 6px rgba(0,0,0,0.04);
    font-size: 0.95rem;
}

/* Mobile Optimisation */
@media (max-width: 600px) {
    .container {
        padding: 20px;
    }
    .stat-value {
        font-size: 1.7rem;
    }
    .controls button {
        flex: 1 1 100%;
    }
}

    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="dashboard-card text-center">
                    <h1 class="display-4 fw-bold">
                        <i class="bi bi-graph-up"></i> System Logs Dashboard
                    </h1>
                    <p class="lead text-muted">Real-time monitoring and analytics for your Ubuntu system</p>
                    <div class="row mt-4">
                        <div class="col-md-3">
                            <div class="system-health" id="systemHealth">Checking...</div>
                            <small class="text-muted">System Health</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold" id="lastUpdate">--:--:--</div>
                            <small class="text-muted">Last Update</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold" id="totalLogs">0</div>
                            <small class="text-muted">Total Logs</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold" id="activeAlerts">0</div>
                            <small class="text-muted">Active Alerts</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Stats Row -->
        <div class="row">
            <div class="col-md-3">
                <div class="dashboard-card resource-card text-center">
                    <i class="bi bi-cpu display-6 text-primary mb-3"></i>
                    <div class="stat-number" id="cpuPercent">0%</div>
                    <div class="stat-label">CPU Usage</div>
                    <div class="progress mt-3">
                        <div class="progress-bar bg-primary" id="cpuBar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="dashboard-card resource-card text-center">
                    <i class="bi bi-memory display-6 text-success mb-3"></i>
                    <div class="stat-number" id="memoryPercent">0%</div>
                    <div class="stat-label">Memory Usage</div>
                    <div class="progress mt-3">
                        <div class="progress-bar bg-success" id="memoryBar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="dashboard-card resource-card text-center">
                    <i class="bi bi-hdd display-6 text-warning mb-3"></i>
                    <div class="stat-number" id="diskPercent">0%</div>
                    <div class="stat-label">Disk Usage</div>
                    <div class="progress mt-3">
                        <div class="progress-bar bg-warning" id="diskBar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="dashboard-card resource-card text-center">
                    <i class="bi bi-people display-6 text-info mb-3"></i>
                    <div class="stat-number" id="userCount">0</div>
                    <div class="stat-label">Active Users</div>
                    <div class="mt-3">
                        <span class="badge bg-info" id="processCount">0 processes</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="row mt-4">
            <!-- Left Column -->
            <div class="col-md-8">
                <!-- Recent Logs -->
                <div class="dashboard-card">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h3><i class="bi bi-clock-history"></i> Recent Activity</h3>
                        <button class="btn-dashboard btn-sm" onclick="collectLogs()">
                            <i class="bi bi-plus-circle"></i> Collect Now
                        </button>
                    </div>
                    <div id="recentLogs">
                        <div class="text-center py-5">
                            <div class="spinner-border text-primary" role="status"></div>
                            <p class="mt-3">Loading recent logs...</p>
                        </div>
                    </div>
                </div>
                
                <!-- Alerts -->
                <div class="dashboard-card">
                    <h3><i class="bi bi-bell"></i> Recent Alerts</h3>
                    <div id="recentAlerts">
                        <p class="text-muted">No recent alerts</p>
                    </div>
                </div>
            </div>
            
            <!-- Right Column -->
            <div class="col-md-4">
                <!-- Quick Actions -->
                <div class="dashboard-card">
                    <h3><i class="bi bi-lightning"></i> Quick Actions</h3>
                    <div class="d-grid gap-2">
                        <button class="btn-dashboard" onclick="collectLogs()">
                            <i class="bi bi-collection"></i> Collect Logs
                        </button>
                        <button class="btn-dashboard" onclick="generateReport()">
                            <i class="bi bi-file-text"></i> Generate Report
                        </button>
                        <button class="btn-dashboard" onclick="checkAlerts()">
                            <i class="bi bi-shield-check"></i> Check Alerts
                        </button>
                        <button class="btn-dashboard" onclick="viewOnGitHub()">
                            <i class="bi bi-github"></i> View on GitHub
                        </button>
                        <button class="btn-dashboard" onclick="openLogFolder()">
                            <i class="bi bi-folder"></i> Open Log Folder
                        </button>
                    </div>
                </div>
                
                <!-- System Info -->
                <div class="dashboard-card">
                    <h3><i class="bi bi-pc-display"></i> System Info</h3>
                    <div id="systemInfo">
                        <p><i class="bi bi-hdd"></i> <strong>Hostname:</strong> <span id="infoHostname">Loading...</span></p>
                        <p><i class="bi bi-ubuntu"></i> <strong>OS:</strong> <span id="infoOS">Loading...</span></p>
                        <p><i class="bi bi-clock"></i> <strong>Uptime:</strong> <span id="infoUptime">Loading...</span></p>
                        <p><i class="bi bi-calendar"></i> <strong>Today's Logs:</strong> <span id="infoTodayLogs">0</span></p>
                    </div>
                </div>
                
                <!-- GitHub Status -->
                <div class="dashboard-card">
                    <h3><i class="bi bi-git"></i> GitHub Sync</h3>
                    <div id="gitStatus">
                        <div class="d-flex align-items-center">
                            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                            <span>Checking status...</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="dashboard-card text-center">
                    <p class="text-muted mb-0">
                        <i class="bi bi-code-slash"></i> System Logs Dashboard v2.0 |
                        <span id="currentTime">--:--:--</span> |
                        Auto-refresh: <span id="refreshCountdown">60</span>s
                    </p>
                </div>
            </div>
        </div>
    </div>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Global variables
        let refreshInterval = 30000; // 30 seconds
        let countdown = 60;
        
        // Update current time
        function updateTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = 
                now.toLocaleTimeString();
        }
        
        // Countdown for refresh
        function updateCountdown() {
            countdown--;
            if (countdown <= 0) {
                countdown = 60;
                refreshDashboard();
            }
            document.getElementById('refreshCountdown').textContent = countdown;
        }
        
        // Collect logs
        async function collectLogs() {
            try {
                const response = await fetch('/api/collect');
                const result = await response.json();
                alert(result.message);
                refreshDashboard();
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        // Generate report
        async function generateReport() {
            try {
                const response = await fetch('/api/report');
                const result = await response.json();
                alert(result.message);
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        // Check alerts
        async function checkAlerts() {
            try {
                const response = await fetch('/api/check-alerts');
                const result = await response.json();
                alert(result.message);
                loadAlerts();
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        // View on GitHub
        function viewOnGitHub() {
            window.open('https://github.com/Zilleali/Logs-Ubuntu-Zill', '_blank');
        }
        
        // Open log folder
        function openLogFolder() {
            alert('Logs location: ~/simple-logs/');
        }
        
        // Load system stats
        async function loadSystemStats() {
            try {
                const response = await fetch('/api/system-stats');
                const data = await response.json();
                
                // Update resource percentages
                document.getElementById('cpuPercent').textContent = data.cpu_percent + '%';
                document.getElementById('memoryPercent').textContent = data.memory_percent + '%';
                document.getElementById('diskPercent').textContent = data.disk_percent + '%';
                document.getElementById('userCount').textContent = data.user_count;
                document.getElementById('processCount').textContent = data.process_count + ' processes';
                
                // Update progress bars
                document.getElementById('cpuBar').style.width = data.cpu_percent + '%';
                document.getElementById('memoryBar').style.width = data.memory_percent + '%';
                document.getElementById('diskBar').style.width = data.disk_percent + '%';
                
                // Update system health
                const healthElem = document.getElementById('systemHealth');
                healthElem.className = 'system-health ';
                if (data.cpu_percent > 80 || data.memory_percent > 85 || data.disk_percent > 90) {
                    healthElem.classList.add('health-critical');
                    healthElem.textContent = '⚠️ Critical';
                } else if (data.cpu_percent > 60 || data.memory_percent > 70) {
                    healthElem.classList.add('health-warning');
                    healthElem.textContent = '⚠️ Warning';
                } else {
                    healthElem.classList.add('health-good');
                    healthElem.textContent = '✅ Healthy';
                }
                
                // Update system info
                document.getElementById('infoHostname').textContent = data.hostname;
                document.getElementById('infoOS').textContent = data.os;
                document.getElementById('infoUptime').textContent = data.uptime;
                
            } catch (error) {
                console.error('Error loading system stats:', error);
            }
        }
        
        // Load recent logs
        async function loadRecentLogs() {
            try {
                const response = await fetch('/api/recent-logs');
                const data = await response.json();
                
                const container = document.getElementById('recentLogs');
                if (data.logs.length === 0) {
                    container.innerHTML = '<p class="text-muted">No logs collected yet</p>';
                    return;
                }
                
                let html = '';
                data.logs.forEach(log => {
                    html += `
                    <div class="log-entry">
                        <div class="d-flex justify-content-between">
                            <div>
                                <strong>${log.time}</strong>
                                <div class="text-muted small">${log.file}</div>
                            </div>
                            <div class="text-end">
                                <span class="badge bg-primary">CPU ${log.cpu}%</span>
                                <span class="badge bg-success">Mem ${log.memory}%</span>
                            </div>
                        </div>
                    </div>`;
                });
                
                container.innerHTML = html;
            } catch (error) {
                console.error('Error loading recent logs:', error);
            }
        }
        
        // Load alerts
        async function loadAlerts() {
            try {
                const response = await fetch('/api/recent-alerts');
                const data = await response.json();
                
                const container = document.getElementById('recentAlerts');
                document.getElementById('activeAlerts').textContent = data.count;
                
                if (data.alerts.length === 0) {
                    container.innerHTML = '<p class="text-success">✅ No active alerts</p>';
                    return;
                }
                
                let html = '';
                data.alerts.forEach(alert => {
                    const badgeClass = alert.type === 'critical' ? 'bg-danger' : 'bg-warning';
                    html += `
                    <div class="log-entry">
                        <div class="d-flex align-items-center">
                            <span class="badge ${badgeClass} me-2">${alert.type.toUpperCase()}</span>
                            <div>
                                <strong>${alert.message}</strong>
                                <div class="text-muted small">${alert.time}</div>
                            </div>
                        </div>
                    </div>`;
                });
                
                container.innerHTML = html;
            } catch (error) {
                console.error('Error loading alerts:', error);
            }
        }
        
        // Load GitHub status
        async function loadGitStatus() {
            try {
                const response = await fetch('/api/git-status');
                const data = await response.json();
                
                const container = document.getElementById('gitStatus');
                let html = '';
                
                if (data.connected) {
                    html = `
                    <div class="alert alert-success">
                        <i class="bi bi-check-circle"></i> Connected to GitHub
                        <div class="small mt-2">
                            Last push: ${data.last_push || 'Never'}
                            <br>Commits: ${data.commit_count}
                        </div>
                    </div>`;
                } else {
                    html = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> Not connected to GitHub
                        <div class="small mt-2">
                            Run: git remote add origin git@github.com:USERNAME/Logs-Ubuntu-Zill.git
                        </div>
                    </div>`;
                }
                
                container.innerHTML = html;
            } catch (error) {
                console.error('Error loading Git status:', error);
            }
        }
        
        // Load dashboard stats
        async function loadDashboardStats() {
            try {
                const response = await fetch('/api/dashboard-stats');
                const data = await response.json();
                
                document.getElementById('lastUpdate').textContent = data.last_update;
                document.getElementById('totalLogs').textContent = data.total_logs;
                document.getElementById('infoTodayLogs').textContent = data.today_logs;
            } catch (error) {
                console.error('Error loading dashboard stats:', error);
            }
        }
        
        // Refresh entire dashboard
        async function refreshDashboard() {
            console.log('Refreshing dashboard...');
            await loadSystemStats();
            await loadRecentLogs();
            await loadAlerts();
            await loadGitStatus();
            await loadDashboardStats();
            updateTime();
        }
        
        // Initial load
        document.addEventListener('DOMContentLoaded', function() {
            refreshDashboard();
            
            // Update time every second
            setInterval(updateTime, 1000);
            
            // Update countdown every second
            setInterval(updateCountdown, 1000);
            
            // Auto-refresh dashboard
            setInterval(refreshDashboard, refreshInterval);
        });
    </script>
</body>
</html>
''')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system-stats')
def api_system_stats():
    """Get current system statistics"""
    import platform
    import time
    
    return jsonify({
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "user_count": len(psutil.users()),
        "process_count": len(psutil.pids()),
        "hostname": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "uptime": format_uptime(time.time() - psutil.boot_time())
    })

@app.route('/api/recent-logs')
def api_recent_logs():
    """Get recent log files"""
    logs = []
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(LOG_DIR, "daily", today)
    
    if os.path.exists(today_dir):
        json_files = sorted(glob.glob(os.path.join(today_dir, "*.json")), reverse=True)[:10]
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                logs.append({
                    "file": os.path.basename(file_path),
                    "time": data.get("metadata", {}).get("collection_time", "Unknown"),
                    "cpu": data.get("resources", {}).get("cpu", {}).get("percent", 0),
                    "memory": data.get("resources", {}).get("memory", {}).get("percent", 0)
                })
            except:
                continue
    
    return jsonify({"logs": logs})

@app.route('/api/recent-alerts')
def api_recent_alerts():
    """Get recent alerts"""
    alerts = []
    alert_dir = os.path.join(LOG_DIR, "alerts")
    
    if os.path.exists(alert_dir):
        alert_files = sorted(glob.glob(os.path.join(alert_dir, "*.json")), reverse=True)[:5]
        
        for file_path in alert_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                for alert in data.get("critical_alerts", []):
                    alerts.append({
                        "type": "critical",
                        "message": alert,
                        "time": data.get("timestamp", "Unknown")
                    })
                
                for alert in data.get("warnings", []):
                    alerts.append({
                        "type": "warning",
                        "message": alert,
                        "time": data.get("timestamp", "Unknown")
                    })
            except:
                continue
    
    return jsonify({
        "alerts": alerts[:10],  # Limit to 10 most recent
        "count": len(alerts)
    })

@app.route('/api/git-status')
def api_git_status():
    """Get Git repository status"""
    import subprocess
    
    git_dir = os.path.join(LOG_DIR, ".git")
    
    if not os.path.exists(git_dir):
        return jsonify({"connected": False})
    
    try:
        # Check if connected to remote
        result = subprocess.run(
            ['git', 'remote', '-v'],
            cwd=LOG_DIR,
            capture_output=True,
            text=True
        )
        
        connected = "origin" in result.stdout
        
        # Get last commit
        last_commit = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=relative'],
            cwd=LOG_DIR,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        # Count commits
        commit_count = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            cwd=LOG_DIR,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        return jsonify({
            "connected": connected,
            "last_push": last_commit if last_commit else "Never",
            "commit_count": commit_count if commit_count.isdigit() else "Unknown"
        })
    except:
        return jsonify({"connected": False})

@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    """Get dashboard statistics"""
    total_logs = 0
    today_logs = 0
    
    daily_dir = os.path.join(LOG_DIR, "daily")
    if os.path.exists(daily_dir):
        for root, dirs, files in os.walk(daily_dir):
            for file in files:
                if file.endswith('.json'):
                    total_logs += 1
                    if datetime.now().strftime("%Y-%m-%d") in root:
                        today_logs += 1
    
    return jsonify({
        "total_logs": total_logs,
        "today_logs": today_logs,
        "last_update": datetime.now().strftime("%H:%M:%S")
    })

@app.route('/api/collect')
def api_collect_logs():
    """Trigger log collection"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['python3', os.path.join(LOG_DIR, 'log-collector-enhanced.py')],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            "success": result.returncode == 0,
            "message": result.stdout if result.returncode == 0 else result.stderr
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/report')
def api_generate_report():
    """Generate daily report"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['python3', os.path.join(LOG_DIR, 'daily-report.py')],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            "success": result.returncode == 0,
            "message": "Report generated successfully" if result.returncode == 0 else result.stderr
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/check-alerts')
def api_check_alerts():
    """Check for alerts"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['python3', os.path.join(LOG_DIR, 'alert-system.py')],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            "success": result.returncode == 0,
            "message": "Alert check completed" if result.returncode == 0 else result.stderr
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

def format_uptime(seconds):
    """Format seconds into human readable uptime"""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    if days > 0:
        return f"{int(days)}d {int(hours)}h"
    elif hours > 0:
        return f"{int(hours)}h {int(minutes)}m"
    else:
        return f"{int(minutes)}m"

def open_browser():
    """Open browser to dashboard"""
    import time
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Start browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("🚀 Starting System Logs Dashboard...")
    print("🌐 Open your browser to: http://localhost:5000")
    print("📁 Logs directory: ~/simple-logs")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    app.run(host='127.0.0.1', port=5000, debug=False)