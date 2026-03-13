#!/bin/bash
set -e

INSTALL_DIR="$HOME/.config/text-polisher"

echo "=== Text Polisher Uninstaller ==="

OS="$(uname -s)"

# Stop and remove daemon
if [ "$OS" = "Darwin" ]; then
    PLIST="$HOME/Library/LaunchAgents/com.text-polisher.plist"
    if [ -f "$PLIST" ]; then
        launchctl unload "$PLIST" 2>/dev/null || true
        rm -f "$PLIST"
        echo "Removed launchd daemon"
    fi
elif [ "$OS" = "Linux" ]; then
    systemctl --user stop text-polisher 2>/dev/null || true
    systemctl --user disable text-polisher 2>/dev/null || true
    rm -f "$HOME/.config/systemd/user/text-polisher.service"
    systemctl --user daemon-reload 2>/dev/null || true
    echo "Removed systemd service"
fi

# Remove venv
if [ -d "$INSTALL_DIR/venv" ]; then
    rm -rf "$INSTALL_DIR/venv"
    echo "Removed virtual environment"
fi

# Ask about config
read -p "Remove config and logs ($INSTALL_DIR)? [y/N] " answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    rm -rf "$INSTALL_DIR"
    echo "Removed config directory"
else
    echo "Kept config directory"
fi

echo ""
echo "=== Uninstall complete ==="
