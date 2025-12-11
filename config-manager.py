#!/usr/bin/env python3
"""
Configuration manager for the logging system
"""

import json
import os
import sys
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file="~/simple-logs/config.json"):
        self.config_file = os.path.expanduser(config_file)
        self.default_config = {
            "system": {
                "log_interval": 300,  # 5 minutes
                "retention_days": 30,
                "compression": True,
                "encryption": False
            },
            "alerts": {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "disk_threshold": 90,
                "enable_email": False,
                "enable_webhook": False
            },
            "api": {
                "enabled": True,
                "port": 8080,
                "auth_required": True,
                "cors_enabled": True
            },
            "dashboard": {
                "port": 5001,
                "realtime_updates": True,
                "update_interval": 5
            },
            "paths": {
                "logs": "~/simple-logs/daily",
                "backups": "~/simple-logs/backups",
                "alerts": "~/simple-logs/alerts",
                "reports": "~/simple-logs/reports"
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                print(f"Error loading config, using defaults")
                return self.default_config
        else:
            return self.default_config
    
    def save_config(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def update_setting(self, section, key, value):
        """Update a specific setting"""
        if section in self.config:
            self.config[section][key] = value
        else:
            self.config[section] = {key: value}
        self.save_config()
    
    def get_setting(self, section, key, default=None):
        """Get a specific setting"""
        return self.config.get(section, {}).get(key, default)
    
    def validate_config(self):
        """Validate configuration settings"""
        errors = []
        
        # Check required paths
        required_paths = ["logs", "alerts"]
        for path_key in required_paths:
            path = self.get_setting("paths", path_key)
            if path:
                full_path = os.path.expanduser(path)
                try:
                    os.makedirs(full_path, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create path {full_path}: {e}")
        
        # Validate thresholds
        thresholds = ["cpu_threshold", "memory_threshold", "disk_threshold"]
        for threshold in thresholds:
            value = self.get_setting("alerts", threshold, 80)
            if not 0 <= value <= 100:
                errors.append(f"Invalid {threshold}: {value}. Must be 0-100")
        
        return errors
    
    def generate_config_report(self):
        """Generate configuration report"""
        report = {
            "config_file": self.config_file,
            "exists": os.path.exists(self.config_file),
            "settings": self.config,
            "validation_errors": self.validate_config(),
            "paths": {}
        }
        
        # Check all paths
        for key, path in self.config.get("paths", {}).items():
            full_path = os.path.expanduser(path)
            report["paths"][key] = {
                "path": full_path,
                "exists": os.path.exists(full_path),
                "is_dir": os.path.isdir(full_path) if os.path.exists(full_path) else None
            }
        
        return report

# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuration Manager")
    parser.add_argument("action", choices=["show", "set", "validate", "report"])
    parser.add_argument("--section", help="Configuration section")
    parser.add_argument("--key", help="Configuration key")
    parser.add_argument("--value", help="Value to set")
    
    args = parser.parse_args()
    config = ConfigManager()
    
    if args.action == "show":
        if args.section:
            if args.key:
                value = config.get_setting(args.section, args.key)
                print(f"{args.section}.{args.key} = {value}")
            else:
                section_data = config.config.get(args.section, {})
                print(json.dumps(section_data, indent=2))
        else:
            print(json.dumps(config.config, indent=2))
    
    elif args.action == "set":
        if args.section and args.key and args.value:
            # Try to convert value type
            try:
                if args.value.lower() in ["true", "false"]:
                    value = args.value.lower() == "true"
                elif args.value.isdigit():
                    value = int(args.value)
                elif args.value.replace('.', '', 1).isdigit():
                    value = float(args.value)
                else:
                    value = args.value
                
                config.update_setting(args.section, args.key, value)
                print(f"Updated {args.section}.{args.key} = {value}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Error: --section, --key, and --value required for set action")
    
    elif args.action == "validate":
        errors = config.validate_config()
        if errors:
            print("Validation Errors:")
            for error in errors:
                print(f"  ❌ {error}")
        else:
            print("✅ Configuration is valid")
    
    elif args.action == "report":
        report = config.generate_config_report()
        print(json.dumps(report, indent=2))