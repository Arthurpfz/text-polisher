#!/bin/bash
set -e

INSTALL_DIR="$HOME/.config/text-polisher"
VENV_DIR="$INSTALL_DIR/venv"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Text Polisher Installer ==="

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Darwin) PLATFORM="macos" ;;
    Linux)  PLATFORM="linux" ;;
    *)      echo "Error: Unsupported OS ($OS)"; exit 1 ;;
esac
echo "Platform: $PLATFORM"

# Check Python >= 3.11
PYTHON=""
for cmd in python3.13 python3.12 python3.11 python3; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Error: Python >= 3.11 required. Install it first."
    exit 1
fi
echo "Python: $PYTHON ($($PYTHON --version))"

# Check platform dependencies
if [ "$PLATFORM" = "linux" ]; then
    for dep in xdotool xclip; do
        if ! command -v "$dep" &>/dev/null; then
            echo "Error: $dep not found. Install it: sudo apt install $dep"
            exit 1
        fi
    done
    echo "Linux dependencies: OK"
fi

# Create venv and install
echo "Creating virtual environment..."
mkdir -p "$INSTALL_DIR"
"$PYTHON" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "Installing text-polisher..."
pip install --quiet --upgrade pip
pip install --quiet "$SCRIPT_DIR"

# Install platform extras
if [ "$PLATFORM" = "macos" ]; then
    pip install --quiet "$SCRIPT_DIR[tray-macos]" 2>/dev/null || true
elif [ "$PLATFORM" = "linux" ]; then
    pip install --quiet "$SCRIPT_DIR[tray-linux]" 2>/dev/null || true
fi

# Create .env if not exists
if [ ! -f "$INSTALL_DIR/.env" ]; then
    if [ -f "$SCRIPT_DIR/.env" ]; then
        cp "$SCRIPT_DIR/.env" "$INSTALL_DIR/.env"
    else
        cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env"
        echo ""
        echo "IMPORTANT: Edit $INSTALL_DIR/.env and add your ANTHROPIC_API_KEY"
    fi
fi

# Get the venv python path
VENV_PYTHON="$VENV_DIR/bin/python"

# Setup daemon
if [ "$PLATFORM" = "macos" ]; then
    PLIST="$HOME/Library/LaunchAgents/com.text-polisher.plist"
    API_KEY="${ANTHROPIC_API_KEY:-$(grep ANTHROPIC_API_KEY "$INSTALL_DIR/.env" 2>/dev/null | cut -d= -f2 || echo '')}"
    cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.text-polisher</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PYTHON</string>
        <string>-m</string>
        <string>text_polisher</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>ANTHROPIC_API_KEY</key>
        <string>$API_KEY</string>
    </dict>
    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/daemon.log</string>
    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/daemon.log</string>
</dict>
</plist>
PLISTEOF
    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load "$PLIST"
    echo "Daemon installed and started (launchd)"

    echo ""
    echo "IMPORTANT: Grant Accessibility permissions!"
    echo "System Settings > Privacy & Security > Accessibility"
    echo "Add your terminal app and/or Python to the list."

elif [ "$PLATFORM" = "linux" ]; then
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
    SERVICE_FILE="$SERVICE_DIR/text-polisher.service"
    API_KEY="${ANTHROPIC_API_KEY:-$(grep ANTHROPIC_API_KEY "$INSTALL_DIR/.env" 2>/dev/null | cut -d= -f2 || echo '')}"
    cat > "$SERVICE_FILE" <<SVCEOF
[Unit]
Description=Text Polisher
After=graphical-session.target

[Service]
ExecStart=$VENV_PYTHON -m text_polisher
WorkingDirectory=$INSTALL_DIR
Restart=on-failure
Environment=ANTHROPIC_API_KEY=$API_KEY
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
SVCEOF
    systemctl --user daemon-reload
    systemctl --user enable text-polisher
    systemctl --user restart text-polisher
    echo "Daemon installed and started (systemd)"
fi

echo ""
echo "=== Installation complete ==="
echo "Config: $INSTALL_DIR/config.toml"
echo "Logs:   $INSTALL_DIR/polisher.log"
