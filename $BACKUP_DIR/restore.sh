#!/bin/bash
# Restore logs system configuration

echo "Restoring logs system configuration..."

# Restore systemd files
cp -r simple-logs-* ~/.config/systemd/user/ 2>/dev/null || true

# Restore manager script
cp logs-manager.sh ~/

# Make executable
chmod +x ~/logs-manager.sh

# Reload systemd
systemctl --user daemon-reload

echo "✅ Configuration restored!"
echo "Run: ~/logs-manager.sh setup"
RESTORE

chmod +x "$BACKUP_DIR/restore.sh"

echo "✅ Backup complete!"
echo "To restore: cd $BACKUP_DIR && ./restore.sh"