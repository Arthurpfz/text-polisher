import platform
import subprocess
import time
import logging

logger = logging.getLogger("text_polisher")

_IS_MAC = platform.system() == "Darwin"


def copy_selection() -> str:
    """Simulate Cmd+C / Ctrl+C on the focused app, then read clipboard."""
    if _IS_MAC:
        subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to keystroke "c" using command down'],
            timeout=2,
            capture_output=True,
        )
    else:
        subprocess.run(["xdotool", "key", "ctrl+c"], timeout=2, capture_output=True)

    time.sleep(0.15)

    if _IS_MAC:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2)
    else:
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o"],
            capture_output=True, text=True, timeout=2,
        )
    return result.stdout


def paste_text(text: str) -> None:
    """Write text to clipboard, then simulate Cmd+V / Ctrl+V."""
    if _IS_MAC:
        subprocess.run(["pbcopy"], input=text, text=True, timeout=2, capture_output=True)
        time.sleep(0.05)
        subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to keystroke "v" using command down'],
            timeout=2,
            capture_output=True,
        )
    else:
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text, text=True, timeout=2, capture_output=True,
        )
        time.sleep(0.05)
        subprocess.run(["xdotool", "key", "ctrl+v"], timeout=2, capture_output=True)
