#!/bin/bash
# Backup logs system configuration

BACKUP_DIR="$HOME/simple-logs/backup/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

echo "Backing up configuration to: $BACKUP_DIR"

# Backup systemd files
cp -r ~/.config/systemd/user/simple-logs-* "$BACKUP_DIR/" 2>/dev/null || true

# Backup scripts
cp ~/logs-manager.sh "$BACKUP_DIR/"
cp ~/simple-logs/*.py "$BACKUP_DIR/"
cp ~/simple-logs/*.sh "$BACKUP_DIR/"
