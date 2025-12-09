#!/usr/bin/env python3
"""
Generate daily summary reports
"""

import json
import os
import glob
from datetime import datetime, timedelta
import statistics

def generate_daily_report():
    """Generate report for today's logs"""
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")
    
    # Find today's log files
    log_pattern = os.path.expanduser(f"~/simple-logs/daily/{today_str}/*.json")
    log_files = glob.glob(log_pattern)
    
    if not log_files:
        print(f"No logs found for {today_str}")
        return
    
    # Collect data from all logs
    all_cpu = []
    all_memory = []
    all_disk = []
    timestamps = []
    
    for log_file in sorted(log_files):
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
                
            if 'resources' in data:
                all_cpu.append(data['resources']['cpu_percent'])
                all_memory.append(data['resources']['memory_percent'])
                all_disk.append(data['resources']['disk_percent'])
                timestamps.append(data.get('collection_time', 'Unknown'))
        except:
            continue
    
    if not all_cpu:
        print("No valid data found")
        return
    
    # Calculate statistics
    report = {
        "date": today_str,
        "total_logs": len(log_files),
        "time_period": f"{timestamps[0]} to {timestamps[-1]}" if timestamps else "Unknown",
        "cpu": {
            "average": round(statistics.mean(all_cpu), 1),
            "max": round(max(all_cpu), 1),
            "min": round(min(all_cpu), 1),
            "trend": "↑" if all_cpu[-1] > all_cpu[0] else "↓"
        },
        "memory": {
            "average": round(statistics.mean(all_memory), 1),
            "max": round(max(all_memory), 1),
            "min": round(min(all_memory), 1)
        },
        "disk": {
            "average": round(statistics.mean(all_disk), 1),
            "current": all_disk[-1]
        }
    }
    
    # Save report
    report_dir = os.path.expanduser("~/simple-logs/reports")
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"report_{today_str}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Create readable summary
    summary_file = os.path.join(report_dir, f"summary_{today_str}.md")
    with open(summary_file, 'w') as f:
        f.write(f"# Daily System Report - {today_str}\n\n")
        f.write(f"**Period:** {report['time_period']}\n")
        f.write(f"**Total Logs:** {report['total_logs']}\n\n")
        
        f.write("## 📊 CPU Usage\n")
        f.write(f"- Average: {report['cpu']['average']}%\n")
        f.write(f"- Maximum: {report['cpu']['max']}%\n")
        f.write(f"- Minimum: {report['cpu']['min']}%\n")
        f.write(f"- Trend: {report['cpu']['trend']}\n\n")
        
        f.write("## 🎯 Memory Usage\n")
        f.write(f"- Average: {report['memory']['average']}%\n")
        f.write(f"- Maximum: {report['memory']['max']}%\n")
        f.write(f"- Minimum: {report['memory']['min']}%\n\n")
        
        f.write("## 💾 Disk Usage\n")
        f.write(f"- Average: {report['disk']['average']}%\n")
        f.write(f"- Current: {report['disk']['current']}%\n\n")
        
        f.write("---\n")
        f.write(f"*Report generated at {datetime.now().strftime('%H:%M:%S')}*\n")
    
    print(f"✅ Daily report generated: {summary_file}")
    
    # Print quick summary
    print(f"\n📈 Today's Summary ({today_str}):")
    print(f"   Logs collected: {report['total_logs']}")
    print(f"   Avg CPU: {report['cpu']['average']}% (Max: {report['cpu']['max']}%)")
    print(f"   Avg Memory: {report['memory']['average']}%")
    print(f"   Current Disk: {report['disk']['current']}%")

def main():
    generate_daily_report()

if __name__ == "__main__":
    main()