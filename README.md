# Text Polisher

System-wide hotkey tool that rewrites selected text using Claude API. Select text in any app, press a hotkey, and get a polished version auto-pasted in place.

## Features

- **V1 — Core**: Global hotkey (`Ctrl+Shift+P`) to polish selected text via Claude API
- **V2 — Language & Tone**: Tray icon with language (English/French/German) and tone (Professional/Friendly/Informal/Ironic) options
- **V3 — Voice Dictation**: Push-to-talk (`Ctrl+Shift+D`) records audio, transcribes locally with Whisper, and polishes the result

## Requirements

- Python 3.11+
- macOS or Linux (X11)
- [Anthropic API key](https://console.anthropic.com/)

### Platform-specific

**macOS**: No extra dependencies (uses built-in `pbcopy`, `pbpaste`, `osascript`)

**Linux**: Install `xdotool` and `xclip`:
```bash
sudo apt install xdotool xclip  # Debian/Ubuntu
sudo pacman -S xdotool xclip    # Arch
```

## Quick Start

```bash
# Clone and install
git clone <repo-url> text-polisher
cd text-polisher

# Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the installer (creates venv, installs deps, sets up daemon)
./install.sh
```

### Manual Run (without daemon)

```bash
export ANTHROPIC_API_KEY="your-key"
pip install .
python -m text_polisher
```

## Usage

1. Select text in any application
2. Press `Ctrl+Shift+P` — text is polished and pasted back
3. (V3) Hold `Ctrl+Shift+D` — speak while held, release to transcribe and polish

### Tray Menu (V2)

A tray icon appears with options:
- **Language**: English / French / German
- **Tone**: Professional / Friendly / Informal / Ironic
- Settings persist across restarts

## Configuration

Config file: `~/.config/text-polisher/config.toml`

```toml
[hotkeys]
polish = "<ctrl>+<shift>+p"
dictate = "<ctrl>+<shift>+d"

[polish]
language = "english"
tone = "professional"

[whisper]
model = "base"  # tiny | base | small
```

## Uninstall

```bash
./uninstall.sh
```

## macOS Accessibility

Text Polisher needs Accessibility permissions to simulate keystrokes:

**System Settings > Privacy & Security > Accessibility** — add your terminal app (or Python) to the allowed list.

## Security

- **API key**: Stored only in environment variables or `.env` file, never in code
- **No content logging**: Message text is never written to disk or log files. Logs only record events like "Polish hotkey triggered" and "API call completed"
- **Local transcription**: Voice dictation uses a local Whisper model — audio never leaves your machine
- **`.gitignore`**: Pre-configured to exclude `.env`, logs, and any files that could contain secrets
- **Audio handling**: Recorded audio is kept in memory only, never saved to disk

## Troubleshooting

**Hotkey not working (macOS)**: Grant Accessibility permissions (see above)

**Hotkey not working (Linux)**: Ensure X11 (not Wayland). Install `xdotool` and `xclip`.

**"ANTHROPIC_API_KEY not set"**: Export the key or add it to `~/.config/text-polisher/.env`

**Logs**: Check `~/.config/text-polisher/polisher.log`
