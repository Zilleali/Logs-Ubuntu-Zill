# 📊 Ubuntu System Logging & Monitoring System

## 🚀 Overview

A comprehensive, automated system monitoring solution for Ubuntu that
collects system metrics, generates alerts, creates daily reports,
provides a web dashboard, and automatically backs up logs to GitHub.
Built with Python and Systemd for reliable, scheduled automation.

## ✨ Features

### 📈 Core Monitoring

-   **System Metrics:** CPU, memory, disk, network, and process
    monitoring\
-   **User Activity:** Login tracking, session monitoring, and user
    analytics\
-   **Resource Analytics:** Historical data collection with 30-day
    retention\
-   **Performance Metrics:** Real-time system performance tracking

### 🔔 Intelligent Alerts

-   **Smart Thresholds:** Configurable alerts for high resource usage\
-   **Multi-level Alerts:** Warning (80--90%) and Critical (\>90%)
    notifications\
-   **Security Monitoring:** Failed login attempts and suspicious
    activity detection\
-   **Desktop Notifications:** Real-time system tray alerts

### 📊 Reporting & Analytics

-   Daily Reports with insights\
-   Matplotlib visual charts\
-   Export in JSON, Markdown, and text formats\
-   Recommendations for system optimization

### 🌐 Web Dashboard

-   Real-time charts\
-   Mobile responsive interface\
-   REST API\
-   Quick system control buttons

### 🔄 Automation & Integration

-   Systemd-based automation\
-   GitHub backup\
-   Self-healing services\
-   Easy configuration backup

## 🏗️ Architecture

``` mermaid
graph TB
    A[Data Collection<br/>psutil] --> B[Processing & Analysis<br/>Python]
    B --> C[Storage & Backup<br/>GitHub]
    A --> D[Systemd Timers<br/>Automation]
    B --> E[Web Dashboard<br/>Flask]
    B --> F[Alerts & Notifications<br/>notify-send]

    style A fill:#fffff
    style B fill:#fffff
    style C fill:#fffff
    style D fill:#fffff
    style E fill:#fffff
    style F fill:#fffff
```

## 📁 Project Structure

    simple-logs/
    ├── daily/
    │   ├── 2024-12-09/
    │   │   ├── system_log_14-30-00.json
    │   │   └── summary_14-30.txt
    │   └── ...
    ├── alerts/
    ├── reports/
    ├── backup/
    ├── .vscode/
    ├── log-collector-enhanced.py
    ├── alert-system.py
    ├── daily-report.py
    ├── dashboard.py
    ├── git-upload.sh
    ├── logs-manager.sh
    ├── requirements.txt
    ├── install-deps.sh
    ├── check-imports.py
    └── README.md

## 🚀 Quick Start

### **Prerequisites**

-   Ubuntu 20.04+
-   Python 3.8+
-   Git with SSH
-   Systemd

### **Installation**

``` bash
cd ~
git clone <your-repo-url> simple-logs
cd simple-logs
./install-deps.sh
./logs-manager.sh setup
./logs-manager.sh start
./logs-manager.sh dashboard
```

## 🛠️ Configuration

### **GitHub Sync**

``` bash
cd ~/simple-logs
git remote add origin git@github.com:yourusername/Logs-Ubuntu-Zill.git
./git-upload.sh
```

### **Alert Thresholds**

``` python
CPU_CRITICAL = 90
CPU_WARNING = 80
MEMORY_CRITICAL = 95
MEMORY_WARNING = 85
DISK_CRITICAL = 95
DISK_WARNING = 90
```

## 📊 Automation Schedule

  Component        Frequency       Time           Description
  ---------------- --------------- -------------- ------------------
  Log Collection   Every 30 min    \*/30          Collects metrics
  Alert Checks     Hourly          0 \*           Checks alerts
  GitHub Backup    Every 2 hours   \*/2           Push backup
  Daily Reports    Daily           23:30          Generates report
  Log Cleanup      Monthly         1st of month   Removes old logs

## 🎛️ Management Commands

``` bash
./logs-manager.sh start
./logs-manager.sh stop
./logs-manager.sh collect
./logs-manager.sh report
./logs-manager.sh dashboard
```

## 🌐 Web Dashboard

Visit: **http://localhost:5000**

-   Real-time metrics\
-   Historical charts\
-   Quick actions\
-   GitHub sync status

## 🔧 Troubleshooting

``` bash
sudo apt install python3-psutil python3-flask python3-matplotlib python3-pandas
systemctl --user daemon-reload
journalctl --user -u simple-logs-collect.service -f
```

## 📈 Data Collected

-   CPU, memory, disk\
-   Network usage\
-   Processes\
-   Logins\
-   Services\
-   Temperature\
-   Battery

## 🔐 Security

-   Local storage\
-   Optional GitHub sync\
-   600 file permissions\
-   SSH authentication

## 🛠️ Development

-   Add metrics\
-   Add dashboard widgets\
-   Run tests\
-   Follow PEP 8

## 🤝 Contributing

Fork → Branch → Commit → PR

## 📄 License

MIT License

## ⭐ Support

GitHub Issues\
Email support\
Community discussions

*Last Updated: 2024 \| Version 2.0.0*
