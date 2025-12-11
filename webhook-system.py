#!/usr/bin/env python3
"""
Webhook system for external notifications
"""

import requests
import json
import os
from datetime import datetime

class WebhookManager:
    def __init__(self):
        self.config_file = os.path.expanduser("~/simple-logs/webhooks.json")
        self.webhooks = self.load_config()
    
    def load_config(self):
        """Load webhook configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            'discord': None,
            'slack': None,
            'telegram': None,
            'custom': []
        }
    
    def save_config(self):
        """Save webhook configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.webhooks, f, indent=2)
    
    def send_alert(self, alert_data, webhook_type='all'):
        """Send alert to configured webhooks"""
        sent = []
        
        # Discord webhook
        if webhook_type in ['all', 'discord'] and self.webhooks.get('discord'):
            try:
                self.send_discord(alert_data, self.webhooks['discord'])
                sent.append('discord')
            except Exception as e:
                print(f"Discord webhook failed: {e}")
        
        # Slack webhook
        if webhook_type in ['all', 'slack'] and self.webhooks.get('slack'):
            try:
                self.send_slack(alert_data, self.webhooks['slack'])
                sent.append('slack')
            except Exception as e:
                print(f"Slack webhook failed: {e}")
        
        # Custom webhooks
        for webhook in self.webhooks.get('custom', []):
            try:
                self.send_custom(alert_data, webhook)
                sent.append(f"custom:{webhook.get('name', 'unknown')}")
            except Exception as e:
                print(f"Custom webhook failed: {e}")
        
        return sent
    
    def send_discord(self, alert_data, webhook_url):
        """Send to Discord webhook"""
        color = 0xff0000 if alert_data.get('severity') == 'CRITICAL' else 0xff9900
        
        embed = {
            "title": f"🚨 System Alert: {alert_data.get('type', 'Unknown')}",
            "description": alert_data.get('message', 'No message'),
            "color": color,
            "fields": [
                {"name": "Severity", "value": alert_data.get('severity', 'UNKNOWN'), "inline": True},
                {"name": "Time", "value": alert_data.get('timestamp', datetime.now().isoformat()), "inline": True},
                {"name": "Host", "value": alert_data.get('hostname', 'Unknown'), "inline": True}
            ],
            "footer": {"text": "System Logs Monitor"}
        }
        
        payload = {
            "embeds": [embed],
            "username": "System Monitor"
        }
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    
    def send_slack(self, alert_data, webhook_url):
        """Send to Slack webhook"""
        color = "danger" if alert_data.get('severity') == 'CRITICAL' else "warning"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 System Alert: {alert_data.get('type', 'Unknown')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{alert_data.get('severity', 'UNKNOWN')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{alert_data.get('timestamp', 'Unknown')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Message:*\n{alert_data.get('message', 'No message')}"
                }
            }
        ]
        
        payload = {"blocks": blocks}
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    
    def send_custom(self, alert_data, webhook_config):
        """Send to custom webhook"""
        url = webhook_config.get('url')
        method = webhook_config.get('method', 'POST')
        headers = webhook_config.get('headers', {})
        template = webhook_config.get('template', {})
        
        # Apply template
        if template:
            payload = template.copy()
            # Replace variables
            import string
            template_str = json.dumps(payload)
            formatter = string.Formatter()
            
            for _, field, _, _ in formatter.parse(template_str):
                if field in alert_data:
                    template_str = template_str.replace(f'{{{field}}}', str(alert_data[field]))
            
            payload = json.loads(template_str)
        else:
            payload = alert_data
        
        if method.upper() == 'POST':
            response = requests.post(url, json=payload, headers=headers)
        elif method.upper() == 'GET':
            response = requests.get(url, params=payload, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
    
    def add_webhook(self, name, config):
        """Add new webhook"""
        if name == 'discord':
            self.webhooks['discord'] = config['url']
        elif name == 'slack':
            self.webhooks['slack'] = config['url']
        elif name == 'custom':
            self.webhooks.setdefault('custom', []).append(config)
        
        self.save_config()
        print(f"✅ Webhook '{name}' added")

# Example usage
if __name__ == "__main__":
    manager = WebhookManager()
    
    # Example alert
    test_alert = {
        'type': 'HIGH_CPU',
        'severity': 'CRITICAL',
        'message': 'CPU usage is at 95%',
        'timestamp': datetime.now().isoformat(),
        'hostname': 'server-01',
        'value': 95
    }
    
    print("Testing webhooks...")
    sent = manager.send_alert(test_alert)
    
    if sent:
        print(f"✅ Alerts sent to: {', '.join(sent)}")
    else:
        print("ℹ️ No webhooks configured")
        print("\nTo configure webhooks, edit:")
        print("  ~/simple-logs/webhooks.json")
        print("\nOr use the webhook manager API")