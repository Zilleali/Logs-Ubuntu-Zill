#!/usr/bin/env python3
"""
System audit logging for security events
"""

import json
import os
import subprocess
from datetime import datetime
import hashlib

class SystemAuditor:
    def __init__(self):
        self.audit_dir = os.path.expanduser("~/simple-logs/audit")
        os.makedirs(self.audit_dir, exist_ok=True)
    
    def log_event(self, event_type, description, severity="INFO", user=None):
        """Log security event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'description': description,
            'severity': severity,
            'user': user or os.getenv('USER', 'unknown'),
            'hostname': os.uname().nodename
        }
        
        # Save to daily audit file
        date_str = datetime.now().strftime("%Y-%m-%d")
        audit_file = os.path.join(self.audit_dir, f"audit_{date_str}.jsonl")
        
        with open(audit_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Print to console if critical
        if severity in ["CRITICAL", "HIGH"]:
            print(f"🚨 {severity}: {description}")
        
        return event
    
    def check_suspicious_activity(self):
        """Check for suspicious system activity"""
        events = []
        
        # Check for failed logins
        try:
            result = subprocess.run(
                ['grep', 'Failed password', '/var/log/auth.log'],
                capture_output=True,
                text=True
            )
            failed_count = len(result.stdout.strip().split('\n'))
            if failed_count > 5:
                events.append(self.log_event(
                    'FAILED_LOGINS',
                    f'High failed login attempts: {failed_count}',
                    'HIGH'
                ))
        except:
            pass
        
        # Check for sudo usage
        try:
            result = subprocess.run(
                ['sudo', 'tail', '-20', '/var/log/auth.log'],
                capture_output=True,
                text=True
            )
            if 'sudo' in result.stdout:
                events.append(self.log_event(
                    'SUDO_USAGE',
                    'Sudo command executed',
                    'INFO'
                ))
        except:
            pass
        
        # Check file integrity (simple example)
        critical_files = ['/etc/passwd', '/etc/shadow', '/etc/sudoers']
        for file in critical_files:
            if os.path.exists(file):
                mtime = os.path.getmtime(file)
                if datetime.now().timestamp() - mtime < 3600:  # Modified in last hour
                    events.append(self.log_event(
                        'FILE_MODIFIED',
                        f'Critical file modified: {file}',
                        'MEDIUM'
                    ))
        
        return events
    
    def generate_audit_report(self):
        """Generate daily audit report"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        audit_file = os.path.join(self.audit_dir, f"audit_{date_str}.jsonl")
        
        if not os.path.exists(audit_file):
            return None
        
        events = []
        with open(audit_file, 'r') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        # Generate report
        report = {
            'date': date_str,
            'total_events': len(events),
            'by_severity': {},
            'by_type': {},
            'events': events[-50:]  # Last 50 events
        }
        
        for event in events:
            report['by_severity'][event['severity']] = report['by_severity'].get(event['severity'], 0) + 1
            report['by_type'][event['type']] = report['by_type'].get(event['type'], 0) + 1
        
        # Save report
        report_file = os.path.join(self.audit_dir, f"report_{date_str}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📋 Audit report generated: {report_file}")
        return report_file

def main():
    """Main audit function"""
    auditor = SystemAuditor()
    
    print("🔍 Running security audit...")
    
    # Check for suspicious activity
    events = auditor.check_suspicious_activity()
    
    # Generate report
    report = auditor.generate_audit_report()
    
    if events:
        print(f"🚨 Found {len(events)} security events")
        for event in events:
            print(f"  • {event['severity']}: {event['description']}")
    else:
        print("✅ No security issues found")
    
    return len(events) > 0

if __name__ == "__main__":
    main()