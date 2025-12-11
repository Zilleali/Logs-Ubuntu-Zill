#!/usr/bin/env python3
"""
Maintenance and backup utilities
"""

import os
import shutil
import json
import tarfile
from datetime import datetime, timedelta
import subprocess

class LogMaintenance:
    def __init__(self, base_dir="~/simple-logs"):
        self.base_dir = os.path.expanduser(base_dir)
        
    def cleanup_old_logs(self, retention_days=30):
        """Clean up logs older than retention period"""
        logs_dir = os.path.join(self.base_dir, "daily")
        removed = []
        
        if not os.path.exists(logs_dir):
            return removed
        
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        for date_dir in os.listdir(logs_dir):
            try:
                dir_date = datetime.strptime(date_dir, "%Y-%m-%d")
                if dir_date < cutoff:
                    dir_path = os.path.join(logs_dir, date_dir)
                    shutil.rmtree(dir_path)
                    removed.append(date_dir)
                    print(f"Removed old logs: {date_dir}")
            except ValueError:
                continue
        
        return removed
    
    def create_backup(self, backup_dir="~/simple-logs/backups"):
        """Create backup of all logs and configuration"""
        backup_dir = os.path.expanduser(backup_dir)
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"logs_backup_{timestamp}.tar.gz")
        
        with tarfile.open(backup_file, "w:gz") as tar:
            # Add log directories
            for dir_name in ["daily", "alerts", "audit", "reports"]:
                dir_path = os.path.join(self.base_dir, dir_name)
                if os.path.exists(dir_path):
                    tar.add(dir_path, arcname=dir_name)
            
            # Add configuration files
            for file_name in ["config.json", "webhooks.json"]:
                file_path = os.path.join(self.base_dir, file_name)
                if os.path.exists(file_path):
                    tar.add(file_path, arcname=file_name)
            
            # Add scripts
            for script in os.listdir(self.base_dir):
                if script.endswith('.py'):
                    tar.add(os.path.join(self.base_dir, script), arcname=f"scripts/{script}")
        
        # Compress further if large
        if os.path.getsize(backup_file) > 100 * 1024 * 1024:  # > 100MB
            subprocess.run(["gzip", "-f", backup_file])
            backup_file += ".gz"
        
        print(f"Backup created: {backup_file}")
        print(f"Size: {os.path.getsize(backup_file) / (1024*1024):.1f} MB")
        
        return backup_file
    
    def verify_integrity(self):
        """Verify integrity of log files"""
        issues = []
        logs_dir = os.path.join(self.base_dir, "daily")
        
        if not os.path.exists(logs_dir):
            return issues
        
        for date_dir in os.listdir(logs_dir):
            date_path = os.path.join(logs_dir, date_dir)
            if not os.path.isdir(date_path):
                continue
            
            for file in os.listdir(date_path):
                if file.endswith('.json'):
                    file_path = os.path.join(date_path, file)
                    try:
                        with open(file_path, 'r') as f:
                            json.load(f)
                    except json.JSONDecodeError as e:
                        issues.append(f"Invalid JSON in {file_path}: {e}")
                    except Exception as e:
                        issues.append(f"Error reading {file_path}: {e}")
        
        return issues
    
    def generate_report(self):
        """Generate maintenance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "backups": {},
            "cleanup": {},
            "integrity": {}
        }
        
        # Check backup directory
        backup_dir = os.path.join(self.base_dir, "backups")
        if os.path.exists(backup_dir):
            backups = sorted([
                f for f in os.listdir(backup_dir) 
                if f.startswith('logs_backup_') and (f.endswith('.tar.gz') or f.endswith('.tar.gz.gz'))
            ], reverse=True)
            
            report["backups"] = {
                "count": len(backups),
                "latest": backups[0] if backups else None,
                "total_size_mb": sum(
                    os.path.getsize(os.path.join(backup_dir, f)) 
                    for f in backups
                ) / (1024*1024)
            }
        
        # Run cleanup
        removed = self.cleanup_old_logs()
        report["cleanup"] = {
            "removed_directories": removed,
            "count": len(removed)
        }
        
        # Check integrity
        issues = self.verify_integrity()
        report["integrity"] = {
            "issues": issues,
            "count": len(issues),
            "status": "PASS" if not issues else "FAIL"
        }
        
        # Save report
        reports_dir = os.path.join(self.base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        report_file = os.path.join(reports_dir, f"maintenance_{datetime.now().strftime('%Y%m%d')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def main():
    """Main maintenance function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Log Maintenance Utilities")
    parser.add_argument("action", choices=["cleanup", "backup", "verify", "report", "all"])
    parser.add_argument("--retention-days", type=int, default=30, help="Days to keep logs")
    parser.add_argument("--backup-dir", default="~/simple-logs/backups", help="Backup directory")
    
    args = parser.parse_args()
    maintenance = LogMaintenance()
    
    if args.action == "cleanup":
        removed = maintenance.cleanup_old_logs(args.retention_days)
        print(f"Cleaned up {len(removed)} old log directories")
        if removed:
            print("Removed:", ", ".join(removed))
    
    elif args.action == "backup":
        backup_file = maintenance.create_backup(args.backup_dir)
        print(f"Backup created: {backup_file}")
    
    elif args.action == "verify":
        issues = maintenance.verify_integrity()
        if issues:
            print(f"Found {len(issues)} integrity issues:")
            for issue in issues:
                print(f"  ❌ {issue}")
        else:
            print("✅ All log files are valid")
    
    elif args.action == "report":
        report = maintenance.generate_report()
        print("Maintenance Report:")
        print(f"  Backups: {report['backups']['count']} files, {report['backups']['total_size_mb']:.1f} MB")
        print(f"  Cleanup: Removed {report['cleanup']['count']} directories")
        print(f"  Integrity: {report['integrity']['status']} ({report['integrity']['count']} issues)")
    
    elif args.action == "all":
        print("Running complete maintenance...")
        print("1. Creating backup...")
        maintenance.create_backup()
        
        print("2. Cleaning up old logs...")
        maintenance.cleanup_old_logs(args.retention_days)
        
        print("3. Verifying integrity...")
        issues = maintenance.verify_integrity()
        
        print("4. Generating report...")
        report = maintenance.generate_report()
        
        print("\n✅ Maintenance complete!")
        if issues:
            print(f"⚠️  Found {len(issues)} integrity issues")
        else:
            print("✅ All checks passed")

if __name__ == "__main__":
    main()